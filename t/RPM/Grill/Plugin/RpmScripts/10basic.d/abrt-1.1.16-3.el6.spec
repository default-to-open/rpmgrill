%{!?python_site: %define python_site %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(0)")}
# platform-dependent
%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

# please modify the "_buildid" define in a way that identifies
# that the built package isn't the stock distribution package,
# for example, by setting the define to ".local" or ".bz123456"
#
# % define _buildid .local

%if 0%{?_buildid}
%define pkg_release 0.%{?_buildid}%{?dist}
%else
%define pkg_release 3%{?dist}
%endif

Summary: Automatic bug detection and reporting tool
Name: abrt
Version: 1.1.16
Release: %{?pkg_release}
License: GPLv2+
Group: Applications/System
URL: https://fedorahosted.org/abrt/
Source: https://fedorahosted.org/released/%{name}/%{name}-%{version}.tar.gz
Source1: abrt.init
Patch0: abrt-1.1.8-rhel_conf.patch
Patch1: abrt-1.1.8-disable_koopsorg.patch
Patch2: abrt-1.1.7-rhel_keys.patch
Patch3: abrt-1.1.7-hideprefs.patch
Patch4: blacklist.patch
Patch5: disable_di_install.patch
Patch6: rpm_to_c.patch
Patch7: enable_mailx.patch
Patch8: use_component_in_hash.patch
Patch9: rhtsupport_user_agent.c
BuildRequires: dbus-devel
BuildRequires: gtk2-devel
BuildRequires: curl-devel
BuildRequires: rpm-devel >= 4.6
BuildRequires: sqlite-devel > 3.0
BuildRequires: desktop-file-utils
BuildRequires: libnotify-devel
BuildRequires: xmlrpc-c-devel
BuildRequires: xmlrpc-c-client
BuildRequires: file-devel
BuildRequires: python-devel
BuildRequires: gettext
BuildRequires: polkit-devel
BuildRequires: libtar-devel, bzip2-devel, zlib-devel
BuildRequires: intltool
BuildRequires: bison
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires: %{name}-libs = %{version}-%{release}
Requires: abrt-plugin-mailx = %{version}-%{release}
Requires(pre): shadow-utils
Obsoletes: abrt-plugin-sqlite3

%description
%{name} is a tool to help users to detect defects in applications and
to create a bug report with all informations needed by maintainer to fix it.
It uses plugin system to extend its functionality.

%package libs
Summary: Libraries for %{name}
Group: System Environment/Libraries

%description libs
Libraries for %{name}.

%package devel
Summary: Development libraries for %{name}
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}

%description devel
Development libraries and headers for %{name}.

%package gui
Summary: %{name}'s gui
Group: User Interface/Desktops
Requires: %{name} = %{version}-%{release}
Requires: dbus-python, pygtk2, pygtk2-libglade,
Requires: gnome-python2-gnomevfs, gnome-python2-gnomekeyring
# only if gtk2 version < 2.17:
#Requires: python-sexy
# we used to have abrt-applet, now abrt-gui includes it:
Provides: abrt-applet = %{version}-%{release}
Obsoletes: abrt-applet < 0.0.5
Conflicts: abrt-applet < 0.0.5

%description gui
GTK+ wizard for convenient bug reporting.

%package addon-ccpp
Summary: %{name}'s C/C++ addon
Group: System Environment/Libraries
Requires: elfutils
Requires: yum-utils
Requires: %{name} = %{version}-%{release}

%description addon-ccpp
This package contains hook for C/C++ crashed programs and %{name}'s C/C++
analyzer plugin.

%package addon-kerneloops
Summary: %{name}'s kerneloops addon
Group: System Environment/Libraries
Requires: curl
Requires: %{name} = %{version}-%{release}
Obsoletes: kerneloops
Obsoletes: abrt-plugin-kerneloops
Obsoletes: abrt-plugin-kerneloopsreporter

%description addon-kerneloops
This package contains plugin for collecting kernel crash information
and reporter plugin which sends this information to specified server,
usually to kerneloops.org.

%package plugin-logger
Summary: %{name}'s logger reporter plugin
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}

%description plugin-logger
The simple reporter plugin which writes a report to a specified file.

%package plugin-mailx
Summary: %{name}'s mailx reporter plugin
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}
Requires: mailx

%description plugin-mailx
The simple reporter plugin which sends a report via mailx to a specified
email address.

%package plugin-runapp
Summary: %{name}'s runapp plugin
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}

%description plugin-runapp
Plugin to run external programs.

%package plugin-sosreport
Summary: %{name}'s sosreport plugin
Group: System Environment/Libraries
Requires: sos
Requires: %{name} = %{version}-%{release}

%description plugin-sosreport
Plugin to include an sosreport in an abrt report.

%package plugin-bugzilla
Summary: %{name}'s bugzilla plugin
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}

%description plugin-bugzilla
Plugin to report bugs into the bugzilla.

%package plugin-rhtsupport
Summary: %{name}'s RHTSupport plugin
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}
Obsoletes: abrt-plugin-catcut
Obsoletes: abrt-plugin-rhfastcheck
Obsoletes: abrt-plugin-rhticket

%description plugin-rhtsupport
Plugin to report bugs into RH support system.

%package plugin-reportuploader
Summary: %{name}'s reportuploader plugin
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}
Obsoletes: abrt-plugin-ticketuploader

%description plugin-reportuploader
Plugin to report bugs into anonymous FTP site associated with ticketing system.

%package plugin-filetransfer
Summary: %{name}'s File Transfer plugin
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}

%description plugin-filetransfer
Plugin to uploading files to a server.

%package addon-python
Summary: %{name}'s addon for catching and analyzing Python exceptions
Group: System Environment/Libraries
Requires: %{name} = %{version}-%{release}

%description addon-python
This package contains python hook and python analyzer plugin for handling
uncaught exception in python programs.

%package cli
Summary: %{name}'s command line interface
Group: User Interface/Desktops
Requires: %{name} = %{version}-%{release}
# analyzers
Requires: %{name}-addon-kerneloops
Requires: %{name}-addon-ccpp, %{name}-addon-python
# reporters
Requires: %{name}-plugin-logger, %{name}-plugin-rhtsupport
# action
Requires: %{name}-plugin-sosreport


%description cli
This package contains simple command line client for controlling abrt daemon over
the sockets.

%package desktop
Summary: Virtual package to install all necessary packages for usage from desktop environment
Group: User Interface/Desktops
# This package gets installed when anything requests bug-buddy -
# happens when users upgrade Fn to Fn+1;
# or if user just wants "typical desktop installation".
# Installing abrt-desktop should result in the abrt which works without
# any tweaking in abrt.conf (IOW: all plugins mentioned there must be installed)
Requires: %{name} = %{version}-%{release}
Requires: %{name}-addon-kerneloops
Requires: %{name}-addon-ccpp, %{name}-addon-python
# Default config of addon-ccpp requires gdb
Requires: gdb >= 7.0-3
Requires: %{name}-gui
Requires: %{name}-plugin-logger, %{name}-plugin-sosreport
Requires: %{name}-plugin-rhtsupport
Obsoletes: bug-buddy
Provides: bug-buddy

%description desktop
Virtual package to make easy default installation on desktop environments.

%prep
%setup -q
#rhel specific patches, DO NOT REMOVE!
%patch0 -p1 -b .rhel_defaults
%patch1 -p1 -b .rhel_disable_kooporg
%patch2 -p1 -b .rhel_gpg_keys
%patch5 -p1 -b .disable_di_install
%patch7 -p1 -b .enable_mailx
#Fedora/rhel patch
%patch3 -p1 -b .hideprefs
%patch4 -p1 -b .blacklist
# general patches
%patch6 -p1 -b .rpm_to_c
%patch8 -p1 -b .hash
%patch9 -p1 -b .user_agent

%build
# disable systemd otherwise the build fails on unpacked files
%configure --with-systemdsystemunitdir=""
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
CFLAGS="-fno-strict-aliasing"
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT mandir=%{_mandir}
%find_lang %{name}

