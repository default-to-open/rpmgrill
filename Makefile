#
# hand-built makefile
#
NAME     = rpmgrill

SPECFILE = $(NAME).spec

VERSION = $(shell rpm -q --specfile $(SPECFILE) --queryformat '%{VERSION}')
RELEASE = $(shell rpm -q --specfile $(SPECFILE) --queryformat '%{RELEASE}')

# Magic tag thingy for building
DIST = fc19

$(NAME)-$(VERSION).tar.bz2:
	@rm -rf $(NAME)-0.0 $(NAME)-$(VERSION)
	perl Build.PL
	./Build distdir
	test -d $(NAME)-0.0 || exit 1
	find $(NAME)-0.0 -type f | xargs perl -pi -e "s/VERSION\s+=\s+'.*?';/VERSION = '$(VERSION)';/"
	-rm -f $(NAME)-0.0/doc/tooltips.txt
	perl -Ilib bin/make-tooltips >| $(NAME)-0.0/doc/tooltips.txt
	mv $(NAME)-0.0 $(NAME)-$(VERSION)
	tar cjf $(NAME)-$(VERSION).tar.bz2 $(NAME)-$(VERSION)
	rm -rf $(NAME)-$(VERSION)


$(NAME)-$(VERSION)-$(RELEASE).$(DIST).src.rpm: $(NAME)-$(VERSION).tar.bz2
	rpmbuild -bs --nodeps --define "_sourcedir ." --define "_srcrpmdir ." --define "dist .$(DIST)" $(SPECFILE)


# Shortcut names for the above
tarball:	$(NAME)-$(VERSION).tar.bz2
srpm:		$(NAME)-$(VERSION)-$(RELEASE).$(DIST).src.rpm
