#!/usr/bin/env python3

import argparse
import sys
import os
import platform
import subprocess
import json
import shlex
import shutil
import tempfile

from . import log, exit_error

base_dir = ""
include_dirs = []
volumes = set()

def add_volume(dir):
    global volumes
    volumes.add(os.path.realpath(dir))

def add_volume_for(file):
    global volumes
    volumes.add(os.path.dirname(os.path.realpath(file)))

def ostree_repo_init(path):
    if not os.path.isdir(path):
        log.debug("Initializing repo %s", path)
        subprocess.run(["ostree", "init", "--repo", path, "--mode", "archive"], check=True)

def ostree_refs(path):
    r = subprocess.run(["ostree", "refs", "--repo", path], capture_output=True, check=True)
    out = r.stdout.decode("utf-8").rstrip()
    if out:
        return out.split("\n")
    return []

def ostree_rev_parse(path, ref):
    r = subprocess.run(["ostree", "rev-parse", "--repo", path, ref], capture_output=True, check=True)
    return r.stdout.decode("utf-8").rstrip()

def list_dist(_args, _tmpdir):
    distros = set()
    for inc in include_dirs:
        for f in os.listdir(os.path.join(inc, "distro")):
            if f.endswith(".ipp.yml"):
                distros.add(f[:-8])
    for d in sorted(distros):
        print(d)

def list_targets(_args, _tmpdir):
    targets = set()
    for inc in include_dirs:
        for f in os.listdir(os.path.join(inc, "targets")):
            if f.endswith(".ipp.yml"):
                targets.add(f[:-8])
    for d in sorted(targets):
        print(d)

def run(args, cmdline, use_sudo=False, use_container=False, use_non_root_user_in_container=False):
    if use_container and args.container:

        podman_args = ["--rm", "--privileged", "--workdir", os.path.realpath(os.getcwd()) ]
        if not use_non_root_user_in_container:
            podman_args.extend(["--security-opt", "label=type:unconfined_t"])
        for v in sorted(volumes):
            podman_args.append("-v")
            podman_args.append(v + ":" + v)

        if args.container_autoupdate:
            podman_args.append("--pull=newer")

        if use_non_root_user_in_container:
            podman_args.append("--user")
            podman_args.append(f"{os.getuid()}:{os.getgid()}")

        conman = "podman"
        if shutil.which("podman") is None and shutil.which("docker") is not None:
            conman = "docker"

        cmdline = [conman, "run",  ] + podman_args + [args.container] + cmdline

    if use_sudo and vars(args).get("sudo", False):
        cmdline = ["sudo"] + cmdline

    log.debug("Running: %s", shlex.join(cmdline))

    try:
        subprocess.run(cmdline, check=True)
    except subprocess.CalledProcessError:
        sys.exit(1) # cmd will have printed the error

# Its a pain to have to quote simple strings in arguments, if the
# json parsing fails we try to parse it as a string
def define_value_looks_like_string(v):
    v = v.lstrip()
    if len(v) == 0:
        return False
    # Dont' start with numerics
    if v[0].isnumeric():
        return False
    # No case mis-spellings of true/false like False
    if v.lower() == "false" or v.lower() == "true":
        return False
    # No json type character or escapes
    invalid_chars = '"{}[]\\'
    for invalid_char in invalid_chars:
        if invalid_char in v:
            return False
    return True

def parse_define(d, option):
    parts = d.split("=", 2)
    if len(parts) != 2:
        exit_error("Invalid option passed to %s: '%s', should be key=value", option, d)
    k = parts[0]
    json_v = parts[1]
    try:
        v = json.loads(json_v)
    except json.decoder.JSONDecodeError as e:
        # Try it as a string too
        if define_value_looks_like_string(json_v):
            try:
                v = json.loads('"' + json_v + '"')
            except json.decoder.JSONDecodeError:
                exit_error("Invalid value passed to %s: '%s': %s", option, json_v, e)
        else:
            exit_error("Invalid value passed to %s: '%s': %s", option, json_v, e)
    return k, v

