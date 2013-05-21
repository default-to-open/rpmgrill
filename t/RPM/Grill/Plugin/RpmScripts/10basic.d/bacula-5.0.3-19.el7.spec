%bcond_without	fedora

Name:			bacula
Version:		5.0.3
Release:		19%{?dist}
Summary:		Cross platform network backup for Linux, Unix, Mac and Windows
# See LICENSE for details
License:		GPLv2 with exceptions
Group:			System Environment/Daemons
URL:			http://www.bacula.org
BuildRoot:		%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Source0:		http://download.sourceforge.net/bacula/bacula-%{version}.tar.gz
Source2:		bacula.logrotate
Source3:		bacula-checkconf
Source4:		bacula-fd.init
Source5:		bacula-dir.init
Source6:		bacula-sd.init
Source7:		bacula-fd.service
Source8:		bacula-dir.service
Source9:		bacula-sd.service
Source10:		bacula-wxconsole.desktop
Source11:		bacula-traymonitor.desktop
Source12:		bacula-bat.desktop
Source13:		bacula-traymonitor.console_apps
Source14:		bacula-wxconsole.console_apps
Source15:		bacula-fd.sysconfig
Source16:		bacula-dir.sysconfig
Source17:		bacula-sd.sysconfig

Patch1:			bacula-5.0.3-config.patch
Patch2:			bacula-5.0.3-nagios-ent-fd.patch
Patch3:			bacula-5.0.3-pamd.patch
Patch4:			bacula-5.0.2-openssl.patch
Patch5:			bacula-5.0.3-queryfile.patch
Patch6:			bacula-5.0.2-python27.patch
Patch7:			bacula-5.0.3-log-path.patch
Patch8:			bacula-5.0.3-sqlite-priv.patch
Patch9:			bacula-5.0.3-tray-dir.patch
Patch10:		bacula-5.0.3-mysql55.patch
Patch11:		bacula-5.0.3-maxvalue.patch

BuildRequires:		openssl-devel, ncurses-devel, perl, glibc-devel
BuildRequires:		libstdc++-devel, libxml2-devel, zlib-devel
BuildRequires:		mysql-devel, postgresql-devel, sqlite-devel
BuildRequires:		desktop-file-utils, python-devel, lzo-devel, sed
BuildRequires:		libacl-devel, tetex-latex, tetex, ghostscript
BuildRequires:		readline-devel, libcap-devel

BuildRequires:		atk-devel, pango-devel, pkgconfig, wxGTK-devel
BuildRequires:		gtk2-devel, libgnomeui-devel, GConf2-devel, bonobo-activation-devel
BuildRequires:		ORBit2-devel, libbonobo-devel, libbonoboui-devel

%if 0%{?fedora} >= 12 || 0%{?rhel} >= 6
BuildRequires:		qt4-devel >= 4.6.2
%endif

%if 0%{?fedora} >= 7 || 0%{?rhel} >= 6
BuildRequires:		tcp_wrappers-devel
%else
BuildRequires:		tcp_wrappers
%endif

%if 0%{?fedora} >= 9 || 0%{?rhel} >= 6
BuildRequires:		dvipdfm
%endif

%if 0%{?fedora} >= 16 || 0%{?rhel} > 6
BuildRequires:		systemd-units
%endif

%if 0%{?fedora} >= 9 || 0%{?rhel} >= 5
BuildRequires:		latex2html
%endif

%description
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture and is
efficient and relatively easy to use, while offering many advanced
storage management features that make it easy to find and recover lost
or damaged files.


%package director-mysql
Summary:		Bacula Director with MySQL database support
Group:			System Environment/Daemons
Provides:		bacula-director = %{version}-%{release}
Requires:		bacula-director-common = %{version}-%{release}
Requires:		bacula-common = %{version}-%{release}

%description director-mysql
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This package contains the bacula director, the server which controls 
your backup run.
This director has support for the MySQL database.


%package director-sqlite
Summary:		Bacula Director with sqlite database support
Group:			System Environment/Daemons
Provides:		bacula-director = %{version}-%{release}
Requires:		bacula-director-common = %{version}-%{release}
Requires:		bacula-common = %{version}-%{release}

%description director-sqlite
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This package contains the bacula director, the server which controls 
your backup run.
This director has support for the sqlite database.


%package director-postgresql
Summary:		Bacula Director with PostgresSQL database support
Group: 			System Environment/Daemons
Provides:		bacula-director = %{version}-%{release}
Requires:		bacula-director-common = %{version}-%{release}
Requires:		bacula-common = %{version}-%{release}

%description director-postgresql
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This package contains the bacula director, the server which controls 
your backup run.
This director has support for the PostgresSQL database.


%package director-common
Summary:		Common Bacula Director files
Group:			System Environment/Daemons
Requires:		bacula-director = %{version}-%{release}
Requires:		bacula-common = %{version}-%{release}
Requires:		logwatch
Requires(pre):		fedora-usermgmt
Requires(postun):	fedora-usermgmt
%if 0%{?fedora} >= 16 || 0%{?rhel} > 6
Requires(post):		systemd-sysv
Requires(post):		systemd-units
Requires(preun):	systemd-units
Requires(postun):	systemd-units
%else
Requires(post):		/sbin/chkconfig
Requires(preun):	/sbin/chkconfig
Requires(preun):	/sbin/service
Requires(postun):	/sbin/service
%endif

%description director-common
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This package contains the common director files, which are shared 
between all database backends. You have to select a possible
database backend though, which provides the needed bacula-director
dependency. Please choose from bacula-director-mysql,
bacula-director-sqlite or bacula-director-postgresql.


%package client
Summary:		Bacula backup client
Group:			System Environment/Daemons
Requires:		bacula-common = %{version}-%{release}
%if 0%{?fedora} >= 16 || 0%{?rhel} > 6
Requires(post):		systemd-sysv
Requires(post):		systemd-units
Requires(preun):	systemd-units
Requires(postun):	systemd-units
%else
Requires(post):		/sbin/chkconfig
Requires(preun):	/sbin/chkconfig
Requires(preun):	/sbin/service
Requires(postun):	/sbin/service
%endif

%description client
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This package contains the bacula client, the daemon running on the 
system to be backed up.


%package storage-common
Summary:		Common Bacula storage daemon files
Group:			System Environment/Daemons
Requires:		bacula-storage = %{version}-%{release}
Requires:		bacula-common = %{version}-%{release}
%if 0%{?fedora} >= 16 || 0%{?rhel} > 6
Requires(post):		systemd-sysv
Requires(post):		systemd-units
Requires(preun):	systemd-units
Requires(postun):	systemd-units
%else
Requires(post):		/sbin/chkconfig
Requires(preun):	/sbin/chkconfig
Requires(preun):	/sbin/service
Requires(postun):	/sbin/service
%endif

%description storage-common
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This package contains the storage daemon, the daemon responsible for 
writing the data received from the clients onto tape drives or other 
mass storage devices.


