Name:           rpmgrill
Version:        0.21
Release:        1%{?dist}
Summary:        A utility for catching problems in koji builds
Group:          Development/Tools
License:        Artistic 2.0
Source0:        %{name}-%{version}.tar.bz2
URL:            https://git.fedorahosted.org/git/rpmgrill.git
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

# For bz876281 (polkit)
Requires: /usr/bin/xsltproc

# Optional module, allows RpmMetadata plugin to check https URLs
Requires: perl-IO-Socket-SSL

# For bz928428 - ruby gems
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
* Wed Jul  3 2013 Ed Santiago <santiago@redhat.com> 0.21-1
- bz966075: ManPages test: deal with file in noarch, man pages in arch
