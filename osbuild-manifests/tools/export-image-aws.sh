#!/usr/bin/env bash
# SPDX-License-Identifier: MIT-0
set -e
[ "$DEBUG" == 'true' ] && set -x

ARGC=$#
if [ $ARGC -ne 3 ]; then
    echo "USAGE: $(basename $0) <Image Path> <S3 Bucket Name> <AMI Image Size in GB>"
    exit 1
fi
IMAGE_FILE_PATH=$1
IMPORT_BUCKET_NAME=$2
AMI_DISK_SIZE_GB=$3

declare -A ARCHS_MAP=( ["x86_64"]="x86_64" ["aarch64"]="arm64")

IMAGE_NAME="$(basename -- ${IMAGE_FILE_PATH})"
AMI_NAME="${IMAGE_NAME%.*}"
IMAGE_ARCH="${AMI_NAME##*.}"

TMPDIR=$(mktemp -d)
IMAGE_IMPORT_JSON_FILE="${TMPDIR}/image-import.json"
AMI_REGISTER_JSON_FILE="${TMPDIR}/register-ami.json"

aws s3 cp "${IMAGE_FILE_PATH}" "s3://${IMPORT_BUCKET_NAME}"

cat <<EOF > "${IMAGE_IMPORT_JSON_FILE}"
{
    "Description": "CentOS Stream 9 with Container support",
    "Format": "RAW",
    "UserBucket": {
        "S3Bucket": "${IMPORT_BUCKET_NAME}",
        "S3Key": "${IMAGE_NAME}"
    }
}
EOF

echo "Importing image file into snapshot "
IMPORT_TASK_ID=$(aws ec2 import-snapshot --disk-container "file://${IMAGE_IMPORT_JSON_FILE}" | jq -r '.ImportTaskId')

IMPORT_STATUS=$(aws ec2 describe-import-snapshot-tasks --import-task-ids $IMPORT_TASK_ID | jq -r '.ImportSnapshotTasks[].SnapshotTaskDetail.Status')
x=0
while [ "$IMPORT_STATUS" = "active" ] && [ $x -lt 120 ]
do
  IMPORT_STATUS=$(aws ec2 describe-import-snapshot-tasks --import-task-ids $IMPORT_TASK_ID | jq -r '.ImportSnapshotTasks[].SnapshotTaskDetail.Status')
  IMPORT_STATUS_MSG=$(aws ec2 describe-import-snapshot-tasks --import-task-ids $IMPORT_TASK_ID | jq -r '.ImportSnapshotTasks[].SnapshotTaskDetail.StatusMessage')
  echo "Import Status: ${IMPORT_STATUS} / ${IMPORT_STATUS_MSG}"
  x=$(( $x + 1 ))
  sleep 15
done
if [ $x -eq 120 ]; then
    echo "ERROR: Import task taking too long, exiting..."; exit 1;
elif [ "$IMPORT_STATUS" = "completed" ]; then
    echo "Import completed Successfully"
else
    echo "Import Failed, exiting"; exit 2;
fi

SNAPSHOT_ID=$(aws ec2 describe-import-snapshot-tasks --import-task-ids $IMPORT_TASK_ID | jq -r '.ImportSnapshotTasks[].SnapshotTaskDetail.SnapshotId')

aws ec2 wait snapshot-completed --snapshot-ids $SNAPSHOT_ID


echo "Registering AMI with Snapshot $SNAPSHOT_ID"
cat <<EOF > "${AMI_REGISTER_JSON_FILE}"
{
    "Architecture": "${ARCHS_MAP[$IMAGE_ARCH]}",
    "BlockDeviceMappings": [
        {
            "DeviceName": "/dev/sda1",
            "Ebs": {
                "DeleteOnTermination": true,
                "SnapshotId": "${SNAPSHOT_ID}",
                "VolumeSize": ${AMI_DISK_SIZE_GB},
                "VolumeType": "gp2"
            }
        }
    ],
    "Description": "CS9 image with container support for ${IMAGE_ARCH}",
    "RootDeviceName": "/dev/sda1",
    "BootMode": "uefi",
    "VirtualizationType": "hvm",
    "EnaSupport": true
}
EOF

aws ec2 register-image --name ${AMI_NAME} --cli-input-json="file://${AMI_REGISTER_JSON_FILE}"
echo "AMI name: "${AMI_NAME}
