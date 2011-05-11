%global qpid_version 0.10

Summary:        MRG management system agent
Name:           sesame
Version:        0.10
Release:        1%{?dist}
License:        GPL
Group:          System Environment/Libraries
URL:            http://svn.fedorahosted.org/svn/cumin/trunk/sesame/cpp/
Source0:        %{name}-%{version}.tar.gz
Patch0:         bz481770.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  qpid-qmf-devel == %{qpid_version}
BuildRequires:  db4-devel
BuildRequires:  libtool
BuildRequires:  pkgconfig
BuildRequires:  dbus-devel

Requires:       qpid-qmf == %{qpid_version}
Requires:       /usr/bin/uuidgen
Requires:       dbus

Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts

%description
Sesame is the MRG management system agent.

%prep
%setup -q
%patch0 -p1

%build
export CXXFLAGS="%{optflags} -DNDEBUG -O3"

./bootstrap
%configure
make # %{?_smp_mflags}

%install
rm -rf %{buildroot}
mkdir -p -m0755 %{buildroot}
make install DESTDIR=%{buildroot}

install -d %{buildroot}%{_sysconfdir}/rc.d/init.d
install -T -m 0755 etc/sysvinit-sesame %{buildroot}%{_sysconfdir}/rc.d/init.d/sesame
install -d %{buildroot}%{_localstatedir}/log/sesame
install -d %{buildroot}%{_localstatedir}/lib/sesame

%pre
getent group sesame > /dev/null || groupadd -r sesame
getent passwd sesame > /dev/null || useradd -r \
       -g sesame -d %{_localstatedir}/lib/sesame -s /sbin/nologin \
       -c "Owner of the sesame daemon" sesame
exit 0

%post
uuidgen > %{_localstatedir}/lib/sesame/uuid
chown sesame:sesame %{_localstatedir}/lib/sesame/uuid
/sbin/chkconfig --add sesame

%preun
if [ $1 = 0 ] ; then
    /sbin/service sesame stop >/dev/null 2>&1
    /sbin/chkconfig --del sesame
fi

%postun
if [ "$1" -ge "1" ] ; then
    /sbin/service sesame condrestart >/dev/null 2>&1 || :
fi

%clean
rm -rf %{buildroot}

%files
%defattr(-,sesame,sesame,-)
%doc README COPYING
%{_bindir}/sesame
%config %{_sysconfdir}/sesame/sesame.conf
%{_localstatedir}/log/sesame
%{_localstatedir}/lib/sesame
%defattr(-,root,root,-)
%{_sysconfdir}/rc.d/init.d/sesame

%changelog
* Thu Mar 24 2011 Justin Ross <jross@redhat.com> - 0.10-1
- Rebuilding for updated qmf libs
- Updated URL

* Thu Feb 24 2011 Nuno Santos <nsantos@redhat.com> - 0.9.4443-1
- Rebased to svn rev 4443

* Thu Sep 16 2010 Nuno Santos <nsantos@redhat.com> - 0.7.4297-1
- Rebased to svn rev 4297

* Mon Sep 13 2010 Nuno Santos <nsantos@redhat.com> - 0.7.3918-7
- BZ621317: Sesame does not shutdown when uninstalled

* Tue Jul 27 2010 Nuno Santos <nsantos@redhat.com> - 0.7.3918-5
- Rebuilding for updated qmf libs

* Wed Jun 16 2010 Nuno Santos <nsantos@redhat.com> - 0.7.3918-3
- Rebuilding for updated qmf libs

* Wed May 19 2010 Justin Ross <jross@redhat.com> - 0.7.3891-2
- Initial build
