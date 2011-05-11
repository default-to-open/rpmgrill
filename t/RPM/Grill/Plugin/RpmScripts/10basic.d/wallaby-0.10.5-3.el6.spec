%{!?ruby_sitelib: %global ruby_sitelib %(ruby -rrbconfig -e 'puts Config::CONFIG["sitelibdir"] ')}
%define rel 3

Summary: Configuration store via QMF
Name: wallaby
Version: 0.10.5
Release: %{rel}%{?dist}
Group: Applications/System
License: ASL 2.0
URL: http://git.fedorahosted.org/git/grid/wallaby.git
Source0: %{name}-%{version}-%{rel}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires: ruby(abi) = 1.8
Requires: ruby
Requires: ruby-spqr >= 0.3.0
Requires: ruby-rhubarb >= 0.2.6
Requires: ruby-qmf >= 0.7.929717
Requires: ruby-wallaby = %{version}-%{release}
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts
BuildArch: noarch

%description
A QMF accessible configuration store.

%package utils
Summary: Configuration store utilities
Group: Applications/System
Requires: ruby(abi) = 1.8
Requires: ruby
Requires: ruby-qmf >= 0.7.929717
Requires: ruby-wallaby

%description utils
Utilities for interacting with wallaby

%package -n ruby-wallaby
Summary: wallaby qmf api methods
Group: Applications/System
Requires: ruby(abi) = 1.8
Requires: ruby
Requires: ruby-irb
Requires: ruby-qmf >= 0.7.929717
BuildRequires: ruby

%if 0%{?fedora} >= 12
%package -n wallaby-http-server
Summary: wallaby web service
Group: Applications/System
Requires: ruby(abi) = 1.8
Requires: ruby
Requires: ruby-irb
Requires: ruby-qmf >= 0.7.929717
Requires: ruby-wallaby = %{version}-%{release}
Requires: wallaby-utils = %{version}-%{release}
Requires: rubygem-sinatra
BuildRequires: ruby

%description -n wallaby-http-server
Functions to communicate with wallaby over qmf
%endif

%description -n ruby-wallaby
Functions to communicate with wallaby over qmf

