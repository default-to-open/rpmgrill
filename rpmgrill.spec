Name:           rpmgrill
Version:        0.32
Release:        1%{?dist}
Summary:        A utility for catching problems in koji builds
Group:          Development/Tools
License:        Artistic 2.0
Source0:        https://github.com/default-to-open/%{name}/archive/%{version}.tar.gz
URL:            https://github.com/default-to-open/rpmgrill
BuildArch:      noarch
Requires:       perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
Requires:       perl(Module::Pluggable)

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

# Test dependencies
BuildRequires:  perl(CGI)
BuildRequires:  perl(Digest::SHA1)
BuildRequires:  perl(File::LibMagic)
BuildRequires:  perl(File::Slurp)
BuildRequires:  perl(File::Which)
BuildRequires:  perl(File::Copy::Recursive)
BuildRequires:  perl(HTML::Entities)
BuildRequires:  perl(IPC::Run)
BuildRequires:  perl(JSON::XS)
BuildRequires:  perl(Module::Build)
BuildRequires:  perl(Module::Pluggable)
BuildRequires:  perl(Net::DNS)
BuildRequires:  perl(Sort::Versions)
BuildRequires:  perl(Test::Deep)
BuildRequires:  perl(Test::Differences)
BuildRequires:  perl(Test::Exception)
BuildRequires:  perl(Test::Harness)
BuildRequires:  perl(Test::LongString)
BuildRequires:  perl(Test::MockModule)
BuildRequires:  perl(Test::MockObject)
BuildRequires:  perl(Test::Perl::Critic)
BuildRequires:  perl(Test::Simple)
BuildRequires:  perl(Time::ParseDate)
BuildRequires:  perl(Time::Piece)
BuildRequires:  perl(XML::Simple)
BuildRequires:  perl(YAML)
BuildRequires:  perl(YAML::Syck)
BuildRequires:  perl(boolean)
BuildRequires:  perl(open)
BuildRequires:  perl-generators
BuildRequires:  clamav
BuildRequires:  clamav-data
BuildRequires: /usr/bin/xsltproc
BuildRequires: /usr/bin/desktop-file-validate

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

%check
prove -lrcf t

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
