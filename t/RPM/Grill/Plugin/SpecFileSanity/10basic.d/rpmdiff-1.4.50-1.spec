%define rpmdiffdir /opt/rpmdiff
%define webuidir /var/www/html

# We link to libmagic, so we need a sufficiently recent version of "file"
# RHEL5 has this, but RHEL3/4 don't, so we need to build/run against a
# special build of file.  For this reason, I've built:
#   file-4.17-10.rpmdiff.1.el3
#   file-4.17-10.rpmdiff.1.el4
# into
#   dist-3.0E-eso
#   dist-4E-eso
# respectively, based off the RHEL5 file-4.17-10 package
#
# though on RHEL4, 4.10-3.EL4.5 is in buildroot and seems to be late enough
%define minFileVR 4.17

# We want to share a common specfile between releases
# Ideally we'd use the dist tag idea desribed here:
#    http://fedoraproject.org/wiki/Packaging/DistTag
#
# Unfortunately, it's only supported in Brew for RHEL5,
# not for RHEL3 and RHEL4, due to risk concerns
#
# Hence we synthesize our own implementation by scraping
# from redhat-release
# with an override by setting RHEL env var to allow
# convenient building of src rpm with appropriate tags
%define RHEL %(echo $RHEL)

%if 0%{?RHEL}

# RHEL env var was defined, use it:
%define myrhel %{RHEL}

%else

# RHEL env var not defined

# Scrape a value for "myrhel" from the first character of the version of
# the redhat-release package.
#
# This works for RHEL3 and RHEL4 without needing buildsys-macros to
# be present
#
# On RHEL5 dist-5E-eso, the redhat-release version is still 4.90
# so attempts to look at the first character leave us with "4" not "5"
# However, in this case the dist and rhel tags _are_ defined, in the
# buildsys-macros package, so we can use that
# Specifically:
#   buildsys-macros-5-4.el5.noarch.rpm
# contains the file:
#   /etc/rpm/macros.disttag
# which has this content (which I've commented out here):
# %%rhel 5
# %%dist .el5
# See https://engineering.redhat.com/rt3/Ticket/Display.html?id=12938
%if 0%{?rhel}
%define myrhel %{rhel}
%else
%define myrhel %(rpm -q --qf "%{VERSION}\n" redhat-release | head -c1)
%endif

%endif # of clause for RHEL env var not defined

# Now set mydist from myrhel:
%define mydist .el%{myrhel}

Summary: A utility for comparing RPMs
Name: rpmdiff
Version: 1.4.50
Release: 1%{?mydist}
Source: rpmdiff-%{version}.tar.bz2
License: Red Hat internal.  Do not redistribute.
Group: Development/Tools
BuildRoot: %{_tmppath}/%{name}-root
ExclusiveArch: %{ix86} x86_64

BuildRequires: file >= %{minFileVR}
# for /usr/include/magic.h

BuildRequires: pcre-devel
BuildRequires: pkgconfig
BuildRequires: glib2-devel
BuildRequires: libxml2-devel
BuildRequires: rpm
BuildRequires: rpm-libs
BuildRequires: rpm-devel

%if %{myrhel} >= 5
BuildRequires: /usr/bin/makedepend
%else
BuildRequires: /usr/X11R6/bin/makedepend
%endif
# /usr/X11R6/bin/makedepend provided by:
#    XFree86-devel on RHEL3
#    xorg-x11-devel on RHEL4
# /usr/bin/makedepend provided by:
#    imake in fc5/RHEL5 and later

# Build requirements for abicheck binary:
BuildRequires: elfutils-devel
BuildRequires: elfutils-libelf-devel

%description
rpmdiff runs a number of tests of two versions of an RPM and reports the
differences between the two.

It is split into a worker daemon and a scheduler daemon.  The core package
contains code shared by the two.

%package worker
Summary: worker daemon for rpmdiff runs.
Group: Development/Tools
Requires: rpmdiff = %{version}-%{release}

# gcc-c++ is needed for c++filt:
Requires: gcc-c++

# Needed for /usr/bin/md5sum and others:
Requires: coreutils

# Anti-virus checker also required:
Requires: clamav

# As of 2010-10-04, we need 0.149 for running abicheck
Requires: elfutils >= 0.149-1

# We need libxml2 for xmllint:
Requires: libxml2

# We need desktop-file-utils for desktop-file-validate:
Requires: desktop-file-utils

# We need binutils for objdump:
Requires: binutils

Requires: /sbin/modinfo
Requires: /sbin/depmod
# provided by:
#    module-init-tools on RHEL4, RHEL5
#    modutils on RHEL3

# if enabled, then we require rpmlint:
Requires: rpmlint

# add gdb and the debuginfo subpackage to the requirements, to help us get
# good debug backtraces if we ever segfault
Requires: gdb
Requires: rpmdiff-debuginfo = %{version}-%{release}

# Required by shell syntax test:
Requires: /bin/bash
Requires: /bin/csh
Requires: /bin/ksh
Requires: /bin/sh
Requires: /bin/zsh

# Requirements for recursive extraction:
Requires: util-linux
# ...for mount and umount

Requires: unzip

Requires: squashfs-tools
# ...for /usr/sbin/unsquashfs

Requires: gzip
# ...for zcat

Requires: /usr/bin/7z
# from p7zip-plugins

# abicheck.py uses /usr/lib/rpm/find-provides, from rpm-build; see bug 517213:
Requires: rpm-build

# buildroot.py requires brew module:
# Disabled; brew is deprecated in favor of koji
# See [redhat.com #929218]
# Requires: brew

Requires: diffstat

%description worker
The worker daemon queries the scheduler via XML-RPC and performs runs

%package tree
Summary: tree utilities for the worker daemon
Group: Development/Tools
Requires: rpmdiff = %{version}-%{release}

# Need rpm >= 4.6 to grok RHEL6 packages, see BZ 527783
%if %{myrhel} >= 5
Requires: rpm >= 4.6.0
Requires: rpm-libs >= 4.6.0
%else
Requires: rpm
%endif
# Needed to get yum data; latter is in EPEL; would have been nice to do this with brew...
Requires: rpm-build
Requires: yum-utils

%description tree
Tree utilities for the worker daemon when doing mass runs (brings in EPEL
dependency)

%package scheduler
Summary: scheduler daemon for rpmdiff runs.
Group: Development/Tools
Requires: rpmdiff = %{version}-%{release}

# SQLAlchemy module required for python scripts
# Will require other modules, based on which backend module you're using
Requires: python-sqlalchemy >= 0.4

# SQLAlchemy has various database backends:
# | Provider string | Python Module | RPM package     |
# +-----------------+---------------+-----------------+
# | postgres        | psycopg2      | python-psycopg2 |
# | mysql           | MySQLdb       | MySQL-python    |
# +-----------------+---------------+-----------------+
# etc

# For now, hardcode the dependency on both postgres and mysql backends
# for sqlalchemy:
Requires: python-psycopg2
Requires: MySQL-python

%description scheduler
The scheduler daemon handles all database access for the workers, exposing
an XML-RPC interface for them


%package cli
Summary: Command line tools for using rpmdiff
Group: Development/Tools
Requires: python

%description cli
rpmdiff runs a number of tests of two versions of an RPM and reports the
differences between the two.

This package contains command-line tools for scheduling rpmdiff jobs via
XML-RPC


%package release
Summary: Configuration files for rpmdiff yum repositories
Group: Development/Tools
Requires: yum

%description release
rpmdiff runs a number of tests of two versions of an RPM and reports the
differences between the two.

This package contains yum .repo configuration files for subscribing a
machine to either the production or development stream of rpmdiff

%package adhoc-webui
Summary: Web UI for adhoc runs
Group: Development/Tools
Requires: php
Requires: php-pgsql
Requires: httpd

%description adhoc-webui
rpmdiff runs a number of tests of two versions of an RPM and reports the
differences between the two.

This package contains the web UI for adhoc runs

%package selftests
Summary: Selftests for rpmdiff code
Group: Development/Tools
Requires: rpmdiff-worker
Requires: rpmdiff-scheduler
Requires: rpmdiff-cli
Requires: rpmdiff-adhoc-webui
Requires: postgresql-server
Requires: mysql-server
# 2010-09-29 esm: commented out because I can't find
# internal yum repos that have these.
#Requires: perl-IPC-Run
#Requires: perl-Test-Differences

# Some unit tests test library usage, so libpng is used, somewhat arbitarily:
Requires: libpng-devel

# unittesting.py uses xml.dom.ext, which is in PyXML:
Requires: PyXML

# unittesting.py uses javac(1) and jar(1), both via rpmfluff.py:
Requires: java-1.6.0-openjdk-devel

# abidiff.py runs the abicheck binary under valgrind:
Requires: valgrind

%description selftests
rpmdiff runs a number of tests of two versions of an RPM and reports the
differences between the two.

This package contains selftests for rpmdiff itself


%prep
%setup -q