#rm -rf $RPM_BUILD_ROOT/%{_libdir}/lib*.la
#rm -rf $RPM_BUILD_ROOT/%{_libdir}/%{name}/lib*.la
# remove all .la and .a files
find $RPM_BUILD_ROOT -name '*.la' -or -name '*.a' | xargs rm -f
mkdir -p ${RPM_BUILD_ROOT}/%{_initrddir}
install -m 755 %SOURCE1 ${RPM_BUILD_ROOT}/%{_initrddir}/abrtd
# /var/cache/%{name} is to be removed in 1.3.x timeframe
mkdir -p $RPM_BUILD_ROOT/var/cache/%{name}
mkdir -p $RPM_BUILD_ROOT/var/cache/%{name}-di
mkdir -p $RPM_BUILD_ROOT/var/run/%{name}
mkdir -p $RPM_BUILD_ROOT/var/spool/%{name}
mkdir -p $RPM_BUILD_ROOT/var/spool/%{name}-upload

desktop-file-install \
        --dir ${RPM_BUILD_ROOT}%{_datadir}/applications \
        --vendor redhat \
        --delete-original \
        ${RPM_BUILD_ROOT}%{_datadir}/applications/%{name}.desktop

desktop-file-install \
        --dir ${RPM_BUILD_ROOT}%{_sysconfdir}/xdg/autostart \
        src/Applet/%{name}-applet.desktop

%clean
rm -rf $RPM_BUILD_ROOT

%pre
#uidgid pair 173:173 reserved in setup rhbz#670231
%define abrt_gid_uid 173
getent group abrt >/dev/null || groupadd -f -g %{abrt_gid_uid} --system abrt
getent passwd abrt >/dev/null || useradd --system -g abrt -u %{abrt_gid_uid} -d /etc/abrt -s /sbin/nologin abrt
exit 0

%post
/sbin/chkconfig --add %{name}d

%post gui
# update icon cache
touch --no-create %{_datadir}/icons/hicolor || :
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%post libs -p /sbin/ldconfig

%preun
if [ "$1" -eq "0" ] ; then
  service %{name}d stop >/dev/null 2>&1
  /sbin/chkconfig --del %{name}d
fi

%postun libs -p /sbin/ldconfig

%postun gui
touch --no-create %{_datadir}/icons/hicolor || :
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%posttrans
if [ "$1" -eq "0" ]; then
    service %{name}d condrestart >/dev/null 2>&1 || :
fi

%files -f %{name}.lang
%defattr(-,root,root,-)
%doc README COPYING
%{_sbindir}/%{name}d
%{_bindir}/%{name}-debuginfo-install
%{_bindir}/%{name}-handle-upload
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/%{name}/gpg_keys
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/dbus-%{name}.conf
%{_initrddir}/%{name}d
# /var/cache/%{name} is to be removed in 1.3.x timeframe
%dir %attr(0755, abrt, abrt) %{_localstatedir}/cache/%{name}
%dir %attr(0755, abrt, abrt) %{_localstatedir}/spool/%{name}
%dir %attr(0700, abrt, abrt) %{_localstatedir}/spool/%{name}-upload
%dir /var/run/%{name}
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/plugins
%dir %{_libdir}/%{name}
%{_mandir}/man8/abrtd.8.gz
%{_mandir}/man5/%{name}.conf.5.gz
%{_mandir}/man7/%{name}-plugins.7.gz
%{_datadir}/polkit-1/actions/org.fedoraproject.abrt.policy
%{_datadir}/dbus-1/system-services/com.redhat.abrt.service
%config(noreplace) %{_sysconfdir}/%{name}/plugins/SQLite3.conf
%{_libdir}/%{name}/libSQLite3.so*
%{_mandir}/man7/%{name}-SQLite3.7.gz

%files libs
%defattr(-,root,root,-)
%{_libdir}/lib*.so.*

