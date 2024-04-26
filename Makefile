PREFIX=/usr
BINDIR=$(PREFIX)/bin
DATADIR=$(PREFIX)/lib/automotive-image-builder
DESTDIR=

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

test: tests/test.mpp.yml
	tests/test.sh
