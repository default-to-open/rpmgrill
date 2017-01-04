#
# hand-built makefile
#
NAME     = rpmgrill

SPECFILE = $(NAME).spec

VERSION = $(shell git describe --abbrev=0)
RELEASE = $(shell rpm -q --specfile $(SPECFILE) --queryformat '%{RELEASE}')
BUILDDIR = /tmp/rpmbuild

# Magic tag thingy for building
DIST = fc24

$(VERSION).tar.gz:
	@rm -rf $(NAME)-$(VERSION)
	git archive --prefix=$(NAME)-$(VERSION)/ -o $(VERSION).tar.gz HEAD


$(NAME)-$(VERSION)-$(RELEASE).src.rpm: $(VERSION).tar.gz
	rpmbuild -bs --nodeps --define "_sourcedir ." --define "_srcrpmdir ." --define "dist .$(DIST)" $(SPECFILE)

.PHONY: rpmbuild rpmtest
rpmbuild: $(VERSION).tar.gz
	@rm -rf $(BUILDDIR)
	docker pull mmornati/mock-rpmbuilder:v1.0
	mkdir $(BUILDDIR)
	mv $< $(BUILDDIR)
	cp rpmgrill.spec $(BUILDDIR)
	chown -R 1000:1000 $(BUILDDIR)
	docker run --cap-add=SYS_ADMIN -it\
		-e MOCK_CONFIG=fedora-24-x86_64\
		-e SOURCES=$< \
		-e SPEC_FILE=rpmgrill.spec\
		-v $(BUILDDIR):/rpmbuild\
		mmornati/mock-rpmbuilder:v1.0

# poor mans check if the rpm build was successful
rpmtest: rpmbuild
	find $(BUILDDIR)/output -name 'rpmgrill-*.noarch.rpm' | egrep '.*'

# Shortcut names for the above
.PHONY: tarball srpm
tarball:	$(VERSION).tar.gz
srpm:		$(NAME)-$(VERSION)-$(RELEASE).src.rpm
