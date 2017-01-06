Name:           rpmgrill
Version:        0.30
Release:        1%{?dist}
Summary:        A utility for catching problems in koji builds
Group:          Development/Tools
License:        Artistic 2.0
Source0:        https://github.com/default-to-open/%{name}/archive/%{version}.tar.gz
URL:            https://github.com/default-to-open/rpmgrill
BuildArch:      noarch
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires:       perl(Module::Pluggable)
Requires:       perl(XMLRPC::Lite)
Requires:       perl(File::Fetch)
Requires:       perl(List::AllUtils)
BuildRequires:  perl-generators
BuildRequires:  perl(Module::Build)
BuildRequires:  perl(Test::Simple)
BuildRequires:  perl(Test::MockModule)
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

# The SecurityPolicy plugin uses strings
Requires: binutils

# Not strictly necessary for rpmgrill, but rpmgrill-fetch-build uses it
# to download Fedora builds.
Requires: koji

%description
rpmgrill runs a series of tests against a set of RPMs, reporting problems
that may require a developer's attention.  For instance: unapplied patches,
multilib incompatibilities.

%prep
%setup -q -n %{name}-%{version}

%build
%{__perl} Build.PL --installdirs vendor
./Build

%install
./Build pure_install --destdir %{buildroot}

find %{buildroot} -type f -name .packlist -exec rm -f {} \;

%{_fixperms} %{buildroot}/*

%files
%doc README.asciidoc LICENSE AUTHORS
%{perl_vendorlib}/*
%{_bindir}/*
%{_mandir}/man1/*
%{_mandir}/man3/*
%{_datadir}/%{name}/*

%changelog
