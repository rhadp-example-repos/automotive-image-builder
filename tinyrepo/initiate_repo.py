#!/usr/bin/python3

"""
This script queries content resolver at: https://tiny.distro.builders to retrieve
a list of all the packages of interest for the automotive SIG.

Requirements:
  - python-requests

"""

import argparse
import os
import re
import sys

import requests


environments = [
    "https://tiny.distro.builders/workload--automotive-c9s-workload-development--automotive-c9s-env-minimum--automotive-c9s-repositories--aarch64.json",
    "https://tiny.distro.builders/workload--automotive-c9s-workload-minimum--automotive-c9s-env-minimum--automotive-c9s-repositories--aarch64.json",
    "https://tiny.distro.builders/workload--automotive-c9s-workload-ostree--automotive-c9s-env-minimum--automotive-c9s-repositories--aarch64.json",
    "https://tiny.distro.builders/workload--automotive-c9s-workload-podman--automotive-c9s-env-minimum--automotive-c9s-repositories--aarch64.json",
]

cs_urls = [
    "http://mirror.stream.centos.org/9-stream/AppStream/{arch}/os/Packages/{nvr}",
    "http://mirror.stream.centos.org/9-stream/BaseOS/{arch}/os/Packages/{nvr}",
    "http://mirror.stream.centos.org/9-stream/CRB/{arch}/os/Packages/{nvr}",
    "https://composes.stream.centos.org/development/latest-CentOS-Stream/compose/BaseOS/{arch}/os/Packages/{nvr}",
    "https://composes.stream.centos.org/development/latest-CentOS-Stream/compose/AppStream/{arch}/os/Packages/{nvr}",
    "https://composes.stream.centos.org/development/latest-CentOS-Stream/compose/CRB/{arch}/os/Packages/{nvr}",
]

epoch_re = re.compile("-\d+:")


def get_packages():
    """ Queries content resolver and returns a tuple of two set, the first
    set contains the name of every package, the second set contains the NVR
    of every package.
    """
    packages_set = set()
    nvr_set = set()
    for env in environments:
        req = requests.get(env)
        if not req.ok:
            print(f"Failed to retrieve info from {env}")
            continue
        data = req.json()
        data = data["data"]
        for key in ("pkg_env_ids", "pkg_added_ids"):
            for pkg in data[key]:
                name = pkg.rsplit("-", 2)[0]
                # Drop the architecture
                nvr = pkg.rsplit(".", 1)[0]
                # Drop epoch if there is one
                if len(epoch_re.findall(nvr)) == 1:
                    for mat in epoch_re.findall(nvr):
                        nvr = nvr.replace(mat, "-")
                elif len(epoch_re.findall(nvr)) > 1:
                    print("More than one -\d: matched in {nvr}")
                packages_set.add(name)
                nvr_set.add(nvr)

    return (packages_set, nvr_set)


def download_nvrs(folder, nvrs):
    """ Queries the CentOS-Stream mirror and download the package specified by
    the given NVR.
    """
    notfound = 0
    out_files = []
    for nvr in sorted(nvrs):
        for arch in ("x86_64", "aarch64"):
            out_filename = f"{nvr}.{arch}.rpm"
            output_folder = os.path.join(folder, arch, "packages")
            out_path = os.path.join(output_folder, out_filename)

            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            if os.path.exists(out_path):
                out_files.append(out_filename)
                continue

            found = False
            for url in cs_urls:
                nurl = f"{url}.{arch}.rpm".format(arch=arch, nvr=nvr)
                req = requests.head(nurl)
                # print(req.status_code, url)
                if req.ok:
                    found = True
                    out_files.append(out_filename)
                    req = requests.get(nurl)
                    with open(out_path, "wb") as stream:
                        stream.write(req.content)
                    break
                else:
                    # print(req.status_code, nurl)
                    # Check if it's a noarch RPM
                    nurl = f"{url}.noarch.rpm".format(arch=arch, nvr=nvr)
                    req = requests.head(nurl)
                    if req.ok:
                        found = True
                        out_files.append(f"{nvr}.noarch.rpm")
                        req = requests.get(nurl)
                        with open(out_path, "wb") as stream:
                            stream.write(req.content)
                        break
                    # else:
                        # print(req.status_code, nurl)
            if not found:
                print(f"Package {nvr}.{arch} not found on the mirrors")
                notfound += 1

    print(f"{notfound} packages not found on the mirrors")
    return out_files


def parse_arguments(args):
    """Parse the CLI arguments and return the corresponding argparse object.
    """
    parser = argparse.ArgumentParser(description="Instantiate george")
    parser.add_argument("folder", nargs="?", default=".",
                        help="Folder in which to put the downloaded RPMs")
    parser.add_argument("--pkgslist",
                        help="Name of the file in which to output the list of all the RPMs found")

    return parser.parse_args(args)


if __name__ == "__main__":
    args = parse_arguments(sys.argv[1:])
    pkgs, nvrs = get_packages()
    # print("-", "\n- ".join(sorted(pkgs)))
    print(len(pkgs), "packages found")
    print("Corresponding to", len(nvrs), "nvr")
    out_files = download_nvrs(args.folder, nvrs)
    if args.pkgslist:
        with open(args.pkgslist, "w") as stream:
            stream.write("\n".join(out_files))