%prep
%setup -q

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}/%{ruby_sitelib}/mrg/grid/config/dbmigrate
mkdir -p %{buildroot}/%{ruby_sitelib}/mrg/grid/config/shell
mkdir -p %{buildroot}/%{ruby_sitelib}/mrg/grid/util
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_localstatedir}/lib/wallaby
mkdir -p %{buildroot}/%{_initrddir}
mkdir -p %{buildroot}/%{_sysconfdir}
mkdir -p %{buildroot}/%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}/%{_localstatedir}/log/wallaby
cp -f bin/wallaby %{buildroot}/%{_bindir}
cp -f bin/wallaby-agent %{buildroot}/%{_bindir}
cp -f lib/mrg/grid/*.rb %{buildroot}/%{ruby_sitelib}/mrg/grid
cp -f lib/mrg/grid/util/*.rb %{buildroot}/%{ruby_sitelib}/mrg/grid/util
cp -f lib/mrg/grid/config/*.rb %{buildroot}/%{ruby_sitelib}/mrg/grid/config
cp -f lib/mrg/grid/config/shell/*.rb %{buildroot}/%{ruby_sitelib}/mrg/grid/config/shell
# These aren't packaged
rm -f %{buildroot}/%{ruby_sitelib}/mrg/grid/config/shell/cmd_force_pull.rb
rm -f %{buildroot}/%{ruby_sitelib}/mrg/grid/config/shell/cmd_force_restart.rb
%if 0%{?fedora} < 12
# XXX: change this when Sinatra is packaged for RHEL
rm -f %{buildroot}/%{ruby_sitelib}/mrg/grid/config/shell/cmd_http_server.rb
%endif
cp -f lib/mrg/grid/config/dbmigrate/*.rb %{buildroot}/%{ruby_sitelib}/mrg/grid/config/dbmigrate
cp -f etc/wallaby %{buildroot}/%{_initrddir}/wallaby
cp -f etc/sysconfig/wallaby-agent %{buildroot}/%{_sysconfdir}/sysconfig/wallaby-agent

%clean
rm -rf %{buildroot}

%files
%defattr(-, root, root, -)
%doc LICENSE README.rdoc TODO
%defattr(0755,wallaby,wallaby,-)
%dir %{_localstatedir}/lib/wallaby
%dir %{_localstatedir}/log/wallaby
%defattr(0755,root,root,-)
%{_bindir}/wallaby-agent
%{_initrddir}/wallaby
%config(noreplace) %{_sysconfdir}/sysconfig/wallaby-agent

%pre
getent group wallaby >/dev/null || groupadd -r wallaby
getent passwd wallaby >/dev/null || \
  useradd -r -g condor -d %{_localstatedir}/lib/wallaby -s /sbin/nologin \
    -c "Owner of Wallaby service" wallaby

%post
# This adds the proper /etc/rc*.d links for the script
/sbin/chkconfig --add wallaby

%preun
if [ $1 = 0 ] ; then
    /sbin/service wallaby stop >/dev/null 2>&1
    /sbin/chkconfig --del wallaby
fi

%postun
if [ "$1" -ge "1" ] ; then
    /sbin/chkconfig --del wallaby
    /sbin/chkconfig --add wallaby
    chown -R wallaby:wallaby /var/lib/wallaby /var/log/wallaby
    /sbin/service wallaby condrestart >/dev/null 2>&1 || :
fi

%files utils
%defattr(-, root, root, -)
%doc LICENSE
%defattr(0755,root,root,-)
%{_bindir}/wallaby

%files -n ruby-wallaby
%defattr(-, root, root, -)
%{ruby_sitelib}/mrg/grid/config.rb
%{ruby_sitelib}/mrg/grid/config-client.rb
%{ruby_sitelib}/mrg/grid/config-proxies.rb
%{ruby_sitelib}/mrg/grid/config/ArcLabel.rb
%{ruby_sitelib}/mrg/grid/config/ArcUtils.rb
%{ruby_sitelib}/mrg/grid/config/Configuration.rb
%{ruby_sitelib}/mrg/grid/config/ConfigValidating.rb
%{ruby_sitelib}/mrg/grid/config/DirtyElement.rb
%{ruby_sitelib}/mrg/grid/config/DataValidating.rb
%{ruby_sitelib}/mrg/grid/config/Feature.rb
%{ruby_sitelib}/mrg/grid/config/Group.rb
%{ruby_sitelib}/mrg/grid/config/InconsistencyDetecting.rb
%{ruby_sitelib}/mrg/grid/config/Node.rb
%{ruby_sitelib}/mrg/grid/config/NodeMembership.rb
%{ruby_sitelib}/mrg/grid/config/Parameter.rb
%{ruby_sitelib}/mrg/grid/config/QmfUtils.rb
%{ruby_sitelib}/mrg/grid/config/Snapshot.rb
%{ruby_sitelib}/mrg/grid/config/Store.rb
%{ruby_sitelib}/mrg/grid/config/Subsystem.rb
%{ruby_sitelib}/mrg/grid/config/dbmeta.rb
%{ruby_sitelib}/mrg/grid/config/errors.rb
%{ruby_sitelib}/mrg/grid/config/version.rb
%{ruby_sitelib}/mrg/grid/config/dbmigrate/1.rb
%{ruby_sitelib}/mrg/grid/config/dbmigrate/2.rb
%{ruby_sitelib}/mrg/grid/config/dbmigrate/3.rb
%{ruby_sitelib}/mrg/grid/config/dbmigrate/4.rb
%{ruby_sitelib}/mrg/grid/config/dbmigrate/5.rb
%{ruby_sitelib}/mrg/grid/util/graph.rb
%{ruby_sitelib}/mrg/grid/util/daemon.rb
%{ruby_sitelib}/mrg/grid/config/shell.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_apropos.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_console.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_explain.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_help.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_load.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_param.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_feature.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_node.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_new_command.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_feature_import.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_sanitize.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_snapshot.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_inventory.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_dump.rb
%{ruby_sitelib}/mrg/grid/config/shell/cmd_activate.rb
%{ruby_sitelib}/mrg/grid/config/shell/entity_ops.rb
%{ruby_sitelib}/mrg/grid/config/shell/command.rb
%{ruby_sitelib}/mrg/grid/config/shell/skel.rb


%if 0%{?fedora} >= 12
%files -n wallaby-http-server
%defattr(-, root, root, -)
%{ruby_sitelib}/mrg/grid/config/shell/cmd_http_server.rb
%endif

%changelog

* Thu Mar 31 2011 willb <willb@redhat> - 0.10.5-3
- Changes to default broker authentication

* Wed Mar 30 2011 willb <willb@redhat> - 0.10.5-2
- Minor cleanups to Ruby client library
- "wallaby" and shell commands now understand "-v"

* Fri Feb 4 2011 willb <willb@redhat> - 0.10.5
- Fixes BZ 675324

* Fri Jan 28 2011 willb <willb@redhat> - 0.10.4-3
- Fixes BZs 635628 (was bounced), 673502

* Thu Jan 27 2011 willb <willb@redhat> - 0.10.4-2
- Fixes BZs 668798, 668799

* Tue Jan 25 2011 willb <willb@redhat> - 0.10.4-1
- Fixes BZ 669829
- Automatic cleanup for spuriously-generated versioned snapshots

* Fri Jan 21 2011 willb <willb@redhat> - 0.10.3-1
- Added "wallaby sanitize" shell command (for ease of submitting bug reports)
- Fixes for "wallaby new-command" code generation
- Fixes BZ 671185

* Tue Jan 11 2011 willb <willb@redhat> - 0.10.2-1
- Fixes a small regression introduced in 0.10.1

* Tue Jan 11 2011 willb <willb@redhat> - 0.10.1-1
- Fixes BZs 668459, 668797, 668798, 668799, 668800, 668802, 668803.

* Thu Dec 23 2010 willb <willb@redhat> - 0.10.0-2
- Fix for a stray SQLite 3.3 incompatibility

* Tue Dec 14 2010 willb <willb@redhat> - 0.10.0-1
- verification for BZs 654810, 654813
- minor contract change:  Parameter#setMustChange will fail if the parameter has a default value unless WALLABY_PERMISSIVE_PARAMETERS is set
- optimizations to config validation (~7% faster in test suite)
- fixes BZ 660509
- config client objects now support to_hash and to_yaml methods
- new api methods and properties
- wallaby shell support for feature CRUD operations

* Sat Dec 4 2010 willb <willb@redhat> - 0.9.24-1
- fixes BZ 657055

* Thu Oct 21 2010 willb <willb@redhat> - 0.9.23-1
- "wallaby new-command" shell command
- improved exception handling in shell commands
- fixes for user-local commands
- fixed BZ 635628

* Wed Oct 20 2010 willb <willb@redhat> - 0.9.22-1
- re-implemented timestamp; removed rhubarb dependency from wallaby shell commands

* Wed Oct 20 2010 willb <willb@redhat> - 0.9.21-1
- Fixes for many shell-related BZs, including 635975, 636161, 636172, 636175, 636177, 636179, 636568, 636569, 636577, 636580.
- First pass at a public shell-command API (see skel.rb for an example); this should be finalized in 0.10.x
- "wallaby help" shell command
- Various refactorings.

* Fri Oct 15 2010 willb <willb@redhat> - 0.9.20-1
- Parameter names are now case-preserving but case-insensitive, viz., adding "fooBar" and searching for "FOOBAR" will get you "fooBar"
- 'wallaby http-server' improvements:  runs as daemon (and optionally as a different user); changes-to and help routes

* Thu Oct 14 2010 willb <willb@redhat> - 0.9.19-1
- More flexible support for user-local wallaby shell commands (no public API yet, though)
- 'wallaby explain' shell command
- 'wallaby http-server' shell command and package (Fedora only; requires Sinatra)

* Fri Sep 17 2010 willb <willb@redhat> - 0.9.18-2
- package upgrades should uninstall and reinstall the wallaby initscript in the appropriate runlevels

* Fri Sep 17 2010 willb <willb@redhat> - 0.9.18-1
- fix for BZ 634641

* Thu Sep 16 2010 willb <willb@redhat> - 0.9.17-1
- fix for BZ 634625

* Thu Sep 16 2010 willb <willb@redhat> - 0.9.16-2
- fixed missing RPM dependency on ruby-irb

* Wed Sep 15 2010 willb <willb@redhat> - 0.9.16-1
- fixed missing include in wallaby inventory

* Wed Sep 15 2010 willb <willb@redhat> - 0.9.15-2
- fixed performance regression in querying groups
- bumped API version number to final (1.0) version
- fixes for relationship-maintenance issues uncovered in 0.9.8

* Fri Sep 10 2010 willb <willb@redhat> - 0.9.8-1
- Dramatic performance enhancements in activateConfiguration (> 10x in medium-size configurations; > 21x in large configurations)
- wallaby console tool

* Wed Sep 1 2010 willb <willb@redhat> - 0.9.7-1
- Improved wallaby-shell functionality
- Removed old-style command-line tools

* Wed Aug 25 2010 willb <willb@redhat> - 0.9.6-1
- Improved reliability of command-line tools
- Workarounds for BZS 612425, 613666

* Tue Aug 17 2010 willb <willb@redhat> - 0.9.5-1
- Updated to source version 0.9.5
- Improved memory performance of proactive inconsistency detection

* Mon Aug 16 2010 willb <willb@redhat> - 0.9.4-1
- Updated to source version 0.9.4

* Mon Aug 16 2010 willb <willb@redhat> - 0.9.3-1
- Updated to source version 0.9.3

* Tue Aug 3 2010 willb <willb@redhat> - 0.9.2-1
- Updated to source version 0.9.2

* Tue Aug 3 2010 willb <willb@redhat> - 0.9.1-1
- Updated to source version 0.9.1

* Mon Aug 2 2010 willb <willb@redhat> - 0.9.0-1
- Updated to source version 0.9.0

* Tue Jul 27 2010 willb <willb@redhat> - 0.6.3-1
- Updated to source version 0.6.3

* Fri Jun 25 2010 willb <willb@redhat> - 0.6.2-1
- Updated to source version 0.6.2

* Fri Jun 25 2010 rrati <rrati@redhat> - 0.6.1-2
- Packaging fixes

* Fri Jun 25 2010 rrati <rrati@redhat> - 0.6.1-1
- Updated to source version 0.6.1

* Wed Jun 23 2010 willb <willb@redhat> - 0.6.0-1
- Updated to source version 0.6.0
- Init script fixes

* Fri Jun 11 2010 willb <willb@redhat> - 0.5.1-1
- Updated to source version 0.5.1

* Fri Jun 11 2010 willb <willb@redhat> - 0.5.0-1
- Updated to source version 0.5.0

* Thu Jun 10 2010 willb <willb@redhat> - 0.4.2-1
- Updated to source version 0.4.2

* Thu Jun 10 2010 willb <willb@redhat> - 0.4.1-1
- Updated to source version 0.4.1

* Thu Jun 10 2010 willb <willb@redhat> - 0.4.0-1
- Updated to source version 0.4.0

* Wed May 26 2010 willb <willb@redhat> - 0.3.5-2
- Packaging and initscript fixes

* Fri May 21 2010 willb <willb@redhat> - 0.3.5-1
- Updated to source version 0.3.5

* Tue Apr 20 2010 willb <willb@redhat> - 0.3.2-1
- Updated to source version 0.3.2

* Mon Apr 12 2010 willb <willb@redhat> - 0.3.1-1
- Updated to source version 0.3.1

* Fri Apr 9 2010 willb <willb@redhat> - 0.3.0-1
- Updated to source version 0.3.0

* Tue Mar 30 2010 willb <willb@redhat> - 0.2.12-1
- Updated to source version 0.2.12

* Thu Mar 25 2010 willb <willb@redhat> - 0.2.11-1
- Updated to source version 0.2.11

* Tue Mar 9 2010 willb <willb@redhat> - 0.2.10-1
- Updated to source version 0.2.10

* Fri Mar 5 2010 willb <willb@redhat> - 0.2.9-1
- Updated to source version 0.2.9

* Thu Mar 4 2010 willb <willb@redhat> - 0.2.8-1.0
- Updated to source version 0.2.8

* Fri Feb 27 2010 willb <willb@redhat> - 0.2.7-1.0
- Updated to source version 0.2.7

* Thu Feb 26 2010 willb <willb@redhat> - 0.2.6-1.0
- Updated to source version 0.2.6

* Wed Feb 25 2010 willb <willb@redhat> - 0.2.5-1.0
- Updated to source version 0.2.5

* Wed Feb 25 2010 willb <willb@redhat> - 0.2.4-1.0
- Updated to source version 0.2.4

* Tue Feb 23 2010 willb <willb@redhat> - 0.2.3-1.0
- Updated to source version 0.2.3

* Tue Feb 23 2010 rrati <rrati@redhat> - 0.2.2-1.0
- Updated to source version 0.2.2

* Tue Feb 23 2010 rrati <rrati@redhat> - 0.2.1-1.0
- Updated to source version 0.2.1

* Fri Feb 19 2010 willb <willb@redhat> - 0.2.0-1.0
- Event functionality
- Configuration activation
- wallaby-activate tool

* Wed Feb 10 2010 rrati <rrati@redhat> - 0.1.0-0.1
- Initial package
