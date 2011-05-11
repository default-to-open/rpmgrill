#
# Spec file for Qpid C++ packages: qpid-cpp-server*, qpid-cpp-client* and qmf
# svn revision: $Rev$
#

%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%{!?ruby_sitelib: %define ruby_sitelib %(/usr/bin/ruby -rrbconfig  -e 'puts Config::CONFIG["sitelibdir"] ')}
%{!?ruby_sitearch: %define ruby_sitearch %(/usr/bin/ruby -rrbconfig -e 'puts Config::CONFIG["sitearchdir"] ')}


# base version of qpid
%define qpid_release 0.10

# NOTE: these flags should not all be set at the same time!
# RHEL-6 builds should have all flags set to 0.
# Set fedora to 1 for Fedora builds that use so_number.patch
%define fedora                0
# Set rhel_4 to 1 for RHEL-4 builds
%define rhel_4                0
# Set rhel_5 to 1 for RHEL-5 builds
%define rhel_5                1

# LIBRARY VERSIONS
# these should be updated every time we release these packages to customers
%global QPIDCOMMON_VERSION_INFO             5:0:0
%global QPIDTYPES_VERSION_INFO              3:0:2
%global QPIDBROKER_VERSION_INFO             5:0:0
%global QPIDCLIENT_VERSION_INFO             5:0:0
%global QPIDMESSAGING_VERSION_INFO          4:0:1
%global RDMAWRAP_VERSION_INFO               5:0:0
%global SSLCOMMON_VERSION_INFO              5:0:0

# Single var with all lib version params (except store) for make
%global LIB_VERSION_MAKE_PARAMS QPIDCOMMON_VERSION_INFO=%{QPIDCOMMON_VERSION_INFO} QPIDTYPES_VERSION_INFO=%{QPIDTYPES_VERSION_INFO} QPIDBROKER_VERSION_INFO=%{QPIDBROKER_VERSION_INFO} QPIDCLIENT_VERSION_INFO=%{QPIDCLIENT_VERSION_INFO} QPIDMESSAGING_VERSION_INFO=%{QPIDMESSAGING_VERSION_INFO} RDMAWRAP_VERSION_INFO=%{RDMAWRAP_VERSION_INFO} SSLCOMMON_VERSION_INFO=%{SSLCOMMON_VERSION_INFO}

# ===========

# Note: if the mix is changed between MRG_core and MRG_non_core, then
# the files that will be removed at the end of the install section will
# need to be adjusted (moved from one section to the other).
%define client            1
%define server            1
%define qmf               0
%define ruby_qmf          0
%define client_devel      1
%define client_devel_docs 1
%define server_devel      1
%define qmf_devel         0
%define client_rdma       1
%define server_rdma       1
%define client_ssl        1
%define server_ssl        1
%define server_xml        1
%define server_cluster    1
%define server_store      1
%define rh_tests          1

%define name qpid-cpp-mrg

# This overrides the package name - do not change this! It keeps all package
# names consistent, irrespective of the {name} variable - which changes for
# core and non-core builds.
%define pkg_name qpid-cpp

Name:           %{name}
Version:        %{qpid_release}
Release:        5%{?dist}
Summary:        Libraries for Qpid C++ client applications
Group:          System Environment/Libraries
License:        ASL 2.0
URL:            http://qpid.apache.org
Source0:        %{name}-%{version}.tar.gz
Source1:        store-%{version}.tar.gz
%if ! %{rhel_4}
Source2:        qpidd.pp
%endif

Source3:        qpidd.sasldb
Source4:        cpp_doxygen_html.tar.gz

%if %{fedora}
Patch0:         so_number.patch
%endif

%if %{rhel_4}
Patch0:         RHEL4_SASL_Conf.patch
Patch1:         qpidd.patch
Patch2:         bz530364-rhel4.patch
%endif

Patch3:         mrg_2.0.x.patch
Patch4:         bz689907-qpid.patch
Patch5:         bz689907-store.patch


BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
ExclusiveArch:  i386 x86_64
Vendor:         Red Hat, Inc.

BuildRequires: boost-devel
BuildRequires: doxygen
BuildRequires: libtool
BuildRequires: pkgconfig
BuildRequires: ruby
BuildRequires: ruby-devel
BuildRequires: python
BuildRequires: python-devel
BuildRequires: cyrus-sasl-devel
%if ! %{rhel_4}
BuildRequires: cyrus-sasl-lib
%endif
BuildRequires: cyrus-sasl
BuildRequires: libibverbs-devel
%if ! %{rhel_4}
BuildRequires: librdmacm-devel
%endif
BuildRequires: nss-devel
BuildRequires: nspr-devel
BuildRequires: xqilla-devel
BuildRequires: xerces-c-devel
BuildRequires: swig
BuildRequires: db4-devel
BuildRequires: libaio-devel
%if %{rhel_4} || %{rhel_5}
BuildRequires: e2fsprogs-devel
%if %{rhel_5}
BuildRequires: openais-devel
BuildRequires: cman-devel
%endif
%else
BuildRequires: boost-program-options
BuildRequires: boost-filesystem
BuildRequires: libuuid-devel
BuildRequires: corosynclib-devel >= 1.0.0-1
BuildRequires: clusterlib-devel >= 3.0.0-20
%endif


%description

Run-time libraries for AMQP client applications developed using Qpid
C++. Clients exchange messages with an AMQP message broker using
the AMQP protocol.

# === Package: qpid-cpp-client ===

%if %{client}

%package -n %{pkg_name}-client
Summary: Libraries for Qpid C++ client applications
Group: System Environment/Libraries
Requires: boost
Obsoletes: qpidc

Requires(post):/sbin/chkconfig
Requires(preun):/sbin/chkconfig
Requires(preun):/sbin/service
Requires(postun):/sbin/service

%description -n %{pkg_name}-client
Run-time libraries for AMQP client applications developed using Qpid
C++. Clients exchange messages with an AMQP message broker using
the AMQP protocol.

%files -n %{pkg_name}-client
%defattr(-,root,root,-)
%doc cpp/LICENSE
%doc cpp/NOTICE
%doc cpp/README.txt
%doc cpp/INSTALL
%doc cpp/RELEASE_NOTES
%doc cpp/DESIGN
%_libdir/libqpidcommon.so.*
%_libdir/libqpidclient.so.*
%_libdir/libqpidmessaging.so.*
%_libdir/libqpidtypes.so.*
%dir %_libdir/qpid
%dir %_libdir/qpid/client
%dir %_sysconfdir/qpid
%config(noreplace) %_sysconfdir/qpid/qpidc.conf

