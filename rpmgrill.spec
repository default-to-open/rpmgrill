Name:           rpmgrill
Version:        0.09
Release:        1%{?dist}
Summary:        A utility for catching problems in brew builds
Group:          Development/Tools
License:        Red Hat internal.  Do not redistribute.
URL:            http://git.engineering.redhat.com/?p=users/esantiag/%{name}.git;a=summary
Source0:        %{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
Requires:       perl
BuildRequires:  perl-Module-Build
BuildRequires:  perl-Test-Simple

# For the antivirus plugin
Requires: clamav
Requires: clamav-data

# For checking desktop/icon files
Requires: /usr/bin/desktop-file-validate

# For LibGather, Rpath : need eu-readelf
Requires: elfutils

# Optional module, allows RpmMetadata plugin to check https URLs
Requires: perl-IO-Socket-SSL

%description
rpmgrill runs a series of tests against a set of RPMs, reporting problems
that may require a developer's attention.  For instance: unapplied patches,
multilib incompatibilities.  rpmgrill is a spinoff of rpmdiff, intended
to run earlier in the development cycle.

%prep
%setup -q

%build
%{__perl} Build.PL --installdirs vendor
./Build

%install
rm -rf $RPM_BUILD_ROOT

###make pure_install PERL_INSTALL_ROOT=$RPM_BUILD_ROOT
./Build pure_install --destdir $RPM_BUILD_ROOT

find $RPM_BUILD_ROOT -type f -name .packlist -exec rm -f {} \;
find $RPM_BUILD_ROOT -depth -type d -exec rmdir {} 2>/dev/null \;

%{_fixperms} $RPM_BUILD_ROOT/*

%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc
%{perl_vendorlib}/*
%{_bindir}/*
%{_mandir}/man1/*
%{_mandir}/man3/*
/usr/share/rpmgrill/*

%changelog
- bz802555 (Fedora/branding), cont'd: also check RPM Summary
- bz802555, cont'd: check for multiple occurrences of Fedora
- bz813869 (MacroSurprise verbosity): instead of warning about all macros,
define an explicit blacklist of potentially-troublesome ones: patch, if, ...

* Mon May 14 2012 Ed Santiago <santiago@redhat.com> 0.09-1
- bz802555 (Fedora/branding): ignore "fedora" in filenames in srpm

* Tue May  8 2012 Ed Santiago <santiago@redhat.com> 0.08-1
- RELRO tests: try to identify daemon files (and complain about missing RELRO)
- bz809907: look for and gripe about executables built with -gstabs
- UID/GID test: look for UID conflicts, e.g. amanda-3.3.0-5.el7
- better tooltip documentation

* Tue Apr  3 2012 Ed Santiago <santiago@redhat.com> 0.07-1
- bz802554 - new test for RHEL7 files not under /usr
- bz802555 - new test for "Fedora" in RPM description
- internal cleanup

* Thu Mar 29 2012 Ed Santiago <santiago@redhat.com> 0.06-1
- version string cleanup

* Mon Mar 26 2012 Ed Santiago <santiago@redhat.com> 0.05-1
- bz802557 - test for non-systemd files
- cleanup in FHS test
- lots more cleanup

* Fri Dec  2 2011 Ed Santiago <santiago@redhat.com> 0.04-1
- bz750537 - suid whitelist now in /mnt/redhat/scripts/rel-eng
- add a Requires for elfutils
- new rpath plugin
- new Manifest plugin: checks for non-FHS files (eg /usr/local/lib/perl5),
  and for a weird situation (seen in mailman) where mid-level subdirs
  are created but not in the manifest.

* Thu Jul  7 2011 Eduardo Santiago <santiago@redhat.com> - 0.03-1
- add a Requires for desktop-file-validate
- RpmMetadata plugin: fix for WrongVersion test [eg v7-1.4-6.el5]
- specfile: require perl IO::Socket::SSL, for testing https URLs

* Fri Jun  3 2011 Eduardo Santiago <santiago@redhat.com> - 0.02-1
- First attempt at a brew build

* Tue Dec 21 2010 Eduardo Santiago <santiago@redhat.com> - 0.01-1
- Initial packaging