%package storage-mysql
Summary:		MySQL Bacula storage daemon files
Group:			System Environment/Daemons
Provides:		bacula-storage = %{version}-%{release}
Requires:		bacula-storage-common = %{version}-%{release}
Requires:		bacula-common = %{version}-%{release}

%description storage-mysql
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This package contains the storage daemon, the daemon responsible for 
writing the data received from the clients onto tape drives or other 
mass storage devices.


%package storage-sqlite
Summary:		SQLite Bacula storage daemon files
Group:			System Environment/Daemons
Provides:		bacula-storage = %{version}-%{release}
Requires:		bacula-storage-common = %{version}-%{release}
Requires:		bacula-common = %{version}-%{release}

%description storage-sqlite
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This package contains the storage daemon, the daemon responsible for 
writing the data received from the clients onto tape drives or other 
mass storage devices.


%package storage-postgresql
Summary:		Common Bacula storage daemon files
Group:			System Environment/Daemons
Provides:		bacula-storage = %{version}-%{release}
Requires:		bacula-storage-common = %{version}-%{release}
Requires:		bacula-common = %{version}-%{release}

%description storage-postgresql
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This package contains the storage daemon, the daemon responsible for 
writing the data received from the clients onto tape drives or other 
mass storage devices.


%package common
Summary:		Common Bacula utilities
Group:			System Environment/Daemons
Requires(pre):		fedora-usermgmt
Obsoletes:		bacula-console-gnome <= 3.0.3

%description common
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.


%package console
Summary:		Bacula management console
Group:			System Environment/Daemons
Requires:		bacula-common = %{version}-%{release}

%description console
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This package contains the command-line management console for the bacula 
backup system.

%if 0%{?fedora} >= 12 || 0%{?rhel} >= 6
%package console-bat
Summary:		Bacula bat console
Group:			System Environment/Daemons
Requires:		bacula-common = %{version}-%{release}
Requires:		usermode

%description console-bat
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This package contains the bat version of the bacula management console
%endif

%package console-wxwidgets
Summary:		Bacula console using the wx widgets toolkit
Group:			System Environment/Daemons
Requires:		bacula-common = %{version}-%{release}
Requires:		usermode

%description console-wxwidgets
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This package contains the wxWidgets version of the bacula management 
console.


%package traymonitor
Summary:		Bacula monitor for the Gnome and KDE system tray
Group:			System Environment/Daemons
Requires:		bacula-common = %{version}-%{release}

%description traymonitor
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This package contains the Gnome- and KDE-compatible tray monitor to 
monitor your bacula server.


%package devel
Summary:		Bacula development files
Group:			Development/Libraries

%description devel
Bacula is a set of programs that allow you to manage the backup,
recovery, and verification of computer data across a network of
different computers. It is based on a client/server architecture.

This development package contains static libraries and header files.


%package -n nagios-plugins-bacula
Summary:		Nagios Plugin - check_bacula
Group:			Applications/System

%description -n nagios-plugins-bacula
Provides check_bacula support for Nagios.


%prep
%setup -q -c -n bacula-%{version}

pushd bacula-%{version}
%patch1 -p1 -b .config
%patch2 -p1 -b .nagios-ent-fd
%patch3 -p1 -b .pamd
%patch4 -p2 -b .openssl
%patch5 -p1 -b .queryfile
%patch6 -p0 -b .python27
%patch7 -p2 -b .log-path
%patch8 -p0 -b .priv
%patch9 -p2 -b .tray-dir
%patch10 -p0 -b .mysql55
%patch11 -p1 -b .maxvalue


# Remove execution permissions from files we're packaging as docs later on
find examples -type f | xargs chmod -x
find updatedb -type f | xargs chmod -x
popd

# Remove cvs left-overs
find -name '.cvsignore' | xargs rm -f 

# Fix perms of c files to silent rpmlint
find -type f -name '*.c' | xargs chmod -x 
find -type f -name '*.h' | xargs chmod -x 

# We are building the source several times, each with a different storage backend
# and all the common files separated so we can also reduce compilation time
# and build graphical consoles where allowed.
mkdir bacula-mysql bacula-postgresql bacula-sqlite bacula-base

