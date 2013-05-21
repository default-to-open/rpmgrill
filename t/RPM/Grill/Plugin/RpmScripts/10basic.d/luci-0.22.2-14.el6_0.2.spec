%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitelib_arch: %define python_sitelib_arch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}
%{!?pyver: %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")}

Name: luci
Version: 0.22.2
Release: 14%{?dist}.2
Summary: Web-based high availability administration application
Group: Applications/System
License: GPLv2
URL: http://sources.redhat.com/cluster/conga
Source0: http://people.redhat.com/rmccabe/luci/luci-0.22.2.tar.bz2
Source1: logo.png
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: python-devel python-setuptools python-paste python-paste-script cyrus-sasl-devel
Requires: TurboGears2 openssl python-repoze-who-friendlyform python-tw-forms
Requires: python-paste >= 1.7.2-5.el6
Requires(post): chkconfig initscripts
Requires(preun): chkconfig initscripts
Requires(postun): initscripts
ExclusiveArch: i686 x86_64

Patch0: bz600080.patch
Patch1: bz600079.patch
Patch2: bz600076.patch
Patch3: bz599074.patch
Patch4: bz602482.patch
Patch5: bz599080.patch
Patch6: bz598859.patch
Patch7: bz600069.patch
Patch8: bz600052.patch
Patch9: bz600058.patch
Patch10: bz600066.patch
Patch11: bz600073.patch
Patch12: bz600075.patch
Patch13: bz602482-2.patch
Patch14: bz600050.patch
Patch15: bz600047.patch
Patch16: bz600074.patch
Patch17: bz600061.patch
Patch18: bz600073-2.patch
Patch19: bz600075-2.patch
Patch20: bz603833.patch
Patch21: bz600071.patch
Patch22: bz600060.patch
Patch23: bz605780.patch
Patch24: bz600059.patch
Patch25: bz600083.patch
Patch26: bz600077.patch
Patch27: bz604740.patch
Patch28: bz600056.patch
Patch29: bz600021.patch
Patch30: bz613868.patch
Patch31: bz600021-2.patch
Patch32: bz600045.patch
Patch33: bz615096.patch
Patch34: bz614434.patch
Patch35: bz614439.patch
Patch36: bz615929.patch
Patch37: bz615917.patch
Patch38: bz615911.patch
Patch39: bz600040.patch
Patch40: bz615929-2.patch
Patch41: bz600027.patch
Patch42: bz615468.patch
Patch43: bz616094.patch
Patch44: bz616230.patch
Patch45: bz616244.patch
Patch46: bz600055.patch
Patch47: bz615872.patch
Patch48: bz615889.patch
Patch49: bz615911-2.patch
Patch50: bz618424.patch
Patch51: bz600055-2.patch
Patch52: bz600027-2.patch
Patch53: bz616382.patch
Patch54: bz613871.patch
Patch55: bz619220.patch
Patch56: bz614433.patch
Patch57: bz617575.patch
Patch58: bz617591.patch
Patch59: bz617602.patch
Patch60: bz618577.patch
Patch61: bz619641.patch
Patch62: bz619220-2.patch
Patch63: bz619652.patch
Patch64: bz615926.patch
Patch65: bz619220-3.patch
Patch66: bz614130.patch
Patch67: bz618578.patch
Patch68: bz642140.patch
Patch69: bz681764.patch

%description
Luci is a web-based high availability administration application built on the
TurboGears 2 framework.

%prep
%setup -q
cp %{_sourcedir}/logo.png %{_builddir}/luci-0.22.2/luci/public/images
%patch0 -p1 -b .bz600080
%patch1 -p1 -b .bz600079
%patch2 -p1 -b .bz600076
%patch3 -p1 -b .bz599074
%patch4 -p1 -b .bz602482
%patch5 -p1 -b .bz599080
%patch6 -p1 -b .bz598859
%patch7 -p1 -b .bz600069
%patch8 -p1 -b .bz600052
%patch9 -p1 -b .bz600058
%patch10 -p1 -b .bz600066
%patch11 -p1 -b .bz600073
%patch12 -p1 -b .bz600075
%patch13 -p1 -b .bz602482
%patch14 -p1 -b .bz600050
%patch15 -p1 -b .bz600047
%patch16 -p1 -b .bz600074
%patch17 -p1 -b .bz600061
%patch18 -p1 -b .bz600073
%patch19 -p1 -b .bz600075
%patch20 -p1 -b .bz603833
%patch21 -p1 -b .bz600071
%patch22 -p1 -b .bz600060
%patch23 -p1 -b .bz605780
%patch24 -p1 -b .bz600059
%patch25 -p1 -b .bz600083
%patch26 -p1 -b .bz600077
%patch27 -p1 -b .bz604740
%patch28 -p1 -b .bz600056
%patch29 -p1 -b .bz600021
%patch30 -p1 -b .bz613868
%patch31 -p1 -b .bz600021
%patch32 -p1 -b .bz600045
%patch33 -p1 -b .bz615096
%patch34 -p1 -b .bz614434
%patch35 -p1 -b .bz614439
%patch36 -p1 -b .bz615929
%patch37 -p1 -b .bz615917
%patch38 -p1 -b .bz615911
%patch39 -p1 -b .bz600040
%patch40 -p1 -b .bz615929
%patch41 -p1 -b .bz600027
%patch42 -p1 -b .bz615468
%patch43 -p1 -b .bz616094
%patch44 -p1 -b .bz616230
%patch45 -p1 -b .bz616244
%patch46 -p1 -b .bz600055
%patch47 -p1 -b .bz615872
%patch48 -p1 -b .bz615889
%patch49 -p1 -b .bz615911
%patch50 -p1 -b .bz618424
%patch51 -p1 -b .bz600055
%patch52 -p1 -b .bz600027
%patch53 -p1 -b .bz616382
%patch54 -p1 -b .bz613871
%patch55 -p1 -b .bz619220
%patch56 -p1 -b .bz614433
%patch57 -p1 -b .bz617575
%patch58 -p1 -b .bz617591
%patch59 -p1 -b .bz617602
%patch60 -p1 -b .bz618577
%patch61 -p1 -b .bz619641
%patch62 -p1 -b .bz619220
%patch63 -p1 -b .bz619652
%patch64 -p1 -b .bz615926
%patch65 -p1 -b .bz619220
%patch66 -p1 -b .bz614130
%patch67 -p1 -b .bz618578
%patch68 -p1 -b .bz642140
%patch69 -p1 -b .bz681764

%build
python setup.py build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/var/log/luci
python setup.py install --skip-build --root %{buildroot}
cd init.d && make DESTDIR=%{buildroot} install;cd ..
cd config && make DESTDIR=%{buildroot} install;cd ..
cd lucipam && python setup.py install --root %{buildroot};  cd ..

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc README.txt COPYING
%{python_sitelib}/%{name}-%{version}-py%{pyver}.egg-info/
%{python_sitelib}/%{name}/
%{python_sitelib_arch}/LuciPAM-1.0-py2.6.egg-info
%{python_sitelib_arch}/lucipam.so

%config(noreplace)      /etc/pam.d/luci
%config(noreplace)      %{_localstatedir}/lib/luci/etc/luci.ini
%attr(0600,luci,luci)   %{_localstatedir}/lib/luci/etc/luci.ini
%config(noreplace)      %{_localstatedir}/lib/luci/etc/cacert.config
%attr(0600,luci,luci)   %{_localstatedir}/lib/luci/etc/cacert.config
%attr(0750,luci,luci)   %{_localstatedir}/lib/luci
%config(noreplace)      %{_sysconfdir}/rc.d/init.d/luci
%attr(750, luci, luci)  %dir /var/log/luci

# We alter this file in %post - it is not user serviceable.
%verify(not md5 mtime size) %{_localstatedir}/lib/luci/etc/who.ini

%pre
/usr/sbin/groupadd -g 141 luci 2> /dev/null
/usr/sbin/useradd -u 141 -g 141 -d /var/lib/luci -s /sbin/nologin -r \
        -c "luci user" luci 2> /dev/null
exit 0

%post
/sbin/chkconfig --add luci
secret="$(dd if=/dev/urandom bs=8 count=1 2>/dev/null | od -t x8 -A n | sed 's/^[ ]*//')"
sedcmd=":a /^\[plugin:auth_tkt\]\$/! {p;d;ba}; {:b \$! {N;bb}; {s/\([ \t]*secret[ \t]*=[ \t]*\)[^\n]*/\1$secret/1;p;d}}"
sed -ni "$sedcmd" %{_localstatedir}/lib/luci/etc/who.ini
exit 0

%preun
if [ "$1" == "0" ]; then
    /sbin/service luci stop >&/dev/null
    /sbin/chkconfig --del luci 
fi
exit 0

%postun
if [ "$1" == "1" ]; then
    /sbin/service luci condrestart >&/dev/null
fi
exit 0

%changelog
* Wed Apr 13 2011 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-14.2
- Fix bz681764 (readd urgently fence_brocade to the list of shipped fence_agents in luci)

* Mon Oct 11 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-14.1
- Fix bz642140 (add support for unfencing conf. generation for SAN fencing agents and fence_scsi)

* Thu Sep 09 2010 Lon Hohberger <lhh@redhat.com> - 0.22.2-14
- Randomize secret key in who.ini on each installation.
  Specfile patch from Jan Pokorny.
- Resolves: rhbz#626415

* Tue Aug 03 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-13
- Remove extra debugging logging from the fix for bz619220
- Fix bz614130 (implement tomcat6 resource agent)
- Fix bz618578 (ip resource should have netmask field)

* Tue Aug 03 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-12
- Fix bz615926 (luci does not handle qdisk / cman config correctly)
- Fix bz619220 (Luci does extra queries which slows down page load)
- Fix bz619652 (luci sometimes prints a traceback when deleting multiple nodes at the same time)
- Fix bz619641 (luci init script prints a python traceback when status is queried by a non-root user)

* Thu Jul 29 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-11
- Fix bz614433 (cannot configure ipport for fence agents)
- Fix bz617575 (Unclear options when configuring a cluster)
- Fix bz617591 (Some fields when adding an IP address are unclear)
- Fix bz617602 (Fields in "Fence Daemon Properties" have no units)
- Fix bz618577 (wrong message displayed when adding ip resource)
- Fix bz619220 (Luci does extra queries which slows down page load)

* Tue Jul 26 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-10
- Additional fixes for bz600027 (Fix cluster service creation/configuration UX issues)
- Additional fixes for bz600055 ("cluster busy" dialog does not work)
- Fix bz618424 (Can't remove nodes in node add dialog or create cluster dialog)
- Fix bz616382 (luci db error removing a node from a cluster)
- Fix bz613871 (luci should not give ungraceful error messages when encountering fence devices that it does not recognize/support)

* Mon Jul 26 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-9
- Fix bz600027 (Fix cluster service creation/configuration UX issues)
- Fix bz600040 (Add nodes to existing cluster does not work)
- Fix bz600045 (Removing nodes from existing clusters fails)
- Fix bz600055 ("cluster busy" dialog does not work)
- Fix bz613868 (Remove fence_virsh from luci UI since this fence is not supported with RHEL HA/Cluster)
- Fix bz614434 (adding an IP resource ends with an error 500)
- Fix bz614439 (adding GFS2 resource type in RHEL6 cluster is "interesting")
- Fix bz615096 (Traceback when unchecking "Prioritized" in Failover Domains)
- Fix bz615468 (When creating a new failover domain, adding nodes has no effect)
- Fix bz615872 (unicode error deleting a cluster)
- Fix bz615889 (luci cannot start an imported cluster)
- Fix bz615911 (luci shows many unsupported fence devices when adding a new fence device)
- Fix bz615917 (adding per node fence instance results in error 500 if no fence devices are configured)
- Fix bz615929 (luci generated cluster.conf with fence_scsi fails to validate)
- Fix bz616094 (Deleting a fence device which is in use, causes a traceback on Nodes page)
- Fix bz616228 (Clicking on cluster from manage clusters page results in traceback (500 error))
- Fix bz616230 (Clicking on the join button doesn't work on nodes page)
- Fix bz616244 (Clicking on the leave button doesn't work on nodes page.)

* Wed Jul 14 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-8
- Fix bz600021 (Fix node fence configuration UX issues)

* Tue Jul 13 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-7
- Build fix for bz600056

* Tue Jul 13 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-6
- Build fix for bz600056

* Tue Jul 13 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-5
- Fix bz604740 (Support nfsserver resource agent which is for NFSv4 and NFSv3)
- Fix bz600056 (Replace logo image)

* Fri Jul 09 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-4
- Fix bz600059 (Hide optional fields for fence_scsi)
- Fix bz600077 (cman "two_node" attribute should not be set when using qdisk)
- Fix bz600083 (Add text to broadcast mode to note that it is for demos only - no production support)
- Fix bz605780 (Qdisk shouldn't be part of the main page, it should be in the configuration tab)

* Fri Jun 18 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-3
- Fix bz598859 (Adding fence_xvm fence device through luci interface throws TypeError Traceback)
- Fix bz599074 ("Use same password for all nodes" doesn't work.)
- Fix bz599080 (Conga ignores "reboot nodes" check box)
- Fix bz600047 (luci allows deletion of global resources that are used by services)
- Fix bz600050 (luci requires wrongly requires users to fill interval / tko / minimum score / votes fields for qdisk configuration)
- Fix bz600052 (luci allows deletion of the last qdisk heuristics row)
- Fix bz600058 (ssh_identity field values are dropped)
- Fix bz600060 (Formatting error on fence devices overview page)
- Fix bz600061 (Default values not populated in advanced network configuration)
- Fix bz600066 (Update resource agent labels)
- Fix bz600069 (Configuration page always returns to General Properties Page)
- Fix bz600071 (If luci cannot communicate with the nodes they don't appear in the list of nodes)
- Fix bz600073 (Update resource agent list)
- Fix bz600074 (Fix display error on the resource list page)
- Fix bz600075 (update fence_virt / fence_xvm configuration)
- Fix bz600076 (When creating a cluster no default radio button is selected for Download Packages/Use locally installed packages)
- Fix bz600079 (Unable to edit existing resources)
- Fix bz600080 (Homebase page only shows a '-' for Nodes Joined)
- Fix bz602482 (Multicast settings are not relayed to cluster.conf and no default)
- Fix bz603833 ("Nodes Joined" in main page is inaccurate when no nodes have joined)

* Tue Jun 01 2010 Chris Feist <cfeist@redhat.com> - 0.22.2-2
- Fix missing requires which will cause some installations to fail
- Resolves: rhbz#598725

* Fri May 26 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.2-1
- Fix for bugs related to cluster service creation and editing (bz593836).

* Wed May 26 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.1-3
- Fix remaining unresolved issues for 593836
  - Make sure the cluster version is updated when creating services
  - Fix a bug that caused IP resources to fail in services

* Wed May 26 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.1-2
- Rebuild to fix a bug introduced during last build.

* Wed May 26 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.1-1
- Fix service creation, display, and edit.
- Fix qdisk heuristic submission.

* Wed May 19 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.0-16
- Rebase to upstream

* Mon May 17 2010 Chris Feist <cfeist@redhat.com> - 0.22.0-13
- Added static UID/GID for luci user
- Resolves: rhbz#585988

* Wed May 12 2010 Chris Feist <cfeist@redhat.com> - 0.22.0-11
- Add support for PAM authentication
- Resync with main branch
- Resolves: rhbz#518206

* Wed May 12 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.21.0-8
- Do not build on ppc and ppc64.
  Resolves: rhbz#590987

* Tue Apr 27 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.0-4
- Update from devel tree.

* Thu Apr 22 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.0-3
- Update from development tree.

* Thu Apr 08 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.0-2
- Update from development tree.

* Tue Mar 09 2010 Ryan McCabe <rmccabe@redhat.com> - 0.22.0-1
- Rebase to luci version 0.22.0

* Mon Mar  1 2010 Fabio M. Di Nitto <fdinitto@redhat.com> - 0.21.0-7
- Resolves: rhbz#568005
- Add ExcludeArch to drop s390 and s390x

* Tue Jan 19 2010 Ryan McCabe <rmccabe@redhat.com> - 0.21.0-6
- Remove dependency on python-tg-devtools

* Wed Nov 04 2009 Ryan McCabe <rmccabe@redhat.com> - 0.21.0-4
- And again.

* Wed Nov 04 2009 Ryan McCabe <rmccabe@redhat.com> - 0.21.0-2
- Fix missing build dep.

* Tue Nov 03 2009 Ryan McCabe <rmccabe@redhat.com> - 0.21.0-1
- Add init script.
- Run as the luci user, not root.
- Turn off debugging.

* Fri Sep 25 2009 Ryan McCabe <rmccabe@redhat.com> - 0.20.0-1
- Initial build.