%files devel
%defattr(-,root,root,-)
%{_includedir}/*
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/*

%files gui
%defattr(-,root,root,-)
%{_bindir}/%{name}-gui
%dir %{_datadir}/%{name}
# all glade, gtkbuilder and py files for gui
%{_datadir}/%{name}/*.py*
%{_datadir}/%{name}/*.glade
%{_datadir}/applications/redhat-%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/*
%{_datadir}/icons/hicolor/*/status/*
%{_datadir}/%{name}/icons/hicolor/*/status/*
%{_bindir}/%{name}-applet
%{_sysconfdir}/xdg/autostart/%{name}-applet.desktop

%files addon-ccpp
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/plugins/CCpp.conf
%dir %{_localstatedir}/cache/%{name}-di
%{_libdir}/%{name}/libCCpp.so*
%{_libexecdir}/abrt-hook-ccpp

%files addon-kerneloops
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/plugins/Kerneloops.conf
%{_bindir}/dumpoops
%{_libdir}/%{name}/libKerneloops.so*
%{_libdir}/%{name}/libKerneloopsScanner.so*
%{_mandir}/man7/%{name}-KerneloopsScanner.7.gz

%files plugin-logger
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/plugins/Logger.conf
%{_libdir}/%{name}/libLogger.so*
%{_libdir}/%{name}/Logger.glade
%{_mandir}/man7/%{name}-Logger.7.gz

%files plugin-mailx
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/plugins/Mailx.conf
%{_libdir}/%{name}/libMailx.so*
%{_libdir}/%{name}/Mailx.glade
%{_mandir}/man7/%{name}-Mailx.7.gz

%files plugin-runapp
%defattr(-,root,root,-)
%{_libdir}/%{name}/libRunApp.so*
%{_mandir}/man7/%{name}-RunApp.7.gz

%files plugin-sosreport
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/plugins/SOSreport.conf
%{_libdir}/%{name}/libSOSreport.so*


%files plugin-bugzilla
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/plugins/Bugzilla.conf
%{_libdir}/%{name}/libBugzilla.so*
%{_libdir}/%{name}/Bugzilla.glade
%{_mandir}/man7/%{name}-Bugzilla.7.gz

%files plugin-rhtsupport
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/plugins/RHTSupport.conf
%{_libdir}/%{name}/libRHTSupport.so*
%{_libdir}/%{name}/RHTSupport.glade

%files plugin-reportuploader
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/plugins/ReportUploader.conf
%{_libdir}/%{name}/libReportUploader.so*
%{_libdir}/%{name}/ReportUploader.glade
%{_mandir}/man7/%{name}-ReportUploader.7.gz

%files plugin-filetransfer
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/plugins/FileTransfer.conf
%{_libdir}/%{name}/libFileTransfer.so*
%{_mandir}/man7/%{name}-FileTransfer.7.gz

%files addon-python
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/%{name}/plugins/Python.conf
%{_libdir}/%{name}/libPython.so*
%{python_site}/*.py*
%{python_site}/abrt.pth


%files cli
%defattr(-,root,root,-)
%{_bindir}/abrt-cli
%{_mandir}/man1/abrt-cli.1.gz
%{_sysconfdir}/bash_completion.d/abrt-cli.bash

%files desktop
%defattr(-,root,root,-)

%changelog
* Thu Apr 07 2011 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.16-3
- improved support for GSS customer portal
  - fixed the hash generating: use component name instead of package NVR
  - added a user-agent header to rhtsupport requests for easier hash algorithm
    matching
- Resolves: #694410

* Fri Mar 11 2011 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.16-2
- enabled mailx as a crash notify
- Resolves: #678724

* Fri Feb 04 2011 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.16-1
- added list of attachments to comment rhbz#668875
- stop consuming non-standard header rhbz#670492
- Resolves: #670492, #668875

* Tue Jan 18 2011 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.15-2
- add a gui/uid to useradd/groupadd command (reserved in setup rhbz#670231)
- Resolves: #650975

* Mon Jan 10 2011 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.15-1
- removed unused files (jmoskovc@redhat.com)
- update po files (jmoskovc@redhat.com)
- removed some unused files (jmoskovc@redhat.com)
- pass old pattern to ccpp hook and use it (dvlasenk@redhat.com)
- GUI: added warning when gnome-keyring can't be accessed rhbz#576866 (jmoskovc@redhat.com)
- 666893 - Unable to make sense of XML-RPC response from server (npajkovs@redhat.com)
- PyHook: ignore SystemExit exception rhbz#636913 (jmoskovc@redhat.com)
- 665405 - ABRT's usage of sos does not grab /var/log/messages (npajkovs@redhat.com)
- add a note in report if kernel is tainted (npajkovs@redhat.com)
- KerneloopsScanner.cpp: make a room for NULL byte (npajkovs@redhat.com)
- fix multicharacter warring (npajkovs@redhat.com)
- open help page instead of about rhbz#666267
- Resolves: #665405, #576866, #649309, #623142, #614486, #650975, #666267

* Mon Jan 10 2011 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.14-1
- updated po files (jmoskovc@redhat.com)
- GUI: make how to mandatory (jmoskovc@redhat.com)
- silent rules (npajkovs@redhat.com)
- fixed segv in abrt-hook-ccpp rhbz#652338 (jmoskovc@redhat.com)
- rhbz 623142 (npajkovs@redhat.com)
- GUI: make the "install debuginfo" hint selectable rhbz#644343 (jmoskovc@redhat.com)
- GUI: wrap howto and comments rhbz#625237 (jmoskovc@redhat.com)
- GUI: show horizontal scrollbar when needed (jmoskovc@redhat.com)
- GUI: wrap lines in the backtrace window rhbz#625232 (jmoskovc@redhat.com)
- GUI: changed '*' to '•' rhbz#625236 (jmoskovc@redhat.com)
- rm abrt_test.py (jmoskovc@redhat.com)
- added utf-8 coding tag into .py files (jmoskovc@redhat.com)
- GUI: show the scrollbar in summary only when needed (jmoskovc@redhat.com)
- GUI: added accelerator key "Delete" to the delete button rrakus@redhat.com (jmoskovc@redhat.com)
- backtrace rating check in abrt-cli (mtoman@redhat.com)
- Localization of [y/n] response in abrt-cli (kklic@redhat.com)
- abrt-cli --info: Make coredump and rating fields optional (kklic@redhat.com)
- GUI: increase dbus timeout in Report() call (vda.linux@googlemail.com)
- GUI: make the bt viewer not-editable rhbz#621871 (jmoskovc@redhat.com)
- increased version to 1.1.14 (jmoskovc@redhat.com)
- new bt parser (kklic) (jmoskovc@redhat.com)
- disable polkit (jmoskovc@redhat.com)
- add example of tainted kernel module (npajkovs@redhat.com)

* Thu Aug 26 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.13-4
- fixed typo kenel->kernel rhbz#627580
- Resovles: #627580

* Wed Aug 25 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.13-3
- fixed problem with redirection (http response 30x) rhbz#613164
- Resolves: #613164

* Wed Aug 18 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.13-2
- increased timeout in gui to prevent timeouts when uploading large files
- added update messages during upload
- Resolves: #625012

* Mon Aug 09 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.13-1
- updated translations rhbz#619340
- removed dependency on libzip
- added libxml-2.0 into configure (npajkovs@redhat.com)
- fixed typo in man page rhbz#610748 (jmoskovc@redhat.com)
- RHTSupport: GUI's SSLVerify checkbox had one missing bit of code (vda.linux@googlemail.com)
- Resolves: rhbz#619340

* Wed Jul 28 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.12-2
- minor fix to rhtsupport plugin
- Resolves: rhbz#612548

* Wed Jul 28 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.12-1
- updated translations
- made some more strings translatable rhbz#574693
- fixed SIGABRT in dumpoops rhbz#612548 (dvlasenk@redhat.com)
- moved abrtd.lock and abrt.socket to /var/run/abrt
- disabled debuginfo install
- Resolves: #612548, #574693

* Tue Jul 27 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.10-3
- blacklisted mono-core and /usr/bin/nspluginviewer

* Wed Jul 21 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.10-2
- enabled GPG check rhbz#609404
- made RHTSupport the default reporter instead of bugzilla rhbz#603056
- Resolves: #603056, #609404

* Wed Jul 14 2010 Karel Klic <kklic@redhat.com> 1.1.10-1
- a bugfix release
- die with an error message if the database plugin is not accessible when needed (kklic@redhat.com)
- change RHTSupport URL protocol from HTTP to HTTPS (dvlasenk@redhat.com)
- the Logger plugin returns a message as the result of Report() call instead of a file URL (kklic@redhat.com)
- Cut off prelink suffixes from executable name if any (mtoman@redhat.com)
- CCpp: abrt-debuginfo-install output lines can be long, accomodate them (dvlasenk@redhat.com)
- do not pop up message on crash if the same crash is the same (dvlasenk@redhat.com)
- Resolves: #612997, #612838, #611145

* Tue Jul 13 2010 Karel Klic <kklic@redhat.com> 1.1.9-1
- a bugfix release
- fedora bugs do not depend on rhel bugs (npajkovs@redhat.com)
- GUI: fixed problem with no gkeyring and just one reporter enabled rhbz#612457 (jmoskovc@redhat.com)
- added a document about interpreted language integration (kklic@redhat.com)
- moved devel header files to inc/ and included them in -devel package (jmoskovc@redhat.com, npajkovs@redhat.com)
- renamed abrt-utils.pc to abrt.pc (jmoskovc@redhat.com)
- string updates based on a UI text review (kklic@redhat.com)
- rhtsupport obsoletes the old rh plugins (jmoskovc@redhat.com)
- list allowed items in RHTSupport.conf (kklic@redhat.com)
- GUI: fixed package name in warning message when the packge is kernel rhbz#612191 (jmoskovc@redhat.com)
- remove rating for python crashes (jmoskovc@redhat.com)
- CCpp: give zero rating to an empty backtrace (jmoskovc@redhat.com)
- GUI: allow sending crashes without rating (jmoskovc@redhat.com)
- RHTSupport: set default URL to api.access.redhat.com/rs (dvlasenk@redhat.com)
- abort initialization on abrt.conf parsing errors (dvlasenk@redhat.com)
- changing NoSSLVerify to SSLVerify in bugzilla plugin (mtoman@redhat.com)
- Resolves: #612874, #612191, #612186, #612404, #568747

* Wed Jun 30 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.8-2
- added rating to python crashes
- Resolves: #607684

* Wed Jun 30 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.8-1
- show hostname in cli (kklic@redhat.com)
- disable the GPG check until GA
- updated po files (jmoskovc@redhat.com)
- added support for package specific actions rhbz#606917 (jmoskovc@redhat.com)
- renamed TicketUploader to ReportUploader (jmoskovc@redhat.com)
- bad hostnames on remote crashes (npajkovs@redhat.com)
- unlimited MaxCrashReportsSize (npajkovs@redhat.com)
- abrt_rh_support: improve error messages rhbz#608698 (vda.linux@googlemail.com)
- Added BacktraceRemotes option. (kklic@redhat.com)
- Allow remote crashes to not to belong to a package. Skip GPG check on remote crashes. (kklic@redhat.com)
- remove obsolete Catcut and rhfastcheck reporters (vda.linux@googlemail.com)
- make rhel bug point to correct place rhbz#578397 (npajkovs@redhat.com)
- Show comment and how to reproduce fields when reporing crashes in abrt-cli (kklic@redhat.com)
- Bash completion update (kklic@redhat.com)
- Rename --get-list to --list (kklic@redhat.com)
- Update man page (kklic@redhat.com)
- Options overhaul (kklic@redhat.com)
- Resolves: #607684, #608693, #608698, #578397

* Wed Jun 23 2010 Denys Vlasenko <dvlasenk@redhat.com> 1.1.7-2
- abrt should not point to Fedora bugs but create new RHEL bug instead (npajkovs@redhat.com)
- Resolves: #578397

* Wed Jun 23 2010 Denys Vlasenko <dvlasenk@redhat.com> 1.1.7-1
- Don't show global uuid in report (npajkovs@redhat.com)
- GUI: don't try to use action plugins as reporters (jmoskovc@redhat.com)
- Added WatchCrashdumpArchiveDir directive to abrt.conf and related code (vda.linux@googlemail.com)
- GUI: don't show the placehondler icon rhbz#605693 (jmoskovc@redhat.com)
- Make "Loaded foo.conf" message less confusing (vda.linux@googlemail.com)
- Fixed a flaw in strbuf_prepend_str (kklic@redhat.com)
- TicketUploader: do not add '\n' to text files in crashdump (vda.linux@googlemail.com)
- Resolves: #604706, #604088, #590698

* Wed Jun 16 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.6-1
- updated translation
- GUI: skip the plugin selection, if it's not needed (jmoskovc@redhat.com)
- Check conf file for syntax errors (kklic@redhat.com)
- move misplaced sanity checks in cron parser (vda.linux@googlemail.com)
- GUI: don't require the rating for all reporters (jmoskovc@redhat.com)
- GUI: fixed exception when there is no configure dialog for plugin rhbz#603745 (jmoskovc@redhat.com)
- Add a GUI config dialog for RHTSupport plugin (vda.linux@googlemail.com)
- abrt_curl: fix a problem with incorrect content-length on 32-bit arches (vda.linux@googlemail.com)
- sosreport: save the dump directly to crashdump directory (vda.linux@googlemail.com)
- plugin rename: rhticket -> RHTSupport (vda.linux@googlemail.com)
- Daemon socket for reporting crashes (karel@localhost.localdomain)
- GUI: fixed few typos (jmoskovc@redhat.com)
- Resolves: #604085, #568747

* Wed Jun 09 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.5-1
- GUI: polished the reporter assistant (jmoskovc@redhat.com)
- Logger reporter: do not store useless info (vda.linux@googlemail.com)
- ccpp hook: add SaveBinaryImage option which saves of the crashed binary (vda.linux@googlemail.com)
- SPEC: added CFLAGS="-fno-strict-aliasing" to fix the rpmdiff warnings rhbz#599364 (jmoskovc@redhat.com)
- GUI: don't remove user comments when re-reporting the bug rhbz#601779 (jmoskovc@redhat.com)
- remove "(deleted)" from executable path rhbz#593037 (jmoskovc@redhat.com)
- CCpp analyzer: add 60 sec cap on gdb run time. (vda.linux@googlemail.com)
- add new file *hostname* into debugdump directory (npajkovs@redhat.com)
- rhticket: upload real tarball, not a bogus file (vda.linux@googlemail.com)
- abrt-hook-ccpp: eliminate race between process exit and compat coredump creation rhbz#584554 (vda.linux@googlemail.com)
- rhticket: actually do create ticket, using Gavin's lib code (vda.linux@googlemail.com)
- properly obsolete gnome-python2-bugbuddy rhbz#579748 (jmoskovc@redhat.com)
- GUI: remember comment and howto on backtrace refresh rhbz#545690 (jmoskovc@redhat.com)
- use header case in button label rhbz#565812 (jmoskovc@redhat.com)
- make log window resizable (vda.linux@googlemail.com)
- rename a few remaining /var/cache/abrt -> /var/spool/abrt (vda.linux@googlemail.com)
- suppress misleading "crash 'XXXXXXXX' is not in database" messages rhbz#591843
- fixed race in creating user coredump rhbz#584554
- fixed few grammar errors rhbz#601785
- Resolves: rhbz#591843, rhbz#584554

* Fri Jun 04 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.4-2
- added CFLAGS="-fno-strict-aliasing"
- Resolves: rhbz#599364

* Wed May 26 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.4-1
- added reporting wizard partialy fixes rhbz#572379 (jmoskovc@redhat.com)
- fixed few leaked fds - selinux is happy now (vda.linux@googlemail.com)
- fixed kerneloops --- cut here --- problem rhbz#592152 (vda.linux@googlemail.com)
- updated translations
- Resolves: #572379

* Fri May 24 2010 Denys Vlasenko <dvlasenk@redhat.com> 1.1.3-1
- More fixes for /var/cache/abrt -> /var/spool/abrt conversion
- Resolves: #594688

* Thu May 20 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.2-3
- updated init script rhbz#594412

* Thu May 20 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.2-2
- added /var/spool to spec rhbz#593906
- Resolves: #574693

* Wed May 19 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.2-1
- updated translation rhbz#574693
- obsolete gnome-python2-bugbuddy rhbz#579748 (jmoskovc@redhat.com)
- Report "INFO: possible recursive locking detected rhbz#582378 (vda.linux@googlemail.com)
- kill yumdownloader if abrt-debuginfo-install is terminated mid-flight (vda.linux@googlemail.com)
- do not create Python dumps if argv[0] is not absolute (vda.linux@googlemail.com)
- improve kerneloops hash (vda.linux@googlemail.com)
- Move /var/cache/abrt to /var/spool/abrt. rhbz#568101. (vda.linux@googlemail.com)
- bugzilla: better summary and decription messages (npajkovs@redhat.com)
- renamed daemon pid and lock file rhbz#588315 (jmoskovc@redhat.com)
- Move hooklib from src/Hooks to lib/Utils (kklic@redhat.com)

* Wed May 12 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.1-1
- updated translations
- removed avant-window-navigator from blacklist (jmoskovc@redhat.com)
- Abort debuginfo download if low on disk space (partially addresses #564451) (vda.linux@googlemail.com)
- fix bug 588945 - sparse core files performance hit (vda.linux@googlemail.com)
- Add BlackListedPaths option to abrt.conf. Fixes #582421 (vda.linux@googlemail.com)
- Do not die when /var/cache/abrt/*/uid does not contain a number (rhbz#580899) (kklic@redhat.com)
- rid of rewriting config in /etc/abrt/abrt.conf (npajkovs@redhat.com)
- fix bug 571411: backtrace attachment of the form /var/cache/abrt/foo-12345-67890/backtrace (vda.linux@googlemail.com)
- Do not echo password to terminal in abrt-cli (kklic@redhat.com)
- Resolves: #591504

* Wed May 05 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.1.0-1
- updated translations
- fixed backtrace attaching rhbz#571411 (vda.linux@googlemail.com)
- fixed abrt-debuginfo-install rhbz#579038 (vda.linux@googlemail.com)
- don't echo password in cli rhbz#587283 (kklic@redhat.com)
- updated icons rhbz#587698 (jmoskovc@redhat.com)
- Show error message when abrtd service is run as non-root. rhbz#584352 (kklic@redhat.com)
- Crash function is now detected even for threads without an abort frame (kklic@redhat.com)
- do not catch perl/python crashes when the script is not of known package origin (kklic@redhat.com)
- comment can be private (npajkovs@redhat.com)
- kerneloop is more informative when failed (npajkovs@redhat.com)
- add function name into summary(if it's found) (npajkovs@redhat.com)
- Change kerneloops message when it fails to send the report (npajkovs@redhat.com)
- Resolves: #579038

* Wed Apr 28 2010 Jiri Moskovcak <jmoskovc@redhat.com> 1.0.9-1
- update to the latest stable upstream
- fixed problem with localized yum messages rhbz#581804
- better bugzilla summary (napjkovs@redhat.com)
- ignore interpreter (py,perl) crashes caused by unpackaged scripts (kklic@redhat.com)
- hooklib: fix excessive rounding down in free space calculation (bz#575644) (vda.linux@googlemail.com)
- gui: fix 551989 "crash detected in abrt-gui-1.0.0-1.fc12" and such (vda.linux@googlemail.com)
- trivial: fix 566806 "abrt-gui sometimes can't be closed" (vda.linux@googlemail.com)
- gui: fix the last case where gnome-keyring's find_items_sync() may throw DeniedError (vda.linux@googlemail.com)
- updated translation
- minor fix to sosreport to make it work with latest sos rhbz#576861 (jmoskovc@redhat.com)
- GUI: total rewrite based on design from Mairin Duffy (jmoskovc@redhat.com)
- trivial: better HTTP/curl error reporting (vda.linux@googlemail.com)
- Use backtrace parser from abrtutils, new backtrace rating algorithm, store crash function if it's known (kklic@redhat.com)
- PYHOOK: don't use sitecustomize.py rhbz#539497 (jmoskovc@redhat.com)
- rhfastcheck: a new reporter plugin based on Gavin's work (vda.linux@googlemail.com)
- rhticket: new reporter plugin (vda.linux@googlemail.com)
- Kerneloops: use 1st line of oops as REASON. Closes rhbz#574196. (vda.linux@googlemail.com)
- Kerneloops: fix a case when we file an oops w/o backtrace (vda.linux@googlemail.com)
- minor fix in abrt-debuginfo-install to make it work with yum >= 3.2.26 (jmoskovc@redhat.com)
- GUI: added action to applet to directly report last crash (jmoskovc@redhat.com)
- Never flag backtrace as binary file (fixes problem observed in bz#571411) (vda.linux@googlemail.com)
- improve syslog file detection. closes bz#565983 (vda.linux@googlemail.com)
- add arch, package and release in comment (npajkovs@redhat.com)
- add ProcessUnpackaged option to abrt.conf (vda.linux@googlemail.com)
- abrt-debuginfo-install: use -debuginfo repos which match enabled "usual" repos (vda.linux@googlemail.com)
- fix format security error (fcrozat@mandriva.com)
- icons repackaging (jmoskovc@redhat.com)
- partial fix for bz#565983 (vda.linux@googlemail.com)
- SPEC: Updated source URL (jmoskovc@redhat.com)
- removed unneeded patches
- Resolves: 572641, 572237, 576861

* Tue Apr  6 2010  Jiri Moskovcak <jmoskovc@redhat.com> 1.0.7-5
- removed sos-1.9 support as it's not in the trees yet
- removed hardcoded repository name "rhel-debuginfo" in debuginfo install
- and enabled the debuginfo install by default
- Resolves: #579038

* Wed Mar 31 2010  Jiri Moskovcak <jmoskovc@redhat.com> 1.0.7-4
- fixed problem with running sosreport
- Resolves: #576861

* Thu Feb 25 2010  Jiri Moskovcak <jmoskovc@redhat.com> 1.0.7-3
- fixed translation rhbz#574693 (jmoskovc@redhat.com)
- improved kerneloops summary in bugzilla rhbz#574196 (dvlasenk@reshat.com)
- fixed bug in initscript which prevents abrtd from restarting after update (npajkovs@redhat.com)
- fixed abrt-debuginfo-install to work with rhel dbeuginfo repos
- Resolves: #574196, #574693

* Thu Feb 25 2010  Jiri Moskovcak <jmoskovc@redhat.com> 1.0.7-2
- fixed problem with bz plugin
- Resolves: #564366

* Fri Feb 12 2010  Jiri Moskovcak <jmoskovc@redhat.com> 1.0.7-1
- Load plugin settings also from ~/.abrt/*.conf (kklic@redhat.com)
- fix bz#541088 "abrt should not catch python excp EPIPE" (vda.linux@googlemail.com)
- fix bz#554242 "Cannot tab between input areas in report dialog" (vda.linux@googlemail.com)
- fix bz#563484 "abrt uses unnecessary disk space when getting debug info" (vda.linux@googlemail.com)
- Don't show empty 'Not loaded plugins' section - fix#2 rhbz#560971 (jmoskovc@redhat.com)
- fix big-endian build problem (vda.linux@googlemail.com)
- Fixes, displays package owners (kklic@redhat.com)
- GUI: fixed exception in plugin settings dialog rhbz#560851 (jmoskovc@redhat.com)
- GUI: respect system settings for toolbars rhbz#552161 (jmoskovc@redhat.com)
- python hook: move UUID generation to abrtd; generate REASON, add it to bz title (vda.linux@googlemail.com)
- make "reason" field less verbose; bz reporter: include it in "summary" (vda.linux@googlemail.com)
- added avant-window-navigator to blacklist per maintainer request (jmoskovc@redhat.com)
- CCpp analyzer: fix rhbz#552435 (bt rating misinterpreting # chars) (vda.linux@googlemail.com)
- Ask for login and password if missing from reporter plugin. (kklic@redhat.com)
- abrtd: fix handling of dupes (weren't deleting dup's directory); better logging (vda.linux@googlemail.com)
- abrtd: handle "perl -w /usr/bin/script" too (vda.linux@googlemail.com)
- Component-wise duplicates (kklic@redhat.com)
- abrtd: fix rhbz#560642 - don't die on bad plugin names (vda.linux@googlemail.com)
- Fixed parsing backtrace from rhbz#549293 (kklic@redhat.com)
- GUI: fixed scrolling in reporter dialog rhbz#559687 (jmoskovc@redhat.com)
- fixed button order in plugins windows rhbz#560961 (jmoskovc@redhat.com)
- GUI: fixed windows icons and titles rhbz#537240, rhbz#560964 (jmoskovc@redhat.com)
- Fix to successfully parse a backtrace from rhbz#550642 (kklic@redhat.com)
- cli: fix the problem of not showing oops text in editor (vda.linux@googlemail.com)
- GUI: fix rhbz#560971 "Don't show empty 'Not loaded plugins' section" (vda.linux@googlemail.com)

* Tue Feb  2 2010  Jiri Moskovcak <jmoskovc@redhat.com> 1.0.6-1
- print __glib_assert_msg (rhbz#549735);
- SPEC: added some requires to abrt-cli to make it work out-of-the-box (jmoskovc@redhat.com)
- abrt-hook-ccpp: fix rhbz#560612 "limit '18446744073709551615' is bogus" rhbz#560612(vda.linux@googlemail.com)
- APPLET: don't show the icon when abrtd is not running rhbz#557866 (jmoskovc@redhat.com)
- GUI: made report message labels wrap (jmoskovc@redhat.com)
- GUI: don't die if daemon doesn't send the gpg keys (jmoskovc@redhat.com)
- disabled the autoreporting of kerneloopses (jmoskovc@redhat.com)
- Kerneloops: fix BZ reporting of oopses (vda.linux@googlemail.com)
- GUI: wider report message dialog (jmoskovc@redhat.com)
- moved the gpg key list from abrt.conf to gpg_keys file (jmoskovc@redhat.com)
- Logger: create log file with mode 0600 (vda.linux@googlemail.com)
- GUI: fixed the rating logic, to prevent sending BT with rating < 3 (jmoskovc@redhat.com)
- Report GUI: made more fields copyable - closed rhbz#526209; tweaked wording (vda.linux@googlemail.com)
- GUI: fixed bug caused by failed gk-authorization (jmoskovc@redhat.com)

* Fri Jan 29 2010  Jiri Moskovcak <jmoskovc@redhat.com> 1.0.5-1
- moved the gpg key list from abrt.conf to gpg_keys file (jmoskovc@redhat.com)
- Logger: create log file with mode 0600 rhbz#559545 (vda.linux@googlemail.com)
- GUI: fixed the rating logic, to prevent sending BT with rating < 3 (jmoskovc@redhat.com)
- Report GUI: made more fields copyable - closed rhbz#526209; tweaked wording (vda.linux@googlemail.com)
- GUI: fixed bug caused by failed gk-authorization (jmoskovc@redhat.com)
- fix bug 559881 (kerneloops not shown in "new" GUI) (vda.linux@googlemail.com)
- GUI ReporterDialog: hide log button (vda.linux@googlemail.com)
- added valgrind and strace to blacklist (jmoskovc@redhat.com)
- SOSreport: do not leave stray files in /tmp (vda.linux@googlemail.com)
- Save the core where it belongs if ulimit -c is > 0 (jmoskovc@redhat.com)
- reenabled gpg check (jmoskovc@redhat.com)
- SOSreport: run it niced (vda.linux@googlemail.com)
- report GUI: rename buttons: Log -> Show log, Send -> Send report (vda.linux@googlemail.com)
- applet: reduce blinking timeout to 3 sec (vda.linux@googlemail.com)
- fix dbus autostart (vda.linux@googlemail.com)
- abrtd: set "Reported" status only if at least one reporter succeeded (vda.linux@googlemail.com)
- SQLite3: disable newline escaping, SQLite does not handle it (vda.linux@googlemail.com)
- SOSreport: make it avoid double runs; add forced regeneration; upd PLUGINS-HOWTO (vda.linux@googlemail.com)
- attribute SEGVs in perl to script's package, like we already do for python (vda.linux@googlemail.com)

* Wed Jan 20 2010  Jiri Moskovcak <jmoskovc@redhat.com> 1.0.4-1
- enabled sosreport
- fixes in ticketuploader
- GUI: redesign of reporter dialog (jmoskovc@redhat.com)
- Set the prgname to "Automatic Bug Reporting Tool" fixes rhbz#550357 (jmoskovc@redhat.com)
- CCpp analyzer: display __abort_msg in backtrace. closes rhbz#549735 (vda.linux@googlemail.com)
- s/os.exit/sys.exit - closes rhbz#556313 (vda.linux@googlemail.com)
- use repr() to print variable values in python hook rhbz#545070 (jmoskovc@redhat.com)
- gui: add logging infrastructure (vda.linux@googlemail.com)
- Added "Enabled = yes" to all plugin's config files (jmoskovc@redhat.com)
- *: disable plugin loading/unloading through GUI. Document keyring a bit (vda.linux@googlemail.com)
- fix memory leaks in catcut plugin (npajkovs@redhat.com)
- fix memory leaks in bugzilla (npajkovs@redhat.com)
- abrt-hook-python: sanitize input more; log to syslog (vda.linux@googlemail.com)
- Fixed /var/cache/abrt/ permissions (kklic@redhat.com)
- Kerneloops: we require commandline for every crash, save dummy one for oopses (vda.linux@googlemail.com)
- *: remove nss dependencies (vda.linux@googlemail.com)
- CCpp: use our own sha1 implementation (less pain with nss libs) (vda.linux@googlemail.com)
- DebugDump: more consistent logic in setting mode and uid:gid on dump dir (vda.linux@googlemail.com)
- fixes based on security review (vda.linux@googlemail.com)
- SOSreport/TicketUploader: use more restrictive file modes (vda.linux@googlemail.com)
- abrt-hook-python: add input sanitization and directory size guard (vda.linux@googlemail.com)
- RunApp: safer chdir. Overhauled "sparn a child and get its output" in general (vda.linux@googlemail.com)
- DebugDump: use more restrictive modes (vda.linux@googlemail.com)
- SQLite3: check for SQL injection (vda.linux@googlemail.com)
- replace plugin enabling via EnabledPlugins by par-plugin Enabled = yes/no (vda.linux@googlemail.com)
- abrt.spec: move "requires: gdb" to abrt-desktop (vda.linux@googlemail.com)
- ccpp: add a possibility to disable backtrace generation (vda.linux@googlemail.com)
- abrtd: limit the number of frames in backtrace to 3000 (vda.linux@googlemail.com)

* Tue Jan  5 2010  Jiri Moskovcak <jmoskovc@redhat.com> 1.0.3-1
- speed optimalization of abrt-debuginfo-install (jmoskovc@redhat.com)
- updated credits (jmoskovc@redhat.com)
- GUI: fixed crash when abrt-gui is run without X server rhbz#552039 (jmoskovc@redhat.com)
- abrt-backtrace manpage installed (kklic@redhat.com)
- cmdline and daemon checking is done by abrt-python-hook (kklic@redhat.com)
- moved get_cmdline() and daemon_is_ok() to abrtlib (kklic@redhat.com)
- large file support for whole abrt (kklic@redhat.com)
- made s_signal_caught volatile (vda.linux@googlemail.com)
- abrt-debuginfo-install: fixes for runs w/o cachedir (vda.linux@googlemail.com)
- remove unsafe log() from signal handler (vda.linux@googlemail.com)
- src/Hooks/CCpp.cpp: use and honour 'c' (core limit size). (vda.linux@googlemail.com)
- lib/Plugins/CCpp.cpp: save gdb error messages too (vda.linux@googlemail.com)
- prevent destructors from throwing exceptions; check curl_easy_init errors (vda.linux@googlemail.com)
- don't blame python for every crash in /usr/bin/python rhbz#533521 trac#109 (jmoskovc@redhat.com)
- GUI: autoscroll log window (jmoskovc@redhat.com)
- Kerneloops.conf: better comments (vda.linux@googlemail.com)
- applet: reduce blinking time to 30 seconds (vda.linux@googlemail.com)
- add paranoia checks on setuid/setgid (vda.linux@googlemail.com)
- more "obviously correct" code for secure opening of /dev/null (vda.linux@googlemail.com)
- get rid of ugly sleep call inside while() (vda.linux@googlemail.com)

* Mon Dec 14 2009  Jiri Moskovcak <jmoskovc@redhat.com> 1.0.2-1
- disabled GPG check again (jmoskovc@redhat.com)
- abrt-pyhook-helper rename (vda.linux@googlemail.com)
- abrt-cli: report success/failure of reporting. closes bug 71 (vda.linux@googlemail.com)
- less logging (vda.linux@googlemail.com)
- mkde abrt-gui --help and --version behave as expected. closes bug 85 (vda.linux@googlemail.com)
- dbus lib: fix parsing of 0-element arrays. Fixes bug 95 (vda.linux@googlemail.com)
- make "abrt-cli --delete randomuuid" report that deletion failed. closes bug 59 (vda.linux@googlemail.com)
- applet: make animation stop after 1 minute. (closes bug 108) (vda.linux@googlemail.com)
- show comment and how to reproduce fields, when BT rating > 3 (jmoskovc@redhat.com)
- Gui: make report status window's text wrap. Fixes bug 82 (vda.linux@googlemail.com)
- CCpp analyzer: added "info sharedlib" (https://fedorahosted.org/abrt/ticket/90) (vda.linux@googlemail.com)
- added link to bugzilla new account page to Bugzilla config dialog (jmoskovc@redhat.com)
- GUI: added log window (jmoskovc@redhat.com)

* Tue Dec  8 2009  Jiri Moskovcak <jmoskovc@redhat.com> 1.0.1-1
- PyHook: better logic for checking if abrtd is running rhbz#539987 (jmoskovc@redhat.com)
- re-enabled gpg sign checking (jmoskovc@redhat.com)
- PyHook: use repr() for displaying variables rhbz#545070 (jmoskovc@redhat.com)
- kerneloops: fix the linux kernel version identification (aarapov@redhat.com)
- gui review (rrakus@redhat.com)
- when we trim the dir, we must delete it from DB too rhbz#541854 (vda.linux@googlemail.com)
- improved dupe checking (kklic@redhat.com)
- GUI: handle cases when gui fails to start daemon on demand rhbz#543725 (jmoskovc@redhat.com)
- Add abrt group only if it is missing; fixes rhbz#543250 (kklic@redhat.com)
- GUI: more string fixes rhbz#543266 (jmoskovc@redhat.com)
- abrt.spec: straighten out relations between abrt-desktop and abrt-gui (vda.linux@googlemail.com)
- refuse to start if some required plugins are missing rhbz#518422 (vda.linux@googlemail.com)
- GUI: survive gnome-keyring access denial rhbz#543200 (jmoskovc@redhat.com)
- typo fixes rhbz#543266 (jmoskovc@redhat.com)
- abrt-debuginfo-install: better fix for incorrect passing double quotes (vda.linux@googlemail.com)
- APPLET: stop animation when it's not needed rhbz#542157 (jmoskovc@redhat.com)
- ccpp hook: reanme it, and add "crash storm protection" (see rhbz#542003) (vda.linux@googlemail.com)
- Hooks/CCpp.cpp: add MakeCompatCore = yes/no directive. Fixes rhbz#541707 (vda.linux@googlemail.com)
- SPEC: removed sqlite3 package, fixed some update problems (jmoskovc@redhat.com)
- Kerneloops are reported automaticky now when AutoReportUIDs = root is in Kerneloops.conf (npajkovs@redhat.com)
- remove word 'detected' from description rhbz#541459 (vda.linux@googlemail.com)
- src/Hooks/CCpp.cpp: do save abrtd's own coredumps, but carefully... (vda.linux@googlemail.com)
- CCpp.cpp: quote parameters if needed rhbz#540164 (vda.linux@googlemail.com)

* Fri Nov 20 2009  Jiri Moskovcak <jmoskovc@redhat.com> 1.0.0-1
- new version
- comment input wraps words rhbz#531276
- fixed hiding password dialog rhbz#529583
- easier kerneloops reporting rhbz#528395
- made menu entry translatable rhbz#536878 (jmoskovc@redhat.com)
- GUI: don't read the g-k every time we want to use the setting (jmoskovc@redhat.com)
- GUI: survive if g-k access is denied rhbz#534171 (jmoskovc@redhat.com)
- include more info into oops (we were losing the stack dump) (vda.linux@googlemail.com)
- make BZ insert small text attachments inline; move text file detection code (vda.linux@googlemail.com)
- GUI: fixed text wrapping in comment field rhbz#531276 (jmoskovc@redhat.com)
- GUI: added cancel to send dialog rhbz#537238 (jmoskovc@redhat.com)
- include abrt version in bug descriptions (vda.linux@googlemail.com)
- ccpp hook: implemented ReadonlyLocalDebugInfoDirs directive (vda.linux@googlemail.com)
- GUI: added window icon rhbz#537240 (jmoskovc@redhat.com)
- add support for \" escaping in config file (vda.linux@googlemail.com)
- add experimental saving of /var/log/Xorg*.log for X crashes (vda.linux@googlemail.com)
- APPLET: changed icon from default gtk-warning to abrt specific, add animation (jmoskovc@redhat.com)
- don't show icon on abrtd start/stop rhbz#537630 (jmoskovc@redhat.com)
- /var/cache/abrt permissions 1775 -> 0775 in spec file (kklic@redhat.com)
- Daemon properly checks /var/cache/abrt attributes (kklic@redhat.com)
- abrt user group; used by abrt-pyhook-helper (kklic@redhat.com)
- pyhook-helper: uid taken from system instead of command line (kklic@redhat.com)
- KerneloopsSysLog: fix breakage in code which detects abrt marker (vda.linux@googlemail.com)
- GUI: added support for backtrace rating (jmoskovc@redhat.com)
- InformAllUsers support. enabled by default for Kerneloops. Tested wuth CCpp. (vda.linux@googlemail.com)
- abrtd: call res_init() if /etc/resolv.conf or friends were changed rhbz#533589 (vda.linux@googlemail.com)
- supress errors in python hook to not colide with the running script (jmoskovc@redhat.com)

* Tue Nov 10 2009 Jiri Moskovcak <jmoskovc@redhat.com> 0.0.11-2
- spec file fixes

* Mon Nov  2 2009  Jiri Moskovcak <jmoskovc@redhat.com> 0.0.11-1
- re-enabled kerneloops
- abrt-debuginfo-install: download packages one-by-one - better logging (vda.linux@googlemail.com)
- do not report empty fields (vda.linux@googlemail.com)
- Added abrt.png, fixed rhbz#531181 (jmoskovc@redhat.com)
- added option DebugInfoCacheMB to limit size of unpacked debuginfos (vda.linux@googlemail.com)
- fixed the problem with overwriting the default plugin settings (jmoskovc@redhat.com)
- disabled kerneloops in config file (jmoskovc@redhat.com)
- added dependency to gdb >= 7.0 (jmoskovc@redhat.com)
- better format of report text (vda.linux@googlemail.com)
- Python backtrace size limited to 1 MB (kklic@redhat.com)
- lib/Plugins/Bugzilla: better message at login failure (vda.linux@googlemail.com)
- build fixes, added plugin-logger to abrt-desktop (jmoskovc@redhat.com)
- blacklisted nspluginwrapper, because it causes too many useless reports (jmoskovc@redhat.com)
- GUI: Wrong settings window is not shown behind the reporter dialog rhbz#531119 (jmoskovc@redhat.com)
- Normal user can see kerneloops and report it Bugzilla memory leaks fix (npajkovs@redhat.com)
- dumpoops: add -s option to dump results to stdout (vda.linux@googlemail.com)
- removed kerneloops from abrt-desktop rhbz#528395 (jmoskovc@redhat.com)
- GUI: fixed exception when enabling plugin rhbz#530495 (jmoskovc@redhat.com)
- Improved abrt-cli (kklic@redhat.com)
- Added backtrace rating to CCpp analyzer (dnovotny@redhat.com)
- GUI improvements (jmoskovc@redhat.com)
- Added abrt-pyhook-helper (kklic@redhat.com)

* Thu Oct 15 2009  Jiri Moskovcak <jmoskovc@redhat.com> 0.0.10-1
- new version
- added more logging (vda.linux@googlemail.com)
- made polkit policy to be more permissive when installing debuginfo (jmoskovc@redhat.com)
- lib/Plugins/CCpp.cpp: add build-ids to backtrace (vda.linux@googlemail.com)
- lib/Plugins/CCpp.cpp: do not use temp file for gdb commands - use -ex CMD instead (vda.linux@googlemail.com)
- GUI: added refresh button, added sanity check to plugin settings (jmoskovc@redhat.com)
- Initial man page for abrt-cli (kklic@redhat.com)
- Added --version, -V, --help, -? options. Fixed crash caused by unknown option. (kklic@redhat.com)
- Date/time honors current system locale (kklic@redhat.com)
- fixed saving/reading user config (jmoskovc@redhat.com)
- SPEC: added gnome-python2-gnomekeyring to requirements (jmoskovc@redhat.com)
- GUI: call Report() with the latest pluginsettings (jmoskovc@redhat.com)
- Fix Bug 526220 -  [abrt] crash detected in abrt-gui-0.0.9-2.fc12 (vda.linux@googlemail.com)
- removed unsecure reading/writting from ~HOME directory rhbz#522878 (jmoskovc@redhat.com)
- error checking added to archive creation (danny@rawhide.localdomain)
- try using pk-debuginfo-install before falling back to debuginfo-install (vda.linux@googlemail.com)
- abrt-gui: make "report" toolbar button work even if abrtd is not running (vda.linux@googlemail.com)
- set LIMIT_MESSAGE to 16k, typo fix and daemon now reads config information from dbus (npajkovs@redhat.com)
- add support for abrtd autostart (vda.linux@googlemail.com)
- GUI: reversed the dumplist, so the latest crashes are at the top (jmoskovc@redhat.com)
- rewrite FileTransfer to use library calls instead of commandline calls for compression (dnovotny@redhat.com)
- and many minor fixes ..

* Wed Sep 23 2009  Jiri Moskovcak <jmoskovc@redhat.com> 0.0.9-2
- added bug-buddy to provides rhbz#524934

* Tue Sep 22 2009  Jiri Moskovcak <jmoskovc@redhat.com> 0.0.9-1
- new version
- comments and how to reproduce are stored now (npajkovs@redhat.com)
- reduce verbosity a bit (vda.linux@googlemail.com)
- GUI: fixed word wrap in Comment field rhbz#524349 (jmoskovc@redhat.com)
- remove last vestives of dbus-c++ from build system (vda.linux@googlemail.com)
- GUI: added popup menu, fixed behaviour when run with root privs (jmoskovc@redhat.com)
- add dbus signalization when quota exceeded (npajkovs@redhat.com)
- Added cleaning of attachment variable, so there should not be mixed attachmetn anymore. (zprikryl@redhat.com)
- fixed closing of debug dump in case of existing backtrace (zprikryl@redhat.com)
- remove C++ dbus glue in src/CLI; fix a bug in --report (vda.linux@googlemail.com)
- new polkit action for installing debuginfo, default "yes" (danny@rawhide.localdomain)
- Polkit moved to Utils (can be used both in daemon and plugins) (danny@rawhide.localdomain)
- oops... remove stray trailing '\' (vda.linux@googlemail.com)
- GUI: added missing tooltips (jmoskovc@redhat.com)
- PYHOOK: ignore KeyboardInterrupt exception (jmoskovc@redhat.com)
- added ticket uploader plugin (gavin@redhat.com) (zprikryl@redhat.com)
- GUI: added UI for global settings (just preview, not usable!) (jmoskovc@redhat.com)
- Add checker if bugzilla login and password are filled in. (npajkovs@redhat.com)
- Add new config option InstallDebuginfo into CCpp.conf (npajkovs@redhat.com)
- translation updates
- many other fixes

* Fri Sep  4 2009  Jiri Moskovcak <jmoskovc@redhat.com> 0.0.8.5-1
- new version
- APPLET: added about dialog, removed popup, if icon is not visible, fixed (trac#43) (jmoskovc@redhat.com)
- renamed abrt to abrtd, few minor spec file fixes (jmoskovc@redhat.com)
- Made abrt service start by deafult (jmoskovc@redhat.com)
- add gettext support for all plugins (npajkovs@redhat.com)
- APPLET: removed the warning bubble about not running abrt service (walters)
- APPLET: changed tooltip rhbz#520293 (jmoskovc@redhat.com)
- CommLayerServerDBus: rewrote to use dbus, not dbus-c++ (vda.linux@googlemail.com)
- fixed timeout on boot causing [ FAILED ] message (vda.linux@googlemail.com)
- and many other fixes

* Wed Sep 02 2009  Colin Walters <watlers@verbum.org> 0.0.8-2
- Change Conflicts: kerneloops to be an Obsoletes so we do the right thing
  on upgrades.  Also add an Obsoletes: bug-buddy.

* Wed Aug 26 2009  Jiri Moskovcak <jmoskovc@redhat.com> 0.0.8-1
- new version
- resolved: Bug 518420 -  ordinary user's abrt-applet shows up for root owned crashes (npajkovs)
- GUI: added support for gettext (+part of czech translation) (jmoskovc)
- added support for saving settings (zprikryl)
- fixed conf: comment in the middle of the line isn't supported anymore (zprikryl)
- BZ#518413 PATCH ... furious kerneloops reporting (aarapov)
- GUI: added first part of support for gettext (jmoskovc)
- add new parameter to FileTransfer plugin (dnovotny)
- added support for updating abrt's table (zprikryl)
- added check for cc-list and reporter. +1 is created iff reporter is somebody else and current user isn't in cc list. (zprikryl)
- GUI: few improvements, to be more userfriendly (jmoskovc)
- LOGGER: return valid uri of the log file on succes (jmoskovc)
- GUI: bring the GUI up to front instead of just blinking in taskbar (trac#60, rhbz#512390) (jmoskovc)
- Try to execute $bindir/abrt-gui, then fall back to $PATH search. Closes bug 65 (vda.linux)
- APPLET: added popup menu (trac#37, rhbz#518386) (jmoskovc)
- Improved report results (zprikryl)
- Fixed sigsegv (#rhbz 518609) (zprikryl)
- GUI: removed dependency on libsexy if gtk2 >= 2.17 (jmoskovc)
- fixed signature check (zprikryl)
- KerneloopsSysLog: check line length to be >= 4 before looking for "Abrt" (vda.linux)
- Comment cannot start in the middle of the line. Comment has to start by Char # (first char in the line) (zprikryl)
- command mailx isn't run under root anymore. (zprikryl)
- GUI: added horizontal scrolling to report window (jmoskovc)
- GUI: added clickable link to "after report" status window (jmoskovc)
- added default values for abrt daemon (zprikryl)
- Plugins/CCpp: remove trailing \n from debuginfo-install's output (vda.linux)
- explain EnableGPGCheck option better (vda.linux)
- mailx: correct English (vda.linux)
- Bugzilla.conf: correct English (vda.linux)
- GUI: nicer after report message (jmoskovc)
- BZ plugin: removed /xmlrpc.cgi from config, made the report message more user friendly (jmoskovc)
- CCpp plugin: do not abort if debuginfos aren't found (vda.linux)
- abrt.spec: bump version to 0.0.7-2 (vda.linux)
- mailx removed dangerous parameter option (zprikryl)
- minimum timeout is 1 second (zprikryl)
- in case of plugin error, don't delete debug dumps (zprikryl)
- abrt-gui: fix crash when run by root (vda.linux)
- and lot more in git log ...

* Thu Aug 20 2009  Jiri Moskovcak <jmoskovc@redhat.com> 0.0.7.2-1
- new version
- fixed some bugs found during test day

* Wed Aug 19 2009  Jiri Moskovcak <jmoskovc@redhat.com> 0.0.7.1-1
- fixes to bugzilla plugin and gui to make the report message more user-friendly

* Tue Aug 18 2009  Denys Vlasenko <dvlasenk@redhat.com> 0.0.7-2
- removed dangerous parameter option
- minimum plugin activation period is 1 second
- in case of plugin error, don't delete debug dumps
- abrt-gui: fix crash when run by root
- simplify parsing of debuginfo-install output

* Tue Aug 18 2009  Jiri Moskovcak <jmoskovc@redhat.com> 0.0.7-1
- new version
- added status window to show user some info after reporting a bug

* Mon Aug 17 2009  Denys Vlasenko <dvlasenk@redhat.com> 0.0.6-1
- new version
- many fixes

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.0.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Thu Jun 25 2009  Jiri Moskovcak <jmoskovc@redhat.com> 0.0.4-3
- fixed dependencies in spec file

* Tue Jun 16 2009 Daniel Novotny <dnovotny@redhat.com> 0.0.4-2
- added manual pages (also for plugins)

* Mon Jun 15 2009  Jiri Moskovcak <jmoskovc@redhat.com> 0.0.4-1
- new version
- added cli (only supports sockets)
- added python hook
- many fixes

* Fri Apr 10 2009  Jiri Moskovcak <jmoskovc@redhat.com> 0.0.3-1
- new version
- added bz plugin
- minor fix in reporter gui
- Configurable max size of debugdump storage rhbz#490889
- Wrap lines in report to keep the window sane sized
- Fixed gui for new daemon API
- removed unneeded code
- removed dependency on args
- new guuid hash creating
- fixed local UUID
- fixed debuginfo-install checks
- renamed MW library
- Added notification thru libnotify
- fixed parsing settings of action plugins
- added support for action plugins
- kerneloops - plugin: fail gracefully.
- Added commlayer to make dbus optional
- a lot of kerneloops fixes
- new approach for getting debuginfos and backtraces
- fixed unlocking of a debugdump
- replaced language and application plugins by analyzer plugin
- more excetpion handling
- conf file isn't needed
- Plugin's configuration file is optional
- Add curl dependency
- Added column 'user' to the gui
- Gui: set the newest entry as active (ticket#23)
- Delete and Report button are no longer active if no entry is selected (ticket#41)
- Gui refreshes silently (ticket#36)
- Added error reporting over dbus to daemon, error handling in gui, about dialog

* Wed Mar 11 2009  Jiri Moskovcak <jmoskovc@redhat.com> 0.0.2-1
- added kerneloops addon to rpm (aarapov)
- added kerneloops addon and plugin (aarapov)
- Made Crash() private
- Applet requires gui, removed dbus-glib deps
- Closing stdout in daemon rhbz#489622
- Changed applet behaviour according to rhbz#489624
- Changed gui according to rhbz#489624, fixed dbus timeouts
- Increased timeout for async dbus calls to 60sec
- deps cleanup, signal AnalyzeComplete has the crashreport as an argument.
- Fixed empty package Description.
- Fixed problem with applet tooltip on x86_64

* Wed Mar  4 2009 Jiri Moskovcak <jmoskovc@redhat.com> 0.0.1-13
- More renaming issues fixed..
- Changed BR from gtkmm24 to gtk2
- Fixed saving of user comment
- Added a progress bar, new Comment entry for user comments..
- FILENAME_CMDLINE and FILENAME_RELEASE are optional
- new default path to DB
- Rename to abrt

* Tue Mar  3 2009 Jiri Moskovcak <jmoskovc@redhat.com> 0.0.1-12
- initial fedora release
- changed SOURCE url
- added desktop-file-utils to BR
- changed crash-catcher to %%{name}

* Mon Mar  2 2009 Jiri Moskovcak <jmoskovc@redhat.com> 0.0.1-11
- more spec file fixes according to review
- async dbus method calls, added exception handler
- avoid deadlocks (zprikryl)
- root is god (zprikryl)
- create bt only once (zprikryl)

* Sat Feb 28 2009 Jiri Moskovcak <jmoskovc@redhat.com> 0.0.1-10
- New gui
- Added new method DeleteDebugDump to daemon
- Removed gcc warnings from applet
- Rewritten CCpp hook and removed dealock in DebugDumps lib (zprikryl)
- fixed few gcc warnings
- DBusBackend improvements

* Fri Feb 27 2009 Jiri Moskovcak <jmoskovc@redhat.com> 0.0.1-9
- fixed few gcc warnings
- added scrolled window for long reports

* Thu Feb 26 2009 Adam Williamson <awilliam@redhat.com> 0.0.1-8
- fixes for all issues identified in review

* Thu Feb 26 2009 Jiri Moskovcak <jmoskovc@redhat.com> 0.0.1-7
- Fixed cancel button behaviour in reporter
- disabled core file sending
- removed some debug messages

* Thu Feb 26 2009 Jiri Moskovcak <jmoskovc@redhat.com> 0.0.1-6
- fixed DB path
- added new signals to handler
- gui should survive the dbus timeout

* Thu Feb 26 2009 Jiri Moskovcak <jmoskovc@redhat.com> 0.0.1-5
- fixed catching debuinfo install exceptions
- some gui fixes
- added check for GPGP public key

* Thu Feb 26 2009 Jiri Moskovcak <jmoskovc@redhat.com> 0.0.1-4
- changed from full bt to simple bt

* Thu Feb 26 2009 Jiri Moskovcak <jmoskovc@redhat.com> 0.0.1-3
- spec file cleanups
- changed default paths to crash DB and log DB
- fixed some memory leaks

* Tue Feb 24 2009 Jiri Moskovcak <jmoskovc@redhat.com> 0.0.1-2
- spec cleanup
- added new subpackage gui

* Wed Feb 18 2009 Zdenek Prikryl <zprikryl@redhat.com> 0.0.1-1
- initial packing