def parse_args(args):
    isRoot = os.getuid() == 0
    parser = argparse.ArgumentParser(prog="automotive-image-builder",
                                     description="Build automotive images")
    parser.add_argument("--verbose", default=False, action="store_true")
    parser.add_argument("--container", default=False, action="store_true",
                        help="Use containerized build")
    container_image_name_default = "quay.io/centos-sig-automotive/automotive-osbuild"
    parser.add_argument("--container-image-name", action="store", type=str, default=container_image_name_default,
                        help=f"Container image name, {container_image_name_default} is default if this option remains unused")
    parser.add_argument("--container-autoupdate", default=False, action="store_true",
                        help="Automatically pull new container image if available")
    parser.add_argument("--include", action="append",type=str,default=[],
                        help="Add include directory")
    parser.set_defaults(func=no_subcommand)
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_list_dist = subparsers.add_parser('list-dist', help='list available distributions')
    parser_list_dist.set_defaults(func=list_dist)

    parser_list_dist = subparsers.add_parser('list-targets', help='list available targets')
    parser_list_dist.set_defaults(func=list_targets)

    format_parser = argparse.ArgumentParser(add_help=False)
    format_parser.add_argument("--arch", default=platform.machine(), action="store",
                        help=f"Arch to run for (default {platform.machine()})")
    format_parser.add_argument("--osbuild-mpp", action="store",type=str,default=os.path.join(base_dir, "mpp/aib-osbuild-mpp"),
                        help="Use this osbuild-mpp binary")
    format_parser.add_argument("--target", action="store",type=str,default="qemu",
                        help="Build for this target")
    format_parser.add_argument("--mode", action="store",type=str,default="image",
                        help="Build this image mode (package, image)")
    format_parser.add_argument("--distro", action="store",type=str,default="cs9",
                        help="Build for this distro specification")
    format_parser.add_argument("--mpp-arg", action="append",type=str,default=[],
                        help="Add custom mpp arg")
    format_parser.add_argument("--cache", action="store",type=str,
                        help="Add mpp cache-directory to use")
    format_parser.add_argument("--define", action="append",type=str,default=[],
                        help="Define key=json-value")
    format_parser.add_argument("--define-file", action="append",type=str,default=[],
                        help="Add json file of defines")
    format_parser.add_argument("--extend-define", action="append",type=str,default=[],
                        help="Extend array by item or list key=json-value")
    format_parser.add_argument("--ostree-repo", action="store",type=str,
                        help="Path to ostree repo")

    parser_compose = subparsers.add_parser('compose', help='Compose osbuild manifest', parents=[format_parser])
    parser_compose.add_argument("manifest", type=str, help="Source manifest file")
    parser_compose.add_argument("out", type=str, help="Output osbuild json")
    parser_compose.set_defaults(func=compose)

    parser_build = subparsers.add_parser('build', help='Compose osbuild manifest', parents=[format_parser])
    parser_build.add_argument("--osbuild-manifest", action="store",type=str,
                        help="Path to store osbuild manifest")
    parser_build.add_argument("--cache-max-size", action="store",type=str,
                        help="Max cache size")
    parser_build.add_argument("--osbuild-arg", action="append",type=str,default=[],
                        help="Add custom osbuild arg")
    parser_build.add_argument("--export", action="append",type=str,default=[],
                        help="Export this image type")
    parser_build.add_argument("--build-dir", action="store",type=str,
                        help="Directory where intermediary files are stored)")
    parser_build.add_argument("--sudo", default=not isRoot, action="store_true",
                              help="Use sudo to start programs that need privileges (default if not run as root)")
    parser_build.add_argument("--nosudo", default=False, action="store_true",
                              help="Don't use sudo to start programs")

    parser_build.add_argument("manifest", type=str, help="Source manifest file")
    parser_build.add_argument("out", type=str, help="Output path")
    parser_build.set_defaults(func=build)
    return parser.parse_args(args)

def create_osbuild_manifest(args, manifest, out):
    if not os.path.isfile(manifest):
        exit_error("No such file %s", manifest)

    add_volume_for(manifest)
    add_volume_for(out)

    defines = {
        "_basedir": base_dir,
        "arch": args.arch,
        "target": args.target,
        "distro_name": args.distro,
        "image_mode": args.mode,
        # This is a leftover for backwards compatibilty:
        "image_type": "ostree" if args.mode == "image" else "regular",
    }

    if args.ostree_repo:
        ostree_repo_init(args.ostree_repo)
        revs = {}
        for ref in ostree_refs(args.ostree_repo):
            rev = ostree_rev_parse(args.ostree_repo, ref)
            revs[ref] = rev
            defines["ostree_parent_refs"] = revs

    for d in args.define:
        k, v = parse_define(d, "--define")
        defines[k] = v

    for df in args.define_file:
        try:
            with open(df) as f:
                file_defines = json.load(f)
            if not isinstance(file_defines, dict):
                exit_error("Define file must be json dict")
            for k,v in file_defines.items():
                defines[k]=v
        except json.decoder.JSONDecodeError as e:
            exit_error("Invalid json define file '%s': %s", df, e)

    for d in args.extend_define:
        k, v = parse_define(d, "--extend-define")
        if not isinstance(v, list):
            v = [v]
        if not k in defines:
            defines[k] = []
        defines[k].extend(v)

    cmdline = [ args.osbuild_mpp ]
    for inc in include_dirs:
        cmdline += [ "-I", inc ]

    for k in sorted(defines.keys()):
        v = defines[k]
        cmdline += [ "-D", f'{k}={json.dumps(v)}' ]

    for arg in args.mpp_arg:
        cmdline += [ arg ]

    if args.cache:
        cmdline += [ "--cache", args.cache ]

    cmdline += [ manifest, out ]

    run(args, cmdline, use_sudo=True, use_container=True, use_non_root_user_in_container=True)