%endif

# === Package: qpid-cpp-client-devel ===

%if %{client_devel}

%package -n %{pkg_name}-client-devel
Summary: Header files, documentation and testing tools for developing Qpid C++ clients
Group: Development/System
Requires: %{pkg_name}-client = %version-%release
Requires: boost-devel
%if %{rhel_5} || %{rhel_4}
Requires: e2fsprogs-devel
%else
Requires: boost-filesystem
Requires: boost-program-options
Requires: libuuid-devel
%endif
Requires: python
Obsoletes: qpidc-devel
Obsoletes: qpidc-perftest

%description -n %{pkg_name}-client-devel
Libraries, header files and documentation for developing AMQP clients
in C++ using Qpid.  Qpid implements the AMQP messaging specification.

%files -n %{pkg_name}-client-devel
%defattr(-,root,root,-)
%dir %_includedir/qpid
%_includedir/qpid/*.h
%_includedir/qpid/amqp_0_10
%_includedir/qpid/client
#%_includedir/qpid/console
%_includedir/qpid/framing
%_includedir/qpid/sys
%_includedir/qpid/log
%_includedir/qpid/management
%_includedir/qpid/messaging
#%_includedir/qpid/agent
%_includedir/qpid/types
%if %{rhel_4}
%_includedir/qpid-boost
%endif
#%_includedir/qmf
%_libdir/libqpidcommon.so
%_libdir/libqpidclient.so
%_libdir/libqpidmessaging.so
%_libdir/libqpidtypes.so
# new - is this the right location for qpid.pc ?
%_libdir/pkgconfig/qpid.pc
%_datadir/qpidc/examples/messaging
%defattr(755,root,root,-)
%_bindir/qpid-perftest
%_bindir/qpid-topic-listener
%_bindir/qpid-topic-publisher
%_bindir/qpid-latency-test
%_bindir/qpid-client-test
%_bindir/qpid-txtest

%endif

# === Package: qpid-cpp-client-devel-docs ===

%if %{client_devel_docs}

%package -n %{pkg_name}-client-devel-docs
Summary: AMQP client development documentation
Group: Documentation
#BuildArch: noarch
Obsoletes: qpidc-devel-docs


%description -n %{pkg_name}-client-devel-docs
This package includes the AMQP clients development documentation in HTML
format for easy browsing.

%files -n %{pkg_name}-client-devel-docs
%defattr(-,root,root,-)
%doc html

%endif

# === Package: qpid-cpp-server ===

%if %{server}

%package -n %{pkg_name}-server
Summary: An AMQP message broker daemon
Group: System Environment/Daemons
Requires: %{pkg_name}-client = %version-%release
Requires: cyrus-sasl
%if ! %{rhel_4}
Requires(pre): selinux-policy-base
Requires(post): /usr/sbin/semodule
Requires(postun): /usr/sbin/semodule
%endif
Obsoletes: qpidd
Obsoletes: qpidd-acl

%description -n %{pkg_name}-server
A message broker daemon that receives stores and routes messages using
the open AMQP messaging protocol.

%files -n %{pkg_name}-server
%defattr(-,root,root,-)
%if ! %{rhel_4}
%_datadir/selinux/packages/qpidd.pp
%endif
%_libdir/libqpidbroker.so.*
%_libdir/qpid/daemon/replicating_listener.so
%_libdir/qpid/daemon/replication_exchange.so
%_sbindir/qpidd
%config(noreplace) %_sysconfdir/qpidd.conf
%if %{rhel_4}
%config(noreplace) %_libdir/sasl2/qpidd.conf
%else
%config(noreplace) %_sysconfdir/sasl2/qpidd.conf
%endif
%{_initrddir}/qpidd
%dir %_libdir/qpid/daemon
%_libdir/qpid/daemon/acl.so
%attr(755, qpidd, qpidd) %_localstatedir/lib/qpidd
%attr(755, qpidd, qpidd) /var/run/qpidd
%attr(600, qpidd, qpidd) %config(noreplace) %_localstatedir/lib/qpidd/qpidd.sasldb
%doc %_mandir/man1/qpidd.*

%pre -n %{pkg_name}-server
getent group qpidd >/dev/null || groupadd -r qpidd
getent passwd qpidd >/dev/null || \
  useradd -r -M -g qpidd -d %{_localstatedir}/lib/qpidd -s /sbin/nologin \
    -c "Owner of Qpidd Daemons" qpidd
exit 0

%post -n %{pkg_name}-server
# This adds the proper /etc/rc*.d links for the script
/sbin/chkconfig --add qpidd
/sbin/ldconfig
%if ! %{rhel_4}
/usr/sbin/semodule -i %_datadir/selinux/packages/qpidd.pp
%endif

%preun -n %{pkg_name}-server
# Check that this is actual deinstallation, not just removing for upgrade.
if [ $1 = 0 ]; then
        /sbin/service qpidd stop >/dev/null 2>&1 || :
        /sbin/chkconfig --del qpidd
fi

%postun -n %{pkg_name}-server
if [ $1 -ge 1 ]; then
        /sbin/service qpidd condrestart >/dev/null 2>&1 || :
fi
/sbin/ldconfig
%if ! %{rhel_4}
if [ $1 = 0 ]; then
	/usr/sbin/semodule -r qpidd
fi
%endif

%endif

# === Package: qpid-cpp-server-devel ===

%if %{server_devel}

%package -n %{pkg_name}-server-devel
Summary: Libraries and header files for developing Qpid broker extensions
Group: Development/System
Requires: %{pkg_name}-client-devel = %version-%release
Requires: %{pkg_name}-server = %version-%release
Requires: boost-devel
%if ! %{rhel_5} && ! %{rhel_4}
Requires: boost-filesystem
Requires: boost-program-options
%endif
Obsoletes: qpidd-devel

%description -n %{pkg_name}-server-devel
Libraries and header files for developing extensions to the
Qpid broker daemon.

%files -n %{pkg_name}-server-devel
%defattr(-,root,root,-)
%defattr(-,root,root,-)
%_libdir/libqpidbroker.so
%_includedir/qpid/broker

%endif

# === Package: qpid-cpp-client-rdma ===

%if %{client_rdma} && ! %{rhel_4}

%package -n %{pkg_name}-client-rdma
Summary: RDMA Protocol support (including Infiniband) for Qpid clients
Group: System Environment/Libraries
Requires: %{pkg_name}-client = %version-%release
Obsoletes: qpidc-rdma

%description -n %{pkg_name}-client-rdma
A client plugin and support library to support RDMA protocols (including
Infiniband) as the transport for Qpid messaging.

%files -n %{pkg_name}-client-rdma
%defattr(-,root,root,-)
%_libdir/librdmawrap.so.*
%_libdir/qpid/client/rdmaconnector.so
%config(noreplace) %_sysconfdir/qpid/qpidc.conf

%post -n %{pkg_name}-client-rdma
/sbin/ldconfig

%postun -n %{pkg_name}-client-rdma
/sbin/ldconfig

%endif

# === Package: qpid-cpp-server-rdma ===

%if %{server_rdma} && ! %{rhel_4}

%package -n %{pkg_name}-server-rdma
Summary: RDMA Protocol support (including Infiniband) for the Qpid daemon
Group: System Environment/Libraries
Requires: %{pkg_name}-server = %version-%release
Requires: %{pkg_name}-client-rdma = %version-%release
Obsoletes: qpidd-rdma

%description -n %{pkg_name}-server-rdma
A Qpid daemon plugin to support RDMA protocols (including Infiniband) as the
transport for AMQP messaging.

%files -n %{pkg_name}-server-rdma
%defattr(-,root,root,-)
%_libdir/qpid/daemon/rdma.so

%endif

# === Package: qpid-cpp-client-ssl ===

%if %{client_ssl}

%package -n %{pkg_name}-client-ssl
Summary: SSL support for Qpid clients
Group: System Environment/Libraries
Requires: %{pkg_name}-client = %version-%release
Obsoletes: qpidc-ssl

%description -n %{pkg_name}-client-ssl
A client plugin and support library to support SSL as the transport
for Qpid messaging.

%files -n %{pkg_name}-client-ssl
%defattr(-,root,root,-)
%_libdir/libsslcommon.so.*
%_libdir/qpid/client/sslconnector.so

%post -n %{pkg_name}-client-ssl
/sbin/ldconfig

%postun -n %{pkg_name}-client-ssl
/sbin/ldconfig

%endif

# === Package: qpid-cpp-server-ssl ===

%if %{server_ssl}

%package -n %{pkg_name}-server-ssl
Summary: SSL support for the Qpid daemon
Group: System Environment/Libraries
Requires: %{pkg_name}-server = %version-%release
Requires: %{pkg_name}-client-ssl = %version-%release
Obsoletes: qpidd-ssl

%description -n %{pkg_name}-server-ssl
A Qpid daemon plugin to support SSL as the transport for AMQP
messaging.

%files -n %{pkg_name}-server-ssl
%defattr(-,root,root,-)
%_libdir/qpid/daemon/ssl.so

%endif

# === Package: qpid-cpp-server-xml ===

%if %{server_xml}

%package -n %{pkg_name}-server-xml
Summary: XML extensions for the Qpid daemon
Group: System Environment/Libraries
Requires: %{pkg_name}-server = %version-%release
Requires: xqilla
Requires: xerces-c
Obsoletes: qpidd-xml

%description -n %{pkg_name}-server-xml
A Qpid daemon plugin to support extended XML-based routing of AMQP
messages.

%files -n %{pkg_name}-server-xml
%defattr(-,root,root,-)
%_libdir/qpid/daemon/xml.so

%endif

# === Package: qpid-cpp-server-cluster ===

%if %{server_cluster} && ! %{rhel_4}

%package -n %{pkg_name}-server-cluster
Summary: Cluster support for the Qpid daemon
Group: System Environment/Daemons
Requires: %{pkg_name}-server = %version-%release
Requires: %{pkg_name}-client = %version-%release
Requires: openais
Requires: cman
Obsoletes: qpidd-cluster

%description -n %{pkg_name}-server-cluster
A Qpid daemon plugin enabling broker clustering using openais

%files -n %{pkg_name}-server-cluster
%defattr(-,root,root,-)
%_libdir/qpid/daemon/cluster.so
%_libdir/qpid/daemon/watchdog.so
%_libexecdir/qpid/qpidd_watchdog


%if %{rhel_5}
%post -n %{pkg_name}-server-cluster
# Make the qpidd user a member of the root group, and also make
# qpidd's primary group == ais.
usermod -g ais -G root qpidd
%endif

%endif

# === Package: qpid-cpp-server-store ===

%if %{server_store}

%package -n %{pkg_name}-server-store
Summary: Red Hat persistence extension to the Qpid messaging system
Group: System Environment/Libraries
License: LGPL 2.1+
Requires: %{pkg_name}-server = %{version}-%{release}
Requires: %{pkg_name}-client = %{version}-%{release}
Requires: db4
Requires: libaio
Obsoletes: rhm

%description -n %{pkg_name}-server-store
Red Hat persistence extension to the Qpid AMQP broker: persistent message
storage using either a libaio-based asynchronous journal, or synchronously
with Berkeley DB.

%files -n %{pkg_name}-server-store
%defattr(-,root,root,-)
%doc ../store-%{version}/README 
%_libdir/qpid/daemon/msgstore.so*
%{python_sitearch}/qpid/__init__.py*
%{python_sitearch}/qpid/jerr.py*
%{python_sitearch}/qpid/jrnl.py*
%{python_sitearch}/qpid/janal.py*
%_libexecdir/qpid/resize
%_libexecdir/qpid/store_chk

%attr(0775,qpidd,qpidd) %dir %_localstatedir/rhm

%endif

# === Package: rh-qpid-cpp-tests ===

%if %{rh_tests}

%package -n rh-%{pkg_name}-tests
Summary: Internal Red Hat test utilities
Group: System Environment/Tools
Requires: %{pkg_name}-server = %{version}-%{release}
Requires: %{pkg_name}-client = %{version}-%{release}

%description -n rh-%{pkg_name}-tests
Tools which can be used by Red Hat for doing different tests
in RHTS and other places and which customers do not need
to receive at all.

%files -n rh-%{pkg_name}-tests
%defattr(755,root,root,-)
/opt/rh-qpid/failover/run_failover_soak
/opt/rh-qpid/failover/failover_soak
/opt/rh-qpid/clients/declare_queues
/opt/rh-qpid/clients/replaying_sender
/opt/rh-qpid/clients/resuming_receiver
/opt/rh-qpid/clients/receiver
/opt/rh-qpid/clients/sender
/opt/rh-qpid/clients/qpid-receive
/opt/rh-qpid/clients/qpid-send

%endif

# ===

%prep
%setup -q -n %{name}-%{version}
%setup -q -T -D -b 1 -n %{name}-%{version}
%if %{rhel_4}
# set up boost for rhel-4
pushd ./cpp/boost-1.32-support
make apply
popd
pushd ../store-%{version}/rhel4-support
make apply
popd

# apply rhel-4 patches
%patch0
%patch1
%patch2

%endif

%if %{fedora}
%patch0
%endif

# apply qpid patches here
%patch3 -p2
%patch4 -p2

# apply store patch here
pushd ../store-%{version}
%patch5
popd


%define perftests "qpid-perftest qpid-topic-listener qpid-topic-publisher qpid-latency-test qpid-client-test qpid-txtest"

%define rh_qpid_tests_failover "failover_soak run_failover_soak"

%define rh_qpid_tests_clients "replaying_sender resuming_receiver declare_queues sender receiver qpid-send qpid-receive"

%if ! %{rhel_4}
install -d selinux
install %{SOURCE2} selinux
%endif

cp %{SOURCE3} ./cpp/etc
tar -xzf %{SOURCE4} --no-same-owner

%build
pushd cpp
./bootstrap
%if %{rhel_4}
CXXFLAGS="%{optflags} -DNDEBUG -O3" \
%configure --disable-static --without-cpg --without-graphviz --without-help2man --without-rdma
%else
CXXFLAGS="%{optflags} -DNDEBUG -O3" \
%configure --disable-static --with-cpg --without-graphviz --without-help2man
%endif
ECHO=echo make %{LIB_VERSION_MAKE_PARAMS}

# Make perftest utilities
pushd src/tests
for ptest in %{perftests}; do
  ECHO=echo make $ptest
done
# Make rh-qpid-test programs (RH internal)
for rhtest in %{rh_qpid_tests_failover} %{rh_qpid_tests_clients}; do
        make $rhtest
done
# Patch run_failover_soak to make it work outside source tree
mv -f run_failover_soak run_failover_soak.orig
cat run_failover_soak.orig | sed -e "s#^src_root=..#src_root=/usr/sbin#" \
                                 -e "s#\$src_root/\.libs#%{_libdir}/qpid/daemon#" \
                                 -e "s#\`dirname \$0\`#../failover#" \
                                 -e "s#^exec #cd /opt/rh-qpid/clients; exec #" > run_failover_soak

popd
popd

# Store
pushd ../store-%{version}
%if %{rhel_4}
export CXXFLAGS="%{optflags} -DNDEBUG -I/usr/include/qpid-boost" 
%else
export CXXFLAGS="%{optflags} -DNDEBUG" 
%endif
./bootstrap
%configure --disable-static --disable-rpath --disable-dependency-tracking --with-qpid-checkout=%{_builddir}/%{name}-%{version}
make
popd

%install
rm -rf %{buildroot}
mkdir -p -m0755 %{buildroot}/%_bindir
pushd %{_builddir}/%{name}-%{version}/cpp
make install DESTDIR=%{buildroot}
install -Dp -m0755 etc/qpidd %{buildroot}%{_initrddir}/qpidd
install -d -m0755 %{buildroot}%{_localstatedir}/lib/qpidd
install -d -m0755 %{buildroot}%_libdir/qpidd
install -d -m0755 %{buildroot}/var/run/qpidd
%if %{rhel_4}
# boost headers
install -d -m0755 %{buildroot}%_includedir/qpid-boost/boost
cp -pr src/boost/* %{buildroot}%_includedir/qpid-boost/boost
%endif
# Install perftest utilities
pushd src/tests/
for ptest in %{perftests}; do
  libtool --mode=install install -m755 $ptest %{buildroot}/%_bindir
done
# Install rh-qpid-test programs (RH internal)
mkdir -p -m 0755 %{buildroot}/opt/rh-qpid/failover
mkdir -p -m 0755 %{buildroot}/opt/rh-qpid/clients
for rhtest in %{rh_qpid_tests_failover} ; do
        libtool --mode=install install -m 755 $rhtest %{buildroot}/opt/rh-qpid/failover/
done
for rhtest in %{rh_qpid_tests_clients} ; do
        libtool --mode=install install -m 755 $rhtest %{buildroot}/opt/rh-qpid/clients/
done

popd

# remove things we don't want to package

rm -f %{buildroot}%_libdir/*.a
rm -f %{buildroot}%_libdir/*.l
rm -f %{buildroot}%_libdir/*.la
%if ! %{rhel_4}
rm -f %{buildroot}%_libdir/librdmawrap.so
%endif
rm -f %{buildroot}%_libdir/libsslcommon.so
rm -f %{buildroot}%_libdir/qpid/client/*.la
rm -f %{buildroot}%_libdir/qpid/daemon/*.la

# this should be fixed in the examples Makefile (make install)
rm -f %{buildroot}%_datadir/qpidc/examples/Makefile
rm -f %{buildroot}%_datadir/qpidc/examples/README.txt
rm -rf %{buildroot}%_datadir/qpidc/examples/qmf-console
rm -rf %{buildroot}%_datadir/qpidc/examples/old_api

rm -f %{buildroot}%ruby_sitearch/cqmf2.*
rm -f %{buildroot}%ruby_sitearch/cqpid.*
rm -f %{buildroot}%ruby_sitelib/qmf2.rb

rm -f %{buildroot}%python_sitelib/cqmf2.*
rm -f %{buildroot}%python_sitelib/cqpid.*
rm -f %{buildroot}%python_sitelib/qmf2.*

rm -f %{buildroot}%_libdir/libcqpid_perl.so

%if ! %{rhel_4}
install -d %{buildroot}%{_datadir}/selinux/packages
install -m 644 %{_builddir}/%{name}-%{version}/selinux/qpidd.pp %{buildroot}%{_datadir}/selinux/packages
%endif

rm -f %{buildroot}%_libdir/_*
rm -fr %{buildroot}%_libdir/qpid/tests
rm -fr %{buildroot}%_libexecdir/qpid/tests
%if ! %{rhel_4}
rm -f %{buildroot}%{ruby_sitearch}/qmfengine.la
%endif
popd

#Store
pushd %{_builddir}/store-%{version}
make install DESTDIR=%{buildroot}
install -d -m0775 %{buildroot}%{_localstatedir}/rhm
install -d -m0755 %{buildroot}%_libdir/qpid/daemon
rm -f %{buildroot}%_libdir/qpid/daemon/*.a
rm -f %{buildroot}%_libdir/qpid/daemon/*.la
rm -f %{buildroot}%_libdir/*.a
rm -f %{buildroot}%_libdir/*.la
rm -f %{buildroot}%_sysconfdir/rhmd.conf
popd


rm -rf %{buildroot}%_includedir/qmf
rm -rf %{buildroot}%_includedir/qpid/agent
rm -rf %{buildroot}%_includedir/qpid/console
rm -rf %{buildroot}%{python_sitelib}/qmfgen
rm -f  %{buildroot}%_bindir/qmf-gen
rm -f  %{buildroot}%_libdir/libqmf.so
rm -f  %{buildroot}%_libdir/libqmf2.so
rm -f  %{buildroot}%_libdir/libqmfconsole.so
rm -f  %{buildroot}%_libdir/libqmfengine.so
rm -f  %{buildroot}%_libdir/libqmf.so.*
rm -f  %{buildroot}%_libdir/libqmf2.so.*
rm -f  %{buildroot}%_libdir/libqmfconsole.so.*
rm -f  %{buildroot}%_libdir/libqmfengine.so.*
%if ! %{rhel_4}
rm -f  %{buildroot}%{ruby_sitearch}/qmfengine.so
rm -f %{buildroot}%{ruby_sitelib}/qmf.rb
%endif


%clean
rm -rf %{buildroot}

%check
#pushd %{_builddir}/%{name}-%{version}/cpp
# LANG=C needs to be in the environment to deal with a libtool issue
# temporarily disabling make check due to libtool issues
# needs to be re-enabled asap
#LANG=C ECHO=echo make check
#popd

%ifarch i386 i586 i686 x86_64
#RHM
#pushd %{_builddir}/store-%{version}
#make check
#popd
#/RHM
%endif

%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%changelog
* Thu Apr 28 2011 Ted Ross <tross@redhat.com> - 0.10-5
- Intermediate build to address rpmdiff/multilib problems
- BZs: 689907
- Now sourcing qpidd.sasldb from distcvs
- Now sourcing the doxygen-generated HTML from distcvs

* Wed Apr 20 2011 Mike Cressman <mcressman@redhat.com> - 0.10-4
- 2.0 RC build 1
- BZs: 690261,693407,695263,695716,696637,696655,696698

* Tue Apr 5 2011 Mike Cressman <mcressman@redhat.com> - 0.10-3
- minor update for some upstream 0.10 cleanup

* Wed Mar 23 2011 Mike Cressman <mcressman@redhat.com> - 0.10-1
- Rebase to upstream 0.10 rev 1083082 (store rev remains 4446)
- Removing rev from the package names

* Wed Mar 9 2011 Mike Cressman <mcressman@redhat.com> - 0.9.1079953-1
- Redo latest build because of windows build error, revs 1079953 and 4446

* Tue Mar 8 2011 Mike Cressman <mcressman@redhat.com> - 0.9.1078967-1
- Rebase to revs 1078967 and 4446
- Remove qmf packages (they are being moved elsewhere)

* Mon Feb 23 2011 Mike Cressman <mcressman@redhat.com> - 0.9.1073306-1
- Rebase to revs 1073306 and 4443

* Thu Feb 3 2011 Mike Cressman <mcressman@redhat.com> - 0.7.946106-28
- 1.3.2 RC 2 build 2
- BZs 656385,674183,674338

* Thu Jan 20 2011 Mike Cressman <mcressman@redhat.com> - 0.7.946106-27
- 1.3.2 RC 2 build
- BZs 549670,614944,620742,632188,639994,640312,647719,654872,
- BZs 656385,658936,662765,667735,669343,669452

* Wed Jan 5 2011 Mike Cressman <mcressman@redhat.com> - 0.7.946106-26
- 1.3.2 RC 1 build
- BZs 484691,500430,629892,631969,631973

* Thu Dec 9 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-25
- bugfix build with clustering fixes 
- BZs 629756,648927,655141,655078

* Mon Nov 29 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-24
- second build to produce src rpm for .net RC build
- pulled out 647858 -- it's not supported in 1.3 C++ yet

* Wed Nov 24 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-23
- build to produce src rpm for .net RC build
- BZs 647230,647858,648649,649733

* Tue Nov 16 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-22
- BZ 649822

* Fri Nov 12 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-21
- BZ 652463

* Thu Nov 11 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-20
- BZ 647861 - updates to the previous fix
- rev the library versions (types,broker,messaging)

* Tue Nov 9 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-19
- BZs 620687,621468,631567,647860,647861,649733

* Fri Sep 24 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-17
- Release candidate build 4
- BZ 636827 - store bug can crash the broker

* Wed Sep 22 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-16
- Release candidate build 3
- BZ 636262

* Wed Sep 15 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-15
- Release candidate build 2
- BZ 633681 plus an rpmdiff fix in qmf compilation

* Mon Sep 13 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-14
- Release candidate build 1
- BZs 604688,630996,632349,632395
- added receiver,sender,qpid_receive,qpid_send to rh-qpid-cpp-tests

* Tue Sep 7 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-13
- intermediate test build
- BZs 621527,621571,621715,622699,623805,624714,625450,625541,626341,629035

* Thu Aug 12 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-12
- Beta 5 build 2
- Messaging BZs 620418, 621998, 621666, 622422, 623511
- Store BZs 614943, 620676, 622889, 623653
- updated selinux policy - allow destroy of aixexec_t's 

* Mon Aug 2 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-11
- Beta 5 build 1
- BZs 612535, 616489, 619166, 619765, 620402

* Mon Jul 26 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-10
- BZs 614857, 617281, 617357

* Wed Jul 21 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-9
- intermediate build, including missing windows icon file, plus:
- BZs 614861, 614854, 616072, plus some windows cleanup and a cluster race condition

* Fri Jul 16 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-7
- Beta 4 build 3, including these BZs:
- 572984 588766 608807 609258 609682 609801 609803 610156 610493 610772
- 611543 611847 612615 612682 612988 613216 613753 613912 614054 614344
- add libqpidtypes
- new qpidd.pp selinux policy file (updated)

* Tue Jun 29 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-6
- Beta 4 build 2, including:
- BZ 603085 - VB debug symbols included (.pdb files)
- dotnet API cleanup, more C#, VB, powershell examples

* Mon Jun 28 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-5
- Beta 4 build 1, including:
- BZ 603896 - Message traffic freezes after queues back up
- BZ 604842 - cluster test fails intermittently
- BZ 605763 - Fix cluster broker crashes when management is active
- BZ 606761 - Do not unmask signals while waiting for IO to happen
- BZ 606824 - Acquired but not accepted messages not sent to alternate exchange
- BZ 607550 - Spout was ignoring frame while closing connection
- BZ 607552 - ttl is lost for federation routes where trace id is added
- BZ 607748 - Crash on exit in store cluster tests.
- BZ 608118 - New messaging API lacks access to some 0-10 headers

* Fri Jun 18 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-4
- Beta 3 build 2, including:
- new shared library revision numbering mechanism applied
- BZ 602198 - qpidd crashes when testing heartbeats
- BZ 603805 - .NET bindings for the C++ Messaging API
- BZ 603835 - Clean up connections causing extra connection objects in the management agent map
- BZ 603839 - Concurrent tagging of message with trace id while message is delivered from another queue causes segfault
- BZ 604152 - Do not default to auth=no in the default qpidd.conf file

* Mon Jun 14 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-3
- Beta 3 build 1, including:
- BZ 508959 - Attempt to propagate binding info over dynamic link can crash broker if session has already failed
- BZ 538188 - connection.start() hangs if connection is not accepted
- BZ 566691 - Abort in qpid::management::ManagementAgent::periodicProcessing on shutting down qpidd
- BZ 577274 - windows-related work, including updating the examples
- BZ 577362 - Long failover_soak test hangs.
- BZ 582460 - Remove dependency on qpid::sys::AbsTime
- BZ 589675 - Fix initialization-order problem with URL protocol tags
- BZ 589683 - Broker misconfiguration causes broker stop to fail
- BZ 591139 - RDMA fixes
- BZ 591292 - Fix for heartbeat related segfault
- BZ 591650 - Ensure close is called for a disconnect, preventing leaks
- BZ 596765 - Remove global shared_ptr to store in store plugin
- BZ 596907 - Fixed Default behaviour of new messaging client is to retry forever
- BZ 597066 - Python Connection object should use None as default username, not guest
- BZ 597149 - qpid python high level API clients not runnable on RHEL4
- BZ 597362 - Sporadic failure of check-long in cluster_tests.py test_failover.
- BZ 598350 - Fixed compilation error on windows
- BZ 598516 - Fixed sporadic client "reserved bits not 0" exceptions with cluster + encryption.
- BZ 598550 - Alleviates some of the broker load for QMF V2 format requests
- BZ 598557 - qpidd --no-data-dir with store loaded segfaults
- BZ 598597 - fix client leaks on linux
- BZ 598948 - qpid c++ client occasionly fails to authenticate using GSSAPI
- BZ 599470 - options string for connection does not work for some types
- BZ 599700 - Console examples sometimes fail due to not waiting for the broker connection to complete
- BZ 601277 - qpidd broker crash
- BZ 601828 - QMF Agent returning STATUS_USER returns error 7 to QMF Console
- BZ 602347 - Fix cluster-safe assertion in connection negotiation.
- BZ 602672 - Message::getSubject() returns an empty string even if the message has a subject

* Fri May 28 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-2
- Second beta 2 build - first respin
- BZ 558526 - clustered qpidd shutdowns during start-up
- BZ 569698 - sasl_decode buffer overflow under load
- BZ 577353 - Executables in $PATH have bad names
- BZ 586544 - qpid::agent::ManagementAgent::init call doesn't provide complete connection control
- BZ 587182 - clustered broker reports 'ObjectId collision in moveNewObjects'
- BZ 587190 - qpid c++ (perftest) clients hang
- BZ 591420 - C++ clients on windows hang at program end
- BZ 592999 - clustered persistent broker leaves cluster with error when cluster nodes started from clean store
- BZ 593828 - QMF: python console needs ability to filter unsolicited events
- BZ 593831 - QMF: c++ console needs ability to filter unsolicited events
- BZ 594761 - qpidd segfaults under high load
- BZ 595438 - qpidd+msgstore crashes in mrg::msgstore::InactivityFireEvent::~InactivityFireEvent() -> free()
- BZ 596765- Shutdown order in broker causes invalid writes by ManagementObject in store

* Wed May 19 2010 Mike Cressman <mcressman@redhat.com> - 0.7.946106-1
- Rebase to latest trunk revisions (946106,3975) - pre-beta 2 build (not final)
- add libqpidmessaging and new api examples

* Thu Apr 29 2010 Mike Cressman <mcressman@redhat.com> - 0.7.935473-1
- Rebase to latest trunk revisions (939184,3943) - beta 1+ build
- Add two new python scripts to qpid-cpp-server-store deliverables

* Mon Apr 19 2010 Mike Cressman <mcressman@redhat.com> - 0.7.935473-1
- Rebase to latest trunk revisions (935473,3913) - beta 1 build
- require selinux-policy-base

* Wed Mar 31 2010 Mike Cressman <mcressman@redhat.com> - 0.7.929717-1
- Rebase to latest trunk revisions (929717,3889) - alpha 3 build

* Wed Mar 3 2010 Mike Cressman <mcressman@redhat.com> - 0.7.916826-2
- Add back missing rh-qpid-tests (internal) package and qpid-boost

* Mon Mar 1 2010 Mike Cressman <mcressman@redhat.com> - 0.7.916826-1
- Rebase to revs 916826 and 3860
- Merge RHEL-4 specifics into spec file from RHEL-5 (new package names)

* Tue Feb 16 2010 Justin Ross <jross@redhat.com> - 0.7.909548-1
- Rebase qpid to 909548

* Wed Feb 10 2010 Mike Cressman <mcressman@redhat.com> - 0.7.908272-1
- Rebase to latest trunk revisions (908272,3847)

* Thu Feb 4 2010 Mike Cressman <mcressman@redhat.com> - 0.7.904602-4
- Fix typo with e2fsprogs-devel install dependency

* Wed Feb 3 2010 Mike Cressman <mcressman@redhat.com> - 0.7.904602-3
- Merged in RHEL-6 spec file changes

* Wed Feb 3 2010 Kim van der Riet <kim.vdriet@redhat.com> - 0.6.895736-5
- Related: rhbz#554415
  Changed name of fedora_lib_patch flag to simply fedora
  Added rhel_5 flag, and put in switches for rhel-5 libs
  Added new boost libs for RHEL-6/Fedora

* Tue Jan 26 2010 Kim van der Riet <kim.vdriet@redhat.com> - 0.6.895736-3
- Fixed some rpmlint warnings.

* Fri Jan 22 2010 Kim van der Riet <kim.vdriet@redhat.com> - 0.6.895736-2
- Rebuild because of glitch in brew handling new tags.

* Thu Jan 21 2010 Kim van der Riet <kim.vdriet@redhat.com> - 0.6.895736-1
- Corrected naming of rpms by adding pkg_name variable.

* Thu Jan 21 2010 Kim van der Riet <kim.vdriet@redhat.com> - 0.6.895736-1
- First build of qpid non-core components (ie which are part of the MRG
  channel), this build is based on the RHEL-6 spec file.

* Tue Oct 27 2009 Nuno Santos <nsantos@redhat.com> - 0.5.819819-2
- Renaming of subpackages as per http://fedoraproject.org/wiki/Features/ImprovedQpidCppPackaging

* Tue Sep 29 2009 Nuno Santos <nsantos@redhat.com> - 0.5.819819-1
- Rebased to svn rev 819819 for F12 beta

* Thu Sep 24 2009 Nuno Santos <nsantos@redhat.com> - 0.5.818599-1
- Rebased to svn rev 818599
- rhm-cpp-server-store obsoletes rhm top-level package

* Fri Sep 19 2009 Nuno Santos <nsantos@redhat.com> - 0.5.817349
- Rebased to svn rev 817349

* Wed Jul 29 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.5.790661-3
- Update BuildRequires and Requires to use latest stable versions of
  corosync and clusterlib.
- Unbreak perftests define (and fix vim spec syntax coloring).

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.790661-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jul  2 2009 Nuno Santos <nsantos@redhat.com> - 0.5.790661-1
- Rebased to svn rev 790661; .so lib numbers bumped

* Fri Jun 26 2009 Nuno Santos <nsantos@redhat.com> - 0.5.788782-1
- Rebased to svn rev 788782

* Mon Jun 22 2009 Nuno Santos <nsantos@redhat.com> - 0.5.787286-1
- Rebased to svn rev 787286

* Wed Jun 10 2009 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.5.752600-8
- update BuildRequires to use corosynclib-devel in correct version.
- update BuildRequires to use clusterlib-devel instead of the obsoleted
  cmanlib-devel.
- drop Requires on cmanlib. This should come in automatically as part
  of the rpm build process.
- re-align package version to -8. -7 didn't have a changelog entry?
- add patch to port Cluster/Cpg to newest Cpg code.
- change patch tag to use patch0.

* Mon May  4 2009 Nuno Santos <nsantos@redhat.com> - 0.5.752600-5
- patch for SASL credentials refresh

* Wed Apr  1 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 0.5.752600-5
- Fix unowned examples directory in -devel pkg.

* Mon Mar 16 2009 Nuno Santos <nsantos@localhost.localdomain> - 0.5.752600-4
- BZ483925 - split docs into a separate noarch subpackage

* Mon Mar 16 2009 Nuno Santos <nsantos@redhat.com> - 0.5.752600-3
- Disable auth by default; fix selinux requires

* Wed Mar 11 2009 Nuno Santos <nsantos@redhat.com> - 0.5.752600-1
- Rebased to svn rev 752600

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.738618-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.738618-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jan 28 2009 Nuno Santos <nsantos@redhat.com> - 0.4.738618-2
- Rebased to svn rev 738618

* Tue Jan 20 2009 Nuno Santos <nsantos@redhat.com> - 0.4.734452-3
- BZ474614 and BZ474613 - qpidc/rhm unowned directories

* Thu Jan 15 2009 Nuno Santos <nsantos@redhat.com> - 0.4.734452-1
- Rebased to svn rev 734452

* Tue Dec 23 2008 Nuno Santos <nsantos@redhat.com> - 0.4.728142-1
- Rebased to svn rev 728142
- Re-enable cluster, now using corosync

* Tue Dec  2 2008 Nuno Santos <nsantos@redhat.com> - 0.3.722557-1
- Rebased to svn rev 722557
- Temporarily disabled cluster due to openais version incompatibility

* Wed Nov 26 2008 Nuno Santos <nsantos@redhat.com> - 0.3.720979-1
- Rebased to svn rev 720979

* Fri Nov 21 2008  Mick Goulish <mgoulish@redhat.com>
- updated to 719552

* Thu Nov 20 2008  Mick Goulish <mgoulish@redhat.com>
- updated to 719323
- For subpackage qpidd-cluster, added dependency to cman-devel.
- For subpackage qpidd-cluster, added dependency to qpidc.
- added BuildRequires cman-devel

* Fri Nov 14 2008 Justin Ross <jross@redhat.com> - 0.3.714072-1
- Update to svn rev 714072
- Enable building --with-cpg

* Wed Nov 12 2008 Justin Ross <jross@redhat.com> - 0.3.713378-1
- Update to svn rev 713378

* Fri Nov  7 2008 Justin Ross <jross@redhat.com> - 0.3.712127-1
- Update to svn rev 712127

* Thu Nov  6 2008 Nuno Santos <nsantos@redhat.com> - 0.3.711915-2
- Removed extraneous openais-devel dependency

* Thu Nov  6 2008 Justin Ross <jross@redhat.com> - 0.3.711915-1
- Update to svn rev 711915

* Tue Nov  4 2008 Nuno Santos <nsantos@redhat.com> - 0.3.709187-2
- Remove extraneous dependency

* Thu Oct 30 2008 Nuno Santos <nsantos@redhat.com> - 0.3.709187-1
- Rebsed to svn rev 709187

* Tue Oct 28 2008 Nuno Santos <nsantos@redhat.com> - 0.3.708576-1
- Rebased to svn rev 708576

* Mon Oct 27 2008 Nuno Santos <nsantos@redhat.com> - 0.3.708210-1
- Rebased to svn rev 708210; address make check libtool issue

* Fri Oct 24 2008 Justin Ross <jross@redhat.com> - 0.3.707724-1
- Update to revision 707724

* Thu Oct 23 2008 Justin Ross <jross@redhat.com> - 0.3.707468-1
- Don't use silly idenity defines
- Add new ssl and rdma subpackages
- Move cluster and xml plugins into their own subpackages
- Reflect new naming of plugins

* Wed Aug 21 2008 Justin Ross <jross@redhat.com> - 0.2.687156-1
- Update to source revision 687156 of the qpid.0-10 branch

* Wed Aug 14 2008 Justin Ross <jross@redhat.com> - 0.2.685273-1
- Update to source revision 685273 of the qpid.0-10 branch

* Wed Aug  6 2008 Justin Ross <jross@redhat.com> - 0.2.683301-1
- Update to source revision 683301 of the qpid.0-10 branch

* Thu Jul 15 2008 Justin Ross <jross@redhat.com> - 0.2.676581-1
- Update to source revision 676581 of the qpid.0-10 branch
- Work around home dir creation problem
- Use a license string that rpmlint likes

* Thu Jul 10 2008 Nuno Santos <nsantos@redhat.com> - 0.2.667603-3
- BZ453818: added additional tests to -perftest

* Thu Jun 13 2008 Justin Ross <jross@redhat.com> - 0.2.667603-1
- Update to source revision 667603

* Thu Jun 12 2008 Justin Ross <jross@redhat.com> - 0.2.667253-1
- Update to source revision 667253

* Thu Jun 12 2008 Nuno Santos <nsantos@redhat.com> - 0.2.666138-5
- add missing doc files

* Wed Jun 11 2008 Justin Ross <jross@redhat.com> - 0.2.666138-3
- Added directories for modules and pid files to install script

* Wed May 28 2008 David Sommerseth <dsommers@redhat.com> - 0.2.663761-1
- Added perftest utilities

* Thu May 22 2008 Nuno Santos <nsantos@redhat.com> - 0.2.656926-4
- Additional build flags for i686

* Tue May 20 2008 Nuno Santos <nsantos@redhat.com> - 0.2.656926-3
- BZ 432872: remove examples, which are being packaged separately

* Tue May 20 2008 Justin Ross <jross@redhat.com> -0.2.656926-2
- Drop build requirements for graphviz and help2man

* Wed May 14 2008 Nuno Santos <nsantos@redhat.com> - 0.2-34
- Bumped for Beta 4 release

* Fri May  9 2008 Matthew Farrellee <mfarrellee@redhat> - 0.2-33
- Moved qpidd.conf from qpidc package to qpidd package
- Added BuildRequires xqilla-devel and xerces-c-devel to qpidd for XML Exchange
- Added BuildRequires openais-devel to qpidd for CPG
- Added missing Requires xqilla-devel to qpidd-devel

* Thu May  8 2008 Matthew Farrellee <mfarrellee@redhat> - 0.2-32
- Added sasl2 config file for qpidd
- Added cyrus-sasl dependencies

* Wed May  7 2008 Matthew Farrellee <mfarrellee@redhat> - 0.2-31
- Added python dependency, needed by managementgen

* Wed May  7 2008 Matthew Farrellee <mfarrellee@redhat> - 0.2-30
- Added management-types.xml to qpidc-devel package

* Tue May  6 2008 Matthew Farrellee <mfarrellee@redhat> - 0.2-29
- Added managementgen to the qpidc-devel package

* Mon Apr 14 2008 Nuno Santos <nsantos@redhat.com> - 0.2-28
 - Fix home dir permissions
 - Bumped for Fedora 9

* Mon Mar 31 2008 Nuno Santos <nsantos@redhat.com> - 0.2-25
- Create user qpidd, start qpidd service as qpidd

* Mon Feb 18 2008 Rafael Schloming <rafaels@redhat.com> - 0.2-24
- Bug fix for TCK issue in Beta 3

* Thu Feb 14 2008 Rafael Schloming <rafaels@redhat.com> - 0.2-23
- Bumped to pull in fixes for Beta 3

* Tue Feb 12 2008 Alan Conway <aconway@redhat.com> - 0.2-22
- Added -g to compile flags for debug symbols.

* Tue Feb 12 2008 Alan Conway <aconway@redhat.com> - 0.2-21
- Create /var/lib/qpidd correctly.

* Mon Feb 11 2008 Rafael Schloming <rafaels@redhat.com> - 0.2-20
- bumped for Beta 3

* Mon Jan 21 2008 Gordon Sim <gsim@redhat.com> - 0.2-18
- bump up rev for recent changes to plugin modules & mgmt

* Thu Jan 03 2008 Nuno Santos <nsantos@redhat.com> - 0.2-17
- add missing header file SessionManager.h

* Thu Jan 03 2008 Nuno Santos <nsantos@redhat.com> - 0.2-16
- limit builds to i386 and x86_64 archs

* Thu Jan 03 2008 Nuno Santos <nsantos@redhat.com> - 0.2-15
- add ruby as a build dependency

* Tue Dec 18 2007 Nuno Santos <nsantos@redhat.com> - 0.2-14
- include fixes from Gordon Sim (fragmentation, lazy-loading, staging) 
  and Alan Conway (exception handling in the client).

* Thu Dec 6 2007 Alan Conway <aconway@redhat.com> - 0.2-13
- installcheck target to build examples in installation.

* Thu Nov 8 2007 Alan Conway <aconway@redhat.com> - 0.2-10
- added examples to RPM package.

* Thu Oct 9 2007 Alan Conway <aconway@redhat.com> - 0.2-9
- added config(noreplace) for qpidd.conf

* Thu Oct 4 2007 Alan Conway <aconway@redhat.com> - 0.2-8
- Added qpidd.conf configuration file.
- Updated man page to detail configuration options.

* Thu Sep 20 2007 Alan Conway <aconway@redhat.com> - 0.2-7
- Removed apr dependency.

* Wed Aug 1 2007 Alan Conway <aconway@redhat.com> - 0.2-6
- added --disable-cluster flag

* Tue Apr 17 2007 Alan Conway <aconway@redhat.com> - 0.2-5
- Add missing Requires: e2fsprogs-devel for qpidc-devel.

* Tue Apr 17 2007 Alan Conway <aconway@redhat.com> - 0.2-4
- longer broker_start timeout to avoid failures in plague builds.

* Tue Apr 17 2007 Alan Conway <aconway@redhat.com> - 0.2-3
- Add missing Requires: apr in qpidc.

* Mon Apr 16 2007 Alan Conway <aconway@redhat.com> - 0.2-2
- Bugfix for memory errors on x86_64.

* Thu Apr 12 2007 Alan Conway <aconway@redhat.com> - 0.2-1
- Bumped version number for rhm dependencies.

* Wed Apr 11 2007 Alan Conway <aconway@redhat.com> - 0.1-5
- Add qpidd-devel sub-package.

* Mon Feb 19 2007 Jim Meyering <meyering@redhat.com> - 0.1-4
- Address http://bugzilla.redhat.com/220630:
- Remove redundant "cppunit" build-requires.
- Add --disable-static.

* Thu Jan 25 2007 Alan Conway <aconway@redhat.com> - 0.1-3
- Applied Jim Meyerings fixes from http://mail-archives.apache.org/mod_mbox/incubator-qpid-dev/200701.mbox/<87hcugzmyp.fsf@rho.meyering.net>

* Mon Dec 22 2006 Alan Conway <aconway@redhat.com> - 0.1-1
- Fixed all rpmlint complaints (with help from David Lutterkort)
- Added qpidd --daemon behaviour, fix init.rc scripts

* Fri Dec  8 2006 David Lutterkort <dlutter@redhat.com> - 0.1-1
- Initial version based on Jim Meyering's sketch and discussions with Alan
  Conway
