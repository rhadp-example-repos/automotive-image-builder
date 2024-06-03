import os

from . import exit_error


EXPORT_DATAS = {
    "qcow2": {
        "filename": "disk.qcow2"
    },
    "image": {
        "filename": "disk.img"
    },
    "ostree-commit": {
        "filename": "repo",
        "is_dir": True,
    },
    "container": {
        "filename": "container.tar"
    },
    "ostree-oci-image": {
        "filename": "image.oci-archive"
    },
    "rootfs": {
        "filename": None,
        "is_dir": True,
        "no_chown": True
    },
    "ext4": {
        "filename": "rootfs.ext4"
    },
    "tar": {
        "filename": "rootfs.tar"
    },
    "aboot": {
        "filename": "images",
        "is_dir": True,
    },
    "rpmlist": {
        "filename": "rpmlist"
    }
}


def _get_export_data(exp):
    if exp in EXPORT_DATAS:
        return EXPORT_DATAS[exp]
    exit_error("Unsupported export '%s'", exp)


def export(outputdir, dest, dest_is_directory, export, runner):
    exportdir = os.path.join(outputdir, export)
    data = _get_export_data(export)

    filename = data["filename"]
    if filename:
        export_file = os.path.join(exportdir, filename)
    else:
        export_file = os.path.join(exportdir)

    if dest_is_directory:
        dest = os.path.join(dest, os.path.basename(export_file))

    if data.get("is_dir", False):
        # The mv won't replace existing destination, so first remove it
        if os.path.isdir(dest) or os.path.isfile(dest):
            runner.run(["rm", "-rf", dest], use_sudo=True)

    if not data.get("no_chown", False):
        runner.run(["chown", f"{os.getuid()}:{os.getgid()}", export_file],
                   use_sudo=True)

    runner.run(["mv", export_file, dest], use_sudo=True)
