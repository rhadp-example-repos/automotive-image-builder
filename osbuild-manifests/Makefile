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

aarch64_MANIFESTS := \
	cs9/rpi4/rpi4-minimal.mpp.yml \
	cs9/rpi4/rpi4-neptune.mpp.yml \
	$(NULL)

MANIFESTS := \
	cs9/qemu/minimal.mpp.yml \
	cs9/qemu/neptune.mpp.yml \
	$($(CURRENT_ARCH)_MANIFESTS) \
	$(NULL)

CHECKPOINTS=build rootfs

IMAGETYPES := regular ostree direct
FORMATS := img qcow2

manifest-get-name = $(basename $(basename $(notdir $1)))
manifest-get-dir = $(notdir $(patsubst %/,%,$(dir $1)))
image-name = cs9-$(call manifest-get-name,$1)-$2

# variable name for image type
regular_IMAGETYPE := regular
ostree_IMAGETYPE := ostree
direct_IMAGETYPE := directboot

# export names for FORMATS
img_EXPORT := image
qcow2_EXPORT := qcow2

help:
	@echo This is a wrapper around osbuild-mpp and osbuild to easily build images
	@echo
	@echo To build a raw image, run \"make image.img\", or to build a qcow2 image, run \"make image.qcow2\"
	@echo
	@echo For example, to build a minimal qcow2 image with ostree support, run:
	@echo '  make cs9-minimal-ostree.qcow2'
	@echo
	@echo You can pass variable declarations to osbuild-mpp with the DEFINES make variable.
	@echo For example, to add extra rpms to a minimal regular image, use:
	@echo "  make cs9-minimal-regular.qcow2 DEFINES='extra_rpms=[\"gdb\",\"strace\"]'"
	@echo
	@echo You also run \"make manifests\" to generate resolved json manifests for all images without building them.
	@echo
	@echo Available images are:
	@echo " " $(foreach m, $(MANIFESTS), $(foreach i,$(IMAGETYPES), $(call image-name,$m,$i)))

# We pre-create all the toplevel dirs, so that they are owned by the user, not root (when created under sudo)
$(BUILDDIR):
	@mkdir -p $(BUILDDIR)
	@mkdir -p $(STOREDIR)/{objects,refs,sources/org.osbuild.files,tmp}
	@mkdir -p $(OUTPUTDIR)

# Template rule for producing osbuild json manifest from mpp yaml and image type
# $1 == yaml manifest path
# $2 == Image type
define json-rule
$(BUILDDIR)/$(call image-name,$1,$2).json: $1 $(BUILDDIR)
	osbuild-mpp -D image_type="\"$($2_IMAGETYPE)\"" $(foreach def,$(DEFINES),-D '$(def)') $(MPP_ARGS) $$< $$@
.PHONY: $(BUILDDIR)/$(call image-name,$1,$2).json
endef

$(foreach m, $(MANIFESTS), \
 $(foreach i,$(IMAGETYPES), \
   $(eval $(call json-rule,$m,$i))))

# Template rule for producing image from json manifest
# $1 == Manifest path
# $2 == Image type
# $3 == Export format (extension)
# $4 == Export name (name in manifests)
define image-rule
$(call image-name,$1,$2).$3: $(BUILDDIR)/$(call image-name,$1,$2).json
	@mkdir -p $(OUTPUTDIR)/$4
	sudo osbuild $(foreach cp,$(CHECKPOINTS),--checkpoint $(cp)) --store $(STOREDIR) --output-directory $(OUTPUTDIR) --export $4 $$<
	sudo chown $(CURRENT_UIDGID) $(OUTPUTDIR)/$4/disk.$3
	sudo mv $(OUTPUTDIR)/$4/disk.$3 $$@
endef

$(foreach m, $(MANIFESTS), \
  $(foreach f,$(FORMATS), \
    $(foreach i,$(IMAGETYPES), \
      $(eval $(call image-rule,$m,$i,$f,$($f_EXPORT))))))

# Rule to pre-generate all manifests
manifests: $(foreach m, $(MANIFESTS), $(foreach i,$(IMAGETYPES), $(BUILDDIR)/$(call image-name,$m,$i).json))