%build
# Shell function to configure and build a Bacula tree
build() {
cp -rl ../bacula-%{version}/* .
export CFLAGS="$RPM_OPT_FLAGS -I%{_includedir}/ncurses"
export CPPFLAGS="$RPM_OPT_FLAGS -I%{_includedir}/ncurses"
%configure \
	--sysconfdir=%{_sysconfdir}/bacula \
	--with-basename=bacula \
	--with-dir-user=bacula \
	--with-dir-group=bacula \
	--with-sd-user=bacula \
	--with-sd-group=disk \
	--with-fd-user=root \
	--with-fd-group=root \
	--with-dir-password=@@DIR_PASSWORD@@ \
	--with-fd-password=@@FD_PASSWORD@@ \
	--with-sd-password=@@SD_PASSWORD@@ \
	--with-mon-dir-password=@@MON_DIR_PASSWORD@@ \
	--with-mon-fd-password=@@MON_FD_PASSWORD@@ \
	--with-mon-sd-password=@@MON_SD_PASSWORD@@ \
	--with-working-dir=%{_localstatedir}/spool/bacula \
	--with-scriptdir=%{_libexecdir}/bacula \
	--with-smtp-host=localhost \
	--with-subsys-dir=%{_localstatedir}/lock/subsys \
	--with-pid-dir=%{_localstatedir}/run \
	--with-plugindir=%{_libdir}/bacula \
	--disable-conio \
	--enable-readline \
	--enable-largefile \
	--with-openssl \
	--with-tcp-wrappers \
	--with-python \
	--enable-smartalloc \
	--with-x \
	$*

if test $? != 0; then 
  tail -500 config.log
  : configure failed
  exit 1
fi

# Remove RPATH
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

%{__make} %{?_smp_mflags} NO_ECHO=

}				

# Regen bat QT project file and build tools
pushd bacula-base
	%if 0%{?fedora} >= 12 || 0%{?rhel} >= 6
	export QMAKE=/usr/bin/qmake-qt4
	build \
		--enable-bat \
		--enable-bwx-console \
		--enable-tray-monitor \
		--enable-client-only
	pushd src/qt-console
		/usr/bin/qmake-qt4
		make
	popd
	%else
	build \
		--disable-bat \
		--enable-bwx-console \
		--enable-tray-monitor \
		--enable-client-only
	%endif
	pushd examples/nagios/check_bacula
		CFLAGS="%{optflags}" %{__make} LIBS="-lpthread -ldl -lssl -lcrypto -lz"
	popd
popd

# Build sqlite director
pushd bacula-sqlite
	build \
		--disable-bat \
		--disable-bwx-console \
		--disable-tray-monitor \
		--enable-build-stored \
		--enable-build-dird \
		--enable-batch-insert \
		--with-sqlite3
popd

# Build MySQL director
pushd bacula-mysql
	build \
		--disable-bat \
		--disable-bwx-console \
		--disable-tray-monitor \
		--enable-build-stored \
		--enable-build-dird \
		--enable-batch-insert \
		--with-mysql
popd

# Build PostgreSQL director
pushd bacula-postgresql
	build \
		--disable-bat \
		--disable-bwx-console \
		--disable-tray-monitor \
		--enable-build-stored \
		--enable-build-dird \
		--enable-batch-insert \
		--with-postgresql
popd


%install
rm -rf %{buildroot}

pushd bacula-base
	make install DESTDIR=%{buildroot}

	# install the nagios plugin
	%{__mkdir_p} %{buildroot}%{_libdir}/nagios/plugins
	%{__install} -m0755 examples/nagios/check_bacula/.libs/check_bacula %{buildroot}%{_libdir}/nagios/plugins/

	# Desktop Integration
	mkdir -p %{buildroot}%{_bindir}
	install -m 644 -D scripts/bacula.png %{buildroot}%{_datadir}/pixmaps/bacula.png

	# bwxconsole
	install -m 644 -D src/wx-console/wxwin16x16.xpm %{buildroot}%{_datadir}/pixmaps/wxwin16x16.xpm
	install -m 644 -D scripts/wxconsole.pamd %{buildroot}%{_sysconfdir}/pam.d/bwxconsole
	install -m 644 -D %{SOURCE14} %{buildroot}%{_sysconfdir}/security/console.apps/bwxconsole
	ln -sf consolehelper %{buildroot}%{_bindir}/bwxconsole
	desktop-file-install --vendor="fedora" --dir=%{buildroot}%{_datadir}/applications %{SOURCE10}

	install -m 644 -D src/tray-monitor/generic.xpm %{buildroot}%{_datadir}/pixmaps/bacula-tray-monitor.xpm
	install -m 644 -D scripts/bgnome-console.pamd %{buildroot}%{_sysconfdir}/pam.d/bacula-tray-monitor
	install -m 644 -D %{SOURCE13} %{buildroot}%{_sysconfdir}/security/console.apps/bacula-tray-monitor
	ln -sf consolehelper %{buildroot}%{_bindir}/bacula-tray-monitor
	desktop-file-install --vendor="fedora" --dir=%{buildroot}%{_datadir}/applications %{SOURCE11}

	%if 0%{?fedora} >= 12 || 0%{?rhel} >= 6
	install -m 644 -D src/qt-console/images/bat_icon.png %{buildroot}%{_datadir}/pixmaps/bat_icon.png
	install -m 644 -D scripts/bgnome-console.pamd %{buildroot}%{_sysconfdir}/pam.d/bat
	install -m 644 -D scripts/bat.console_apps %{buildroot}%{_sysconfdir}/security/console.apps/bat
	ln -sf consolehelper %{buildroot}%{_bindir}/bat
	desktop-file-install --vendor="fedora" --dir=%{buildroot}%{_datadir}/applications %{SOURCE12}

	install -m 755 -D src/qt-console/.libs/bat %{buildroot}%{_sbindir}
	install -m 644 -D src/qt-console/bat.conf %{buildroot}%{_sysconfdir}/bacula/bat.conf
	%endif
popd

pushd bacula-sqlite
	make install DESTDIR=%{buildroot}
	mv %{buildroot}%{_sbindir}/bacula-dir  %{buildroot}%{_sbindir}/bacula-dir.sqlite
	mv %{buildroot}%{_sbindir}/dbcheck  %{buildroot}%{_sbindir}/dbcheck.sqlite
	mv %{buildroot}%{_sbindir}/bcopy  %{buildroot}%{_sbindir}/bcopy.sqlite
	mv %{buildroot}%{_sbindir}/bscan  %{buildroot}%{_sbindir}/bscan.sqlite

	for script in create_bacula_database drop_bacula_database drop_bacula_tables \
			grant_bacula_privileges make_bacula_tables make_catalog_backup \
			update_bacula_tables; do
		mv %{buildroot}%{_libexecdir}/bacula/${script} %{buildroot}%{_libexecdir}/bacula/${script}.sqlite
	done
popd

pushd bacula-mysql
	make install DESTDIR=%{buildroot}
	mv %{buildroot}%{_sbindir}/bacula-dir  %{buildroot}%{_sbindir}/bacula-dir.mysql
	mv %{buildroot}%{_sbindir}/dbcheck  %{buildroot}%{_sbindir}/dbcheck.mysql
	mv %{buildroot}%{_sbindir}/bcopy  %{buildroot}%{_sbindir}/bcopy.mysql
	mv %{buildroot}%{_sbindir}/bscan  %{buildroot}%{_sbindir}/bscan.mysql

	for script in create_bacula_database drop_bacula_database drop_bacula_tables \
			grant_bacula_privileges make_bacula_tables make_catalog_backup \
			update_bacula_tables; do
		mv %{buildroot}%{_libexecdir}/bacula/${script} %{buildroot}%{_libexecdir}/bacula/${script}.mysql
	done
popd

pushd bacula-postgresql
	make install DESTDIR=%{buildroot}
	mv %{buildroot}%{_sbindir}/bacula-dir  %{buildroot}%{_sbindir}/bacula-dir.postgresql
	mv %{buildroot}%{_sbindir}/dbcheck  %{buildroot}%{_sbindir}/dbcheck.postgresql
	mv %{buildroot}%{_sbindir}/bcopy  %{buildroot}%{_sbindir}/bcopy.postgresql
	mv %{buildroot}%{_sbindir}/bscan  %{buildroot}%{_sbindir}/bscan.postgresql

	for script in create_bacula_database drop_bacula_database drop_bacula_tables \
			grant_bacula_privileges make_bacula_tables make_catalog_backup \
			update_bacula_tables; do
		mv %{buildroot}%{_libexecdir}/bacula/${script} %{buildroot}%{_libexecdir}/bacula/${script}.postgresql
	done
popd

# Fix some wrapper braindeadness
rm -f %{buildroot}%{_libexecdir}/bacula/bconsole
rm -f %{buildroot}%{_libexecdir}/bacula/gconsole
mv %{buildroot}%{_sbindir}/bwx-console %{buildroot}%{_sbindir}/bwxconsole
mv %{buildroot}%{_sysconfdir}/bacula/bwx-console.conf %{buildroot}%{_sysconfdir}/bacula/bwxconsole.conf

# logrotate
mkdir -p %{buildroot}%{_localstatedir}/log/bacula
install -m 644 -D %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/bacula

# And logwatch
install -m 755 -D bacula-base/scripts/logwatch/bacula %{buildroot}%{_sysconfdir}/logwatch/scripts/services/bacula
install -m 755 -D bacula-base/scripts/logwatch/applybaculadate %{buildroot}%{_sysconfdir}/logwatch/scripts/shared/applybaculadate
install -m 644 -D bacula-base/scripts/logwatch/logfile.bacula.conf %{buildroot}%{_sysconfdir}/logwatch/conf/logfiles/bacula.conf
install -m 644 -D bacula-base/scripts/logwatch/services.bacula.conf %{buildroot}%{_sysconfdir}/logwatch/conf/services/bacula.conf

install -m 755 -D %{SOURCE3} %{buildroot}%{_sbindir}/bacula-checkconf
%if 0%{?fedora} >= 16 || 0%{?rhel} > 6
# Systemd unit files
mkdir -p %{buildroot}%{_unitdir}
install -m 755 -D %{SOURCE7}  %{buildroot}%{_unitdir}/bacula-fd.service
install -m 755 -D %{SOURCE8}  %{buildroot}%{_unitdir}/bacula-dir.service
install -m 755 -D %{SOURCE9}  %{buildroot}%{_unitdir}/bacula-sd.service
%else
# Initscripts
install -m 755 -D %{SOURCE7}  %{buildroot}%{_initrddir}/bacula-fd
install -m 755 -D %{SOURCE8}  %{buildroot}%{_initrddir}/bacula-dir
install -m 755 -D %{SOURCE9}  %{buildroot}%{_initrddir}/bacula-sd
%endif

# Sysconfig
install -m 644 -D %{SOURCE15}  %{buildroot}%{_sysconfdir}/sysconfig/bacula-fd
install -m 644 -D %{SOURCE16}  %{buildroot}%{_sysconfdir}/sysconfig/bacula-dir
install -m 644 -D %{SOURCE17}  %{buildroot}%{_sysconfdir}/sysconfig/bacula-sd

# Wipe backup files from the multiple make install calls
rm -vf %{buildroot}%{_sysconfdir}/bacula/*.{new,old}
rm -vf %{buildroot}%{_libexecdir}/bacula/*.{new,old}

# Create the spooling
mkdir -p %{buildroot}%{_localstatedir}/spool/bacula

# Move some files around
mv %{buildroot}%{_libexecdir}/bacula/query.sql %{buildroot}%{_sysconfdir}/bacula/query.sql

# Nuke the scripts we do not need
rm -vf %{buildroot}%{_libexecdir}/bacula/{bacula,bacula-ctl-*,startmysql,stopmysql} 

# Fix up some perms so rpmlint does not complain too much
chmod 755 %{buildroot}%{_sbindir}/*
chmod 755 %{buildroot}%{_libexecdir}/bacula/*
chmod 644 %{buildroot}%{_libexecdir}/bacula/btraceback.*

# Remove extra docs
rm -rf %{buildroot}%{_datadir}/doc/bacula/

# Install headers
%{__mkdir_p} %{buildroot}%{_includedir}/bacula
pushd %{name}-%{version}
	for dir in src src/cats src/console src/dird src/filed src/findlib src/lib src/plugins/sd src/stored; do
		%{__mkdir_p} %{buildroot}%{_includedir}/bacula/$dir
		%{__install} -m 644 $dir/*.h %{buildroot}%{_includedir}/bacula/$dir
	done
popd


%clean
rm -rf %{buildroot}


%post director-mysql
/usr/sbin/alternatives --install /usr/sbin/bacula-dir bacula-dir /usr/sbin/bacula-dir.mysql 50 \
	--slave /usr/sbin/dbcheck bacula-dbcheck /usr/sbin/dbcheck.mysql \
	--slave /usr/libexec/bacula/create_bacula_database create_bacula_database /usr/libexec/bacula/create_bacula_database.mysql \
	--slave /usr/libexec/bacula/drop_bacula_database drop_bacula_database /usr/libexec/bacula/drop_bacula_database.mysql \
	--slave /usr/libexec/bacula/drop_bacula_tables drop_bacula_tables /usr/libexec/bacula/drop_bacula_tables.mysql \
	--slave /usr/libexec/bacula/grant_bacula_privileges grant_bacula_privileges /usr/libexec/bacula/grant_bacula_privileges.mysql \
	--slave /usr/libexec/bacula/make_bacula_tables make_bacula_tables /usr/libexec/bacula/make_bacula_tables.mysql \
	--slave /usr/libexec/bacula/make_catalog_backup make_catalog_backup /usr/libexec/bacula/make_catalog_backup.mysql \
	--slave /usr/libexec/bacula/update_bacula_tables update_bacula_tables /usr/libexec/bacula/update_bacula_tables.mysql

%post director-sqlite
/usr/sbin/alternatives --install /usr/sbin/bacula-dir bacula-dir /usr/sbin/bacula-dir.sqlite 40 \
	--slave /usr/sbin/dbcheck bacula-dbcheck /usr/sbin/dbcheck.sqlite \
	--slave /usr/libexec/bacula/create_bacula_database create_bacula_database /usr/libexec/bacula/create_bacula_database.sqlite \
	--slave /usr/libexec/bacula/drop_bacula_database drop_bacula_database /usr/libexec/bacula/drop_bacula_database.sqlite \
	--slave /usr/libexec/bacula/drop_bacula_tables drop_bacula_tables /usr/libexec/bacula/drop_bacula_tables.sqlite \
	--slave /usr/libexec/bacula/grant_bacula_privileges grant_bacula_privileges /usr/libexec/bacula/grant_bacula_privileges.sqlite \
	--slave /usr/libexec/bacula/make_bacula_tables make_bacula_tables /usr/libexec/bacula/make_bacula_tables.sqlite \
	--slave /usr/libexec/bacula/make_catalog_backup make_catalog_backup /usr/libexec/bacula/make_catalog_backup.sqlite \
	--slave /usr/libexec/bacula/update_bacula_tables update_bacula_tables /usr/libexec/bacula/update_bacula_tables.sqlite

%post director-postgresql
/usr/sbin/alternatives --install /usr/sbin/bacula-dir bacula-dir /usr/sbin/bacula-dir.postgresql 60 \
	--slave /usr/sbin/dbcheck bacula-dbcheck /usr/sbin/dbcheck.postgresql \
	--slave /usr/libexec/bacula/create_bacula_database create_bacula_database /usr/libexec/bacula/create_bacula_database.postgresql \
	--slave /usr/libexec/bacula/drop_bacula_database drop_bacula_database /usr/libexec/bacula/drop_bacula_database.postgresql \
	--slave /usr/libexec/bacula/drop_bacula_tables drop_bacula_tables /usr/libexec/bacula/drop_bacula_tables.postgresql \
	--slave /usr/libexec/bacula/grant_bacula_privileges grant_bacula_privileges /usr/libexec/bacula/grant_bacula_privileges.postgresql \
	--slave /usr/libexec/bacula/make_bacula_tables make_bacula_tables /usr/libexec/bacula/make_bacula_tables.postgresql \
	--slave /usr/libexec/bacula/make_catalog_backup make_catalog_backup /usr/libexec/bacula/make_catalog_backup.postgresql \
	--slave /usr/libexec/bacula/update_bacula_tables update_bacula_tables /usr/libexec/bacula/update_bacula_tables.postgresql

%preun director-mysql
if [ "$1" = 0 ]; then
	/usr/sbin/alternatives --remove bacula-dir /usr/sbin/bacula-dir.mysql
fi

%preun director-sqlite
if [ "$1" = 0 ]; then
	/usr/sbin/alternatives --remove bacula-dir /usr/sbin/bacula-dir.sqlite
fi

%preun director-postgresql
if [ "$1" = 0 ]; then
	/usr/sbin/alternatives --remove bacula-dir /usr/sbin/bacula-dir.postgresql
fi

%pre common
/usr/sbin/fedora-groupadd 33 -r bacula &>/dev/null || :
*/usr/sbin/fedora-useradd  33 -r -s /sbin/nologin -d /var/spool/bacula -M \
	-c 'Bacula Backup System' -g bacula bacula &>/dev/null || :

%post storage-mysql
/usr/sbin/alternatives --install /usr/sbin/bcopy bacula-sd /usr/sbin/bcopy.mysql 50 \
	--slave /usr/sbin/bscan bacula-bscan /usr/sbin/bscan.mysql 

%post storage-sqlite
/usr/sbin/alternatives --install /usr/sbin/bcopy bacula-sd /usr/sbin/bcopy.sqlite 40 \
	--slave /usr/sbin/bscan bacula-bscan /usr/sbin/bscan.sqlite

%post storage-postgresql
/usr/sbin/alternatives --install /usr/sbin/bcopy bacula-sd /usr/sbin/bcopy.postgresql 60 \
	--slave /usr/sbin/bscan bacula-bscan /usr/sbin/bscan.postgresql

%preun storage-mysql
if [ "$1" = 0 ]; then
	/usr/sbin/alternatives --remove bacula-sd /usr/sbin/bcopy.mysql
fi

%preun storage-sqlite
if [ "$1" = 0 ]; then
	/usr/sbin/alternatives --remove bacula-sd /usr/sbin/bcopy.sqlite
fi

%preun storage-postgresql
if [ "$1" = 0 ]; then
	/usr/sbin/alternatives --remove bacula-sd /usr/sbin/bcopy.postgresql
fi

%if 0%{?fedora} >= 16 || 0%{?rhel} > 6

%post client
if [ $1 -eq 1 ] ; then 
    # Initial installation 
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun client
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable bacula-fd.service > /dev/null 2>&1 || :
    /bin/systemctl stop bacula-fd.service > /dev/null 2>&1 || :
fi

%postun client
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart bacula-fd.service >/dev/null 2>&1 || :
fi

%triggerun client -- bacula-client < 5.0.3-10
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply bacula-fd
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save bacula-fd >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del bacula-fd >/dev/null 2>&1 || :
/bin/systemctl try-restart bacula-fd.service >/dev/null 2>&1 || :

%post director-common
if [ $1 -eq 1 ] ; then 
    # Initial installation 
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun director-common
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable bacula-dir.service > /dev/null 2>&1 || :
    /bin/systemctl stop bacula-dir.service > /dev/null 2>&1 || :
fi

%postun director-common
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart bacula-dir.service >/dev/null 2>&1 || :
fi

%triggerun director-common -- bacula-director-common < 5.0.3-10
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply bacula-dir
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save bacula-dir >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del bacula-dir >/dev/null 2>&1 || :
/bin/systemctl try-restart bacula-dir.service >/dev/null 2>&1 || :

%post storage-common
if [ $1 -eq 1 ] ; then 
    # Initial installation 
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun storage-common
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable bacula-sd.service > /dev/null 2>&1 || :
    /bin/systemctl stop bacula-sd.service > /dev/null 2>&1 || :
fi

%postun storage-common
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart bacula-sd.service >/dev/null 2>&1 || :
fi

%triggerun storage-common -- bacula-storage-common < 5.0.3-10 
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply bacula-sd
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save bacula-sd >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del bacula-sd >/dev/null 2>&1 || :
/bin/systemctl try-restart bacula-sd.service >/dev/null 2>&1 || :

%else

%post client
/sbin/chkconfig --add bacula-fd


%preun client
if [ "$1" = 0 ]; then
	/sbin/service bacula-fd stop >/dev/null 2>&1 || :
	/sbin/chkconfig --del bacula-fd
fi


%postun client
if [ "$1" -ge "1" ]; then
	/sbin/service bacula-fd condrestart >/dev/null 2>&1 || :
fi


%post director-common
/sbin/chkconfig --add bacula-dir


%preun director-common
if [ "$1" = 0 ]; then
	/sbin/service bacula-dir stop >/dev/null 2>&1 || :
	/sbin/chkconfig --del bacula-dir
fi


%postun director-common
if [ "$1" -ge "1" ]; then
	/sbin/service bacula-dir condrestart >/dev/null 2>&1 || :
fi


%post storage-common
/sbin/chkconfig --add bacula-sd


%preun storage-common
if [ "$1" = 0 ]; then
	/sbin/service bacula-sd stop >/dev/null 2>&1 || :
	/sbin/chkconfig --del bacula-sd
fi


%postun storage-common
if [ "$1" -ge "1" ]; then
	/sbin/service bacula-sd condrestart >/dev/null 2>&1 || :
fi

%endif


%files common
%defattr(-,root,root,-)
%doc bacula-%{version}/AUTHORS bacula-%{version}/ChangeLog bacula-%{version}/COPYING bacula-%{version}/LICENSE
%doc bacula-%{version}/README bacula-%{version}/SUPPORT bacula-%{version}/VERIFYING bacula-%{version}/ReleaseNotes
%doc bacula-%{version}/examples/
%config(noreplace) %{_sysconfdir}/logrotate.d/bacula
%dir %{_sysconfdir}/bacula
%dir %{_libexecdir}/bacula
%{_libdir}/libbac-%{version}.so
%{_libdir}/libbac.so
%{_libdir}/libbaccfg-%{version}.so
%{_libdir}/libbaccfg.so
%{_libdir}/libbacfind-%{version}.so
%{_libdir}/libbacfind.so
%{_libdir}/libbacpy-%{version}.so
%{_libdir}/libbacpy.so
%{_libdir}/libbacsql-%{version}.so
%{_libdir}/libbacsql.so
%{_sbindir}/bacula-checkconf
%{_sbindir}/bsmtp
%{_sbindir}/btraceback
%{_sbindir}/bacula
%{_libexecdir}/bacula/bacula_config
%{_libexecdir}/bacula/btraceback.dbx
%{_libexecdir}/bacula/btraceback.gdb
%{_libexecdir}/bacula/btraceback.mdb
%{_libexecdir}/bacula/mtx-changer.conf
%{_mandir}/man1/bsmtp.1*
%{_mandir}/man8/bacula.8*
%{_mandir}/man8/btraceback.8*
%dir %attr(750, bacula, bacula) %{_localstatedir}/log/bacula
%dir %attr(750, bacula, bacula) %{_localstatedir}/spool/bacula


%files client
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/bacula/bacula-fd.conf
%config(noreplace) %{_sysconfdir}/sysconfig/bacula-fd
%{_sbindir}/bacula-fd
%{_libdir}/bacula/bpipe-fd.so
%if 0%{?fedora} >= 16 || 0%{?rhel} > 6
%{_unitdir}/bacula-fd.service
%else
%{_initrddir}/bacula-fd
%endif
%{_mandir}/man8/bacula-fd.8*


%files console
%defattr(-,root,root,-)
%attr(640,root,bacula) %config(noreplace) %{_sysconfdir}/bacula/bconsole.conf
%{_sbindir}/bconsole
%{_mandir}/man8/bconsole.8*


%if 0%{?fedora} >= 12 || 0%{?rhel} >= 6
%files console-bat
%defattr(-,root,root,-)
%config %{_sysconfdir}/security/console.apps/bat
%config %{_sysconfdir}/pam.d/bat
%attr(640,root,bacula) %config(noreplace) %{_sysconfdir}/bacula/bat.conf
%{_bindir}/bat
%{_sbindir}/bat
%{_mandir}/man1/bat.1.gz
%{_datadir}/applications/fedora-bacula-bat.desktop
%{_datadir}/pixmaps/bat_icon.png
%{_datadir}/pixmaps/bacula.png
%endif


%files console-wxwidgets
%defattr(-,root,root,-)
%config %{_sysconfdir}/security/console.apps/bwxconsole
%config %{_sysconfdir}/pam.d/bwxconsole
%attr(640,root,bacula) %config(noreplace) %{_sysconfdir}/bacula/bwxconsole.conf
%{_bindir}/bwxconsole
%{_sbindir}/bwxconsole
%{_mandir}/man1/bacula-bwxconsole.1*
%{_datadir}/applications/fedora-bacula-wxconsole.desktop
%{_datadir}/pixmaps/wxwin16x16.xpm


%files director-common
%defattr(-,root,root,-)
%doc bacula-%{version}/updatedb/
%attr(640,root,bacula) %config(noreplace) %{_sysconfdir}/bacula/bacula-dir.conf
%config(noreplace) %{_sysconfdir}/sysconfig/bacula-dir
%config(noreplace) %{_sysconfdir}/bacula/query.sql
%config %{_sysconfdir}/logwatch/conf/logfiles/bacula.conf
%config %{_sysconfdir}/logwatch/conf/services/bacula.conf
%{_sysconfdir}/logwatch/scripts/services/bacula
%{_sysconfdir}/logwatch/scripts/shared/applybaculadate
%if 0%{?fedora} >= 16 || 0%{?rhel} > 6
%{_unitdir}/bacula-dir.service
%else
%{_initrddir}/bacula-dir
%endif
%{_sbindir}/bregex
%{_sbindir}/bwild
%{_mandir}/man8/dbcheck.8*
%{_mandir}/man8/bacula-dir.8*
%{_libexecdir}/bacula/delete_catalog_backup
%{_libexecdir}/bacula/make_catalog_backup.pl


%files director-mysql
%defattr(-,root,root,-)
%{_sbindir}/bacula-dir.mysql
%{_sbindir}/dbcheck.mysql
%{_libexecdir}/bacula/create_mysql_database
%{_libexecdir}/bacula/drop_mysql_database
%{_libexecdir}/bacula/drop_mysql_tables
%{_libexecdir}/bacula/grant_mysql_privileges
%{_libexecdir}/bacula/make_mysql_tables
%{_libexecdir}/bacula/update_mysql_tables
%{_libexecdir}/bacula/create_bacula_database.mysql
%{_libexecdir}/bacula/drop_bacula_database.mysql
%{_libexecdir}/bacula/drop_bacula_tables.mysql
%{_libexecdir}/bacula/grant_bacula_privileges.mysql
%{_libexecdir}/bacula/make_bacula_tables.mysql
%{_libexecdir}/bacula/make_catalog_backup.mysql
%{_libexecdir}/bacula/update_bacula_tables.mysql


%files director-sqlite
%defattr(-,root,root,-)
%{_sbindir}/bacula-dir.sqlite
%{_sbindir}/dbcheck.sqlite
%{_libexecdir}/bacula/create_sqlite3_database
%{_libexecdir}/bacula/drop_sqlite3_database
%{_libexecdir}/bacula/drop_sqlite3_tables
%{_libexecdir}/bacula/grant_sqlite3_privileges
%{_libexecdir}/bacula/make_sqlite3_tables
%{_libexecdir}/bacula/update_sqlite3_tables
%{_libexecdir}/bacula/create_bacula_database.sqlite
%{_libexecdir}/bacula/drop_bacula_database.sqlite
%{_libexecdir}/bacula/drop_bacula_tables.sqlite
%{_libexecdir}/bacula/grant_bacula_privileges.sqlite
%{_libexecdir}/bacula/make_bacula_tables.sqlite
%{_libexecdir}/bacula/make_catalog_backup.sqlite
%{_libexecdir}/bacula/update_bacula_tables.sqlite


%files director-postgresql
%defattr(-,root,root,-)
%{_sbindir}/bacula-dir.postgresql
%{_sbindir}/dbcheck.postgresql
%{_libexecdir}/bacula/create_postgresql_database
%{_libexecdir}/bacula/drop_postgresql_database
%{_libexecdir}/bacula/drop_postgresql_tables
%{_libexecdir}/bacula/grant_postgresql_privileges
%{_libexecdir}/bacula/make_postgresql_tables
%{_libexecdir}/bacula/update_postgresql_tables
%{_libexecdir}/bacula/create_bacula_database.postgresql
%{_libexecdir}/bacula/drop_bacula_database.postgresql
%{_libexecdir}/bacula/drop_bacula_tables.postgresql
%{_libexecdir}/bacula/grant_bacula_privileges.postgresql
%{_libexecdir}/bacula/make_bacula_tables.postgresql
%{_libexecdir}/bacula/make_catalog_backup.postgresql
%{_libexecdir}/bacula/update_bacula_tables.postgresql


%files storage-common
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/bacula/bacula-sd.conf
%config(noreplace) %{_sysconfdir}/sysconfig/bacula-sd
%if 0%{?fedora} >= 16 || 0%{?rhel} > 6
%{_unitdir}/bacula-sd.service
%else
%{_initrddir}/bacula-sd
%endif
%{_sbindir}/bacula-sd
%{_sbindir}/bextract
%{_sbindir}/bls
%{_sbindir}/btape
%{_libexecdir}/bacula/disk-changer
%{_libexecdir}/bacula/dvd-handler
%{_libexecdir}/bacula/mtx-changer
%{_mandir}/man8/bcopy.8*
%{_mandir}/man8/bextract.8*
%{_mandir}/man8/bls.8*
%{_mandir}/man8/bscan.8*
%{_mandir}/man8/btape.8*
%{_mandir}/man8/bacula-sd.8*


%files storage-mysql
%defattr(-,root,root,-)
%{_sbindir}/bcopy.mysql
%{_sbindir}/bscan.mysql


%files storage-sqlite
%defattr(-,root,root,-)
%{_sbindir}/bcopy.sqlite
%{_sbindir}/bscan.sqlite


%files storage-postgresql
%defattr(-,root,root,-)
%{_sbindir}/bcopy.postgresql
%{_sbindir}/bscan.postgresql


%files traymonitor
%defattr(-,root,root,-)
%attr(640,root,bacula) %config(noreplace) %{_sysconfdir}/bacula/tray-monitor.conf
%config %{_sysconfdir}/security/console.apps/bacula-tray-monitor
%config %{_sysconfdir}/pam.d/bacula-tray-monitor
%{_bindir}/bacula-tray-monitor
%{_sbindir}/bacula-tray-monitor
%{_mandir}/man1/bacula-tray-monitor.1*
%{_datadir}/applications/fedora-bacula-traymonitor.desktop
%{_datadir}/pixmaps/bacula-tray-monitor.xpm


%files devel
%defattr(-,root,root,-)
%{_includedir}/bacula
%{_libdir}/libbac.la
%{_libdir}/libbaccfg.la
%{_libdir}/libbacfind.la
%{_libdir}/libbacpy.la
%{_libdir}/libbacsql.la


%files -n nagios-plugins-bacula
%defattr(-,root,root)
%{_libdir}/nagios/plugins/check_bacula


%changelog
* Wed Jan 11 2012 Simone Caronni <negativo17@gmail.com> - 5.0.3-19
- Add devel subpackage.
- Split off docs subpackage.

* Mon Jan 09 2012 Simone Caronni <negativo17@gmail.com> - 5.0.3-18
- Enable batch insert code.

* Mon Jan 02 2012 Simone Caronni <negativo17@gmail.com> - 5.0.3-17
- Revert to SySV init scripts as packaging policies forbid systemd
  migration if not changing Fedora release; thanks Lukáš.

* Fri Dec 23 2011 Simone Caronni <negativo17@gmail.com> - 5.0.3-16
- Add Nagios plugin.
- Add conditionals for RHEL building (initscripts, bat).
- Enable libtool, bpipe-fd.so plugin and remove dsolink patches.

* Fri Dec 23 2011 Simone Caronni <negativo17@gmail.com> - 5.0.3-15
- Spec file cleanup.
- Fix Buildrequires for RHEL.
- Enable POSIX.1e capabilities.
- Enable LZO compression.
- Enable readline support and tab completion in bconsole.
- Remove SQLite 2 support for RHEL 4.
- Add HTML docs.
- Change SQL query file patch.
- Add back sysconf files and remove redundant user/group in systemd
  service files.
- Move build of common parts around to reduce build time and to prepare
  for nagios-plugins and conditionals for RHEL.

* Thu Dec 22 2011 Lukáš Nykrýn <lnykryn@redhat.com> - 5.0.3-14
- removed duplicity from logrotate file (#755970)

* Thu Nov 3 2011 Lukáš Nykrýn <lnykryn@redhat.com> - 5.0.3-13
- fixed creating of bacula MySQL tables and bump

* Fri Oct  9 2011 Lukáš Nykrýn <lnykryn@redhat.com> - 5.0.3-12
- fixed restart option in service files (#745529)
- fixed creating of bacula MySQL tables (#724894)

* Fri Sep  9 2011 Tom Callaway <spot@fedoraproject.org> - 5.0.3-11
- add missing scriptlets

* Thu Sep  8 2011 Tom Callaway <spot@fedoraproject.org> - 5.0.3-10 
- convert to systemd

* Wed Mar 23 2011 Dan Horák <dan@danny.cz> - 5.0.3-9
- rebuilt for mysql 5.5.10 (soname bump in libmysqlclient)

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.0.3-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 03 2011 Jon Ciesla <limb@jcomserv.net> - 5.0.3-7
- Rebuild for MySQL 5.5, with patch.

* Fri Nov 26 2010 Jan Görig <jgorig@redhat.com> - 5.0.3-6
- Fixed previous fix of alternatives
- Changed initscript return value for non-configured service
- Director address is required in tray-monitor config now (#626490)

* Tue Nov 23 2010 Jan Görig <jgorig@redhat.com> - 5.0.3-5
- Fixed alternatives for dbcheck (#650224)
- Moved director log file to /var/log/bacula/
- Changed permission of bacula-dir.conf (RHEL #651786)
- SQLite database is created as bacula user

* Tue Oct 19 2010 Jan Görig <jgorig@redhat.com> - 5.0.3-4
- Fixed initscripts and changed default group of bacula-sd (#629697)
- Better warning for non-configured password (#556669)

* Wed Sep 29 2010 jkeating - 5.0.3-3
- Rebuilt for gcc bug 634757

* Thu Sep 23 2010 Jan Görig <jgorig@redhat.com> - 5.0.3-2
- fixed openssl patch, thanks to Enrico Scholz

* Tue Aug 10 2010 Jon Ciesla <limb@jcomserv.net> - 5.0.3-1
- New upstream.
- DSOlink fix for same.

* Fri Jul 30 2010 Jon Ciesla <limb@jcomserv.net> - 5.0.2-8
- Patched configure scripts for Python 2.7.

* Fri Jul 30 2010 Jon Ciesla <limb@jcomserv.net> - 5.0.2-7
- Rebuild against Python 2.7.

* Wed Jul 14 2010 Dan Horák <dan@danny.cz> - 5.0.2-6
- rebuilt against wxGTK-2.8.11-2

* Thu Jun 3 2010 Jan Görig <jgorig@redhat.com> 5.0.2-5
- removed no longer needed sysconfig subpackage (#593307]
- build with $RPM_OPT_FLAGS, show compiler commands in build log (#575425)
  fixed by Ville Skyttä
- dropped tcp_wrappers build conditional (#537250)
- fixed location of query.xml in config file (#556480)

* Wed Jun 2 2010 Jan Görig <jgorig@redhat.com> 5.0.2-4
- initscripts improvements
- fixed consolehelper settings and menu entries

* Tue Jun 01 2010 Jon Ciesla <limb@jcomserv.net - 5.0.2-3
- Corrected ssl patch, court. jgorig.

* Wed May 19 2010 Jon Ciesla <limb@jcomserv.net - 5.0.2-2
- Corrected bat build, BZ 593149.
- Corrected ssl patch.

* Thu Apr 29 2010 Jon Ciesla <limb@jcomserv.net - 5.0.2-1
- New upstream, 5.0.2.
- Updated openssl patch.

* Thu Feb 25 2010 Jon Ciesla <limb@jcomserv.net - 5.0.1-1
- New upstream, 5.0.1.

* Mon Jan 25 2010 Jon Ciesla <limb@jcomserv.net - 5.0.0-1
- New upstream, 5.0.0.

* Tue Dec 08 2009 Jon Ciesla <limb@jcomserv.net - 3.0.3-5
- Drop broken postun scriptlet and dep, BZ 545226.

* Thu Dec 03 2009 Jon Ciesla <limb@jcomserv.net - 3.0.3-4
- Fix applybaculadate location.

* Tue Dec 01 2009 Jon Ciesla <limb@jcomserv.net - 3.0.3-3
- Add applybaculadate, BZ 540861.

* Tue Nov 24 2009 Kevin Kofler <Kevin@tigcc.ticalc.org> - 3.0.3-2
- Rebuild for Qt 4.6.0 RC1 in F13 (was built against Beta 1 with unstable ABI)

* Mon Oct 19 2009 Jon Ciesla <limb@jcomserv.net - 3.0.3-1
- New upstream, 3.0.3.

* Sat Aug 22 2009 Tomas Mraz <tmraz@redhat.com> - 3.0.2-4
- rebuilt with new openssl

* Mon Aug 10 2009 Jon Ciesla <limb@jcomserv.net - 3.0.2-3
- Dropped user/group removal per guidelines.
- Added -common dep to traymonitor.

* Thu Jul 30 2009 Jon Ciesla <limb@jcomserv.net - 3.0.2-2
- gnome-console consolehelper correction. BZ 426790.
- add tray-monitor to consolehelper. BZ 426790

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.0.2-1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Jul 21 2009 Jon Ciesla <limb@jcomserv.net - 3.0.2-0
- Update to new upstream, 3.0.2.
- Put full paths in desktop files. BZ 426790.
- Moved console requires from sysconfdir to common BZ 505755.

* Thu Apr 30 2009 Jon Ciesla <limb@jcomserv.net - 3.0.1-1
- Update to new upstream, 3.0.1.

* Tue Apr 21 2009 Jon Ciesla <limb@jcomserv.net - 3.0.0-1
- Update to new upstream, 3.0.0.

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.4.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Jan 23 2009 Jon Ciesla <limb@jcomserv.net - 2.4.4-2
- Rebuild against mysql 5.1.

* Mon Jan 05 2009 Jon Ciesla <limb@jcomserv.net - 2.4.4-1
- Update to new upstream, 2.4.4.
- Dropped orphaned jobs patch, python 2.6 patch, applied upstream.

* Mon Dec 15 2008 Jon Ciesla <limb@jcomserv.net - 2.4.3-7
- Patched to support Python 2.6, BZ 476547.

* Fri Dec 12 2008 Jon Ciesla <limb@jcomserv.net - 2.4.3-6
- Fix consolehelper behaviour for bat.

* Wed Dec 10 2008 Jon Ciesla <limb@jcomserv.net - 2.4.3-5
- Re-diffed fuzzy bacula-director-configuration and bacula-config patches.

* Mon Dec 1 2008 Andreas Thienemann <andreas@bawue.net> - 2.4.3-4
- Fixed dependency "issues" #473627 by adding the sysconfdir subpackage.

* Mon Nov 17 2008 Jon Ciesla <limb@jcomserv.net> - 2.4.3-3
- Added upstream orphaned jobs patch.
- Fixed logrotate file.

* Mon Nov 10 2008 Jon Ciesla <limb@jcomserv.net> - 2.4.3-2
- Added bat.  BZ 470800.

* Wed Oct 22 2008 Jon Ciesla <limb@jcomserv.net> - 2.4.3-1
- Update to 2.4.3.

* Tue Sep 09 2008 Jon Ciesla <limb@jcomserv.net> - 2.4.2-2
- Logrotate fix. BZ 457894.
- Alternatives fix. BZ 458432.

* Thu Jul 31 2008 Jon Ciesla <limb@jcomserv.net> - 2.4.2-1
- Update to 2.4.2.

* Wed Jul 30 2008 Andreas Thienemann <athienem@redhat.com> - 2.2.8-2
- Fixed %%{fedora} comparision, making bacula-sqlite build on rawhide

* Fri Jul 25 2008 Jon Ciesla <limb@jcomserv.net> - 2.2.8-1
- Update to 2.2.8. BZ 446461.
- Dropped director and storage DB-server hard Reqs. BZ 426788.
- .desktop fixes.  BZ 450278, 426789.
- Updated config patch.
- Dropped wxconsole patch, applied upstream.
- Updated pamd patch.
- Dropped ampm patch, applied upstream.
- Dropped maxbyteslist patch, N/A.
- Dropped maxwaittime patch, applied upstream.
- Dropped scheduler-next-hour patch, applied upstream.
- Dropped verify patch, applied upstream.
- Dropped tls-disconnect patch, applied upstream.
- Fix for 426791.
- Introduced patch fuzz workaround, will fix.

* Mon Jul  7 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2.0.3-14
- fix conditional comparison
- fix license tag

* Mon Jan 07 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 2.0.3-13
- add BR: dvipdfm

* Thu Dec 06 2007 Release Engineering <rel-eng at fedoraproject dot org> - 2.0.3-12
 - Rebuild for deps

* Wed Sep 5 2007 Andreas Thienemann <andreas@bawue.net> - 2.0.3-11
- Remove spooldir in client, fixing #251879
- Remove dependency on libtermcap, fixing #251158

* Wed Aug 29 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 2.0.3-10
- Rebuild for selinux ppc32 issue.

* Wed Jul 25 2007 Andreas Thienemann <andreas@bawue.net> 2.0.3-9
- Corrected the %%post alternatives calls. Fixing #249560.

* Wed Jul 19 2007 Andreas Thienemann <andreas@bawue.net> 2.0.3-8
- Moved some files around in the %%files section and refactored
  spec parts a bit
- Fixed up the catalog-backup scripts by including them in the
  alternatives system
- Applied tls patch fixing some tls disconnection issues.

* Thu Jul 18 2007 Andreas Thienemann <andreas@bawue.net> 2.0.3-7
- Minor specchanges, mostly typos in the comments
- Incorporated minor changes from dgilmore's review.

* Fri Jul 13 2007 Andreas Thienemann <andreas@bawue.net> 2.0.3-6
- Fixing %%preun scripts. Thx to Dan for spotting this

* Fri Jul 13 2007 Andreas Thienemann <andreas@bawue.net> 2.0.3-5
- Fixed provides and requires

* Wed Jul 11 2007 Andreas Thienemann <andreas@bawue.net> 2.0.3-4
- Fixed many rpmlint issues

* Thu Apr 26 2007 Andreas Thienemann <andreas@bawue.net> 2.0.3-3
- Final cleanups for fedora
- Removed webgui for now. It will be back in a future release
- Added LANG=C calls to the initscripts

* Thu Apr 26 2007 Andreas Thienemann <andreas@bawue.net> 2.0.3-2
- Added logdir
- Fixed up doc-creation to actually work
- Fixed up web interface
- Included docs sub-package
- Included README et al as docs where appropriate

* Sat Mar 10 2007 Andreas Thienemann <andreas@bawue.net> 2.0.3-1
- Updated to 2.0.3
- Reverted the database-check as we're not sure the db is running on the
  local machine. A later revision might parse the bacula-dir.conf file
  and just connect to the db to see if it's running.

* Sat Feb 28 2007 Andreas Thienemann <andreas@bawue.net> 2.0.2-1
- Further updates on the spec

* Sat Feb 18 2007 Andreas Thienemann <andreas@bawue.net> 2.0.2-1
- Much work on the spec
- Updated to 2.0.2

* Sat Feb 18 2006 Andreas Thienemann <andreas@bawue.net> 1.38.11-1
- Initial spec.
