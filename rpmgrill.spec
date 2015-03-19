Name:           rpmgrill
Version:        0.27
Release:        1%{?dist}
Summary:        A utility for catching problems in koji builds
Group:          Development/Tools
License:        Artistic 2.0
Source0:        http://www.edsantiago.com/f/%{name}-%{version}.tar.bz2
URL:            https://git.fedorahosted.org/git/rpmgrill.git
BuildArch:      noarch
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires:       perl(Module::Pluggable)
Requires:       perl(XMLRPC::Lite)
Requires:       perl(File::Fetch)
Requires:       perl(List::AllUtils)
BuildRequires:  perl(Module::Build)
BuildRequires:  perl(Test::Simple)
BuildRequires:  perl(Test::MockObject)

# For the antivirus plugin
Requires: clamav
Requires: clamav-data

# For checking desktop/icon files using /usr/bin/desktop-file-validate
Requires: /usr/bin/desktop-file-validate

# For LibGather, Rpath : need eu-readelf & associated tools
Requires: elfutils

# The SecurityPolicy plugin uses xsltproc to validate polkit files.
Requires: /usr/bin/xsltproc

# The SecurityPolicy plugin checks for vulnerabilities in Ruby gems;
# the database is cached locally using git.
Requires: git

# Not strictly necessary for rpmgrill, but rpmgrill-fetch-build uses it
# to download Fedora builds.
Requires: koji

%description
rpmgrill runs a series of tests against a set of RPMs, reporting problems
that may require a developer's attention.  For instance: unapplied patches,
multilib incompatibilities.

%prep
%setup -q

%build
%{__perl} Build.PL --installdirs vendor
./Build

%install
./Build pure_install --destdir %{buildroot}

find %{buildroot} -type f -name .packlist -exec rm -f {} \;

%{_fixperms} %{buildroot}/*

%files
%doc README.AAA_FIRST LICENSE
%{perl_vendorlib}/*
%{_bindir}/*
%{_mandir}/man1/*
%{_mandir}/man3/*
%{_datadir}/%{name}/*

%changelog
* Fri Apr 10 2015 Róman Joost <rjoost@redhat.com> 0.28-1
- bz1202634: fixes fetch-build has a hardcoded koji URL

* Wed Dec 10 2014 Ed Santiago <santiago@redhat.com> 0.27-1
- bz1172584: missing deps on Module::Pluggable, koji
- bz1160153: fill in rpmgrill POD
- new rpmgrill-analyze-local tool

* Tue Aug 26 2014 Jitka Plesnikova <jplesnik@redhat.com> - 0.26-3
- Perl 5.20 rebuild

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.26-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Oct 22 2013 Ed Santiago <santiago@redhat.com> 0.26-1
- bz1021298: Handle UnversionedDocdirs change in F20
- internal fixes for updated perl-Encode module

* Thu Sep 12 2013 Ed Santiago <santiago@redhat.com> 0.25-2
- Don't just include License file in tarball, package it.

* Wed Sep 11 2013 Ed Santiago <santiago@redhat.com> 0.25-1
- Manifest: include License file, missing selftests

* Mon Sep  9 2013 Ed Santiago <santiago@redhat.com> 0.24-1
- test suite: clamav output differs between f17 & f19
- specfile: fix bad date in changelog; re-update some Requires

* Tue Jul 23 2013 Ed Santiago <santiago@redhat.com> 0.23-1
- package missing RPM::Grill::Util module
- more review feedback; thanks again to Christopher Meng

* Mon Jul  8 2013 Ed Santiago <santiago@redhat.com> 0.22-2
- specfile: remove unnecessary BuildRoot definition

* Wed Jul  3 2013 Ed Santiago <santiago@redhat.com> 0.22-1
- incorporate Fedora review feedback; Thanks to Christopher Meng

* Wed Jul  3 2013 Ed Santiago <santiago@redhat.com> 0.21-1
- bz966075: ManPages test: deal with file in noarch, man pages in arch
