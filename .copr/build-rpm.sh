#!/bin/bash
set -e

PACKAGE_NAME="automotive-image-builder"
POSITIONAL_ARGS=()
BUILD_SOURCE=false
BUILD_BINARY=false
DEV_RELEASE=false
DEV_RELEASE_SUFFIX=""
OUTPUT_DIR=$(pwd)

while [[ $# -gt 0 ]]; do
  case $1 in
    -bs|--build-source)
      BUILD_SOURCE=true
      shift
      ;;
    -bb|--build-binary)
      BUILD_SOURCE=true
      BUILD_BINARY=true
      shift
      ;;
    -h|--help)
      echo "build-rpm.sh [-bs|-bb] spec_file [output_dir]"
      exit 0
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+=("$1") # save positional arg

      # Store SPEC variable from positional arg
      if [ ${#POSITIONAL_ARGS[@]} -eq 1 ]
      then
        if [ -d "$1" ]
        then
          SPEC=$(realpath "$1"/$PACKAGE_NAME.spec.in)
        elif [ -f "$1" ]; then
          SPEC=$(realpath -s "$1")
          if [[ "$SPEC" == */.copr/dev.spec ]]
          then
            DEV_RELEASE=true
            COMMITS_NUM_SINCE_LAST_TAG=$(git log $(git describe --tags --abbrev=0)..HEAD --oneline | wc -l)
            COMMIT_HASH=$(git log -1 --pretty=format:%h)
            DEV_RELEASE_SUFFIX=".dev$COMMITS_NUM_SINCE_LAST_TAG+$COMMIT_HASH"
          fi
        else
          fatal "Spec file doesn't exists: $1"
        fi
      fi

      # Store OUTPUT_DIR variable from positional arg
      if [ ${#POSITIONAL_ARGS[@]} -eq 2 ]
      then
        OUTPUT_DIR="$1"
      fi

      shift # past argument
      ;;
  esac
done

[ "${#POSITIONAL_ARGS[@]}" -gt 0 ] || fatal "missing parameters"

if [ -z "$PACKAGE_VERSION" ] && [ -f ./Makefile ]
then
  PACKAGE_VERSION=$(grep "^VERSION" Makefile | sed -e "s:^VERSION=::g")
fi

if [ $BUILD_SOURCE = true ]
then
  rm -rf .rpmbuild
  mkdir -p .rpmbuild/{BUILD,BUILDROOT,RPMS,SOURCES,SPECS,SRPMS}

  # Copy spec file to the SPECS directory
  cp "$SPEC" .rpmbuild/SPECS/$PACKAGE_NAME.spec

  # Set package version to the spec file
  sed -e "s/@@VERSION@@/$PACKAGE_VERSION/g" -i .rpmbuild/SPECS/$PACKAGE_NAME.spec

  # Add the dev_release_suffix with the commit hash if it is a dev release
  if [ $DEV_RELEASE = true ]
  then
    OLD_SPEC_RELEASE=$(grep "^Release:" .rpmbuild/SPECS/$PACKAGE_NAME.spec)
    NEW_SPEC_RELEASE=${OLD_SPEC_RELEASE/1%/1$DEV_RELEASE_SUFFIX%}
    sed -e "s/^Release:.*$/$NEW_SPEC_RELEASE/g" -i .rpmbuild/SPECS/$PACKAGE_NAME.spec
    sed -e "s/.tar.gz/$DEV_RELEASE_SUFFIX.tar.gz/g" -i .rpmbuild/SPECS/$PACKAGE_NAME.spec
  fi

  cp -f .rpmbuild/SPECS/$PACKAGE_NAME.spec .
  git archive \
    -o ".rpmbuild/SOURCES/$PACKAGE_NAME-$PACKAGE_VERSION$DEV_RELEASE_SUFFIX.tar.gz" \
    --prefix="$PACKAGE_NAME-$PACKAGE_VERSION/" \
    --add-file $PACKAGE_NAME.spec \
    HEAD
  rm $PACKAGE_NAME.spec
fi

if [ $BUILD_BINARY = true ]
then
  rpmbuild --define "_topdir $(pwd)/.rpmbuild" -ba .rpmbuild/SPECS/$PACKAGE_NAME.spec
elif [ $BUILD_SOURCE = true ] && [ $BUILD_BINARY = false ]; then
  rpmbuild --define "_topdir $(pwd)/.rpmbuild" -bs .rpmbuild/SPECS/$PACKAGE_NAME.spec
fi

#Copy rpm packages to the output_dir
find .rpmbuild -name "*.rpm" -exec cp {} "$OUTPUT_DIR" \;

#Copy tar file to the output_dir
find .rpmbuild -name "*.tar.gz" -exec cp {} "$OUTPUT_DIR" \;

# Clean .rpmbuild directory
rm -fr .rpmbuild
