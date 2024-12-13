FROM quay.io/centos/centos:stream9 AS base

RUN dnf update -y && \
    dnf install -y 'dnf-command(config-manager)' 'dnf-command(copr)'

RUN dnf copr enable -y @osbuild/osbuild-stable && \
    dnf copr enable -y @centos-automotive-sig/osbuild-auto


FROM base as builder

ARG MAKE_WHAT="rpm_dev"

COPY . /build
RUN  dnf install -y git rpm-build make && \
     cd /build && make "$MAKE_WHAT"


FROM base as runtime

LABEL name="Automotive Image Builder" \
      usage="This image can be used with rootful privileged containers, https://gitlab.com/CentOS/automotive/src/automotive-image-builder/" \
      summary="Base image for composing Red Hat In-Vehicle Operating System or CentOS Automotive Stream Distribution images"

COPY --from=builder /build/automotive-image-builder-*.noarch.rpm .

RUN dnf localinstall -y automotive-image-builder-*.noarch.rpm && \
    dnf clean all
