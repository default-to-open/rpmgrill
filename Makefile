#
# hand-built makefile
#
NAME     = rpmgrill

SPECFILE = $(NAME).spec

VERSION = $(shell git describe --abbrev=0)
RELEASE = $(shell rpm -q --specfile $(SPECFILE) --queryformat '%{RELEASE}')

# Magic tag thingy for building
DIST = fc24

$(VERSION).tar.gz:
	@rm -rf $(NAME)-$(VERSION)
	git archive --prefix=$(NAME)-$(VERSION)/ -o $(VERSION).tar.gz HEAD


$(NAME)-$(VERSION)-$(RELEASE).src.rpm: $(VERSION).tar.gz
	rpmbuild -bs --nodeps --define "_sourcedir ." --define "_srcrpmdir ." --define "dist .$(DIST)" $(SPECFILE)

.PHONY: dockertest
dockertest: dev-tools/docker/docker-compose.yml
	for target in `egrep -o '^test_\w+' $<`; do \
		docker-compose -f $< build $$target; \
		docker-compose -f $< run $$target /usr/bin/prove -lrcf t || exit 1; \
	done

# Shortcut names for the above
.PHONY: tarball srpm
tarball:	$(VERSION).tar.gz
srpm:		$(NAME)-$(VERSION)-$(RELEASE).src.rpm
