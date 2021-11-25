NULL=
OSBUILD_MPP=osbuild-mpp
OSBUILD=osbuild

DEFINES=
MPP_ARGS=

BUILDDIR=_build
STOREDIR=$(BUILDDIR)/osbuild_store
OUTPUTDIR=$(BUILDDIR)/image_output

CURRENT_ARCH:=$(shell arch)
CURRENT_UIDGID := $(shell id -u):$(shell id -g)

MANIFESTS := \
	cs9/minimal.mpp.yml \
	cs9/neptune.mpp.yml \
	$(NULL)

CHECKPOINTS=build rootfs

IMAGETYPES := regular ostree direct
FORMATS := img qcow2 repo rootfs
aarch64_TARGETS := rpi4
TARGETS := qemu $($(CURRENT_ARCH)_TARGETS)

manifest-get-name = $(basename $(basename $(notdir $1)))
manifest-get-dir = $(notdir $(patsubst %/,%,$(dir $1)))
image-name = cs9-$2-$(call manifest-get-name,$1)-$3

# variable name for image type
regular_IMAGETYPE := regular
ostree_IMAGETYPE := ostree
direct_IMAGETYPE := directboot

# export names for FORMATS
img_EXPORTFILE := disk.img
qcow2_EXPORTFILE := disk.qcow2
repo_EXPORTFILE := repo
rootfs_EXPORTFILE :=

repo_CHOWNARGS := -R

img_EXPORT := image
qcow2_EXPORT := qcow2
repo_EXPORT := ostree-commit
rootfs_EXPORT := rootfs

help:
	@echo This is a wrapper around osbuild-mpp and osbuild to easily build images
	@echo
	@echo To build a raw image, run \"make image.img\", or to build a qcow2 image, run \"make image.qcow2\"
	@echo
	@echo For example, to build a minimal qcow2 image with ostree support targeting qemu, run:
	@echo '  make cs9-qemu-minimal-ostree.qcow2'
	@echo
	@echo Other extensions, \".commit\" and \".rootfs\" are also supported, these create directory trees as
	@echo output rather than images.
	@echo
	@echo You can pass variable declarations to osbuild-mpp with the DEFINES make variable.
	@echo For example, to add extra rpms to a minimal regular image, use:
	@echo "  make cs9-qemu-minimal-regular.qcow2 DEFINES='extra_rpms=[\"gdb\",\"strace\"]'"
	@echo
	@echo You also run \"make manifests\" to generate resolved json manifests for all images without building them.
	@echo
	@echo Available images are:
	@echo " " $(foreach m, $(MANIFESTS), $(foreach t, $(TARGETS), $(foreach i,$(IMAGETYPES), $(call image-name,$m,$t,$i))))

# We pre-create all the toplevel dirs, so that they are owned by the user, not root (when created under sudo)
$(BUILDDIR):
	@mkdir -p $(BUILDDIR)
	@mkdir -p $(STOREDIR)/{objects,refs,sources/org.osbuild.files,tmp}
	@mkdir -p $(OUTPUTDIR)

# Template rule for producing osbuild json manifest from mpp yaml and image type
# $1 == yaml manifest path
# $2 == Target name
# $3 == Image type
define json-rule
$(BUILDDIR)/$(call image-name,$1,$2,$3).json: $1 $(BUILDDIR)
	$(OSBUILD_MPP) -D image_type="\"$($3_IMAGETYPE)\"" -D target="\"$2\"" $(foreach def,$(DEFINES),-D '$(def)') $(MPP_ARGS) $$< $$@
.PHONY: $(BUILDDIR)/$(call image-name,$1,$2,$3).json
endef

$(foreach m, $(MANIFESTS), \
 $(foreach t,$(TARGETS), \
   $(foreach i,$(IMAGETYPES), \
     $(eval $(call json-rule,$m,$t,$i)))))

# Template rule for producing image from json manifest
# $1 == Manifest path
# $2 == Target
# $3 == Image type
# $4 == Export format (extension)
define image-rule
$(call image-name,$1,$2,$3).$4: $(BUILDDIR)/$(call image-name,$1,$2,$3).json
	@mkdir -p $(OUTPUTDIR)/$($4_EXPORT)
	sudo osbuild $(foreach cp,$(CHECKPOINTS),--checkpoint $(cp)) --store $(STOREDIR) --output-directory $(OUTPUTDIR) --export $($4_EXPORT) $$<
	sudo chown $($4_CHOWNARGS) $(CURRENT_UIDGID) $(OUTPUTDIR)/$($4_EXPORT)/$($4_EXPORTFILE)
	@rm -rf $$@
	sudo mv $(OUTPUTDIR)/$($4_EXPORT)/$($4_EXPORTFILE) $$@
endef

$(foreach m, $(MANIFESTS), \
  $(foreach t, $(TARGETS), \
    $(foreach f,$(FORMATS), \
      $(foreach i,$(IMAGETYPES), \
	$(eval $(call image-rule,$m,$t,$i,$f))))))

# Rule to pre-generate all manifests
manifests: $(foreach m, $(MANIFESTS), $(foreach t,$(TARGETS), $(foreach i,$(IMAGETYPES), $(BUILDDIR)/$(call image-name,$m,$t,$i).json)))
