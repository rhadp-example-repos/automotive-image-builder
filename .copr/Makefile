REPO_DIR ?= $(shell pwd)

installdeps:
	dnf -y install git jq rpm-build python3-devel

git_config_pre:
	# From git 2.35.2 we need to mark temporary directory, where the project is cloned to, as safe, otherwise
	# git commands won't work
	git config --global --add safe.directory $(REPO_DIR)

srpm: installdeps git_config_pre
	.copr/build-rpm.sh -bs "$(spec)" "$(outdir)"

.PHONY: installdeps srpm git_config_pre