def compose(args, tmpdir):
    return create_osbuild_manifest(args, args.manifest, args.out)

export_datas = {
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

def get_export_data(exp):
    if exp in export_datas:
        return export_datas[exp]
    exit_error("Unsupported export '%s'", exp)

def export(args, outputdir, dest, dest_is_directory, export):
    exportdir = os.path.join(outputdir, export)
    data = get_export_data(export)

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
            run(args, ["rm", "-rf", dest], use_sudo=True)

    if not data.get("no_chown", False):
        run(args, ["chown", f"{os.getuid()}:{os.getgid()}", export_file], use_sudo=True)

    run(args, ["mv", export_file, dest], use_sudo=True)

def _build(args, tmpdir):
    if args.nosudo:
        args.sudo=False

    if len(args.export) == 0:
        exit_error("No --export option given")

    add_volume_for(args.out)

    osbuild_manifest = os.path.join(tmpdir, "osbuild.json")
    if args.osbuild_manifest:
        osbuild_manifest = args.osbuild_manifest

    create_osbuild_manifest(args, args.manifest, osbuild_manifest)

    builddir = tmpdir
    if args.build_dir:
        builddir = args.build_dir
    add_volume(builddir)
    add_volume("/dev")

    cmdline = [ "osbuild" ]

    outputdir = os.path.join(builddir, "image_output")
    cmdline += [ "--store", os.path.join(builddir, "osbuild_store"),
                 "--output-directory",  outputdir]

    for arg in args.osbuild_arg:
        cmdline += [ arg ]

    if args.build_dir:
        # Cache stuff between builds
        cmdline += [ "--checkpoint", "build"]

    if args.cache_max_size:
        cmdline += [ "--cache-max-size=" + args.cache_max_size]

    has_repo=False
    for exp in args.export:
        if exp == "ostree-commit":
            has_repo=True
        cmdline += ["--export", exp]

    # If ostree repo was specified, also export it if needed
    if not has_repo and args.ostree_repo:
        cmdline += ["--export", "ostree-commit"]

    cmdline += [ osbuild_manifest ]

    run(args, cmdline, use_sudo=True, use_container=True)

    if args.ostree_repo:
        repodir = os.path.join(outputdir, "ostree-commit/repo")
        run(args, ["ostree", "pull-local",  "--repo=" + args.ostree_repo, repodir])

    if len(args.export) == 1:
        # Export directly to args.out
        export(args, outputdir, args.out, False, args.export[0])
    else:
        if os.path.isdir(args.out) or os.path.isfile(args.out):
            run(args, ["rm", "-rf", args.out], use_sudo=True)
        os.mkdir(args.out)
        for exp in args.export:
            export(args, outputdir, args.out, True, exp)

    run(args, ["rm", "-rf", outputdir], use_sudo=True)

def build(args, tmpdir):
    try:
        _build(args, tmpdir)
    finally:

        # Ensure we can clean up these directories, that can have weird permissions
        if args.sudo and (os.path.isdir(os.path.join(tmpdir, "osbuild_store")) or os.path.isdir(os.path.join(tmpdir, "image_output"))):
            run(args, ["rm", "-rf", tmpdir], use_sudo=True)

def no_subcommand(_args, _tmpdir):
    log.info("No subcommand specified, see --help for usage")

def main():
    global base_dir
    base_dir = sys.argv[1]
    args = parse_args(sys.argv[2:])

    if args.container:
        args.container = args.container_image_name

    if args.verbose:
        log.setLevel("DEBUG")

    global include_dirs
    include_dirs = [ base_dir ] + args.include
    global volumes
    add_volume(os.getcwd())
    for d in include_dirs:
        add_volume(d)

    with tempfile.TemporaryDirectory(prefix="automotive-image-builder-", dir="/var/tmp") as tmpdir:
        return args.func(args, tmpdir)

if __name__ == "__main__":
    sys.exit(main())
