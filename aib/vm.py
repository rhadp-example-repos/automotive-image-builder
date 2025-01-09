#!/usr/bin/env python3

import argparse
import os
import platform
import sys
import tempfile
import shlex

from . import vmhelper, log

base_dir = None

default_container_source = "quay.io/centos-sig-automotive/automotive-osbuild"


def no_subcommand(_args):
    log.info("No subcommand specified, see --help for usage")


def create_command(args):
    log.info("create")

    dest_image = f"aibvm-{args.arch}.qcow2"
    dest_kernel = f"aibvm-{args.arch}.vmlinux"
    vmhelper.create_vm_image(base_dir, args.arch, dest_image, dest_kernel)


def run_command(args):
    log.info("run")

    kernel = f"aibvm-{args.arch}.vmlinux"
    rootimg = f"aibvm-{args.arch}.qcow2"
    var_image = f"aibvm-var-{args.arch}.qcow2"
    container_file = f"aibvm-{args.container_image_name.replace('/', '_')}-{
        args.arch}.tar"

    if not os.path.isfile(var_image):
        vmhelper.mk_var(var_image)

    if not os.path.isfile(container_file):
        vmhelper.get_container(
            container_file, args.arch, args.container_image_name
        )

    with tempfile.TemporaryDirectory(prefix="aibvm") as tmpdir:
        run_script = os.path.join(tmpdir, "run")
        with open(run_script, "w") as f:
            f.write("#!/usr/bin/bash\n" + shlex.join(args.command))
        return vmhelper.run_vm(
            args.arch,
            kernel,
            rootimg,
            var_image,
            container_file,
            args.sharedir,
            run_script,
            args.memory,
            args.container_image_name,
            "",
        )


def main():
    global base_dir
    base_dir = os.path.realpath(sys.argv[1])
    parser = argparse.ArgumentParser(
        prog="automotive-image-vm",
        description="Tool for automotive-image-builder build vms",
    )
    parser.add_argument("--verbose", default=False, action="store_true")
    parser.add_argument(
        "--arch",
        default=platform.machine(),
        action="store",
        help=f"Arch to run for (default {platform.machine()})",
    )
    parser.set_defaults(func=no_subcommand)
    subparsers = parser.add_subparsers(help="sub-command help")

    create_parser = subparsers.add_parser("create", help="Create vm")
    create_parser.set_defaults(func=create_command)

    run_parser = subparsers.add_parser("run", help="Run vm")
    container_image_name_default = (
        "quay.io/centos-sig-automotive/automotive-osbuild"
    )
    run_parser.add_argument(
        "--container-image-name",
        action="store",
        type=str,
        default=container_image_name_default,
        help=f"Container image name (default: {container_image_name_default})",
    )
    run_parser.add_argument(
        "--memory", default="2G", help="Memory size (default 2G)"
    )
    run_parser.add_argument(
        "--sharedir", action="store", help="Share directory using virtiofs"
    )
    run_parser.add_argument("command", nargs=argparse.REMAINDER)
    run_parser.set_defaults(func=run_command)

    args = parser.parse_args(sys.argv[2:])

    if args.verbose:
        log.setLevel("DEBUG")

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