%build
make clean
make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall INSTALLDIR=$RPM_BUILD_ROOT%{rpmdiffdir}
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_initrddir}
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d
install -m755 rpmdiff-workerd.init    $RPM_BUILD_ROOT%{_initrddir}/rpmdiff-workerd
install -m755 rpmdiff-schedulerd.init $RPM_BUILD_ROOT%{_initrddir}/rpmdiff-schedulerd
install -m600 rpmdiff-workerd.conf    $RPM_BUILD_ROOT%{_sysconfdir}/rpmdiff-workerd.conf
install -m600 rpmdiff-schedulerd.conf $RPM_BUILD_ROOT%{_sysconfdir}/rpmdiff-schedulerd.conf
install -m755 rpmdiff-admin           $RPM_BUILD_ROOT%{rpmdiffdir}/rpmdiff-admin
ln -s %{rpmdiffdir}/rpmdiff-admin     $RPM_BUILD_ROOT%{_bindir}/rpmdiff-admin
install -m755 rpmdiff-cli             $RPM_BUILD_ROOT%{_bindir}/rpmdiff-cli
install -m644 rpmdiff-cli.conf        $RPM_BUILD_ROOT%{_sysconfdir}/rpmdiff-cli.conf
install -m644 rpmdiff.repo            $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d/rpmdiff.repo
mkdir -p                              $RPM_BUILD_ROOT%{webuidir}
install -m644 webpage/*.php           $RPM_BUILD_ROOT%{webuidir}
# Kludge alert: RHEL6 runs find-debuginfo.sh to generate a debuginfo RPM;
# find-debuginfo barfs on cxgb3.ko which is included only as a selftest.
# Solution: create a dummy .debug file; find-debuginfo will see it & skip.
mkdir -p     $RPM_BUILD_ROOT/usr/lib/debug/opt/rpmdiff/tests/{before,after}
touch        $RPM_BUILD_ROOT/usr/lib/debug/opt/rpmdiff/tests/{before,after}/cxgb3.ko.debug

%post worker
/sbin/chkconfig --add rpmdiff-workerd

%post scheduler
/sbin/chkconfig --add rpmdiff-schedulerd

%preun worker
if [ $1 = 0 ]; then
    /sbin/service rpmdiff-workerd stop > /dev/null 2>&1
    /sbin/chkconfig --del rpmdiff-workerd
fi

%preun scheduler
if [ $1 = 0 ]; then
    /sbin/service rpmdiff-schedulerd stop > /dev/null 2>&1
    /sbin/chkconfig --del rpmdiff-schedulerd
fi

%postun worker
if [ "$1" -ge "1" ]; then
    /sbin/service rpmdiff-workerd condrestart > /dev/null 2>&1
fi
exit 0

%postun scheduler
if [ "$1" -ge "1" ]; then
    /sbin/service rpmdiff-schedulerd condrestart > /dev/null 2>&1
fi
exit 0

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
# Admin tool:
%{_bindir}/rpmdiff-admin
%{rpmdiffdir}/rpmdiff-admin

# Shared directory:
%dir %{rpmdiffdir}
# Shared Python modules:
%{rpmdiffdir}/daemon.py*
%{rpmdiffdir}/erratadiff.py*
%{rpmdiffdir}/interfaces.py*
%{rpmdiffdir}/logscraper.py*
%{rpmdiffdir}/rpmdiff.py*
%{rpmdiffdir}/rpmdiffconf.py*
%{rpmdiffdir}/rpmdiffinit.py*
%{rpmdiffdir}/rpmdifflogging.py*
%{rpmdiffdir}/rpmdiffmail.py*
%{rpmdiffdir}/rpmdiffresults.py*
%{rpmdiffdir}/rpmfluff.py*
%{rpmdiffdir}/table.py*

%files worker
%defattr(-,root,root)
# Daemon stuff:
%{rpmdiffdir}/rpmdiff-workerd
%{rpmdiffdir}/rpmdiff-progress-watcher.py*
%config(noreplace) %{_initrddir}/rpmdiff-workerd
%config(noreplace) %{_sysconfdir}/rpmdiff-workerd.conf

# The binaries:
%{rpmdiffdir}/rpmdiff-checker
%{rpmdiffdir}/abicheck
%{rpmdiffdir}/rpmdiff-compare-pciids

# Worker-only Python modules
%{rpmdiffdir}/backtrace.py*
%{rpmdiffdir}/worker.py*
%{rpmdiffdir}/buildroot.py*
%{rpmdiffdir}/abicheck.py*
%{rpmdiffdir}/manchecker.py*
%{rpmdiffdir}/abidiff.py*
%{rpmdiffdir}/dwarf.py*
%{rpmdiffdir}/abidb.py*

# Other scripts:
%{rpmdiffdir}/debug_runid
%{rpmdiffdir}/extract-jar.sh
%{rpmdiffdir}/extract-tarball.sh
%{rpmdiffdir}/find-rpms.pl
%{rpmdiffdir}/get-packages-with-debuginfo.py*
%{rpmdiffdir}/recursive_setup.py*
%{rpmdiffdir}/rpm_unpack
%{rpmdiffdir}/rpmdiff-elf-get-imported-functions.sh
%{rpmdiffdir}/rpmdiff-multilib-color.py*
%{rpmdiffdir}/rpmdiff-multilib-diff.py*
%{rpmdiffdir}/rpmdiff.sh
%{rpmdiffdir}/setup_rpm_queue.sh.template
%{rpmdiffdir}/setup-rpm-for-errata.py*
%{rpmdiffdir}/invoke-abicheck.py*

%files tree
%defattr(-,root,root)
%{rpmdiffdir}/get-dso-usage.py*
%{rpmdiffdir}/rpmdifftree.py*

%files scheduler
%defattr(-,root,root)
# Daemon stuff:
%{rpmdiffdir}/rpmdiff-schedulerd
%config(noreplace) %{_initrddir}/rpmdiff-schedulerd
%config(noreplace) %{_sysconfdir}/rpmdiff-schedulerd.conf

# Scheduler-only Python modules
%{rpmdiffdir}/rpmdiffscheduler.py*
%{rpmdiffdir}/shimqueue.py*
%{rpmdiffdir}/shimscheduler.py*

%files cli
%defattr(-,root,root)
# Command-line stuff:
%{_bindir}/rpmdiff-cli
%config(noreplace) %{_sysconfdir}/rpmdiff-cli.conf

%files release
%defattr(-,root,root)
# Yum repo:
%config(noreplace) %{_sysconfdir}/yum.repos.d/rpmdiff.repo

%files adhoc-webui
%defattr(-,root,root)
%{webuidir}/*.php

%files selftests
%defattr(-,root,root)
# Self-test specific files:
%{rpmdiffdir}/unittests.sh
%{rpmdiffdir}/integration-tests.sh

# Setup scripts shared by RHTS tests:
%{rpmdiffdir}/setup-worker-for-rhts.pl
%{rpmdiffdir}/configure-worker-for-rhts.py*
%{rpmdiffdir}/setup-scheduler-for-rhts.py*

# XML schemas:
%{rpmdiffdir}/analysis.dtd
%{rpmdiffdir}/rpmdiff-analysis.rng
%{rpmdiffdir}/rpmdiff-result.dtd
%{rpmdiffdir}/rpmdiff-result.rng

# Sample XML instance documents
%{rpmdiffdir}/sample-analysis-file.xml.gz
%{rpmdiffdir}/sample-test-result.xml
%{rpmdiffdir}/sample-analysis-file.xml.gz
%{rpmdiffdir}/sample-test-result.xml
%{rpmdiffdir}/sample-analysis-file-formatted.xml
%{rpmdiffdir}/sample-test-result-formatted.xml
%{rpmdiffdir}/sample-non-ascii-results.xml

# Test-only Python modules:
%{rpmdiffdir}/debugscheduler.py*
%{rpmdiffdir}/fixtures.py*

# Test-only data files:
%dir %{rpmdiffdir}/tests
%dir %{rpmdiffdir}/tests/before
%dir %{rpmdiffdir}/tests/after
%{rpmdiffdir}/tests/before/files.tar.gz
%{rpmdiffdir}/tests/after/files.tar.gz
%{rpmdiffdir}/tests/before/cxgb3.ko
%{rpmdiffdir}/tests/after/cxgb3.ko
%dir %{rpmdiffdir}/database
%{rpmdiffdir}/database/tables
%{rpmdiffdir}/database/fedora
%{rpmdiffdir}/firefox.1.gz
%{rpmdiffdir}/fpicker.uno.so.debug
%{rpmdiffdir}/policy-20071130.patch

# The unit tests:
%{rpmdiffdir}/unittesting.py*

# Integration tests:
%dir %{rpmdiffdir}/integration-tests
%{rpmdiffdir}/integration-tests/test-disk-full.py*
%{rpmdiffdir}/integration-tests/test-errata-run.py*
%{rpmdiffdir}/integration-tests/test-errata-segfault.py*
%{rpmdiffdir}/integration-tests/test-simple-errata.py*
%{rpmdiffdir}/integration-tests/test-simple-errata-2.py*
%{rpmdiffdir}/integration-tests/test-simple-yakko-run.py*
%{rpmdiffdir}/integration-tests/test-cli.py*
%{rpmdiffdir}/integration-tests/soak-test.py*

%changelog
* Fri Oct 15 2010 Ed Santiago <santiago@redhat.com> 1.4.50-1
- filelist.c: bump up max logfile size from 2M to 8,
  for bz642228

* Thu Oct 14 2010 Ed Santiago <santiago@redhat.com> 1.4.49-1
- RHEL6: change 6AS to 6any.  There are a lot of RHEL6
  variants, but no actual 6AS.  Let's use a name that's
  more clearly internal-use-only.
- test suite - more fixes

* Wed Oct 13 2010 Ed Santiago <santiago@redhat.com> 1.4.48-1
- RHEL6: support --release=6AS
- logging: include timestamp in PROGRESS messages.
- test suite fixes

* Tue Oct 12 2010 Ed Santiago <santiago@redhat.com> 1.4.47-2
- (sigh) retry 1.4.47-1, without Time::Piece

* Tue Oct 12 2010 Ed Santiago <santiago@redhat.com> 1.4.47-1
- bz642228 - security-team-level block if build log contains
  "assuming signed overflow does not occur"
- refactoring: rpmreqs.c: remove hand-maintained glibc_*.h
  files. Replace with table-driven glibc-generate script.
- usability: in generated email message, display synopsis
  of tests failing with BAD and VERIFY.

* Mon Oct 11 2010 Ed Santiago <santiago@redhat.com> 1.4.46-1
- sigh.  Work around RHEL5's lack of CPAN packages.

* Mon Oct 11 2010 Ed Santiago <santiago@redhat.com> 1.4.45-1
- bz640126 - rework PCI IDs test
- python: fix popen2-is-deprecated warning
- abicheck test suite: cleanup

* Fri Oct  8 2010 Ed Santiago <santiago@redhat.com> 1.4.44-1
- bz641464 - work around 'mount -o loop' race condition, by
  running it inside a locked code section.

* Wed Sep 29 2010 Ed Santiago <santiago@redhat.com> 1.4.43-1
- sigh again. Remove dependency on perl-*. I can't find a yum
  repo that has them.

* Tue Sep 28 2010 Ed Santiago <santiago@redhat.com> 1.4.42-1
- sigh... .41 was a nop.  Try again.

* Tue Sep 28 2010 Ed Santiago <santiago@redhat.com> 1.4.41-1
- bz524819 - in abicheck.c treat DW_TAG_variable as _member.
  This handles RHEL5-compiled binaries.

* Tue Sep 28 2010 Ed Santiago <santiago@redhat.com> 1.4.40-1
- bz524819 - continuing attempts to get abicheck working on RHEL6

* Thu Aug  5 2010 Ed Santiago <santiago@redhat.com> 1.4.39-1
- bz523614 - previous fix (look for " -s") didn't handle tabs
- bz621548 - false reports of losing a Requires when libx.so bumps version
- abidb updates.  Although the abidb URL is in a separate config file,
  not in the source code, there was some tweaking needed in the source.

* Mon Jul 19 2010 Ed Santiago <santiago@redhat.com> 1.4.38-1
- ouch. Fix broken read_dir().

* Mon Jul 19 2010 Ed Santiago <santiago@redhat.com> 1.4.37-1
- fix missing 'except' in previous checkin

* Sun Jul 18 2010 Ed Santiago <santiago@redhat.com> 1.4.36-1
- improved diagnostic for Patch0: + %patch (unnumbered) situation
- debugging: email contents of stderr to Ed; to help find problems

* Mon Jul 12 2010 Ed Santiago <santiago@redhat.com> 1.4.35-1
- bz594956 - fix memory leak when comparing two giant kernels
- sigh... RHEL5 doesn't have File::Slurp either.

* Wed Jul  7 2010 Ed Santiago <santiago@redhat.com> 1.4.34-1
- sigh... RHEL5 doesn't have Time::Piece.  Remove the dependency.

* Wed Jul  7 2010 Ed Santiago <santiago@redhat.com> 1.4.33-1
- bz610914 - started off as a simple "remove duplicates" fix but has
  ended up being a complete rewrite of the rpm-unpacking code.

* Mon Jun 28 2010 Eduardo Santiago <santiago@redhat.com> 1.4.32-1
- bz594651 - whitespace/comment diffs to config files are OK
- bz543541 - librpm may choke on parsing .spec files; handle it
- bz603116 - reuse SQL connection, to avoid resource leak
- bz542819 - workaround for SEGV in elfutils

* Tue Jun 22 2010 Eduardo Santiago <santiago@redhat.com> 1.4.31-1
- bz523614 - useradd: require space before minus sign in -s/-u,
  to avoid getting confused by 'useradd -c "priv-sep ssh"'
- bz594666 - there are some librpm specfile-parsing errors
  that we really can't handle, but we can at least improve
  our error messages.
- bz596688 - debug mail now goes to configurable address
- bz605206 - handle number-less %patch lines
- bz606383 - RHEL6 issues, e.g. i386->i686

* Wed Jun 16 2010 Eduardo Santiago <santiago@redhat.com> 1.4.30-3
- spec file changes for building on RHEL6: create dummy .debuginfo
  files for included test binary, and use %{ix86} instead of i386
  in ExclusiveArch directive (because RHEL6 uses i686, not 3)
* Mon Jun 14 2010 Eduardo Santiago <santiago@redhat.com> 1.4.30-2
- revert dependency on elfutils 0.147; let's go back to 0.137
* Mon Jun 14 2010 Eduardo Santiago <santiago@redhat.com> 1.4.30-1
- bz594665 - misleading error from /usr/lib/libfoo.so moving to /lib
- bz594625 - don't report on removed debuginfo files
- bz594442 - "bad note description size" can appear multiple times
- bz537919 - hang in check_symlink
- bz529763 - for rpmdiff purposes, treat athlon as == ix86
- bz514614 - better diagnostic for bind, in which libbind.so
  is Provided: by two subpackages
- bz508017 - handle obsolete 'Copyright' tag in old .spec files

* Wed May  5 2010 Ed Santiago <santiago@redhat.com> 1.4.29-1
- selftests: cleanup, fix broken tests, minimize verbosity, refactoring
- bz543978: don't crash on some multilib conflicts
* Thu Nov  5 2009 John W. Lockhart <lockhart@redhat.com> 1.4.28-1
- selftests: fix mounts from fstab.
* Thu Nov  5 2009 John W. Lockhart <lockhart@redhat.com> 1.4.27-1
- selftests: ensure that engarchive is mounted.
* Fri Oct 30 2009 John W. Lockhart <lockhart@redhat.com> 1.4.26-1
- buildlog.c, unittesting.py, cleanbuildlog.c: update to handle difference
  in rpm-tmp directory name due to rpm-4.6 change.
* Wed Oct 28 2009 John W. Lockhart <lockhart@redhat.com> 1.4.25-6
- Fix unittests.sh to run to completion, comment out extraArgs test for now.
* Tue Oct 27 2009 John W. Lockhart <lockhart@redhat.com> 1.4.25-5
- Fixes for selftests, alternative fix for rpm4.6 compatibility.
* Fri Oct 23 2009 John W. Lockhart <lockhart@redhat.com> 1.4.25-4
- Updates for compatibility with rpm v4.6.x.
* Fri Oct 23 2009 John W. Lockhart <lockhart@redhat.com> 1.4.25-3
- Update build requirements.
* Fri Oct 23 2009 John W. Lockhart <lockhart@redhat.com> 1.4.25-2
- Update build to use rpm-4.6.x materials to read RHEL6 RPMs, see BZ 527783.

* Thu Sep 17 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.25-1
- fix a fatal error in rewritten Dangling Symlink test when handling absolute
symlink targets containing more than one leading '/' character (found via mass
run testing using RHTS)

* Wed Sep 16 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.24-1
- Ad-hoc web UI:
  - distinguish between analysis vs comparison in the results page for a run
  - add the status ("score") of the run to the web page, to make what's going
on more obvious when a run hasn't been processed yet
- ABI checker: workaround a change in python-2.4.3-27.el5 subprocess module
that was causing a trailing error message in any ABI check invocations that
listed symbol names (I've reported the python change as bug 523851)

* Tue Sep 15 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.23-1
- fix some bugs found by pylint
- selftest fixes
- remove dead code

* Mon Sep 14 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.22-1
- call out to ABI DB with release="RHEL5.1" for 5Client and 5Server, and don't
call out to the ABI database otherwise (the db will only be populated for
RHEL5, initially)
- File Sizes test: always warn about files going from zero size to non-zero
size (we only tested for the reverse before); reinstate the "changes size by >
20%" testing below /lib/modules, but increase the threshold of the size of the
_change_ for such files to 512KB, so that only the largest changes to kernel
modules are flagged (bug 191809)

* Thu Sep 10 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.21-1
- File Sizes test: suppress the test for a percentage change in the size of a
file when the file is below /lib/modules, since this is continually happening
for the kernel and is expected; we still test for sizes dropping to
zero (bug 191809)
- selftest fixes

* Thu Sep 10 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.20-1
- selftest fix

* Wed Sep  9 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.19-1
- Shell Syntax: don't try to compare the syntactic correctness with that of
the old file if the latter wasn't a shell script (restoring old behavior for
this case)
- speed up ELF handling when using abicheck (by not extracting
externally-visible symbols for use with the old Library Symbols test, since we
never use them when using abicheck)
- internal cleanups
- selftest fixes

* Tue Sep  8 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.18-1
- indicate which shell syntax we tested against when reporting a shell syntax
error (see bug 463586)
- fix major performance regression I accidentally introduced in 1.4.17-1
(caught in RHTS)

* Tue Sep  8 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.17-1
- ELF test: add new test: report a BAD-level error about i386 ELF files that
are found in non-i*86 arch builds (provided they are not in a nested
container) (rfe 476559)
- XML validity test: only run xmllint if we need to, and cache results by MD5
sum, hopefully speeding up checking of large numbers of XML files when the same
content occurs across multiple architectures (kdelibs; bug 507644)
- internal cleanups

* Thu Sep  3 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.16-1
- Extension to "Patches" test: run all new patches through "diffstat".  Report
an INFO-level message about all "large" new patches, containing the result from
diffstat.  "Large" in this context means affecting 20 or more files or touching
5000 or more lines of code (by summing the added/deleted counts) (RFE 514343)
- rework the internals of the virus test (work towards bug 510575)

* Wed Sep  2 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.15-1
- extend the metadata test to issue a VERIFY-level warning about changes to
"License", "Vendor", "Summary", and "Description" fields

* Tue Sep  1 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.14-1
- when using the ABI database results, separate reports of ABI changes into
those that the ABI DB reports as having external consumers vs those that don't.
Add headers and whitespace to try to make the report easier to read.
- selftest fixes

* Mon Aug 31 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.13-1
- rewrite of the "Dangling symlink" test (fixing bug 452135 and bug 462528)
- rework performance threshold for oo.org so that "openoffice.org2" is also
expected to take a long time

* Thu Aug 27 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.12-1
- use changing_path when reporting on permissions changes, and use the standard
cross-arch result-aggregator

* Thu Aug 27 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.11-1
- selftest fixes

* Thu Aug 27 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.10-1
- identify .sys files within virtio-win as being Windows binaries (using the
presence of PE32 substring within magic type)
- disabled extraction of jar files for now: not yet properly tested, not
required for RHEV, and seems to massively slow down oo.org runs
- break out Windows driver .inf files into their own category when considering
changing files, and issue an INFO message with a textual difference for each
one (bug 514789)

* Wed Aug 26 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.9-1
- selftest fixes

* Tue Aug 25 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.8-1
- Improve how rpmdiff handles a conversion from a noarch build to a per-arch
build (bug 490492):
  - Explicitly report when architectures appear and disappear e.g. when a
  noarch build splits into per-arch builds
  - Handle the latter case by matching up the noarch build against one of the
  arch builds, and report changes in a form like "on i386 (relative to noarch)"
  when reporting on a change to a file or subpackage

* Tue Aug 25 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.7-1
- install recursive_setup.py and add to worker subpackage
- enable the three selftests for RHEV with recursive containers

* Tue Aug 25 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.6-1
- enable the recursive unpacking of nested containers
- add the various requirements for recursive extraction to the worker
subpackage
- various source cleanups

* Mon Aug 24 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.5-1
- display fuzzily-matched paths in more places
- selftest fixes
- change default config to stop sending results to katzj@redhat.com

* Fri Aug 21 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.4-1
- display fuzzily-matched paths in a human-readable way throughout:
  e.g: "usr/share/foo-{1.2|2.0}/README.txt changed size"
- further work on nested containers for RHEV, adding selftests for
rhev-hypervisor, virtio-win and xenpv-win (disabled for now until I finish
packaging the worker dependencies)

* Wed Aug 19 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.3-1
- fix a bug in nested container peer matching
- ABI Database hooks: implement two restrictions: only contact the ABI DB for
i386 and x86_64, and for ELF files that have a SONAME (see RT 44952)

* Wed Aug 19 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.2-1
- Rewrite of the multilib test (bug 191786)
  - Report on a per-subpackage and per-arch basis on sub-package/arch/arch
  combinations that change from being multilib-clean to multilib-unclean and
  vice versa.
  - For the former case, list the first 10 files involved, and give a diff of
  the first.
  - Fix so it tests for the ia64 vs i386 pairing (it wasn't before).
  - Continue not to test debuginfo packages, and improve the logic for
  determining this.
  - When giving a multilib diff of a pair of gz files, try decompressing them
  and showing the diff of the resulting files (bug 471012)
- add --abidb-url option to rpmdiff-checker, and rewrite of the harness for the
ABI checker, both working towards querying the ABI database (but 290071; not
yet finished)
- improve error handling within ABI checker (bug 517213)
- various reorganizations of the code, working towards support for nested
containers for RHEV (see bug 514779)
- add option "--no-limits" to rpmdiff-checker, to turn off all rate-limiting
of messages
- selftest fixes

* Mon Aug 10 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.1-1
- fix compilation problem on x86_64

* Mon Aug 10 2009 David Malcolm <dmalcolm@redhat.com> - 1.4.0-1
- enable ABI checking by default, replacing the --abicheck opt-in with
a --no-abicheck opt-out
- reorganization of source tree

* Thu Aug  6 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.204-1
- ABI test: the ABI checker now compares the basename of the decl_file for each
type with the basename of the files in all of the various subpackages.  It
treats basenames that match files under /usr/src/debug and do not match files
elsewhere in the payload (e.g. in a -devel subpackage) as private, and uses
this to treat types defined in such files as private, suppressing many
ABI-change messages (bug 301341)
- Manpage test: handle files with a .gz suffix that aren't actually compressed
(bug 510385)
- selftest for the above, and selftest fixes

* Tue Aug  4 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.203-1
- ABI test:
  - support versioned symbols, rather than emitting a bogus "duplicate symbol"
  message
  - show size and name of enums/base_types in the debug description.
  - Only show the offsets when --debug is supplied, to give arch aggregation a
  better chance.
  - avoid an assertion failure seen on variable DIEs without locations, seen
  occasionally on RHEL4
  - split invocation lines when reporting errors, so that rpmdiff doesn't
  truncate them

- Nested containers (all of this is disabled for now by default; still need to
add the worker dependencies):
  - Add support for .msi files and .cab files, using 7z and cabextract
  - Extract .vfd files using loopback mounting (rfe 514790)
  - Extract initrd images
  - Suppress filetype change noise for Microsoft .cab files and squashfs
  images, if we're recursively comparing their actual content
  - don't extract symlinks to containers, only the containers themselves.
  - don't attempt to do any DSO ABI comparisons within a nested container
  (unclear how we would get at the debuginfo)
  - don't recursively extract within an SRPM
  - remove all usage of "sudo": this is meant to be run as root

- rpmdiff-cli: add --work-dir option to "local-compare" verb, and stop the
default from using an absolute path

* Mon Jul 27 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.202-1
- ABI test:
  - treat types declared within /usr/src/debug as private, along with a
  heuristic for detecting opaque structs; stop the comparison if both types are
  private.  Improves behavior of bug 301341.
  - emit a recursive debug description of the DIEs involved in a type change,
  giving offset, human readable description, and file/line information where
  available
- add link for filing bugs to the ad-hoc web UI (bug 493220)
- selftest fixes

* Fri Jul 24 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.201-1
- fix a segfault in abicheck.c within compare_enum

* Fri Jul 24 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.200-1
- implement nested containers, but disable the recursive extraction hooks
for now (until this code has seen some serious testing)

* Fri Jul 24 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.199-1
- improvements to wording of some error messages
- make the error reporting interface more robust in the face of malformed HTML
- selftest fixes

* Thu Jul 23 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.198-1
- internal cleanups in preparation for nested containers
- fix a bug with symlinks in the new manpages test (bug 513322)
- rpmdiff-cli: fix the "compare-dir" command
- selftest fixes

* Wed Jul 22 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.197-1
- ABI test:
  - ignore "cannot get string value for type" errors from abicheck.c:get_string,
  rather than complaining about them in rpmdiff
  - hopefully finally fix the assertion failure in compare_compound
- Manpages test: extend the manpage test to complain about admin executables
that don't have manpages (RFE 512981)
- Reimplement message-reporting API, removing html vs text split, instead just
supporting the HTML output (preparatory work for supporting nested/recursive
containers e.g. ISO files inside RPMs)
- selftest fixes

* Tue Jul 21 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.196-1
- ABI Checker:
  - when reporting an ABI change within rpmdiff, include the before/after DIE
  offsets of the change, where possible, to make it easier to go back and debug
  a run
  - improve the wording of the output when symbols disappear
  - display the demangled form of C++ symbols, along with the "raw" symbol name
  - make the code more tolerant of various unusual children of a class_type
  DIE, seen on complex C++ examples (openoffice.org)
  - fix behavior when encountering C++ destructors and virtual functions
  - give a more descriptive error when a type tag or type modifier changes
  - selftest fixes for the above
- rpmdiff-cli: add a --arch option to "local-compare", to support restricting
the comparison to just one arch (to make it easier to deal with openoffice)

* Fri Jul 17 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.195-1
- fix a segfault in the abicheck binary when dwarf_getscopes returns 0 (seen
on a bind ppc binary with "_savefpr_14" symbol)
- log the backtrace when abicheck has a segfault, so that it ends up in the
rpmdiff log
- avoid a deadlock when processing large amounts of output from abicheck
- selftest fixes

* Thu Jul 16 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.194-1
- ABI checker:
  - fix various infinite recursions due to DIE graphs that combine mutually
  recursive structs, pointers, callback functions
  - ignore informational lines from abicheck
  - properly compare function pointer types in both implementations of the
  checker ("unhandled type 21/0x15")
  - selftest fixes

* Wed Jul 15 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.193-2
- add build requirements on elfutils-devel and elfutils-libelf-devel for the
abicheck binary

* Wed Jul 15 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.193-1
- "Execshield" test: bulletproof against a degenerate case seen with sparc
binaries (bug 511999)

Continuing work on the "ABI" test:
- Embed a local copy of abicheck into rpmdiff's source tree, incorporating
various bugfixes and cleanups, rather than using an external abicheck rpm;
drop the dependency on the external abicheck package
- give details when reporting on a type changing size
- report on precise changes of type
- fix a long-standing read past end of array during enum handling (detected
with valgrind)
- switch from the python implementation to the abicheck binary, and don't try
to use an ABI db for now
- selftest fixes
- cleanups

* Mon Jul 13 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.192-1
- selftest fixes
- increase required version of elfutils from 0.94.1-2 to 0.137-3

* Mon Jul 13 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.191-1
- selftest fixes

* Fri Jul 10 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.190-1
- Reimplementation of the ABI test:
  - improve the python DWARF parser, building a selftest using a complex
  example of in-the-wild C++ (and C) DWARF data taken from openoffice
  - use the existing test suite for ABI checking to build a fine-grained suite
  of tests. Invoke each test on both the abicheck.c implementation and the
  python implementation, so that we can use the former as an oracle towards
  finishing the latter.
  - improvements to the python-based abi checker:
    - improve abidiff.py so that it has feature parity with abicheck.c, either
    matching its output, or performing better, for each testcase
    - fix non-inline implementation of C++ member functions
    - provide richer information when a variable changes type, detailing what
    the change was, and the file/line in the source code
  - rewrite invoke-abicheck.py so that it uses the python ABI checker,
  unfiltered by the ABI database for now

- "File list" test:
  - gather source files going away below usr/src/debug into a separate, lower
priority category, storing them per-container, and using this to issue a
low-priority message about them (bug 204834)
  - fix the test for CVS and .svn directories so that it is only run upon
directories, and uses an exact match (bug 510753)

- Packaging changes:
  - add abidiff.py, dwarf.py to the worker, and fpicker.uno.so.debug to the
selftests package
  - add explicit requirements on all of the various shells required by the shell
syntax test

* Tue Jul  7 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.189-1
- selftest fixes

* Mon Jul  6 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.188-1
- fix before/after typo introduced in 1.3.185-1 that led to segfaults when a
new unstripped binary was added to a package
- selftest fixes

* Mon Jul  6 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.187-1
- optimize the PCI IDs test
- selftest fixes
- add explicit requirement on /sbin/depmod

* Thu Jul  2 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.186-1
- "Module PCI IDs test": reimplement this test
- "Patches" test: warn about dist tags that aren't of the form %%{?dist};
don't yet warn about missing dist tags, as they aren't mandatory (bug 431946;
based on work by jhrozek)
- remove package scripts

* Wed Jul  1 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.185-1
- "File Types" test: ignore changes that add a ", for GNU/Linux 2.6.9" ELF note
as this appears to be happening for all .debug files (bug 509184)
- "Binary Stripping" test: I rewrote the internals of this test, splitting
out the various cases.  Correctly handle expected values for "real" ELF files
vs ".debug" ELF files, and set the severity of messages to BAD vs INFO when
reporting on a regression/improvement. Should fix bug 204876, bug 225478,
bug 479156, bug 463730.  Don't run the test on kernel modules (bug 496660)
- html-escape errors when reporting them into the result database (bug 247652)

* Mon Jun 29 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.184-1
"Execshield" test: tweak the FORTIFY_SOURCE warning.  In order to trigger this
warning, as well as dropping the import of "_chk" fortified symbols, an ELF
must now also import unfortified symbols (bug 497901)
- "Patches" test: increase the severity of the "Patch is no longer applied"
test from an INFO to a VERIFY if the package has not been rebased (bug 448825).
Report all such patches in a single message, rather than one message per patch
- selftest fixes

* Fri Jun 26 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.183-1
- disable the rpmlint test by default for now, to make it easier to get the
full test suite passing again.  It can be enabled by using a new command-line
option (--enable-rpmlint command) to rpmdiff-checker, and globally for the unit
tests
- selftest and pylint fixes
- avoid getting into infinite loops in the path fuzzymatcher for the case where
repeated substitution of a string doesn't change it
- hopefully fix the zombie progress notifier issue seen on scheduler (bug
247188 again, mbabej)

* Thu Jun 25 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.182-1
- rpmlint test:
  - ignore the "incoherent-version-in-changelog" warning as many packagers
are (rightly, IMHO) omitting the dist tag from their changelog
headers (like I do, in this specfile)
  - filter away architecture and other information from the headers of
rpmlint messages, to enable cross-arch aggregation of the results
- fix an infinite loop that would happen in the desktop file validation test
if a payload directory had a name ending in ".directory" (bug 508118)
- rpmdiff-cli: fix analyse-dir so that it actually creates a group and
schedules the runs into it

* Wed Jun 24 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.181-1
- selftest fixes

* Wed Jun 24 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.180-1
- build our own version of rpmlint, with a --nosummary option to suppress some
noise
- improve path matching for the case where e.g. version-release occurs more
than once in a payload file's path (bug 507877)
- various selftest improvements

* Tue Jun 23 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.179-1
- add worker requirement on rpmlint
- new selftest

* Tue Jun 23 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.178-1
- New test, requiring a new row inserted into the rpmdiff_tests table for both
databases: TEST_METADATA:
  - warns about references to "Fedora" in the summary and description of
packages (bug 242928)
  - warns about any RPMs that have a vendor that isn't "Red Hat, Inc."
  - warns if the "Build Host" is not within ".redhat.com" (bug 450317)
  - generalize the test for unprofessional language from the changelog test so
that it's now also performed on package Summary, Description and License
metadata (RFE 450319)
- Newly enabled test: TEST_RPMLINT (has been within database for a long time,
but test was disabled): run rpmlint on all rpms, and report all messages for
new packages, and all new messages for package comparisons (bug 190892).  Not
yet fully tested; many unit tests pass, but I expect a few failures have been
introduced.  It will be easier to test and track them down in RHTS, hence
committing/building

* Fri Jun 19 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.177-1
- fix segfault (due to uninitialized local) seen on x86_64 machines when doing
a --nocompare run on a specfile containing a hardcoded /usr/lib reference
- rpmdiff-cli: fix reversed order of logging of local worker before/after setup
- "RPM scripts" test: validate "useradd" invocations in scriptlets of all subpackages, not just for the main package (bug 506724); improve error reporting

* Wed Jun 17 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.176-1
- selftest fixes

* Tue Jun 16 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.175-1
- selftest fixes

* Mon Jun 15 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.174-1
- "RPM changelog" test:
  - rewrite of the test for a changelog entry being removed, as it was fragile.
  Instead, we now include a simple unified diff of the changelog between old
  and new: if lines have changed or been removed, this is a VERIFY warning,
  otherwise merely an INFO-level message.  (bug 434833)
  - include the line number when reporting on unprofessional language
- "Desktop file sanity" test: include the errors/warnings from
desktop-file-validate when reporting a failure (bug 505031)

* Tue Jun  9 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.173-1
- capture the error message if parsing the specfile fails
- selftest fixes

* Thu Jun  4 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.172-1
- add java requirement to selftests subpackage
- buildlog test aka "Testsuite Regressions": improve the wording of the "make failures" test, and display the make errors in context (up to the first 20)

* Wed Jun  3 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.171-1
- Various optimizations (based on using "sysprof" during kernel rpmdiff
comparisons), including:
  - do not run "eu-readelf -d" upon kernels, kernel modules, or .debug files,
  as the results are useless, and "sysprof" indicated this was expensive
  - stat each file once rather than twice
  - optimize parsing of /sbin/modparam on kernel modules
  - optimize the new manpage validator (based on perl runs)
- "File Types" test: rewrite and extend the noise suppression for file(1)'s
output upon textual types (bug 440829)
- "Changed Files" test: add a "jar files" category for changed files, so that
they are broken out from merely being "files". They remain medium priority in
the change report, and are reported after changing binaries.
- "Patches" test: add a warning if the specfile can't be parsed.  Set the
_sourcedir macro to the correct location, so that macros that reference source
files can be evaluated (bug 470981)
- selftest enhancements

* Thu May 28 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.170-1
- rewrite of the "man pages" test, replacing broken validator that always
passed with a new validator that can detect bogus manpages (bug 232453)
- display changing patches (within the SRPM), as part of the "Patches" test.
They are displayed with a diff, as an INFO level message (RFE 502427)
- fix the "Unapplied Patches" test so that it knows about the ApplyPatch macro
seen in post-RHEL5 kernels (kernel-rt V1/Fedora 7 kernel onwards) (bug 502238)
- more selftests

* Wed May 27 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.169-1
- fixup worker/scheduler interface checks and documentation; selftest fixes

* Tue May 26 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.168-1
- fix installation of new files

* Tue May 26 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.167-1
- initial implementation of RFE 489891 (needs further work on database design)
- add manchecker.py to the worker subpackage, and firefox.1.gz to the selftest
subpackage

* Wed May 20 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.166-1
- wrap the debuginfo dir/link checks so they're only run for comparisons; they
don't make sense for --nocompare mode

* Tue May 19 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.165-1
- Rework fix for bug 496879 to work with files that weren't part of the old
package (even implicitly), and generalize to work with symlinks as well as
directories (bug 496953)

* Mon May 18 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.164-1
- New test: issue a BAD-level warning on any new patches that are under 4 bytes
in size, trapping "empty patch" mistakes (rfe 486102)
- Fix a reporting error when a new file is added to multiple subpackages (bug 493218)
- Selftest fixes

* Tue May 12 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.163-1
- yet more selftest fixes (this time the integration tests, due to beehive
going away)

* Tue May 12 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.162-1
- lots of selftest fixes

* Tue May 12 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.161-1
- fix bug in email templates
- remove old beehive-only code

* Tue May 12 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.160-1
- selftest fixes

* Mon May 11 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.159-1
- implementation of proposed rewrite of the "files changed" report: categorize
changed files, and emit prioritized messages based on the categories. This
probably breaks many of the self-tests, but it will be easiest to fix them by
running them within RHTS, hence I'm committing this code now. (bug 484251)
- update URLs to results sent within emails (bug 497899)
- suppress individual reporting of directories below usr/lib/debug in debuginfo
rpms that change from being implicitly created to being part of the payload.
Instead, count them, and report them all with a single INFO (noise suppression
after rpmbuild change; bug 496879)

* Mon Apr 20 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.158-1
- selftest fix

* Fri Apr 17 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.157-1
- fix scheduler error with signed RPMs (bug 496282)

* Wed Mar 11 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.156-1
- selftest fixes

* Tue Mar 10 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.155-1
- selftest fixes

* Mon Mar  9 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.154-1
- fix typos in db query code
- selftest fixes

* Fri Mar  6 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.153-1
- remove call to get_released_packages.  Use rpmdiff_runs.old_version for
Errata runs, as described in bug 467254; remove releasedrpms.py* and the grp
failure integration test from the payload

* Fri Mar  6 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.152-1
- fix path/permissions issue with backtraces

* Fri Mar  6 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.151-1
- selftest fixes

* Thu Mar  5 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.150-1
- add a soak test of the scheduler to the test suite

* Wed Mar  4 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.149-1
- fixes for mysql selftests

* Wed Mar  4 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.148-2
- add requirement on mysql-server to rpmdiff-selftests

* Wed Mar  4 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.148-1
- try to extend integration testing to run against both postgres and mysql
databases
- require both postgres and mysql backends for sqlalchemy on the scheduler

* Wed Mar  4 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.147-1
- require sqlalchemy 0.4 or later: EngOps will need to add this to the
production repo (probably also the database backends)
- selftest improvements

* Tue Mar  3 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.146-1
- replace all hand-coded database INSERT calls with SQLAlchemy calls (thus
avoiding dialect and escaping issues); likewise replace some UPDATE calls
- reorganize scheduler code so that most database access is in
rpmdiffscheduler.py, rather than scattered through multiple files

* Tue Mar  3 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.145-1
- fixes to db access and to selftest code

* Mon Mar  2 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.144-1
- fix typos in sqlalchemy code

* Mon Mar  2 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.143-1
- add requirement on python-sqlalchemy; change postgres requirement from
postgresql-python to python-psycopg2

* Mon Mar  2 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.142-1
- initial attempt at generalising scheduler's database access from Postgres to
other db backends.  Not yet known to work; plan to test further in RHTS.
- Will require configuration change on scheduler (add "PROVIDER: postgres" in
the [erratadb] and [yakkodb] stanzas)

* Mon Mar  2 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.141-1
- support hexadecimal keys in signed package fixup, with a test case (fixes
bug 487542)

* Fri Jan 23 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.140-1
- Fix code that adjusts paths to signed packages received from grp

* Fri Jan 23 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.139-2
- remove brew dependency

* Wed Jan 14 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.139-1
- don't use abicheck when running selftests

* Tue Jan  6 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.138-1
- selftest fixes

* Mon Jan  5 2009 David Malcolm <dmalcolm@redhat.com> - 1.3.137-1
- selftest fixes

* Tue Dec  9 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.136-1
- ensure that the ABI db isn't down when running the selftests

* Tue Dec  2 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.135-1
- Don't run the old "library symbol going away" test if we have the abi
checker; it does the same test, and filters the results based on actual
usage, and thus should have a considerably higher signal:noise ratio
- Rework invocation of abicheck, by calling invoke-abicheck.py to do the bulk
of the work (parsing and cleaning the output, making XML-RPC calls, etc)
- Selftest fixes

* Mon Dec  1 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.134-1
- package up the python code for invoking abicheck
- gracefully fall back when XML-RPC errors occur talking to ABI DB
- point the ABI code at rpmgrok-01.lab.bos; various improvements to the
unit tests
- improvements to result emails
- set performance threshold for kernel-rt
- add support for doing local comparisons against beehive packages

* Thu Oct 30 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.133-1
- add support to rpmdiff-cli for specifying packages for local comparison
via paths to srpms; assumes the Brew/Koji layout of archs, subpackages,
build logs (work towards RT #29336)
- remove the comment/waiver form from the ad-hoc UI as it was confusing
people (wasn't wired up to errata system, and won't be)
- don't try to peer-match kernel modules that moved directory when there's
no peer RPM (fix bug 465509)
- fixup various self-tests

* Mon Sep 22 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.132-1
- move repos from porkchop.devel and devserv.devel to lacrosse.corp (see
https://engineering.redhat.com/rt3/Ticket/Display.html?id=28144 )
- mention the presence of whitelisted setuid files,
but don't flag them as security sensitive (which would require the
security team to waive them; see bug 463303)
- use standard arch-aggregation (rather than hardcoding) for the symlink test
and the test for changed files
- don't report changed .pyc and .pyo files individually; they contain
timestamps so will always change.  Instead, add a summary to the end of the
changed files report e.g.
           [INFO] [] 42 .pyo/.pyc file(s) changed
(bug 453592)
- clean up reporting of header file differences (should do a better job of
cross-arch aggregation)
- fixup css URLs in ad-hoc web UI
- internal cleanups

* Thu Aug 14 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.131-1
- use common cross-arch aggregator for consolidating results for the file size
and DT_NEEDED tests (fixes part of bug 458451)
- don't run xmllint on .jsp files

* Wed Jul 23 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.130-1
- disable buildroot diff for now
- use the arch-aggregation code for XML test; fix an assertion failure where a
file becomes XML (bug 456330)
- fix false positive in rpath test (bug 447625)
- attempt to handle paths to "signed" RPMs on /mnt/redhat by trying to find the
unsigned path relative to them
- implement support for Brew scratch builds for local comparisons
- fix false positive from requires/provides test when an epoch is involved (bug
447917)
- lots of internal cleanups
- fix a segfault that happened when a changelog stanza is first added to a
package (bug 449449)
- support doing comparisons based on arbitrary RPM manifest files e.g. for when
a package is renamed, or splits into multiple packages (RFE448770)
- minor improvements to reporting when files/directories/links/libraries move
subpackage, identifying which category they fall into
- selftests for the above

* Fri May 23 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.129-2
- rebuild

* Fri May 23 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.129-1
- new test: show build root differences (remember to add necessary rows to the
databases before deploying to production)
- acroread should no longer take excessively long as bug 433521 is fixed;
remove it from performance threshold special-cases

* Wed May 14 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.128-1
- deal with absolute paths and parameters in Exec= clauses
- add various links to webpage; implement a front page

* Mon May 12 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.127-1
- avoid an assertion failure in XML test when encountering a symlink to an
XML file
- selftest fixes

* Mon May 12 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.126-1
- selftest fixes

* Fri May  9 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.125-1
- simplify many end-user-visible results by grouping equivalent results from
different architectures.  This is now done automatically in the message
reporting layer, replacing various fragile and complex hand-coded approaches to
this with a more general and simpler system, and covering many more tests.
Many messages should now group together, leading to simpler rpmdiff reports for
the end-user.
- rewrite XML test.  This has been doing a wellformedness test on XML files,
but doing it in a buggy way, and reporting errors as being "invalid", which was
misleading as "valid" has special meaning for XML files.  The test should now
be fixed; it checks for the well-formedness (and encoding) of XML files, and
reports errors as such (bug 185678, bug 232480)
- drop the "(new test)" prefix from warnings about an existing patch no longer
being applied - this test is 3 years old, so is hardly new (introduced in CVS
2005-03-29 in r1.24)
- warn about first 5 occurrences of "dereferencing type-punned pointer will
break strict-aliasing rules" seen in build log, for each architecture (rfe
225186)
- extend desktop file test to look for executables and icons referred to in
desktop files, issuing warnings if they are not found, or they do not have
appropriate permissions (rfe 200930)
- improve reporting of metadata changes by capitalizing to Requires, Provides,
Conflicts, Obsoletes, laying out to better resemble specfile syntax, and using
"BuildRequires" where appropriate (bug 221808)
- when taking a textual diff of scriptlets, config files and triggers, avoid
adding the header containing the absolute paths under the workdir into the
result, since this is noise as far as the user is concerned
- don't report all the files from an arch that has newly appeared as "new
files" (bug 198815)
- added test cases for the above
- rpmdiff-cli: generate XML output for local runs
- cut over config of web UI from yakko db to db.engineering

* Wed Apr 23 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.124-1
- distinguish files vs dirs when reporting on setuid/setgid (bug 428989)
- bulletproof requires/provides subpackage test against a segfault seen when
provides list of a subpackage is empty
- selftest fixes

* Tue Apr 22 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.123-1
- selftest fixes

* Tue Apr 22 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.122-1
- issue an INFO-level message about new build requirements, rather than
silently ignoring them (bug 251210)
- work around a performance problem when demangling large numbers of C++
symbols that was causing acroread errata to take 2 hours (bug 433521)
- improve peer-matching in file paths:
  - if a tarball is named something-SOMEVERSION-src.tar.gz, then
  match based on SOMEVERSION (for jbossts, bug 443147)
  - generalize matching on foo-SOMEVERSION from tarballs named just
  foo-SOMEVERSION.tar.gz to also cover those named foo-SOMEVERSION.tar.bz2,
  foo-SOMEVERSION.tgz, and foo-SOMEVERSION.zip
  - if all else fails, match on package version (if longer than 4 characters)
- fix some bugs in message reporting that could lead to a "SUCCESS" subject
line for the notification email even in the presence of errors
- extend requires/provides test to detect the absence of certain explicit
version requirements.  If one subpackage provides a library consumed by another
subpackage(s) and thus have an ABI relationship, then rpmdiff will now warn if
the consuming subpacakges don't have an explicit, exact version requirement on
the providing subpackage.  This is to prevent us having to do QA on every
combination of old and new subpackages, rather than on just the new
subpackages, guarding against cases where a customer only upgrades one of the
subpackages but not the other (bug 204096, which has an example where this
affected a customer)
- selftest fixes

* Wed Apr 16 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.121-1
- reimplement per-release policy hooks (not set for ad-hoc runs), re-enabling
whitelisting of added glibc requirements based on RHEL release, 2.1 epoch
whitelisting (bug 240518)
- extend glibc requirements whitelisting to RHEL5 (bug 442070)
- selftest fixes

* Tue Apr 15 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.120-1
- new test: check rpaths in elf files (RFE 196893); see
http://intranet.corp.redhat.com/ic/intranet/RpmdiffRPathTest.html (needs
database insertion to cover this)
- extend build log testing, warning about all occurrences of
"will always overflow destination buffer" in the build logs (RFE 157465)
- fix warning about perl modules changing version (bug 441723)
- track which files/dirs/links are part of payload, and	which are merely
implicitly created during cpio unpack, and improve added/removed and
permissions tests accordingly (bug 440503, bug 218829)
- issue warning if a failure to expand a macro is detected in the build
log (RFE 250127)
- issue performance warning emails to rpmdiff maintainer if rpmdiff takes
longer than expected on a given package (RFE 440959)
- ignore ABI changes for kernel-debug of the form provides kernel(foo) = bar
since these always change and are not important for that subpackage (bug
440712)
- indicate "directory" vs "file" vs "link" rather than just "file" in some
warnings

* Tue Apr  8 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.119-1
- consolidate db access in web UI
- rewrite version/release fuzzy-matching of peers, extending to cover matching
using versions in source tarball names (bug 238724) and special-case for
sendmail (bug 223853)

* Mon Apr  7 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.118-1
- glibc-debuginfo-common is a debuginfo file (bug 225800)
- fix some filedescriptor leaks when reading rpm headers
- selftest fixes

* Fri Apr  4 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.117-1
- Fix bug 432417: fuzzy-match paths using VERSION-RELEASE fragments
- selftest improvements
- add MD5 sums to output when reporting a changed source tarball
- add --fail-assertion option, to verify handling of how the harness handles
rpmdiff-checker hitting a g_assert
- suppress messages from "file" concerning bad sizes of name/description
for a note segment (bug 253280)
- add text of useradd line from specfile when issuing a	warning about it
- reimplement parsing of some eu-readelf output, so that we can easily
extract extra info (e.g. RPATH, towards addressing bug 196893)
- fix bug 433042: take epoch into account when comparing versions
- detect error messages concerning failure to apply patches, reporting them
as errors with severity level BAD (bug 438709)

* Thu Mar  6 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.116-1
- fixup bug with versioned libraries when gauging severity of abicheck issues
- add breakdown of runs by status to group.php

* Tue Mar  4 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.115-1
- more selftest fixes

* Tue Mar  4 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.114-1
- selftest fixes
- reimplement logic when testing for empty RPMs
- fix test selection in webui's run.php

* Tue Mar  4 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.113-1
- selftest fixes
- fix regression to ghost file handling (second part of bug 230791) that I
introduced when adding the file ownership test

* Mon Mar  3 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.112-1
- clarify wording of TEST_EMPTY error messages, and add architecture to them
- selftest fixes

* Mon Mar  3 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.111-1
- selftest improvements

* Mon Mar  3 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.110-1
- improve handling of changes to requires/provides/obsoletes/conflicts, based
on work by jhrozek; large extension of unit tests to cover this (bug 191822
and bug 226690)
- fix end of results array bug introduced when I added new test

* Mon Mar  3 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.109-1
- disable notification of security-response-team@redhat.com when
security-sensitive results happen, based on IRC chat with bressers
- update db to reflect the two new tests
- move ownership test from TEST_PERMS into its own new test
- new test: check for RPMs with empty payloads (jhrozek, bug 249746)

* Fri Feb 29 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.108-1
- extend TEST_PERMS to issue errors for file owner/groups of
"brewbuilder" or "mockbuild" outside of SRPMs

* Wed Feb 27 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.107-1
- selftest improvements
- only sort list of removed symbols once (see bug 433521)

* Fri Feb 15 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.106-1
- fix compiler warning

* Fri Feb 15 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.105-1
- add -Werror to CFLAGS

* Wed Feb 13 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.104-1
- disable fix for 432417 for now, since	it causes a performance regression for
RHEL5 kernel runs

* Tue Feb 12 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.103-1
- selftest fixes

* Tue Feb 12 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.102-1
- fix intermittent exception reporting a result on a run when a config file
changes (bug 432550, dmalcolm)
- fuzzily-match files based on version-release, which ought to suppress a lot
of noise on kernel errata (bug 432417, dmalcolm)

* Fri Feb  8 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.101-1
- fix to self-test for command-line tool
- fix false positive from "moved packages" test accidentally introduced
in 1.3.97-1 (bug 432051)

* Thu Feb  7 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.100-1
- fixes to self-tests

* Wed Feb  6 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.99-1
- fixes for perfomance testing, to ensure fatal errors are flagged
- fix fatal error when worker reported a result back to scheduler involving
config file changes containing unicode chars above code point 255 (bug 429363)

* Fri Jan 25 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.98-1
- disable threads for now, to see how much they affect performance, and if
the segfault in 1.3.97-1 goes away (c.f. bug 429883)
- fix bug 234078: don't complain about specfiles with shebang lines

* Tue Jan 22 2008 David Malcolm <dmalcolm@redhat.com> - 1.3.97-1
- introduce indexes on exact paths and on fuzzynames to optimize away
various O(n^2) spikes seen on openoffice.org rebase for
"crossreference_files", "fuzzy_match_xref", "package_moves", planting multilib
colors (see RT414527, dmalcolm)
- re-introduce multithreading, optimizing get_file_data ("analyze_files"), and
"fuzzy_match_xref" by running thread pools of parallel tasks (dmalcolm)
- reduce flushing of progress logs, in case this is affecting performance
- Don't complain about shell syntax errors if it was already broken in the
baseline (jhrozek, bug 354271)

* Thu Sep 27 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.96-1
- fix bug in writing out DatabaseConf.ENABLED

* Thu Sep 27 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.95-1
- fix bug with daemonization of scheduler and worker (bug 309471)
- add ENABLED boolean to database configuration stanzas, so that we can
disable db access if needed (enabled by default)
- fix bug 307871 (tabs characters in screendumps got turned into "[0x09]")
- log XML-RPC calls and responses for getReleasedPackages
- improvements to ABI checker (not enabled for errata deployment)

* Fri Sep 21 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.94-1
- fix a bug so that database connections in the scheduler are closed after each
worker poll, rather than waiting for garbage collection
- selftest improvements
- print any exception that's raised by the getReleasedPackages XML-RPC call
into the scheduler log

* Thu Sep 20 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.93-1
- reverted the change of backgrounding the virus check for now due to
lack of good testing and the need to get other fixes into production; may
re-apply it after more testing (c.f. 1.3.90-1; see bug 251925)

* Wed Sep 19 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.92-1
- add tree subpackage to isolate optional EPEL dependency

* Tue Sep 18 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.91-1
- add --snapshot option to binary; when set, on ABI changes, it finds yum
repos in trees within that snapshot, and sets up severity of ABI change,
reporting on what packages appear to use the DSO (towards bug 290071)
- add hardcoded --snapshot argument to extraArgs for RHTS massruns (for
RHEL5.1 testing) for now
- add helper script for this, and add requirements on rpm-build and yum-utils
to worker subpackage to enable it to work
- rpmdiff-schedulerd.conf: update hostname for errata database

* Fri Sep 14 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.90-1
- log which job gets assigned to which machine, to make it easier to track
down broken runs
- don't background the virus check; we are already backgrounded (see
bug 251925)
- correctly handle case where all lines of abicheck output are
filtered (bug 291171)

* Thu Sep 13 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.89-1
- suppress blank lines in abicheck output

* Tue Sep 11 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.88-1
- don't sanitize '\n' characters

* Mon Sep 10 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.87-2
- add unpackaged file

* Mon Sep 10 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.87-1
- sanitize control characters in screendumps to prevent XML-RPC
ProtocolError when reporting results (fixes bug 284671)

* Fri Sep  7 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.86-1
- filter away various lines of output from abicheck in an attempt to
further improve signal:noise ratio for RHEL5.1 runs; run abicheck before
old lib symbols tests
- update the URL for the Errata Tool's getReleasedRpms xmlrpc call to match
the Errata Tool 2.0's preferred URL and method name (lockhart)

* Thu Sep  6 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.85-1
- suppress messages about scriptlet changes when all that's changed is the
version-release or name-version-release string, which e.g. was happening for
every kernel run; add unit test (jhrozek, bug 246239)
- patch leftovers (*.orig) files are now complained about as BAD; add unit
test (jhrozek; bug 223846)
- improvement HTML-to-text conversion to the point where it can deal the HTML
abomination in the database results (dmalcolm)

* Tue Sep  4 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.84-1
- stop abicheck complaining if it can't find .debug files
- don't add an extra empty line to end of screendump inside truncate_screendump
add local-compare and local-analyse commands to rpmdiff-cli, for driving a
local copy of the rpmdiff worker code; not fully working yet
- add package name/version headings to group.php

* Mon Aug 27 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.83-1
- complain if you can't find .debug file when setting up an abicheck run
- don't do multilib test in debuginfo packages; these always vary across
multilib peers

* Fri Aug 24 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.82-1
- try to provide abicheck with exact paths to the .debug file for each
elf (bug 253893); ensure unit tests check for this
- webpage: group.php: indicate owners of runs

* Fri Aug 24 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.81-1
- rpmdiff-cli's compare-dir can now assign run ownership based on Brew package
ownership, based on a Brew tag; currently hardcoded to "dist-5E"
- added a new group.php page to web ui
- scheduler config has gained a NOTIFY_OWNER boolean in [mail] stanza, to
avoid spamming developers on mass runs

* Thu Aug 23 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.80-1
- introduce adhoc-webui subpackage, containing php files for yakko (bug
253759); fix some minor problems on run.php page
- improvements to rpmdiff-cli compare-dir

* Wed Aug 22 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.79-1
- extend scheduler config file, adding [webui] stanza with RESULT_URLBASE
value, rather than hardcoding this, so that staging tests can change this
- libsymbols.c: don't run abicheck on .debug files
- selftest improvements/fixes
- rpmdiff-cli: compare-dir now works; fails early and gracefully if dir
doesn't exist; support an optional [identity] section with an optional EMAIL
field, to avoid need to use Kerberos

* Tue Aug 21 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.78-2
- selftest fixes

* Tue Aug 21 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.78-1
- improve behaviour when an arch disappears (bug 253732)
  - elevate subrpms appearing/disappearing from an INFO to a VERIFY severity
  - don't bother reporting "missing" files/libraries from an arch that went
  away
- improve segfault-handling (part of bug 253674):
  - (hopefully) fix problem where we're not getting meaningful backtraces from
  a segfault when running from bujilt RPMs
  - ensure that emails about a segfault in rpmdiff-checker contain the
  stdout/stderr from it
- fix crash when an architecture in "before" packages is not present in
"after" packages (bug 253674)

* Mon Aug 20 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.77-2
- fix typo in fixtures.py

* Mon Aug 20 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.77-1
- use LOGNAME rather than USER when setting up selftests

* Mon Aug 20 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.76-1
- update setup/fixtures to support running as testuser, not root

* Mon Aug 20 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.75-3
- change worker config file to slow down polling and notifications

* Mon Aug 20 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.75-2
- selftest fix

* Mon Aug 20 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.75-1
- stop hardcoding security response email; add SECURITY_RECIPIENTS field to
scheduler config; will require config file to be merged when upgrading
- fix some selftest issues

* Fri Aug 17 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.74-1
- improvement selftest support (for RHTS)
- improve detection of "all architectures" (e.g. for requires/provides test)

* Thu Aug 16 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.73-2
- add wildcard to deal with pyo/pyc

* Thu Aug 16 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.73-1
- add more setup scripts for RHTS testing
- start implementing analyse-dir and compare-dir commands in rpmdiff-cli

* Mon Aug 13 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.72-2
- make worker subpackage require abicheck on platforms on which the latter
builds (i.e. RHEL5 for now)

* Mon Aug 13 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.72-1
- make abicheck enablement a run-time option, rather than compile-time, and
enable it in when unit testing, if it's found
- add abicheck to RHEL5 yum repos

* Mon Aug  6 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.71-2
- fix a bug in selftests

* Thu Aug  2 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.71-1
- selftest improvements
- optimize check_patches by only looking within the SRPMS arch
within a half
- only bother to sort the list of changed files once, at the end, rather
than continually, and build it with prepend (for O(1) complexity)
- reinstate the sorting/ordering from the old filelist approach

* Wed Aug  1 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.70-2
- improvements to selftests

* Tue Jul 31 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.70-1
- Major internal reorganization of data structures, hoping to ameliorate some
of the spikes in the profile (bug 249147)

* Fri Jul 27 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.31-1
- internal reorganizations to allow optimizations of large runs (work
towards bug 249147)

* Thu Jul 26 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.30-1
- work towards optimizing large runs

* Thu Jul 26 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.29-1
- fix some more bogus execshield activity on kernel (bug 249458)
- more selftest improvements

* Tue Jul 24 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.28-2
- selftest improvements

* Tue Jul 24 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.28-1
- add various protections against overlong screendumps and excessive
number of messages (bug #248944)

* Tue Jul 24 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.27-1
- fix typo in error handler for HTML->text parsing
- fix profile handling so it works on Python 2.3 (RHEL4)

* Mon Jul 23 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.26-2
- remove -Werror for now
- remove jlieskov from RESULT_CCLIST

* Sat Jul 21 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.26-1
- provide a better message in the database message about grp failure, to go
with that sent in the result email
- add a tool for generating profiles from scheduler logs (logscraper.py)
- build with -Werror; code cleanups
- minor fixes to scheduler logging
- optimization of package_moves

* Thu Jul 19 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.25-1
- selftest improvements
- fix typo in security-response-team email address (bug 248724)
- instrument the various operations within fuzzy_match

* Tue Jul 17 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.24-1
- further selftest fixes
- fix bug 247491: success on an INFO as well as a GOOD/OK
- add a note about tests that run successfully without generating errors,
to avoid disturbing people with just a "(none)" output

* Mon Jul 16 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.23-1
- attempt to fix bug 248232 (XML-RPC protocol error when specfile changes
encoding), by converting all screendumps from unknown encoding down to
7-bit ASCII in XML and stdout (escaping values >= 0x80 to a textual
representation)
- various selftest fixes

* Mon Jul 16 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.22-1
- fixes for RHTS testing of rpmdiff
- rpmdiff-cli fixes: fix stray "%s" occurrences in usage messages; suppress
confusing message to stderr from klist ("klist: You have no tickets
cached") that made developers think that scheduling a run had failed

* Mon Jul 16 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.21-1
- recognize kernel-debuginfo-common to be a debug package, and suppress
header change information from it
- improvements to selftests
- force encoding of stdout to be UTF-8, to workaround older versions of
Python ignoring the locale and defaulting to ASCII (work towards bug 247978)
- fix core dump, bug 247977, when a changelog has been completely deleted from
a specfile.  Now flags this difference as BAD if it occurs (lockhart)

* Thu Jul 12 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.20-1
- more fixes for selftests subpackage
- fix 247978: handle non-ascii characters in results

* Wed Jul 11 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.19-1
- Improvements to selftests subpackage towards getting integration tests
running inside RHTS
- Fix bug 247188: Prevent creation of zombie processes by querying exit
status from progress notifier (and throwing away result)
- Fix bug 247553: update kernel-specific version/release regexes in peer
matching to support the "e" character
- fix debug_runid

* Mon Jul  9 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.18-4
- really fix directory creation (I hope) this time

* Mon Jul  9 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.18-3
- fix directory creation

* Mon Jul  9 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.18-2
- add tests/[before|after]/files.tar.gz to selftests payload

* Mon Jul  9 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.18-1
- fix output from rpmdiff-cli; add postgresql-server requirement to
selftests subpackage

* Mon Jul  9 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.17-6
- add more missing files

* Mon Jul  9 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.17-5
- add some missing files; add selftests requirement on PyXML

* Mon Jul  9 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.17-4
- add some missing files to selftests payload

* Mon Jul  9 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.17-3
- split lists of unit and integration tests out into new shell scripts, so
they can be shared by Makefile and RHTS test; package these (rather than the
specfile) in the selftest subpackage

* Mon Jul  9 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.17-2
- add specfile to selftests subpackage, and the various build requirements
to its requirements, so that makefile can work

* Thu Jul  5 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.17-1
- introduce a selftests subpackage, containing the various unit tests and
integration tests
- workers now report "uname -a" to scheduler, and version of python
installed
- use long when extracting DiskStats, rather than int, to avoid a failure
on pre-RHEL4 32-bit workers (fixes bug #247161)
- optimize away various user-space elf tests when they are meaningless for
kernels, kernel modules, and debuginfo .debug files (fixes bug #246301)
- advise developers to forward emails with grp-failure to errata-maint,
not rpmdiff-maint

* Fri Jun 29 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.16-5
- rebuild

* Thu Jun 28 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.16-4
- rebuild

* Thu Jun 28 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.16-3
- weaken file requirement (for RHEL5), and rebuild, hopefully with
correctly populated buildroots this time

* Thu Jun 28 2007 David Malcolm <dmalcolm@redhat.com> 1.3.16-2
- repo creation fixes

* Thu Jun 28 2007 David Malcolm <dmalcolm@redhat.com> 1.3.16-1
- link to libmagic, and require a sufficiently recent version of "file" during
the build

* Thu Jun 28 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.15-2
- fix buildrequires syntax

* Thu Jun 28 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.15-1
- Fix bug 245801; stop calling the "file" binary, instead use <magic.h>
and the implementation of libmagic embedded in librpm to do the file
type detection directly inside the main rpmdiff-checker binary
- For now, the code only builds on RHEL5 (see bug 245801 and
https://engineering.redhat.com/rt3/Ticket/Display.html?id=13252 )
- Fix bug 245810 (backtrace reporting is picking up wrong corefile), by
storing a PID file for the rpmdiff-checker process
- Fix an "import pg" bug on pure worker machines
- Fix bug 245636 (buffer overrun when dealing with relative symlinks)
- Clean up repo creation

* Fri Jun 22 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.14-2
- add missing build requirements on pkgconfig, glib2-devel, libxml2-devel,
rpm-devel

* Fri Jun 22 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.14-1
- try again to fix the build on RHEL5
- fix the admin code so that it can be run from the RPMs
- ensure that dropped changelog items have proper line-breaks (#245355)

* Thu Jun 21 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.13-2
- ensure we have consistent version-releases across subpackages; ensure
root owns files for all subpackages (was using brewbuilder for some); set
"noreplace" flag on all config files

* Thu Jun 21 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.13-1
- add new tool to common subpackage: /usr/bin/rpmdiff-admin

* Thu Jun 21 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.12-1
- indicate old package in email notifications about errata comparisons
- add integration testing for the case where g-r-p succeeds
- fix typos detected by pylint

* Wed Jun 20 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.11-2
- use correct yum repos directory

* Wed Jun 20 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.11-1
- add yum repo support; hopefully fix build on RHEL5

* Tue Jun 19 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.10-1
- fix some undefined variables

* Tue Jun 19 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.9-7
- add "make brew" command to kick off a build across all of RHEL3/4/5

* Tue Jun 19 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.9-6
- foo

* Tue Jun 19 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.9-5
- use correct path for makedepend

* Tue Jun 19 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.9-4
- rebuild for RHEL5

* Tue Jun 19 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.9-3
- rebuild for RHEL4

* Tue Jun 19 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.9-2
- generalize makedepend dependency

* Tue Jun 19 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.9-1
- add configurable CC list for result emails, emulating the old email result
list from erratadiff.sh
- reorganize integration tests fo they work reliably
- add integration test for out-of-disk-space on a worker

* Mon Jun 18 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.8-2
- rebuild for RHEL4

* Mon Jun 18 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.8-1
- better emulation of old database activity (bug #242525)
- fix bug 244322 (world-writable metadata files issue)
- debug improvements
- fix breakage of the rpmdiff-workerd code
- better handling of PID files for services

* Fri Jun 15 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.7-1
- reimplementation of daemon init scripts (bug #244473)

* Fri Jun 15 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.6-2
- rebuild for RHEL4

* Fri Jun 15 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.6-1
- drop postgresql-devel build requirement, as we no longer access database
from C code
- move worker-specific requirements to the worker subpackage, and generalize
the /sbin/modinfo requirement so it works for both RHEL3 and later releases

* Thu Jun 14 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.5-1
- first pass at wiring up progress notifications: currently just logged on
the scheduler, rather than in the web UI

* Wed Jun 13 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.4-1
- fix unpackaged files

* Wed Jun 13 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.3-1
- daemonize the two new daemons, with logging to log files
- detect g-r-p failure, and improve the email and database messages when
this happens
- add utility script for setting up Postgres serving a new fake cluster
- fix obscure XML bug that led to HTML->text failures (bug 243841)
- avoid overflowing XML-RPC when reporting disk usage on very large runs (bug
243801), with a unit test
- improve unit tests for XML result handling

* Mon Jun 11 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.2-1
- reorganize command-line interface into a single executable, with a config
file
- debugging and logging improvements

* Fri Jun  8 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.1-1
- add rpmdiff-cli subpackage, with command line tools to schedule ad-hoc jobs
via XML-RPC; add server-side support for this on scheduler
- improve the notification emails sent by scheduler (include URLs to web UI,
send them to correct people, collapse HTML markup into text etc)
- fix worker code so that it can run on RHEL3 (Python 2.2)
- various debug improvements
- implement configuration files: rpmdiff-workerd.conf and
rpmdiff-schedulerd.conf; read stuff from there rather than hardcoding
- improvement of bug #200792: don't flag world-writable directories if the
sticky bit is set; make world-writable files need security permission to
waive; remove "new test in development" boilerplate
- unit and integration tests for the above

* Wed Jun  6 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.0-2
- reorganise into shared common code, and subpackages for worker and scheduler
daemons

* Wed Jun  6 2007 David Malcolm <dmalcolm@redhat.com> - 1.3.0-1
- Initial, experimental spin of 1.3 branch
- Architectural changes
  - major architectural rewrite, splitting into two components: worker code and
  scheduler code, which communicate via XML-RPC
    - All database access and all regular notification emails occur in
    scheduler (workers can send emails when errors occur); no more database
    access from C code
    - Workers have minimal "policy"; this is passed as input to them by
    the scheduler
    - Workers report stats on runs: disk space and time taken for various
    phases, along with RPM versions of the software they have installed

  - detect when a worker runs out of disk space, and handle this with a
  detailed fatal error diagnostic

  - detect when a worker segfaults, and include a backtrace in the error
  report

  - reorganize binaries: only build one binary: rpmdiff-checker, which writes
  out results as XML (which is then parsed and sent back to scheduler via
  XML-RPC, and then turned into email notifications and database updates)

  - reorganization of layout of how data is extracted on worker machines,
  allowing for other container formats to be supported in the future, and
  for recursion into nested container formats; allow configurable extraction
  locations, rather than hardcoding it as /tmp/rpmdf

  - move all database access out of the C code and into the scheduler

  - port all message reporting to go through a consistent API

  - add --crash option to worker, to test segfault handling

  - record stats on files gathered

  - add framework for presenting progress bars in a web UI (UI doesn't exist
  yet)

  - extend self-test suite, both with unit tests, and integration tests that
  simulate the production pipeline, both errata runs and yakko ad-hoc runs,
  and check that segfaults of the C app are trapped

- User-visible improvements:
  - automatically notify security response team when a security-sensitive
  result occurs
  - determine kernel-space vs user-space ELF files (i.e. kernels and kernel
  modules vs "everything else"), and suppress execshield tests on the
  former (bug #191812)
  - fix bug #193072 (bogus filetype reported for symlink)
  - re-enable check for lost changelog items
  - also in 1.2 branch:
    - multilib color optimization
    - fix for #239489
    - fix for #241305: use variant rather than release when calling g_r_p

* Mon Apr 16 2007 David Malcolm <dmalcolm@redhat.com> - 1.2.10-2
- rebuild for RHEL4; drop dist tag

* Mon Apr 16 2007 David Malcolm <dmalcolm@redhat.com> - 1.2.10-1
- added code coverage support and various other improvements to the self-test
suite; added many new tests to the suite (dmalcolm)
- User-visible bugs fixed:
  - 200318: suppress noise from "File List" test when bumping the upstream
  version by remapping paths in the payload that contain N-V-R, N-V, etc
  (jhrozek, lockhart, dmalcolm)
  - 235688: when unable to locate packages to compare against, rpmdiff would
  claim it was running in --nocompare mode, but actually be running against a
  notional empty set of packages, leading to large numbers of false error
  messages, such as "Specfile not found" from the "Unapplied Patches" test
  (dmalcolm)
  - 232900: suppress spam from filetype test when the timestamp of a gzip
  archive changes (dmalcolm)
  - 235685: fix false-positive for Unapplied Patches test when Patch is
  specified via a URL, rather than just a filename (dmalcolm)
  - 230801: fix a crash due to over-zealous peer-matching of documentation
  files (lockhart)
- improve error-handling diagnostics (lockhart)
- build fixes (lockhart, dmalcolm)

* Tue Feb 27 2007 John Lockhart <lockhart@redhat.com> 1.2.9-3
- Add a buildrequires for postgres-devel
* Tue Feb 27 2007 John Lockhart <lockhart@redhat.com> 1.2.9-2
- Add rpmbuild dist tag for RHEL3/RHEL4 builds.
* Thu Feb 22 2007 John Lockhart <lockhart@redhat.com> 1.2.9-1
- Support RHEL5 errata. (lockhart)
- Improve upstream version report (dmalcolm)
- require postgres-python packages (lockhart)
- improve diagnostics on releasedrpms (lockhart)

* Thu Feb  8 2007 John Lockhart <lockhart@redhat.com> 1.2.8-1
- fix bug 224685: do not diff upstream tarballs with different versions,
check the whitelist instead (lockhart)
- fix: add rhel5 to recognized version whitelists (lockhart)
- fix: ensure the version whitelist is actually loaded and checked (lockhart)
- fix: misc memory leaks and typos, update results URL (lockhart)
- move GetReleasedPackages functionality to its own module, and use
the Errata Tool exclusively for anything with an errata number (lockhart)
- fix: provide short, sane error message and exit if bad collinst is given to
fedoradiff (lockhart)

* Fri Jan 26 2007 David Malcolm <dmalcolm@redhat.com> 1.2.7-1
- partial fix for bug 200318: false positives for files removed when upstream
version changes (lockhart,jhrozek)
- fix bug 223006: false positives for multilib test (dmalcolm)
- fix bug 222052: escape HTML output when addings diffs etc to the web
reports (dmalcolm)

* Tue Jan 16 2007 David Malcolm <dmalcolm@redhat.com> 1.2.6-1
- make multilib conflicts test work for the --nocompare
case, as well as for comparisons.  Fixes #222739. (dmalcolm)
- add diffs between the files when reporting a multilib conflict (dmalcolm)
- fix to the execshield test (lockhart)
- tweak some error messages to report "File/New File" correctly (dmalcolm)

* Tue Jan  9 2007 David Malcolm <dmalcolm@redhat.com> 1.2.5-1
- RPM triggers and scriptlet tests now include textual diff in the report
when a package's triggers/scriplets change (dmalcolm)
- shell syntax test now includes the shell's error report when an invalid
script is detected (dmalcolm)
- dangling symlink test now reports the destination that the symlink points
to (dmalcolm)
- fix shell syntax test to work with sh,bash,csh,ksh,zsh; also allow
whitespace between '#!' and the interpreter, and recognize (but discard)
arguments to the interpreter (#219263, lockhart)
- regex fixes (lockhart)
- add a --verbose/-v option to the rpmcheck binaries (dmalcolm)
- various enhancements to selftests (#221886, dmalcolm)

* Mon Dec 18 2006 David Malcolm <dmalcolm@redhat.com> - 1.2.4-1
- reduce severity of header file changes if the header file is in a debuginfo
package, to avoid spamming about purely internal (dmalcolm)
- rework the IPv6 test so that it only warns about new symbols and new files,
rather than constantly complaining about the same things (dmalcolm)
- improvements to unit tests (dmalcolm)
- various new tests, disabled by default (dmalcolm):
  - test that invokes rpmlint and reports on output/regressions of output
    (disabled since rpmlint is not yet a requirement, and needs more testing)
  - test that invokes abicheck to compare ELF DSOs (disabled for now since this
    tool is currently only available on RHEL5)
  - stub for invoking docbook-lint on DocBook files (not fully implemented)
  - stub for tests of how tempfiles are created (not yet implemented)
  - stub for tests of Perl files (not yet implemented)
  - stub for tests of Python files (not yet implemented)
- improvements to regex handling (lockhart, jhrozek)
- various cleanups to get it closer to running on RHEL5 worker boxes (dmalcolm)
- fix a hang when generating MD5 sums: don't do it on pipes (bug 219229, lockhart)
- better segregation of development and production (lockhart)

* Fri Dec  8 2006 David Malcolm <dmalcolm@redhat.com> 1.2.3-1
- new tests:
  - detect usage of functions that are known to have problems when using IPv6
  (bug 199157, dmalcolm)
  - complain about CVS and .svn directories in payloads (bug 190609, dmalcolm)
  - complain about __MACOSX directories in payloads (bug 197340, dmalcolm)
  - complain about shell scripts with invalid syntax (bug 216057, dmalcolm)
- fix false positive in dangling symlink test when a devel package has a
symlink to the main package (bug 189953, jhrozek, lockhart)
- complaints about broken memset calls in build logs now reach the rpmdiff log
to make it easier to track them down (dmalcolm)
- fix HTML formatting of diffs of header files (dmalcolm)
- debugging and error handling improvements (lockhart, dmalcolm)
- slow down polling for new jobs by worker daemon from every minute to every 5
minutes to help reduce load on database (lockhart)

* Mon Dec  4 2006 David Malcolm <dmalcolm@redhat.com> 1.2.2-1
- new auth details for rodan (dmalcolm)
- bug fixes and RHEL5 support for setuid whitelisting (lockhart)
- speed up the setup by parallelizing many operations (lockhart)
- Changed Files test now registers a change of a header file as a VERIFY
failure needing waiver, rather than an INFO notification, since it might lead
to ABI breakage, and a diff of the old/new header files is included in reports
to help trap possible ABI changes (bug #218098) (dmalcolm)
- Changed Files test always only showed the first 24 files that had changed; it
now tells you that it's suppressing further output, and lets you know how many
changed in total (dmalcolm)
- improvements to determining the baseline for comparison against (lockhart)
- improvements to ELF analysis (lockhart)
- various cleanups (lockhart, dmalcolm)

* Wed Nov 15 2006 John Lockhart <lockhart@redhat.com> 1.2.1-2
- now able to locate get released packages that have no i386 parts (lockhart)
- readelf is no longer used, just eu-readelf.  Should stop coredumps from readelf. (lockhart,drepper)
- debug_runid: close db connections, add messages, prevent traceback for
nonexistent runIDs. (lockhart)
- whitelisted setuid programs now generate Info rather than Bad messages. (lockhart)
- rpmdiffconf.py: use pg.DB, rather than pg.connect when connecting to
databases from Python code (dmalcolm)
* Wed Nov  1 2006 David Malcolm <dmalcolm@redhat.com> 1.2.1-1
- deal with fedoradiff.sh and erratadiff.sh from bailing out by detecting this
in the daemon (via the score for the run on exit): when this occurs, set the
run to be a fail and email a report to rpmdiff-maint (lockhart)
- fedoradiff.sh: fix the case where old and new version strings are
the provided arguments (lockhart)
- improvements to email reports (lockhart)
- fix false-positive debuginfo files not being stripped of debugging
info (lockhart, #204876)
- setuid message reports arch, and deals better with --nocompare case
(dmalcolm)
- CVS can now schedule grouped runs, and generate various reports  (dmalcolm)

* Mon Oct 30 2006 David Malcolm <dmalcolm@redhat.com> 1.2.0-1
- hopefully the final bugfixes for the new unified daemon and --nocompare code

* Mon Oct 30 2006 John Lockhart <lockhart@redhat.com> 1.1.0-18
- fedoradiff.sh: one-char typo fix, doCompare->noCompare.
* Mon Oct 30 2006 John Lockhart <lockhart@redhat.com> 1.1.0-17
- db.c: return NULL if no usable connection is made (lockhart)
- fedoradiff.sh: Add the "Generated by" tagline to results (lockhart)
- groupresults.py: new file: query results across an entire group of
many runs (malcolm)
- Makefile: add rpmdiffconf.py (malcolm)
- rpmdiffconf.py: new file, to hold connection data (ought to be
configuration data) (malcolm)
- debug_runid: move connect code to rpmdiffconf.py (malcolm)
* Mon Oct 30 2006 John Lockhart <lockhart@redhat.com> 1.1.0-16
- Makefile: do not install the removed fedorasrv binary (lockhart)
* Mon Oct 30 2006 John Lockhart <lockhart@redhat.com> 1.1.0-15
- server/main.c: add timestamps prefixes to all logging (malcolm)
- server/main.c: log all sleep calls (malcolm)
- erratadiff.sh: insert a wait so that any bg jobs, such as clamav,
will be completed before the testing starts. (lockhart)
- fedoradiff.sh: enable --nocompare; test -debuginfo packages;
fix handling of SRPMS to match what erratadiff.sh does. (lockhart)
- server/main.c: add various VERBOSE macros, remove verbose
variable (for now), add SQL_LOG command; use these to add extensive
debug logging; add POLL_INTERVAL macro rather han hardcode 60 seconds;
capitalize some of the SQL code (malcolm)
- server/main.c: improve logging; make ENABLE_WORK affect the yakko
stuff (malcolm)
-server/main.c: move yakko-queue code here from fedoraserver/main.c
and reimplement polling so it polls both queues, favoring the Errata
queue (malcolm)
- fedoraserver/main.c: remove source (malcolm)
- fedoraserver/Makefile: remove fedoraserver (malcolm)
- Makefile: remove fedorasrv (malcolm)
- fedoradiff.sh: some brew awareness, and add support for feeding
in version numbers.  Work in progress. (lockhart)
setup_rpm.sh: shell cleanup, and launch clamav in the background. (lockhart)
- server/main.c: make pq_errata a local rather than global variable (malcolm)
- server/main.c: add forward declarations for all functions; add
prefixes to function names based on whether they work on no queue,
either queue, or on the errata queue specifically (malcolm)
- fedoraserver/main.c: rename pq->pq_yakko in preparation to merge
all of this into server/main.c (malcolm)
- server/main.c: rename pq->pq_errata in preparation with merging in
the yakko queue code (malcolm)
- rpmdiff.py: convert ErrataToolQuery.make_beehive_or_brew_delegate
into a new setup_input_for_rpmdiff helper function, which gets the
delegate and then performs the work; rewrite ErrataToolQuery's
setup_input_for_rpmdiff to use this; move get_nvra_from_filename
from being a method of ErrataToolQuery to being a module function,
and add a unit test for this. (malcolm)
- fedoraserver/Makefile: rework to use db.[ch] and connect_to_yakko_db,
so that the tools work on any authorized host, not just on yakko itself (malcolm)
- fedoraserver/yakkorequest.c: ditto (malcolm)
- fedoraserver/main.c: ditto; fix typo (malcolm)
- fedoraserver/fedorascore.c:  ditto; fix usage message (malcolm)
- filelist.c, stripped.c, filelist.h: add FILELIST_SUPPORT_DIST
definition to work towards eliminating this (malcolm)
- db.c, db.h: add connect_to_yakko_db (malcolm)
- rpmdiff.spec: add pcre-devel to build requirements; 1.1.0-14 (malcolm)
- fedoradiff.sh: add NEW_VERSION and OLD_VERSION (malcolm)
- fedoraserver/main.c: get new_version and old_version from the DB when
polling for jobs, and pass them on when invoking fedoradiff.sh (malcolm)
- fedoradiff.sh: massive cleanup of shell scripting (lockhart)
- fedoradiff.sh: give meaningful names to the various arguments (malcolm)
- filesizes.c: more whitespace fixes (lockhart)
- filesizes.c: bz #180323 - change octal printout to %04o, and
permission mask to 07777. (lockhart)
- fuzzymatch.c: remove superfluous debug message (lockhart)

* Fri Oct 27 2006 David Malcolm <dmalcolm@redhat.com> 1.1.0-14
- add pcre-devel to build requirements

* Fri Oct 13 2006 John Lockhart <lockhart@redhat.com> 1.1.0-13
- Add regex code for better pattern matching
- Move moved_module test after fuzzymatch
- Fix NULL dereference in handle_virus
- Improve pattern matching for kernel and kernel-debug modules

* Wed Oct 11 2006 John Lockhart <lockhart@redhat.com> 1.1.0-12
- If getReleasedPackages returns a list, rpmdiff.py now examines it
and chooses an appropriate RPM from the list.

* Mon Oct  9 2006 David Malcolm <dmalcolm@redhat.com> 1.1.0-11
- getReleasePackages fails by file, try by errata number, and print out
success or failure, and which packages we are aworking with. (lockhart)

* Thu Oct  5 2006 David Malcolm <dmalcolm@redhat.com> 1.1.0-10
- force getReleasedPackagesFromErrata to use brew=True (lockhart)
- fix memory leak (lockhart)

* Wed Sep 27 2006 David Malcolm <dmalcolm@redhat.com> 1.1.0-9
- temporarily disabling moved_modules test to help finish run
12699

* Wed Sep 27 2006 David Malcolm <dmalcolm@redhat.com> 1.1.0-8
- add lockhart and jlieskov to spamlist

* Wed Sep 27 2006 David Malcolm <dmalcolm@redhat.com> 1.1.0-7
- remove a stray <tt> from output
- add debug printfs
- set score for run to 4 on a fatal error in setup; set
ulimit to try to get coredumps

* Tue Sep 26 2006 David Malcolm <dmalcolm@redhat.com> 1.1.0-6
- avoid treating 'data' as a brew arch.  Fix one regexp.
- add rpmcheck to the installed binaries, so that it's
available for debug purposes on the production machines
- Make xref_xref_modules print the old path of a module as
well as the new.

* Tue Sep 19 2006 David Malcolm <dmalcolm@redhat.com> 1.1.0-5
- deal with arbitrary SRPMs in package_path by looking them up in brew
(fixes 2006:0687)
- fix version/hostname in emails

* Tue Sep 19 2006 David Malcolm <dmalcolm@redhat.com> 1.1.0-4
- disable the no-longer-meaningful manifest/debuginfo tests
- include the version and the hostname in email reports
- reimplement duplication-marking to support both beehive and brew

* Tue Sep 19 2006 David Malcolm <dmalcolm@redhat.com> 1.1.0-3
- fix unpackaged file (do_setup_rpm.sh)

* Mon Sep 18 2006 David Malcolm <dmalcolm@redhat.com> 1.1.0-2
- reduce debug spew

* Mon Sep 18 2006 David Malcolm <dmalcolm@redhat.com> 1.1.0-1
- use (and require) "variant" information supplied by Errata tool
- scrapped the fragile traversal of /mnt/redhat for determing the baseline
package for comparison in favour of XML-RPC queries
- support both Brew and Beehive-built packages
- new unit tests for verifying rpmdiff's own sanity
- fix bug 204006 (handle filenames containing colons)
- fix bug 204868 (handle "file" bailing out)

* Wed Aug  2 2006 David Malcolm <dmalcolm@redhat.com> 1.0.5-2
- add explicit clamav requirement

* Fri Jul 28 2006 David Malcolm <dmalcolm@redhat.com> 1.0.5-1
- add directories below /tmp/rpmdf/{before|after}/{arch|SRPM}/{packagename} to
the file lists to ensure tests get run on them (bug #200305)
- remove multithreadness of the file gathering (working towards bug #200336)

* Wed Jul 12 2006 David Malcolm <dmalcolm@redhat.com> 1.0.4-3
- workaround for #196984
- beginnings of cleanup of the package setup/extraction scripts
- more self-test cases

* Tue May 23 2006 David Malcolm <dmalcolm@redhat.com> 1.0.4-2
- disable output of debug options to stop it getting into the email reports
being sent to developers
- disable expand_jarfiles as a workaround for #192887 (this feature is not yet
fully-baked)

* Mon May 22 2006 David Malcolm <dmalcolm@redhat.com> 1.0.4.1
- 1.0.4:
- fix bug #191106 (false positive for file types with man pages)
- fix bug #188010 (specialcase type checking for TeX DVI files, since the
type contains a timestamp which will always change)
- fix first part of bug #190173 (stopped bogusly warning that a new ELF file
has dropped GNU_RELRO protection)
- update the server name to reflect changes made by database admin
- add debug_runid tool to help debugging rpmdiff problems (#191235)
- turn off optimizations to make it easier to debug
- suppress some compiler warnings
- add a tool called "taste", working towards the Brew cutover (not yet
functional)
- improved result and first-pass analysis XML formats to work towards Brew cutover, with updated DTDs
- created RELAX-NG schema for the XML formats
- implement sane option parsing within rpmcheck using popt
- refactored to reduce the amount of copy&pasted code
- wrote numerous unit tests to cover all of the above

* Thu Apr 27 2006 David Malcolm <dmalcolm@redhat.com> 1.0.3-8
- don't ship debuginfo for RHEL2.1; more cleanups

* Thu Apr 27 2006 David Malcolm <dmalcolm@redhat.com> 1.0.3-7
- fixed a bug where results were not written back to the database

* Thu Apr 27 2006 David Malcolm <dmalcolm@redhat.com> 1.0.3-6
- avoid traversing inside instimage and image-template hierarchies; lots of
refactoring

* Wed Apr 19 2006  David Malcolm <dmalcolm@redhat.com> - 1.0.3-5
- fix password in setscore; fix bogus disabling of deduplication code

* Wed Apr 19 2006  David Malcolm <dmalcolm@redhat.com> - 1.0.3-4
- fix password in poll daemon

* Wed Apr 19 2006  David Malcolm <dmalcolm@redhat.com> - 1.0.3-3
- use XFree86-devel as build requirement to fix build on RHEL3

* Wed Apr 19 2006  David Malcolm <dmalcolm@redhat.com> - 1.0.3-2
- 1.0.3

* Mon Feb 20 2006 David Malcolm <dmalcolm@redhat.com> - 1.0.2-1
- 1.0.2

* Fri Jan 13 2006 Dennis Gregorovic <dgregor@redhat.com> - 1.0.1-1
- New build for various fixes

* Mon Dec 12 2005 Dennis Gregorovic <dgregor@redhat.com> 1.0-1
- Initial packaging
