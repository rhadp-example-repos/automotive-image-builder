FROM quay.io/centos/centos:stream9

ARG MAKE_WHAT="rpm_dev"

LABEL name="Automotive Image Builder" \
      usage="This image can be used with rootful privileged containers, https://gitlab.com/CentOS/automotive/src/automotive-image-builder/" \
      summary="Base image for composing Red Hat In-Vehicle Operating System or CentOS Automotive Stream Distribution images"

RUN dnf update -y && \
    dnf install -y 'dnf-command(config-manager)' 'dnf-command(copr)' \
    git rpm-build make

RUN dnf copr enable -y @osbuild/osbuild-stable && \
    dnf copr enable -y @centos-automotive-sig/osbuild-auto

# build & install automotive-image-builder
RUN --mount=type=bind,source=/,destination=/build,relabel=shared,rw cd /build && \
    make "$MAKE_WHAT" && \
    dnf localinstall -y automotive-image-builder-*.noarch.rpm && \
    dnf clean all
