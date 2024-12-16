import os
import shutil
import shlex
import subprocess
import sys

from . import log


class Volumes(set):
    def __init__(self):
        super(Volumes, self).__init__()

    def add_volume(self, directory):
        self.add(os.path.realpath(directory))

    def add_volume_for(self, file):
        self.add(os.path.dirname(os.path.realpath(file)))


class Runner:
    def __init__(self, args):
        self.container = args.container_image_name if args.container else ""
        self.container_autoupdate = args.container_autoupdate
        self.sudo = vars(args.args).get("sudo", False)
        self.volumes = Volumes()
        for d in args.include_dirs:
            self.add_volume(d)

    def _collect_podman_args(self, use_non_root_user_in_container):
        podman_args = [
            "--rm",
            "--privileged",
            "--workdir",
            os.path.realpath(os.getcwd()),
            "--read-only=false",
        ]
        for v in sorted(self.volumes):
            podman_args.append("-v")
            podman_args.append(f"{v}:{v}")

        if self.container_autoupdate:
            podman_args.append("--pull=newer")

        if use_non_root_user_in_container:
            podman_args.append("--user")
            podman_args.append(f"{os.getuid()}:{os.getgid()}")
        else:
            podman_args.extend(["--security-opt", "label=type:unconfined_t"])

        return podman_args

    @property
    def conman(self):
        if (
            shutil.which("podman") is None
            and shutil.which("docker") is not None
        ):
            return "docker"
        return "podman"

    def add_volume(self, directory):
        self.volumes.add_volume(directory)

    def add_volume_for(self, file):
        self.volumes.add_volume_for(file)

    def _add_container_cmd(self, use_non_root_user_in_container):
        return (
            [
                self.conman,
                "run",
            ]
            + self._collect_podman_args(use_non_root_user_in_container)
            + [self.container]
        )

    def run(
        self,
        cmdline,
        use_sudo=False,
        use_container=False,
        use_non_root_user_in_container=False,
        capture_output=False,
    ):
        if use_container and self.container:
            cmdline = (
                self._add_container_cmd(use_non_root_user_in_container)
                + cmdline
            )

        if use_sudo and self.sudo:
            allowed_env_vars = [
                "REGISTRY_AUTH_FILE",
                "CONTAINERS_CONF",
                "CONTAINERS_REGISTRIES_CONF",
                "CONTAINERS_STORAGE_CONF",
            ]
            sudo_cmd = [
                "sudo",
                "--preserve-env={}".format(",".join(allowed_env_vars)),
            ]
            cmdline = sudo_cmd + cmdline

        log.debug("Running: %s", shlex.join(cmdline))

        try:
            if capture_output:
                r = subprocess.run(cmdline, capture_output=True, check=True)
                return r.stdout.decode("utf-8").rstrip()
            else:
                subprocess.run(cmdline, check=True)
        except subprocess.CalledProcessError:
            sys.exit(1)  # cmd will have printed the error
