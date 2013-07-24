Name:           rpmgrill
Version:        0.23
Release:        1%{?dist}
Summary:        A utility for catching problems in koji builds
Group:          Development/Tools
License:        Artistic 2.0
Source0:        http://www.edsantiago.com/f/%{name}-%{version}.tar.bz2
URL:            https://git.fedorahosted.org/git/rpmgrill.git
BuildArch:      noarch
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
BuildRequires:  perl(Module::Build)
BuildRequires:  perl(Test::Simple)

# For the antivirus plugin
Requires: clamav
Requires: clamav-data

# For checking desktop/icon files using /usr/bin/desktop-file-validate
Requires: desktop-file-utils

# For LibGather, Rpath : need eu-readelf
Requires: elfutils

# The SecurityPolicy plugin uses xsltproc to validate polkit files.
Requires: libxslt

# The SecurityPolicy plugin checks for vulnerabilities in Ruby gems;
# the database is cached locally using git.
Requires: git

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
%{perl_vendorlib}/*
%{_bindir}/*
%{_mandir}/man1/*
%{_mandir}/man3/*
%{_datadir}/%{name}/*

%changelog
* Tue Jul 23 2013 Ed Santiago <santiago@redhat.com> 0.23-1
- package missing RPM::Grill::Util module
- more review feedback; thanks again to Christopher Meng

* Mon Jul 10 2013 Ed Santiago <santiago@redhat.com> 0.22-2
- specfile: remove unnecessary BuildRoot definition

* Wed Jul  3 2013 Ed Santiago <santiago@redhat.com> 0.22-1
- incorporate Fedora review feedback; Thanks to Christopher Meng

* Wed Jul  3 2013 Ed Santiago <santiago@redhat.com> 0.21-1
- bz966075: ManPages test: deal with file in noarch, man pages in arch
