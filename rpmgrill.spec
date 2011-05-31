Name:           rpmgrill
Version:        0.01
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
%config /etc/brewtap.conf

%changelog
* Tue Dec 21 2010 Eduardo Santiago <santiago@redhat.com> - 0.01-1
- Initial packaging
