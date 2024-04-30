VERSION=0.1.1

PREFIX=/usr
BINDIR=$(PREFIX)/bin
DATADIR=$(PREFIX)/lib/automotive-image-builder
DESTDIR=

.PHONY: all
all:
	@echo Run "make install DESTDIR=..." to install, otherwise run directly from checkout

install:
	mkdir -p $(DESTDIR)$(BINDIR)
	install -t $(DESTDIR)$(BINDIR) automotive-image-builder automotive-image-runner
	for dir in distro include targets ; do \
		mkdir -p $(DESTDIR)$(DATADIR)/$$dir ; \
		install -m 0644 -t $(DESTDIR)$(DATADIR)/$$dir $$dir/*.yml ; \
	done
	mkdir -p $(DESTDIR)$(DATADIR)/files
	install -m 0644 -t $(DESTDIR)$(DATADIR)/files files/*

.PHONY: test
test: tests/test.mpp.yml
	tests/test.sh

.PHONY: automotive-image-builder.spec
automotive-image-builder.spec: automotive-image-builder.spec.in
	sed s/@@VERSION@@/$(VERSION)/ $< > $@

.PHONY: dist
dist: automotive-image-builder.spec
	git archive -o automotive-image-builder-$(VERSION).tar.gz --prefix=automotive-image-builder-$(VERSION)/ --add-file automotive-image-builder.spec HEAD

rpm: dist
	rpmbuild --define "_sourcedir $(shell pwd)" -ba automotive-image-builder.spec

srpm: dist
	rpmbuild --define "_sourcedir $(shell pwd)" -bs automotive-image-builder.spec
