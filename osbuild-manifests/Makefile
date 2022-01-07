NULL=

HOST_ARCH:=$(shell arch)
CURRENT_UIDGID := $(shell id -u):$(shell id -g)

ARCHES := x86_64 aarch64

# All arches define to use VM first
define arch-rule
OSBUILD_$1=osbuildvm/osbuildvm --arch=$1
endef
$(foreach a, $(ARCHES),  $(eval $(call arch-rule,$a)))

# But Override for host arch unless VM=1
VM=0
ifeq ($(VM), 0)
SUDO_$(HOST_ARCH)=sudo
OSBUILD_$(HOST_ARCH)=sudo osbuild
endif

OSBUILD_MPP=osbuild-mpp

DEFINES=
MPP_ARGS=
OSBUILD_ARGS=

BUILDDIR=_build
STOREDIR=$(BUILDDIR)/osbuild_store
OUTPUTDIR=$(BUILDDIR)/image_output

MANIFESTS := $(wildcard cs9/*.mpp.yml)

CHECKPOINTS=build
IMAGETYPES := regular ostree direct
FORMATS := img qcow2 container repo rootfs
aarch64_TARGETS := rpi4
COMMON_TARGETS := qemu
HOST_TARGETS := $(COMMON_TARGETS) $($(HOST_ARCH)_TARGETS)
ALL_TARGETS := $(aarch64_TARGETS) $(COMMON_TARGETS)

manifest-get-name = $(basename $(basename $(notdir $1)))
manifest-get-dir = $(notdir $(patsubst %/,%,$(dir $1)))
image-name-noarch = cs9-$2-$(call manifest-get-name,$1)-$3
image-name = $(call image-name-noarch,$1,$2,$3).$4

# variable name for image type
regular_IMAGETYPE := regular
ostree_IMAGETYPE := ostree
direct_IMAGETYPE := directboot

# export names for FORMATS
img_EXPORTFILE := disk.img
qcow2_EXPORTFILE := disk.qcow2
container_EXPORTFILE := container.tar
repo_EXPORTFILE := repo
rootfs_EXPORTFILE :=

repo_CHOWNARGS := -R

img_EXPORT := image
container_EXPORT := container
qcow2_EXPORT := qcow2
repo_EXPORT := ostree-commit
rootfs_EXPORT := rootfs

help:
	@echo
	@echo This makefile is a wrapper around osbuild-mpp and osbuild to easily build images
	@echo
	@echo To build a raw image, run \"make image.img\", or to build a qcow2 image, run \"make image.qcow2\"
	@echo
	@echo For example, to build a minimal qcow2 image with ostree support targeting qemu, run:
	@echo '  make cs9-qemu-minimal-ostree.$(HOST_ARCH).qcow2'
	@echo
	@echo Other extensions, \".commit\" and \".rootfs\" are also supported, these create directory trees as
	@echo output rather than images.
	@echo
	@echo You can pass variable declarations to osbuild-mpp with the DEFINES make variable.
	@echo For example, to add extra rpms to a minimal regular image, use:
	@echo "  make cs9-qemu-minimal-regular.$(HOST_ARCH).qcow2 DEFINES='extra_rpms=[\"gdb\",\"strace\"]'"
	@echo
	@echo There are some additional targets:
	@echo   manifests: generates resolved json manifests for all images without building them.
	@echo   clean_caches: Removes intermediate image build artifacts \(that improve rebuild speed\)
	@echo   clean_downloads: Removes files downloaded during image builds
	@echo   clean: Run clean_caches and clean_downloads
	@echo   osbuildvm-images: Build a image that can be used to build images inside a VM
	@echo
	@echo If you pass VM=1, then the images used from \"make osbuildvm-images\" will be used to do the
	@echo actual building. This means that you don\'t need sudo rights to run osbuild, and it means
	@echo architectures other than the current ones can be built.
	@echo
	@echo Available image targets \(for $(HOST_ARCH)\) are:
	@echo
	@$(foreach m, $(MANIFESTS), $(foreach t, $(HOST_TARGETS), $(foreach i,$(IMAGETYPES), echo -e "   "  $(call image-name,$m,$t,$i,$(HOST_ARCH)).qcow2 '\t' $(call image-name,$m,$t,$i,$(HOST_ARCH)).img'\t' $(call image-name,$m,$t,$i,$(HOST_ARCH)).container;)))
	@echo

# We pre-create all the toplevel dirs, so that they are owned by the user, not root (when created under sudo)
.PHONY: $(BUILDDIR)
$(BUILDDIR):
	@mkdir -p $(BUILDDIR)
	@mkdir -p $(STOREDIR)/{objects,refs,sources/org.osbuild.files,tmp}
	@mkdir -p $(OUTPUTDIR)

# Template rule for producing osbuild json manifest from mpp yaml and image type
# $1 == yaml manifest path
# $2 == Target name
# $3 == Image type
# $4 == Arch
define json-rule
$(BUILDDIR)/$(call image-name,$1,$2,$3,$4).json: $1 $(BUILDDIR)
	$(OSBUILD_MPP) -D image_type="\"$($3_IMAGETYPE)\"" -D arch=\"$4\" -D target="\"$2\"" $(foreach def,$(DEFINES),-D '$(def)') $(MPP_ARGS) $$< $$@
.PHONY: $(BUILDDIR)/$(call image-name,$1,$2,$3,$4).json
endef

$(foreach m, $(MANIFESTS), \
 $(foreach t,$(ALL_TARGETS), \
   $(foreach i,$(IMAGETYPES), \
    $(foreach a,$(ARCHES), \
     $(eval $(call json-rule,$m,$t,$i,$a))))))

# Template rule for producing image from json manifest
# $1 == Manifest path
# $2 == Target
# $3 == Image type
# $4 == Arch
# $5 == Export format (extension)
define image-rule
$(call image-name,$1,$2,$3,$4).$5: $(BUILDDIR)/$(call image-name,$1,$2,$3,$4).json
	@mkdir -p $(OUTPUTDIR)/$($5_EXPORT)
	$(OSBUILD_$4) $(foreach cp,$(CHECKPOINTS),--checkpoint $(cp)) --store $(STOREDIR) --output-directory $(OUTPUTDIR) $(OSBUILD_ARGS) --export $($5_EXPORT) $$<
	$(SUDO_$4) chown $($5_CHOWNARGS) $(CURRENT_UIDGID) $(OUTPUTDIR)/$($5_EXPORT)/$($5_EXPORTFILE)
	@rm -rf $$@
	$(SUDO_$4) mv $(OUTPUTDIR)/$($5_EXPORT)/$($5_EXPORTFILE) $$@
	$(SUDO_$4) rm -rf $(OUTPUTDIR)/$($5_EXPORT)
endef

$(foreach m, $(MANIFESTS), \
  $(foreach t, $(ALL_TARGETS), \
    $(foreach f,$(FORMATS), \
     $(foreach a,$(ARCHES), \
       $(foreach i,$(IMAGETYPES), \
	$(eval $(call image-rule,$m,$t,$i,$a,$f)))))))

# Rule to pre-generate all manifests
manifests: $(foreach m, $(MANIFESTS), $(foreach t,$(ALL_TARGETS), $(foreach i,$(IMAGETYPES), $(foreach a,$(ARCHES), $(BUILDDIR)/$(call image-name,$m,$t,$i,$a).json))))

define packages-rule
.PHONY: packages-$(call manifest-get-name,$1).json
packages-$(call manifest-get-name,$1).json: $1
	osbuild-mpp $$< -D arch=\"x86_64\" - | jq -f extract-rpms.jq > $$@.x86_64
	osbuild-mpp $$< -D arch=\"aarch64\" - | jq -f extract-rpms.jq > $$@.aarch64
	echo 1 | jq --indent 4 -f create-packagelist.jq --slurpfile x86_64 $$@.x86_64 --slurpfile aarch64 $$@.aarch64 > $$@
endef

$(foreach m, $(MANIFESTS), $(eval $(call packages-rule,$m)))

.PHONY: clean_downloads
clean_downloads:
	sudo rm -rf _build/osbuild_store/sources/org.osbuild.files/*

.PHONY: clean_caches
clean_caches:
	sudo rm -rf $(STOREDIR)/refs/*
	sudo rm -rf $(STOREDIR)/refs_tars/*
	sudo rm -rf $(STOREDIR)/objects/*
	sudo rm -rf $(STOREDIR)/tmp/*
	sudo rm -rf $(STOREDIR)/image_output/*

.PHONY: clean
clean: clean_downloads clean_caches

.PHONY: osbuildvm-images
osbuildvm-images: $(BUILDDIR)
	osbuild-mpp osbuildvm/osbuildvm.mpp.yml _build/osbuildvm-$(HOST_ARCH).json
	$(OSBUILD_$(HOST_ARCH)) --store $(STOREDIR) --output-directory $(OUTPUTDIR) --export osbuildvm _build/osbuildvm-$(HOST_ARCH).json
	cp $(OUTPUTDIR)/osbuildvm/disk.qcow2 _build/osbuildvm-$(HOST_ARCH).img
	cp $(OUTPUTDIR)/osbuildvm/initramfs _build/osbuildvm-$(HOST_ARCH).initramfs
	cp $(OUTPUTDIR)/osbuildvm/vmlinuz _build/osbuildvm-$(HOST_ARCH).vmlinuz
	$(SUDO_$(HOST_ARCH)) rm -rf $(OUTPUTDIR)/osbuildvm
