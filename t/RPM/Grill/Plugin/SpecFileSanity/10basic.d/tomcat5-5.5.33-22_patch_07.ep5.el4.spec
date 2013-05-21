# Copyright (c) 2000-2008, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

%define _with_repolib 1
%define with_signing 1
%define patchnumber 07
%define patchlevel -patch-%{patchnumber}
%define release_patchlevel _patch_%{patchnumber}

%define _with_zips 1
# If you want to build the zips,
# give rpmbuild option '--with zips'

%define with_zips %{?_with_zips:1}%{!?_with_zips:0}
%define without_zips %{!?_with_zips:1}%{?_with_zips:0}

# If you want repolib package to be built,
# issue the following: 'rpmbuild --with repolib'
%define with_repolib %{?_with_repolib:1}%{!?_with_repolib:0}
%define without_repolib %{!?_with_repolib:1}%{?_with_repolib:0}

%define repodir %{_javadir}/repository.jboss.com/apache-tomcat/%{version}%{patchlevel}-brew
%define repodirlib %{repodir}/lib
%define repodirsrc %{repodir}/src

# XXX:
# Note that 5.5.28-0jpp* is a port of tomcat5-5.5.23-6jpp to the existing
# 5.5.17 spec. This is so that the core tomcat5 codebase can be upgraded
# without requiring additional/newer thirdparty dependencies

# XXX:
# Note that the files matching the following globs have been removed:
#  /var/tmp/tomcat5-0-5.5.28-0jpp.1-root/usr/lib/gcj/tomcat5/applet*
#  /var/tmp/tomcat5-0-5.5.28-0jpp.1-root/usr/lib/gcj/tomcat5/jsp-examples*
#  /var/tmp/tomcat5-0-5.5.28-0jpp.1-root/usr/lib/gcj/tomcat5/sample*
#  /var/tmp/tomcat5-0-5.5.28-0jpp.1-root/usr/lib/gcj/tomcat5/servlets-examples*
#  /var/tmp/tomcat5-0-5.5.28-0jpp.1-root/usr/lib/gcj/tomcat5/servlets-cgi*
#  /var/tmp/tomcat5-0-5.5.28-0jpp.1-root/usr/lib/gcj/tomcat5/servlets-ssi*


%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}
# If you want only apis to be built,
# give rpmbuild option '--with apisonly'

%define with_apisonly %{?_with_apisonly:1}%{!?_with_apisonly:0}
%define without_apisonly %{!?_with_apisonly:1}%{?_with_apisonly:0}

# If you don't want direct ecj support to be built in,
# while eclipse-ecj isn't available,
# give rpmbuild option '--without ecj'

%define without_ecj %{?_without_ecj:1}%{!?_without_ecj:0}
%define with_ecj %{!?_without_ecj:1}%{?_without_ecj:0}

%define full_jname jasper5
%define jname jasper
%define majversion 5.5
%define minversion 33
%define servletspec 2.4
%define jspspec 2.0

%define tcuid 91

%define packdname apache-tomcat-%{version}-src

# FHS 2.2 compliant tree structure
# see http://www.pathname.com/fhs/2.2/
%define confdir %{_sysconfdir}/%{name}
# normally this would be _localstatedir instead of _var, see changelog
%define logdir %{_var}/log/%{name}
%define homedir %{_datadir}/%{name}
%define bindir %{_datadir}/%{name}/bin
%define tempdir %{_var}/cache/%{name}/temp
%define workdir %{_var}/cache/%{name}/work
%define appdir %{_var}/lib/%{name}/webapps
%define serverdir %{_var}/lib/%{name}/server
%define commondir %{_var}/lib/%{name}/common
%define shareddir %{_var}/lib/%{name}/shared
%define _initrddir %{_sysconfdir}/init.d

Name: tomcat5
Epoch: 0
Version: %{majversion}.%{minversion}
# XXX:
# 0jpp.1.0.x.el5 <-> 0jpp.2.el5 <-> 0jpp_4rh (RHAPS) <-> 0jpp_5rh (DevSuite)
# When patchnumber is non-zero add %{release_patchnumber} so the 
# release string looks like X%{release_patchlevel}%{?dist}
Release: 22%{release_patchlevel}%{?dist}
Summary: Apache Servlet/JSP Engine, RI for Servlet 2.4/JSP 2.0 API

Group: Networking/Daemons
License: ASL 2.0
URL: http://tomcat.apache.org
Source0: http://www.apache.org/dist/tomcat/tomcat-5/v%{version}/src/%{packdname}.tar.gz
Source1: %{name}-%{majversion}.init
Source2: %{name}-%{majversion}.conf
Source3: %{name}-%{majversion}.wrapper
Source4: %{name}-%{majversion}.logrotate
Source5: %{name}-%{majversion}.relink
Source6: %{name}-5.5.28-component-info.xml
# The jsvc.tar.gz is only availble in the binary zip from apache.org
# wget http://www.apache.org/dist/tomcat/tomcat-5/v5.5.28/bin/apache-tomcat-5.5.28.zip
# unzip apache-tomcat-5.5.28.zip apache-tomcat-5.5.28/bin/jsvc.tar.gz
# mv apache-tomcat-5.5.28/bin/jsvc.tar.gz tomcat5-5.5.28-jsvc.tar.gz
# Source7: %{name}-%{version}-jsvc.tar.gz
# NOTE: 7 Jan 2011: Tomcat5.5.31 binary doesn't provide jsvc.tar.gz. 
Source7: %{name}-5.5.28-jsvc.tar.gz
Source8: %{name}-%{majversion}-src-build.properties
Source9: %{name}-poms-%{version}.tar.bz2
Source10: jasper-OSGi-MANIFEST.MF
Source11: servlet-api-OSGi-MANIFEST.MF
Source12: jsp-api-OSGi-MANIFEST.MF
Source13: %{name}-5.5.33.policy
Source14: %{name}-5.5.33.JBossPublicKey.RSA

Source99: sign-unsigned-jars

Patch0: %{name}-%{majversion}.link_admin_jar.patch
Patch1: %{name}-%{majversion}-skip-build-on-install.patch
Patch2: %{name}-%{majversion}-jt5-build.patch
Patch3: %{name}-%{majversion}-jtc-build.patch
Patch4: %{name}-%{majversion}-jtj-build.patch
# File JSSE13* does not exist since 5.5.33. The code in the patch is now
# in JSSE14SocketFactory and JSSE15SocketFactory
#Patch5: %{name}-%{majversion}-javaxssl.patch
Patch7: %{name}-%{majversion}-catalina.sh.patch
Patch8: %{name}-%{majversion}-jasper.sh.patch
Patch9: %{name}-%{majversion}-jspc.sh.patch
Patch10: %{name}-%{majversion}-setclasspath.sh.patch
Patch12: %{name}-%{majversion}-util-build.patch
Patch13: %{name}-%{majversion}-http11-build.patch
Patch14: %{name}-%{majversion}-jk-build.patch
Patch15: %{name}-%{majversion}-skip-native.patch
Patch16: %{name}-%{majversion}-jspc-classpath.patch
# commented in run list Patch17: %{name}-%{majversion}-gcj-class-init-workaround.patch
#FIXME Disable JSP pre-compilation on ppc64 and x390x
Patch18: %{name}-%{majversion}-skip-jsp-precompile.patch
# The following patch reverses a fix for a memory leak:
# https://issues.apache.org/jira/browse/MODELER-15 that forces the use of
# j-c-modeler-2.x
# Not needed for the JBoss version
#Patch19: %{name}-%{version}-WebappClassLoader-commons-modeler.patch
Patch20: %{name}-%{majversion}-unversioned-commons-logging-jar.patch
# XXX:
# Seems to be only needed when building with ECJ for java 1.5 since
# the default source type for ecj is still 1.4
Patch21: %{name}-%{majversion}-connectors-util-build.patch
# Awkward eclipse version :\
Patch25: %{name}-5.5.28-build-build-properties-default.patch
# Fix for IT #168408
Patch28: tomcat5-5.5.23-IT-168408.patch
Patch33: %{name}-5.5.28-jdtcore.patch
Patch34: %{name}-%{majversion}-build.patch
Patch35: %{name}-5.5.28-sh.patch
# Code in place Patch36: %{name}-5.5.28-load-tcnative.patch
# 12 Jan 2011: Not needed since 5.5.31 contains 37, 38, & 39
# Patch37: %{name}-%{version}-CVE-2009-2693-2901-2902.patch
# Patch38: %{name}-%{version}-CVE-2009-3555-workaround.patch
# Patch39: %{name}-%{version}-CVE-2010-2227.patch
# Resolves JIRA JBAPP 3626
Patch40: %{name}-%{majversion}-hostmanager-welcomefiles-webxml.patch
# Resolves JIRA JBAPP 3627
Patch41: %{name}-%{majversion}-host-manager_help_link.patch
# Patches added for tc 5.5.31 rebase
# Not needed in 5.5.33 Patch42: %{name}-5.5.31-build-properties-default-full-dist-off.patch
Patch43: %{name}-5.5.31-turn_off_native_windows_copy_in_dist-static.patch
#  Do not use crlf in src-zip. Effects build.xml
Patch44: %{name}-5.5.31-stripcrlf.patch
Patch45: tomcat-native-fail-on-error-false.patch
# JBPAPP-3749 applied to zip package only
#Patch46: tomcat5-5.5.33-jbpapp3749-catalina.sh.patch
#JBPAPP-6122 conf hints for JON
Patch47: tomcat5-5.5-jbpapp-6122-jon.patch
Patch48: tomcat5-5.5.33-CVE-2011-2204-rhbz717013.patch
Patch49: tomcat5-5.5.33-CVE-2011-2526-rhbz720948.patch
Patch50: tomcat5-5.5.33-CVE-2011-3190-rhbz-738505.patch
Patch51: tomcat5-5.5.33-CVE-2011-1184-rhbz-738505.patch
Patch52: tomcat5-5.5.33-cve-2012-0022.patch





BuildRoot: %{_tmppath}/%{name}-%{epoch}-%{version}-%{release}-root
%if ! %{gcj_support}
BuildArch: noarch
%endif

Requires: jpackage-utils >= 0:1.6.0
# xml parsing packages
Requires: xerces-j2 >= 0:2.9.1
Requires: xml-commons-apis >= 1.3.04
# jakarta-commons packages
Requires: jakarta-commons-daemon >= 0:1.0.5
Requires(post): jakarta-commons-daemon >= 0:1.0.5
Requires: jakarta-commons-launcher >= 0:1.1
# alternatives
Requires: java-devel >= 0:1.6.0
# And it needs its own API subpackages for running
Requires: %{name}-common-lib = %{epoch}:%{version}-%{release}
Requires: %{name}-server-lib = %{epoch}:%{version}-%{release}
# And it needs its own API subpackages before being installed
Requires(post): %{name}-common-lib = %{epoch}:%{version}-%{release}
Requires(post): %{name}-server-lib = %{epoch}:%{version}-%{release}

BuildRequires: jpackage-utils >= 0:1.6.0
BuildRequires: ant >= 0:1.7.1
%if %{with_apisonly}
BuildRequires: java-devel >= 0:1.4.2
%else
BuildRequires: java-devel >= 0:1.5.0
%endif
%if %{without_apisonly}
%if %{with_ecj}
BuildRequires: ecj >= 1:3.3.1.1
Requires: ecj >= 1:3.3.1.1
%endif
BuildRequires: ant-trax
BuildRequires: xalan-j2 >= 2.7.1
BuildRequires: jakarta-commons-beanutils >= 0:1.8.0
BuildRequires: jakarta-commons-collections >= 0:3.2.1
BuildRequires: jakarta-commons-chain >= 0:1.2
BuildRequires: jakarta-commons-daemon >= 0:1.0.5
BuildRequires: jakarta-commons-dbcp >= 0:1.2.1
BuildRequires: jakarta-commons-dbcp-tomcat5
BuildRequires: jakarta-commons-digester >= 0:1.8.1
BuildRequires: jakarta-commons-logging >= 0:1.1.1
BuildRequires: jakarta-commons-io >= 0:1.4
#BuildRequires: jakarta-commons-io >= 0:1.4
BuildRequires: jakarta-commons-fileupload >= 0:1.1.1
BuildRequires: jakarta-commons-modeler >= 0:2.0-4
BuildRequires: jakarta-commons-pool >= 0:1.3
BuildRequires: jakarta-commons-launcher >= 0:1.1
BuildRequires: jakarta-commons-el >= 0:1.0
BuildRequires: jaas
BuildRequires: jdbc-stdext >= 0:2.0
BuildRequires: jndi >= 0:1.2.1
BuildRequires: jndi-ldap
BuildRequires: jsse >= 0:1.0.3
BuildRequires: junit >= 0:3.8.1
BuildRequires: mx4j >= 0:3.0.1
BuildRequires: regexp >= 0:1.5
BuildRequires: struts12 >= 1.2.9
BuildRequires: xerces-j2 >= 0:2.9.1
# zip utility must be specified. unzip is provided by the env
BuildRequires: zip
# xml-commons-apis is needed by Xerces-J2
BuildRequires: xml-commons-apis >= 1.3.04
# FIXME taglibs-standard is not listed in the Tomcat build.properties.default
BuildRequires: jakarta-taglibs-standard >= 0:1.1.1-9
# formerly non-free stuff
# geronimo-specs replaces non-free jta
BuildRequires: jboss-transaction-1.0.1-api
#BuildRequires: jta >= 0:1.0.1
# jaf can be provided by classpathx-jaf
#BuildRequires: jaf >= 0:1.0.2
BuildRequires: glassfish-jaf >= 1.1.0
# javamail can be provided by classpathx-mail
#BuildRequires: javamail >= 0:1.3.3
BuildRequires: glassfish-javamail >= 0:1.4.2
# for the zip
BuildRequires: jakarta-commons-collections-tomcat5
BuildRequires: jakarta-commons-pool-tomcat5
BuildRequires: jakarta-commons-dbcp-tomcat5
# libgcj aot-compiled native libraries
%if %{gcj_support}
BuildRequires:    	java-gcj-compat-devel >= 1.0.43
Requires(post):   	java-gcj-compat >= 1.0.31
Requires(postun): 	java-gcj-compat >= 1.0.31
%endif
%endif


%description
Tomcat is the servlet container that is used in the official Reference
Implementation for the Java Servlet and JavaServer Pages technologies.
The Java Servlet and JavaServer Pages specifications are developed by
Sun under the Java Community Process.

Tomcat is developed in an open and participatory environment and
released under the Apache Software License. Tomcat is intended to be
a collaboration of the best-of-breed developers from around the world.
We invite you to participate in this open development project. To
learn more about getting involved, click here.

%if %{with_zips}
%package zip
Summary:     Container for the zipped distribution of tomcat5
Group:       Development

%description zip
Container for the zipped distribution of tomcat5.

%package src-zip
Summary:     Container for the sources
Group:       Development

%description src-zip
Container for the sources.
%endif

%if %{without_apisonly}
%if %{with_repolib}
%package	 repolib
Summary:	 Artifacts to be uploaded to a repository library
Group:	Development/Libraries/Java

%description	 repolib
Artifacts to be uploaded to a repository library.
This package is not meant to be installed but so its contents
can be extracted through rpm2cpio
%endif

%package webapps
Group: System Environment/Applications
# Replace PreReq
Requires(pre): %{name} = %{epoch}:%{version}-%{release}
Requires(postun): %{name} = %{epoch}:%{version}-%{release}
Requires: jakarta-taglibs-standard >= 0:1.1.1-9
Summary: Web applications for Apache Tomcat
Requires(post): jpackage-utils
Requires(preun): findutils
Requires(preun): coreutils

%description webapps
Web applications for Apache Tomcat

%package admin-webapps
Group: System Environment/Applications
Summary: Administrative web applications for Apache Tomcat
Requires(pre): %{name} = %{epoch}:%{version}-%{release}
Requires(postun): %{name} = %{epoch}:%{version}-%{release}
Requires: struts12
Requires(post): /bin/rm
Requires(post): jpackage-utils
Requires(post): findutils
Requires(post): jakarta-commons-beanutils >= 1.8.0
Requires(post): jakarta-commons-chain >= 0:1.2
Requires(post): jakarta-commons-collections >= 3.2.1
Requires(post): jakarta-commons-digester >= 1.8.1
Requires(post): jakarta-commons-io >= 1.4
Requires(post): struts12
Requires(preun): findutils
Requires(preun): /bin/rm

%description admin-webapps
The administrative web applications (admin and manager) for Apache Tomcat.
%endif

%package servlet-%{servletspec}-api
Group: Internet/WWW/Dynamic Content
Requires: %{_sbindir}/update-alternatives
Summary: Apache Tomcat Servlet implementation classes
Obsoletes: servletapi5
Provides: servlet
Provides: servlet5
Provides: servlet24
Provides: servletapi5
Provides: servlet_2_4_api

%description servlet-%{servletspec}-api
Contains the implementation classes
of the Apache Tomcat Servlet API (packages javax.servlet).

%package servlet-%{servletspec}-api-javadoc
Group: Development/Documentation
Summary: Javadoc generated documentation for %{name}-servlet-%{servletspec}-api
Obsoletes: servletapi5-javadoc
Provides: servletapi5-javadoc
Requires(post): coreutils
Requires(postun): coreutils

%description servlet-%{servletspec}-api-javadoc
Contains the javadoc generated documentation for the implementation classes
of the Apache Tomcat Servlet and JSP APIs (packages javax.servlet).

%package jsp-%{jspspec}-api
Group: Internet/WWW/Dynamic Content
Requires: %{_sbindir}/update-alternatives
Requires: %{name}-servlet-%{servletspec}-api = %{epoch}:%{version}-%{release}
# We need this to indirectly get rid of legacy jsp included in old
# servlet packages (one day we will be able to remove this)
# Replace PreReq
Requires(pre): %{name}-servlet-%{servletspec}-api = %{epoch}:%{version}-%{release}
Requires(postun): %{name}-servlet-%{servletspec}-api = %{epoch}:%{version}-%{release}
Summary: Apache Tomcat Servlet and JSP implementation classes
Provides: jsp
Provides: jsp_2_0_api

%description jsp-%{jspspec}-api
Contains the implementation classes
of the Apache Tomcat JSP API (packages javax.servlet.jsp).

%package jsp-%{jspspec}-api-javadoc
Group: Development/Documentation
Summary: Javadoc generated documentation for %{name}-jsp-%{jspspec}-api
Requires(post): coreutils
Requires(postun): coreutils

%description jsp-%{jspspec}-api-javadoc
Contains the javadoc generated documentation for the implementation classes
of the Apache Tomcat JSP API (packages javax.servlet.jsp).

%if %{without_apisonly}
%package common-lib
Group: Development/Compilers
Summary: Libraries needed to run the Tomcat Web container (part)
Requires: java >= 0:1.6.0
Requires(post): jpackage-utils >= 0:1.6.0
Requires: ant >= 0:1.7.1
Requires(post): ant >= 0:1.7.1
Requires: jakarta-commons-collections-tomcat5 >= 0:3.1
Requires(post): jakarta-commons-collections-tomcat5 >= 0:3.1
Requires: jakarta-commons-dbcp-tomcat5 >= 0:1.2.1
Requires(post): jakarta-commons-dbcp-tomcat5 >= 0:1.2.1
Requires: jakarta-commons-el >= 0:1.0
Requires(post): jakarta-commons-el >= 0:1.0
Requires: jakarta-commons-logging >= 0:1.1.1
Requires(post): jakarta-commons-logging >= 0:1.1.1
# FIXME commons-pool is not listed in the Tomcat build.properties.default
Requires: jakarta-commons-pool-tomcat5 >= 0:1.2
Requires(post): jakarta-commons-pool-tomcat5 >= 0:1.2
# jaf can be provided by classpathx-jaf
Requires: glassfish-jaf >= 0:1.1.0
Requires(post): glassfish-jaf >= 0:1.1.0
# javamail can be provided by classpathx-mail
Requires: glassfish-javamail >= 0:1.4.2
Requires(post): glassfish-javamail >= 0:1.4.2
Requires: jdbc-stdext
Requires(post): jdbc-stdext
Requires: jndi
Requires(post): jndi
# geronimo-specs replaces non-free jta
#Requires: geronimo-jta-1.0.1B-api
Requires: jboss-transaction-1.0.1-api
#Requires(post): geronimo-jta-1.0.1B-api
Requires(post): jboss-transaction-1.0.1-api
Requires: mx4j >= 0:3.0.1
Requires(post): mx4j >= 0:3.0.1
%if %{with_ecj}
Requires: ecj >= 1:3.3.1.1
Requires(post): ecj >= 1:3.3.1.1
%endif
# Other subpackages must go in first
Requires(post): %{name}-servlet-%{servletspec}-api = %{epoch}:%{version}-%{release}
Requires(post): %{name}-jsp-%{jspspec}-api = %{epoch}:%{version}-%{release}
Requires(post): %{name}-%{jname} = %{epoch}:%{version}-%{release}
Requires: %{name}-servlet-%{servletspec}-api = %{epoch}:%{version}-%{release}
Requires: %{name}-jsp-%{jspspec}-api = %{epoch}:%{version}-%{release}
Requires: %{name}-%{jname} = %{epoch}:%{version}-%{release}
Requires(post): findutils
Requires(preun): findutils
Requires(post): coreutils
Requires(preun): coreutils

%description common-lib
Libraries needed to run the Tomcat Web container (part)

%package server-lib
Group: Development/Compilers
Summary: Libraries needed to run the Tomcat Web container (part)
Requires(post): jpackage-utils >= 0:1.6.0
Requires: jakarta-commons-beanutils >= 0:1.8.0
Requires(post): jakarta-commons-beanutils >= 0:1.8.0
Requires: jakarta-commons-digester >= 0:1.8.1
Requires(post): jakarta-commons-digester >= 0:1.8.1
Requires: jakarta-commons-el >= 0:1.0
Requires(post): jakarta-commons-el >= 0:1.0
#Requires: jakarta-commons-fileupload >= 0:1.1.1jpp
Requires: jakarta-commons-fileupload >= 0:1.1.1
Requires(post): jakarta-commons-fileupload >= 0:1.1.1
Requires: jakarta-commons-logging >= 0:1.1.1
Requires(post): jakarta-commons-logging >= 0:1.1.1
Requires: jakarta-commons-modeler >= 2.0-4
Requires(post): jakarta-commons-modeler >= 2.0-4
Requires: jaas
Requires(post): jaas
Requires: mx4j >= 0:3.0.1
Requires(post): mx4j >= 0:3.0.1
Requires: regexp >= 0:1.5
Requires(post): regexp >= 0:1.5
# Other subpackages must go in first
Requires: %{name}-%{jname} = %{epoch}:%{version}-%{release}
Requires(post): %{name}-%{jname} = %{epoch}:%{version}-%{release}
Requires(post): findutils
Requires(preun): findutils
Requires(post): coreutils
Requires(preun): coreutils

%description server-lib
Libraries needed to run the Tomcat Web container (part)

%package %{jname}
Group: Development/Compilers
Requires: %{name}-servlet-%{servletspec}-api = %{epoch}:%{version}-%{release}
Summary: Compiler JARs and associated scripts for %{name}
Obsoletes: jasper5
Provides: jasper5

%description %{jname}
Compiler JARs and associated scripts for %{name}

%package %{jname}-javadoc
Group: Development/Documentation
Summary: Javadoc generated documentation for %{name}-%{jname}
Obsoletes: jasper5-javadoc
Provides: jasper5-javadoc

%description %{jname}-javadoc
Javadoc for generated documentation %{name}-%{jname}
%endif

%if %{with_ecj}
%package jasper-eclipse
Group: Text Editors/Integrated Development Environments (IDE)
Summary: Jasper OSGi Eclipse plugin

%description jasper-eclipse
Jasper OSGi Eclipse plugin that contains class files from jasper-compiler,
jasper-runtime and ECJ.
%endif

%package parent
Summary:     POM files for tomcat-parent.
Group:       Development

%description parent
POM files for tomcat-parent.

%prep
cat <<EOT

                If you want only apis to be built,
                give rpmbuild option '--with apisonly'

		If you don''t want direct ecj support to be built in,
		while eclipse-ecj isn''t available,
		give rpmbuild option '--without ecj'


EOT

rm -rf $RPM_BUILD_DIR/%{name}-%{version}

%setup -q -c -T -a 0
%setup -q -D -T -a 9

cd %{packdname}
%patch0 
%patch1
%patch2
%patch3
%patch4
#%patch5
#%patch6 -p1
%patch7
%patch8
%patch9
%patch10
# omit jdtcompilerpatch for eclipse-ecj >= 3.1
# %%patch11 -b .p11
%patch12
%patch13
%patch14
%if %{gcj_support}
%patch15
%patch16
#%patch17 -b .p17
%ifarch ppc64 s390x
%patch18
%endif
%endif
# XXX:
# Dont need this! Building against j-c-modeler 1.1 with MODELER-15 patch
# %%patch19 -b .p19
%patch20 -p0
%if %{with_ecj}
%patch21 -p0
%endif

# Still need the eclipse related patch
%patch25

# IT #168408
%patch28

%patch33

%patch34

# %patch36
*# %patch37*
# %patch38
# %patch39
%patch40
%patch41
# %patch42
%patch43
%patch44
%patch45
# %patch46
%patch47
%patch48
%patch49
%patch50
%patch51
%patch52

%if %{without_ecj}
%{__rm} %{jname}/src/share/org/apache/jasper/compiler/JDTCompiler.java
%endif

cat > README.CVE-2007-1355 << EOF
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML><HEAD><TITLE>Examples Removed</TITLE>
<META http-equiv=Content-Type content="text/html">
</HEAD>
<BODY>
<P>
<H>Note: The following files have been removed due to CVE-2007-1355:

</P>
<P>
%{appdir}/servlets-examples/*
</P>
<P>
%{appdir}/jsp-examples/*
</P>
<P>
%{appdir}/tomcat-docs/appdev/sample/*
</P>
<P>
%{appdir}/webdav/*
</P>
</H>
</BODY></HTML>
EOF
cp %{SOURCE7} jsvc.tar.gz

%if %{without_ecj}
    %{__rm} %{jname}/src/share/org/apache/jasper/compiler/JDTCompiler.java
%endif

find -type f -name '*.jsp' | xargs -t perl -pi -e 's/<html:html locale="true">/<html:html>/g'

%build
# remove pre-built binaries
for dir in ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname} ; do
    find $dir \( -name "*.jar" -o -name "*.class" \) | xargs -t %{__rm} -f
done
# copy license for later doc files declaration
# LICENSE already resides in packdname since 5.5.31
# but the release notes and other docs need to be copied 
# up so they can be found later in %files
 pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}
    %{__cp} -p build/{RELE*,RUNNING.txt,BENCHMARKS.txt} .
 popd 
# build jspapi and servletapi as ant dist will require them later
pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/servletapi
    pushd jsr154
        ant -Dservletapi.build="build" \
            -Dservletapi.dist="dist" \
            -Dbuild.compiler="modern" dist
    popd
    pushd jsr152
        ant -Dservletapi.build="build" \
            -Dservletapi.dist="dist" \
            -Dbuild.compiler="modern" dist
    popd
popd
%if %{without_apisonly}
# build jasper subpackage
pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/%{jname}
    %{__cat} > build.properties << EOBP
ant.jar=$(build-classpath ant)
servlet-api.jar=${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/servletapi/jsr154/dist/lib/servlet-api.jar
jsp-api.jar=${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/servletapi/jsr152/dist/lib/jsp-api.jar
tools.jar=%{java.home}/lib/tools.jar
xerces.jar=$(build-classpath xerces-j2)
xercesImpl.jar=$(build-classpath jaxp_parser_impl)
xmlParserAPIs.jar=$(build-classpath xml-commons-apis)
commons-el.jar=$(build-classpath commons-el)
commons-collections.jar=$(build-classpath commons-collections)
commons-logging.jar=$(build-classpath commons-logging)
commons-daemon.jar=$(build-classpath commons-daemon)
junit.jar=$(build-classpath junit)
jasper-compiler-jdt.jar=$(build-classpath ecj)
jdt.jar=$(build-classpath ecj)
struts.jar=$(build-classpath struts12-1.2.9.jar)
EOBP
    ant -Djava.home="%{java_home}" -Dbuild.compiler="modern" javadoc
popd

# build tomcat 5
pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/build
    %{__cat} >> build.properties << EOBP
version=%{version}
version.build=%{minversion}
ant.jar=%{_javadir}/ant.jar
ant-launcher.jar=%{_javadir}/ant.jar
jtc.home=${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/connectors/
%{jname}.home=${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/%{jname}
commons-beanutils.jar=$(build-classpath commons-beanutils)
commons-fileupload.jar=$(build-classpath commons-fileupload)
commons-collections.jar=$(build-classpath commons-collections)
commons-daemon.jar=$(build-classpath commons-daemon)
commons-daemon.jsvc.tar.gz=../jsvc.tar.gz
commons-dbcp.jar=$(build-classpath commons-dbcp)
commons-digester.jar=$(build-classpath commons-digester)
commons-el.jar=$(build-classpath commons-el)
commons-fileupload.jar=$(build-classpath commons-fileupload)
commons-io.jar=$(build-classpath commons-io)
commons-launcher.jar=$(build-classpath commons-launcher)
commons-logging.jar=$(build-classpath commons-logging)
commons-logging-api.jar=$(build-classpath commons-logging-api)
commons-modeler.jar=$(build-classpath commons-modeler)
commons-pool.jar=$(build-classpath commons-pool)
jmx.jar=$(build-classpath mx4j/mx4j-jmx.jar)
jmx-remote.jar=$(build-classpath mx4j/mx4j-remote.jar)
jmx-tools.jar=$(build-classpath mx4j/mx4j-tools.jar)
jmxri.jar=$(build-classpath mx4j/mx4j-jmx.jar)
junit.jar=$(build-classpath junit)
regexp.jar=$(build-classpath regexp)
servlet-api.jar=${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/servletapi/jsr154/dist/lib/servlet-api.jar
jsp-api.jar=${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/servletapi/jsr152/dist/lib/jsp-api.jar
servlet.doc=${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/servletapi/jsr154/dist/docs/api
xercesImpl.jar=$(build-classpath jaxp_parser_impl)
xml-apis.jar=$(build-classpath xml-commons-apis)
struts.jar=$(build-classpath struts12-1.2.9.jar)
struts.lib=%{_datadir}/struts-1.2.9
activation.jar=$(build-classpath jaf)
mail.jar=$(build-classpath javamail/mailapi)
jta.jar=$(build-classpath jta)
jaas.jar=$(build-classpath jaas)
jndi.jar=$(build-classpath jndi)
jdbc20ext.jar=$(build-classpath jdbc-stdext)
jcert.jar=$(build-classpath jsse/jcert)
jnet.jar=$(build-classpath jsse/jnet)
jsse.jar=$(build-classpath jsse/jsse)
servletapi.build.notrequired=true
jspapi.build.notrequired=true
EOBP
ant -Dbuild.compiler="modern" -Djava.home="%{java_home}" init
cp ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/servletapi/jsr154/dist/lib/servlet-api.jar \
        ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/build/build/common/lib/servlet-api.jar
export CLASSPATH=$RPM_BUILD_DIR/%{name}-%{version}/%{packdname}/servletapi/jsr154/dist/lib/servlet-api.jar:$RPM_BUILD_DIR/%{name}-%{version}/%{packdname}/servletapi/jsr152/dist/lib/jsp-api.jar:$(build-classpath jakarta-taglibs-core jakarta-taglibs-standard struts12-1.2.9)
    ant -Dbuild.compiler=modern -Djava.home=%{java_home} build-jasper-compiler-jdt release
popd
# build the connectors
pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/connectors
# use the JARs created above to build
    export CLASSPATH="${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/servletapi/jsr154/dist/lib/servlet-api.jar:${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/jakarta-tomcat-5/build/server/lib/catalina.jar:${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/build/build/server/lib/tomcat-apr.jar"
    %{__cat} > build.properties << EOBP
activation.jar=$(build-classpath jaf)
ant.jar=%{_javadir}/ant.jar
junit.jar=$(build-classpath junit)
commons-beanutils.jar=$(build-classpath commons-beanutils)
commons-collections.jar=$(build-classpath commons-collections)
commons-daemon.jar=$(build-classpath commons-daemon)
commons-digester.jar=$(build-classpath commons-digester)
commons-fileupload.jar=$(build-classpath commons-fileupload)
commons-io.jar=$(build-classpath commons-io)
commons-logging.jar=$(build-classpath commons-logging)
commons-logging-api.jar=$(build-classpath commons-logging-api)
commons-modeler.jar=$(build-classpath commons-modeler)
commons-pool.jar=$(build-classpath commons-pool)
regexp.jar=$(build-classpath regexp)
jmx.jar=$(build-classpath mx4j/mx4j-jmx)
activation.jar=$(build-classpath jaf)
mail.jar=$(build-classpath javamail/mailapi)
jta.jar=$(build-classpath jta_1_0_1B_api)
jaas.jar=$(build-classpath jaas)
jndi.jar=$(build-classpath jndi)
jdbc20ext.jar=$(build-classpath jdbc-stdext)
jcert.jar=$(build-classpath jsse/jcert)
jnet.jar=$(build-classpath jsse/jnet)
jsse.jar=$(build-classpath jsse/jsse)
struts.jar=$(build-classpath struts12-1.2.9.jar)
tomcat5.home=../../build/build
EOBP
    ant -Dbuild.compiler="modern" -Djava.home="%{java_home}" build
popd
%endif

# create jasper-eclipse jar
%if %{with_ecj}
mkdir -p org.apache.jasper
pushd org.apache.jasper
unzip -qq ../apache-tomcat-%{version}-src/build/build/common/lib/jasper-compiler.jar
unzip -qq ../apache-tomcat-%{version}-src/build/build/common/lib/jasper-runtime.jar \
  -x META-INF/MANIFEST.MF org/apache/jasper/compiler/Localizer.class
unzip -qq %{_javadir}/ecj.jar -x META-INF/MANIFEST.MF
cp -p %{SOURCE10} META-INF/MANIFEST.MF
rm -f plugin.properties plugin.xml about.html jdtCompilerAdapter.jar META-INF/eclipse.inf
zip -qq -r ../org.apache.jasper_5.5.17.v200706111724.jar .
popd
%endif

# inject OSGi manifests
mkdir tmp2
pushd tmp2
mkdir -p META-INF
unzip -q ../%{packdname}/servletapi/jsr154/dist/lib/servlet-api.jar -x META-INF/MANIFEST.MF
cp -p %{SOURCE11} META-INF/MANIFEST.MF
rm ../%{packdname}/servletapi/jsr154/dist/lib/servlet-api.jar
zip -q -r ../%{packdname}/servletapi/jsr154/dist/lib/servlet-api.jar .
rm -r *
mkdir -p META-INF
unzip -q ../%{packdname}/servletapi/jsr152/dist/lib/jsp-api.jar -x META-INF/MANIFEST.MF
cp -p %{SOURCE12} META-INF/MANIFEST.MF
rm ../%{packdname}/servletapi/jsr152/dist/lib/jsp-api.jar
zip -q -r ../%{packdname}/servletapi/jsr152/dist/lib/jsp-api.jar .
rm -r *
popd
rm -fr tmp2
pwd

%if %{with_zips}
mkdir tmp
pushd tmp
    unzip -aq ../%{packdname}/build/release/v%{version}/src/%{packdname}.zip
    #tar -xzf../%{packdname}/build/release/v%{version}/src/%{packdname}.tar.gz
pushd %{packdname}
    patch -R -p0  <  %{PATCH7}
    patch -R -p0  <  %{PATCH8}
    patch -R -p0  <  %{PATCH9}
    patch -R -p0  <  %{PATCH10}
    cp $(build-classpath ant) .
    cp $(build-classpath ant-launcher) .
    cp $(build-classpath commons-beanutils) .
    cp $(build-classpath commons-collections) .
    cp $(build-classpath commons-daemon) .
    cp $(build-classpath commons-el) .
    cp $(build-classpath commons-io) .
    cp $(build-classpath commons-logging) .
    cp $(build-classpath commons-logging-api) .
    cp $(build-classpath commons-modeler) .
    cp $(build-classpath log4j) .
    cp $(build-classpath commons-digester) .
    cp $(build-classpath commons-fileupload) .
    cp $(build-classpath xml-commons-apis) .
    cp $(build-classpath junit) .
    cp $(build-classpath commons-launcher) .
    cp $(build-classpath struts12-1.2.9) .
    cp $(build-classpath mx4j/mx4j) .
    cp $(build-classpath mx4j/mx4j-remote) .
    cp $(build-classpath mx4j/mx4j-tools) .
    cp $(build-classpath mx4j/mx4j-jmx) .
    cp $(build-classpath jakarta-taglibs-core) .
    cp $(build-classpath jakarta-taglibs-standard) .
    cp $(build-classpath jaf) .
    cp $(build-classpath glassfish-javamail/mailapi) .
    cp $(build-classpath jta) .
    cp $(build-classpath ecj) .
    cp $(build-classpath jaxp_parser_impl) .
    cp $RPM_BUILD_DIR/%{name}-%{version}/%{packdname}/servletapi/jsr154/dist/lib/servlet-api.jar servletapi/jsr152/servletapi.jar
    mkdir struts
    cp -r %{_datadir}/struts-1.2.9/* struts/
    cp %{SOURCE8} build/build.properties

# jbpapp-3654 last chance to get rid of any junk
	 find . -name "*.orig" | xargs -t %{__rm} -f
popd
    rm ../%{packdname}/build/release/v%{version}/src/%{packdname}.zip
    zip -q -r ../%{packdname}/build/release/v%{version}/src/%{packdname}.zip *
    rm -fr *
    # binary zip
cat > README.CVE-2007-1355.tomcat5 << EOF
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<HTML><HEAD><TITLE>Examples Removed</TITLE>
<META http-equiv=Content-Type content="text/html">
</HEAD>
<BODY>
<P>
<H>Note: The following files have been removed due to CVE-2007-1355:

</P>
<P>
tomcat5/webapps/servlets-examples/*
</P>
<P>
tomcat5/webapps/jsp-examples/*
</P>
<P>
tomcat5/webapps/tomcat-docs/appdev/sample/*
</P>
<P>
tomcat5/webapps/webdav/*
</P>
</H>
</BODY></HTML>
EOF

    unzip -q ../%{packdname}/build/release/v%{version}/bin/apache-tomcat-%{version}.zip
    #create zip for QE to run examples
    cp $(build-classpath jakarta-taglibs-core) apache-tomcat-%{version}/webapps/jsp-examples/WEB-INF/lib/jstl.jar
    cp $(build-classpath jakarta-taglibs-standard) apache-tomcat-%{version}/webapps/jsp-examples/WEB-INF/lib/standard.jar
    find apache-tomcat%{version} -name "*.orig" | xargs -t %{__rm} -f
    zip -q -r ../%{packdname}/build/release/v%{version}/bin/apache-tomcat-%{version}-examples.zip \
         apache-tomcat-%{version}/webapps/servlets-examples/* apache-tomcat-%{version}/webapps/jsp-examples/* \
         apache-tomcat-%{version}/webapps/tomcat-docs/appdev/sample/* apache-tomcat-%{version}/webapps/webdav/*
    chmod 755 apache-tomcat-%{version}/bin/*sh
    sed -i -e 's/\"$_RUNJAVA\"/$_RUNJAVA/g' apache-tomcat-%{version}/bin/catalina.sh \
       apache-tomcat-%{version}/bin/tool-wrapper.sh
    patch -R -p0  <  %{PATCH35}
    find apache-tomcat-%{version} -name "*.orig" | xargs -t %{__rm} -f
    sed -i -e 's:common.loader=${catalina.home}/common/classes,${catalina.home}/common/i18n/\*.jar,${catalina.home}/common/endorsed/\*.jar,${catalina.home}/common/lib/\*.jar:common.loader=${catalina.home}/common/classes,${catalina.home}/common/i18n/\*.jar,${catalina.home}/common/endorsed/\*.jar,${catalina.home}/common/lib/\*.jar,${catalina.home}/server/lib/\*.jar:g' apache-tomcat-%{version}/conf/catalina.properties
    rm apache-tomcat-%{version}/bin/*bat
#	 echo "doing common lib"
    (cd apache-tomcat-%{version}/common/lib; \
			ln -sf $(build-classpath ant) . ;\
#			ln -sf $(build-classpath commons-chain) . ;\
         ln -sf $(build-classpath commons-collections) . ;\
         ln -sf $(build-classpath commons-collections-tomcat5) . ;\
         cp -p $(build-classpath commons-pool) . ;\
#	 echo "doing common lib 2"
#    (cd apache-tomcat-%{version}/common/lib; \
         ln -sf $(build-classpath commons-pool-tomcat5) . ;\
         cp -p $(build-classpath commons-dbcp) . ;\
         ln -sf $(build-classpath commons-dbcp-tomcat5) . ;\
         ln -sf $(build-classpath commons-el) . ;\
         ln -sf $(build-classpath commons-logging-api) . ;\
			ln -sf $(build-classpath commons-logging) . ;\
#	 echo "doing common lib 3"
#    (cd apache-tomcat-%{version}/common/lib; \
         cp -p $(build-classpath mx4j/mx4j) . ;\
         cp -p $(build-classpath mx4j/mx4j-impl) . ;\
         ln -sf $(build-classpath regexp) . ;\
         ln -sf $(build-classpath ecj) . ;\
         ln -sf $(build-classpath javamail) . ;\
         ln -sf $(build-classpath jaf) . ;\
         cp -p ../../../../%{packdname}/build/build/common/lib/jasper-compiler.jar . ;\
         cp -p ../../../../%{packdname}/build/build/common/lib/jasper-runtime.jar . ;\
         ln -sf $(build-classpath jta) . ;\
         ln -sf ../../../../%{packdname}/servletapi/jsr152/dist/lib/jsp-api.jar jsp.jar ;\
         ln -sf ../../../../%{packdname}/servletapi/jsr154/dist/lib/servlet-api.jar servlet.jar )
	 echo "doing server lib"
    (cd apache-tomcat-%{version}/server/lib; \
			ln -sf $(build-classpath commons-beanutils) .; \
         ln -sf $(build-classpath commons-digester) . ;\
         cp -p ../../../../%{packdname}/build/build/server/lib/catalina-ant.jar . ;\
#         ln -sf $(build-classpath commons-el) . ;\
#         ln -sf $(build-classpath commons-fileupload) . ;\
#         ln -sf $(build-classpath commons-logging) . ;\
# mx4j is in common/lib
#         ln -sf $(build-classpath mx4j/mx4j) . ;\
#         ln -sf $(build-classpath mx4j/mx4j-impl) . ;\
         ln -sf $(build-classpath commons-modeler) . )
#    (cd apache-tomcat-%{version}/bin; ln -sf $(build-classpath mx4j/mx4j) jmx.jar )
    (cd apache-tomcat-%{version}/common/endorsed; ln -sf $(build-classpath xml-commons-apis) .; ln -sf $(build-classpath jaxp_parser_impl) . )
    rm -fr apache-tomcat-%{version}/webapps/servlets-examples/* apache-tomcat-%{version}/webapps/jsp-examples/* \
         apache-tomcat-%{version}/webapps/tomcat-docs/appdev/sample/* apache-tomcat-%{version}/webapps/webdav/*
    cp -pr README.CVE-2007-1355.tomcat5 apache-tomcat-%{version}/webapps/servlets-examples/index.html
    cp -pr README.CVE-2007-1355.tomcat5 apache-tomcat-%{version}/webapps/jsp-examples/index.html
    cp -pr README.CVE-2007-1355.tomcat5 apache-tomcat-%{version}/webapps/tomcat-docs/appdev/sample/index.html
    cp -pr README.CVE-2007-1355.tomcat5 apache-tomcat-%{version}/webapps/webdav/index.html
    rm README.CVE-2007-1355.tomcat5
    %{__rm}  apache-tomcat-%{version}/common/lib/servlet.jar
    %{__rm}  apache-tomcat-%{version}/common/lib/jsp.jar
    %{__rm} -f apache-tomcat-%{version}/common/lib/commons-chain.jar
    %{__rm} -f apache-tomcat-%{version}/common/lib/commons-fileupload.jar
    %{__rm}  ../%{packdname}/build/release/v%{version}/bin/apache-tomcat-%{version}.zip
	 %{__cp} %{SOURCE13} apache-tomcat-%{version}/conf/catalina.policy
	 %{__cp} %{SOURCE14} apache-tomcat-%{version}/conf/JBossPublicKey.RSA
    %if %with_signing
	 echo Signing Binary Zip
    cp %{SOURCE99} .
    ./sign-unsigned-jars jbosscodesign2009 .
    rm sign-unsigned-jars
    %endif

# JBPAPP-3654 Last chance to get rid of any junk
	 find apache-tomcat-%{version} -name "*.orig" | xargs -t %{__rm} -f

    zip -q -r ../%{packdname}/build/release/v%{version}/bin/apache-tomcat-%{version}.zip *
    rm -r apache-tomcat-%{version} 
    unzip -q ../%{packdname}/build/release/v%{version}/bin/apache-tomcat-%{version}-admin.zip
	 find apache-tomcat-%{version} -name "*.orig" | xargs -t %{__rm} -f
    (cd apache-tomcat-%{version}/server/webapps/admin/WEB-INF/lib; cp $(build-classpath commons-chain) .; cp $(build-classpath commons-io) . )
    rm ../%{packdname}/build/release/v%{version}/bin/apache-tomcat-%{version}-admin.zip
    %if %with_signing
	 echo Signing Admin Zip
    cp %{SOURCE99} .
    ./sign-unsigned-jars jbosscodesign2009 .
    rm sign-unsigned-jars
    %endif
    zip -q -r ../%{packdname}/build/release/v%{version}/bin/apache-tomcat-%{version}-admin.zip *
popd
rm -rf tmp
%endif

%install
%{__rm} -rf $RPM_BUILD_ROOT
%{__install} -d -m 755 ${RPM_BUILD_ROOT}%{_javadir}
%if %{without_apisonly}
export CLASSPATH="$(build-classpath xalan-j2 xml-commons-apis jakarta-taglibs-core jakarta-taglibs-standard struts12-1.2.9):${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/servletapi/jsr152/dist/lib/jsp-api.jar":${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/servletapi/jsr154/dist/lib/servlet-api.jar
# build initial path structure
%{__install} -d -m 775 \
    ${RPM_BUILD_ROOT}{%{confdir},%{logdir},%{homedir},%{bindir}}
touch ${RPM_BUILD_ROOT}%{logdir}/catalina.out
%{__install} -d -m 755 ${RPM_BUILD_ROOT}{%{serverdir},%{tempdir},%{workdir}}
%{__install} -d -m 775 ${RPM_BUILD_ROOT}{%{appdir},%{commondir},%{shareddir}}
%{__install} -d -m 755 ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d
%{__install} -d -m 755 ${RPM_BUILD_ROOT}%{_initrddir}
%{__install} -d -m 755 ${RPM_BUILD_ROOT}%{_bindir}
%{__install} -d -m 755 ${RPM_BUILD_ROOT}%{_javadir}/%{name}
%{__install} -d -m 755 ${RPM_BUILD_ROOT}%{_datadir}/maven2/poms
%{__install} -m 755 %{SOURCE5} ${RPM_BUILD_ROOT}%{bindir}/relink
# SysV init and configuration
%{__install} -d -m 755 ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig
# Service-specific configuration file
cat > %{name} << EOT
# Service-specific configuration file for %{name} services
# This will be sourced by the SysV service script after the global
# configuration file /etc/%{name}/%{name}.conf, thus allowing values
# to be overridden on a per-service way
#
# NEVER change the init script itself:
# To change values for all services make your changes in
# /etc/%{name}/%{name}.conf
# To change values for a specific service, change it here
# To create a new service, create a link from /etc/init.d/<you new service> to
# /etc/init.d/%{name} (do not copy the init script) and make a copy of the
# /etc/sysconfig/%{name} file to /etc/sysconfig/<you new service> and change
# the property values so the two services won't conflict
# Register the new service in the system as usual (see chkconfig and similars)
#
# JBPAPP-3644 enable security manager in sysconfig
# Uncomment and set to true to start EWS tomcat5 with security manager
#SECURITY_MANAGER=false
EOT
%{__install} -m 0644 %{name} ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig/%{name}
%{__rm} %{name}
%{__install} %{SOURCE1} \
    ${RPM_BUILD_ROOT}%{_initrddir}/%{name}
# Global configuration file
%{__install} -d -m 0775 ${RPM_BUILD_ROOT}%{confdir}
%{__cat} > %{name}.conf << EOT
# System-wide configuration file for %{name} services
# This will be sourced by %{name} and any secondary service
# Values will be overridden by service-specific configuration
# files in /etc/sysconfig
# Use this one to change default values for all services
# Change the service specific ones to affect only one service
# (see, for instance, /etc/sysconfig/%{name})
#
EOT
%{__cat} %{SOURCE2} >> %{name}.conf
%{__install} -m 0664 %{name}.conf ${RPM_BUILD_ROOT}%{confdir}/%{name}.conf
%{__rm} -f %{name}.conf
%{__install} -m 0664 %{SOURCE13} ${RPM_BUILD_ROOT}%{confdir}/catalina.policy
%{__install} -m 0664 %{SOURCE14} ${RPM_BUILD_ROOT}%{confdir}/JBossPublicKey.RSA

CLASSPATH=$(build-classpath xalan-j2 xml-commons-apis jakarta-taglibs-core jakarta-taglibs-standard mx4j/mx4j-jmx struts12-1.2.9)
export CLASSPATH=$CLASSPATH:$RPM_BUILD_DIR/%{name}-%{version}/%{packdname}/servletapi/jsr152/dist/lib/jsp-api.jar:$RPM_BUILD_DIR/%{name}-%{version}/%{packdname}/servletapi/jsr154/dist/lib/servlet-api.jar
pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/build
    export usejikes="false"
    export OPT_JAR_LIST="ant/ant-trax xalan-j2-serializer"
    ant -Dbuild.compiler="modern" -Djava.home=%{java_home} dist
    pushd dist
		 %if %with_signing
		 echo Signing Dist
		 cp %{SOURCE99} .
		 ./sign-unsigned-jars jbosscodesign2009 .
		 rm sign-unsigned-jars
		 %endif
        %{__mv} bin/* ${RPM_BUILD_ROOT}%{bindir}
        # Does not exist in 5.5.31
        # %{__rm} ${RPM_BUILD_ROOT}%{bindir}/jsvc.tar.gz
        %{__mv} common/* ${RPM_BUILD_ROOT}%{commondir}
        %{__mv} conf/* ${RPM_BUILD_ROOT}%{confdir}
        %{__mv} server/* ${RPM_BUILD_ROOT}%{serverdir}
        %{__mv} shared/* ${RPM_BUILD_ROOT}%{shareddir}
        %{__mv} webapps/* ${RPM_BUILD_ROOT}%{appdir}
		  %{__cp} %{SOURCE13} ${RPM_BUILD_ROOT}%{confdir}/catalina.policy
		  %{__cp} %{SOURCE14} ${RPM_BUILD_ROOT}%{confdir}/JBossPublicKey.RSA
        # CVE-2007-1355
        rm -r $RPM_BUILD_ROOT%{appdir}/servlets-examples/*
        rm -r $RPM_BUILD_ROOT%{appdir}/jsp-examples/*
        rm -r $RPM_BUILD_ROOT%{appdir}/tomcat-docs/appdev/sample/*
        rm -r $RPM_BUILD_ROOT%{appdir}/webdav/*
        cp -p ../../README.CVE-2007-1355 $RPM_BUILD_ROOT%{appdir}/servlets-examples/index.html
        cp -p ../../README.CVE-2007-1355 $RPM_BUILD_ROOT%{appdir}/jsp-examples/index.html
        cp -p ../../README.CVE-2007-1355 $RPM_BUILD_ROOT%{appdir}/tomcat-docs/appdev/sample/index.html
        cp -p ../../README.CVE-2007-1355 $RPM_BUILD_ROOT%{appdir}/webdav/index.html
        #
    popd
# Not provided in 5.5.31
#    pushd build/conf
#        ls
#        %{__mv} uriworkermap.properties workers.properties \
#            workers.properties.minimal ${RPM_BUILD_ROOT}%{confdir}
#     popd
popd
# rename catalina.sh into dtomcat5 to let wrapper take precedence
%{__install} ${RPM_BUILD_ROOT}%{bindir}/catalina.sh \
    ${RPM_BUILD_ROOT}%{_bindir}/d%{name}
%{__rm} -f ${RPM_BUILD_ROOT}%{bindir}/catalina.sh.* \
    ${RPM_BUILD_ROOT}%{bindir}/setclasspath.*

# Remove leftover files
find ${RPM_BUILD_ROOT} -name "*.orig" | xargs -t %{__rm} -f
#%{__rm} -f ${RPM_BUILD_ROOT}%{bindir}/*.orig
#%{__rm} -f ${RPM_BUILD_ROOT}%{confdir}/*.orig
# install wrapper as tomcat5
%{__install} %{SOURCE3} ${RPM_BUILD_ROOT}%{_bindir}/%{name}
# install logrotate support
%{__install} %{SOURCE4} ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d/%{name}
# remove / reorder non-usefull stuff
%{__rm} -rf ${RPM_BUILD_ROOT}%{homedir}/src/
%{__rm} -f  ${RPM_BUILD_ROOT}%{bindir}/*.sh ${RPM_BUILD_ROOT}%{bindir}/*.bat
# FHS compliance patches, not easy to track them all boys :)
for i in ${RPM_BUILD_ROOT}%{confdir}/%{name}.conf \
    ${RPM_BUILD_ROOT}%{_sysconfdir}/sysconfig/%{name} \
    ${RPM_BUILD_ROOT}%{_bindir}/d%{name} \
    ${RPM_BUILD_ROOT}%{_bindir}/%{name} \
    ${RPM_BUILD_ROOT}%{_initrddir}/%{name} \
    ${RPM_BUILD_ROOT}%{bindir}/relink \
    ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d/%{name}; do
    %{__sed} -i \
        -e 's|\@\@\@LIBDIR\@\@\@|%{_libdir}|g' \
        -e 's|\@\@\@TCCONF\@\@\@|%{confdir}|g' \
        -e "s|\@\@\@TCCONF\@\@\@|%{confdir}|g" \
        -e "s|\@\@\@TCHOME\@\@\@|%{homedir}|g" \
        -e "s|\@\@\@TCBIN\@\@\@|%{bindir}|g" \
        -e "s|\@\@\@TCCOMMON\@\@\@|%{commondir}|g" \
        -e "s|\@\@\@TCSERVER\@\@\@|%{serverdir}|g" \
        -e "s|\@\@\@TCSHARED\@\@\@|%{shareddir}|g" \
        -e "s|\@\@\@TCAPP\@\@\@|%{appdir}|g" \
        -e "s|\@\@\@TCLOG\@\@\@|%{logdir}|g" $i
done
ls ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/*

%add_to_maven_depmap tomcat tomcat-parent %{version} JPP/%{name} parent
    %{__install} -m 644 \
        ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/tomcat-parent-%{version}.pom \
        $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP.%{name}-parent.pom
# Process bin
# Remove local JARs (to be replaced with jpp links in post)
pushd ${RPM_BUILD_ROOT}%{bindir}
    # tomcat-juli will be installed in a public repository
    %{__mv} tomcat-juli.jar \
        ${RPM_BUILD_ROOT}%{_javadir}/%{name}/tomcat-juli-%{version}.jar
    pushd ${RPM_BUILD_ROOT}%{_javadir}/%{name}
        %{__ln_s} -f tomcat-juli-%{version}.jar tomcat-juli.jar
    popd
    %add_to_maven_depmap tomcat tomcat-juli %{version} JPP/%{name} tomcat-juli
    %{__install} -m 644 \
        ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/tomcat-juli-%{version}.pom \
        $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP.%{name}-tomcat-juli.pom

    find . -name "*.jar" -not -name "*bootstrap*" -not -name "commons-logging-api.jar" \
           -exec %{__rm} -f {} \;
popd
# Process server/lib
# Remove local JARs (to be replaced with jpp links in post)
pushd ${RPM_BUILD_ROOT}%{serverdir}/lib
    find . -name "*.jar" -not -name "catalina*" \
        -not -name "servlets-*" \
        -not -name "tomcat-*" | xargs -t %{__rm} -f
    # catalina-ant will be installed in a public repository
    %{__mv} catalina-ant.jar \
        ${RPM_BUILD_ROOT}%{_javadir}/catalina-ant-%{version}.jar
    pushd ${RPM_BUILD_ROOT}%{_javadir}
        %{__ln_s} -f catalina-ant-%{version}.jar catalina-ant5.jar
    popd
    %add_to_maven_depmap tomcat catalina-ant %{version} JPP catalina-ant5
    %{__install} -m 644 \
        ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/catalina-ant-%{version}.pom \
        $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP.catalina-ant5.pom

    # catalina* jars will be installed in a public repository
    for i in catalina*.jar; do
        j="`echo $i | %{__sed} -e 's|\.jar$||'`"
        %{__mv} ${j}.jar \
            ${RPM_BUILD_ROOT}%{_javadir}/%{name}/${j}-%{version}.jar
        pushd ${RPM_BUILD_ROOT}%{_javadir}/%{name}
            %{__ln_s} -f ${j}-%{version}.jar ${j}.jar
        popd
        %add_to_maven_depmap tomcat ${j} %{version} JPP/tomcat5 ${j}
        %{__install} -m 644 \
            ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/${j}-%{version}.pom \
            $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP.tomcat5-${j}.pom
    done
    # servlets* jars will be installed in a public repository
    for i in servlets-*.jar; do
        j="`echo $i | %{__sed} -e 's|\.jar$||'`"
        %{__mv} ${j}.jar \
            ${RPM_BUILD_ROOT}%{_javadir}/%{name}/${j}-%{version}.jar
        pushd ${RPM_BUILD_ROOT}%{_javadir}/%{name}
            %{__ln_s} -f ${j}-%{version}.jar ${j}.jar
        popd
        %add_to_maven_depmap tomcat ${j} %{version} JPP/tomcat5 ${j}
        %{__install} -m 644 \
            ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/${j}-%{version}.pom \
            $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP.tomcat5-${j}.pom
    done
    # tomcat* jars will be installed in a public repository
    for i in tomcat-*.jar; do
        j="`echo $i | %{__sed} -e 's|\.jar$||'`"
        %{__mv} ${j}.jar \
            ${RPM_BUILD_ROOT}%{_javadir}/%{name}/${j}-%{version}.jar
        pushd ${RPM_BUILD_ROOT}%{_javadir}/%{name}
            %{__ln_s} -f ${j}-%{version}.jar ${j}.jar
        popd
        %add_to_maven_depmap tomcat ${j} %{version} JPP/tomcat5 ${j}
        %{__install} -m 644 \
            ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/${j}-%{version}.pom \
            $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP.tomcat5-${j}.pom
    done
popd
# Process admin webapp server/webapps/admin
pushd ${RPM_BUILD_ROOT}%{serverdir}/webapps/admin/WEB-INF/lib
    find . -name "*.jar" -not -name 'catalina-admin*' | xargs -t %{__rm} -f
    for i in catalina-admin; do
        %{__mv} ${i}.jar \
            ${RPM_BUILD_ROOT}%{_javadir}/%{name}/${i}-%{version}.jar
        pushd ${RPM_BUILD_ROOT}%{_javadir}/%{name}
            %{__ln_s} -f ${i}-%{version}.jar ${i}.jar
        popd
        %add_to_maven_depmap tomcat ${i} %{version} JPP/tomcat5 ${i}
        %{__install} -m 644 \
            ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/${i}-%{version}.pom \
            $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP.tomcat5-${i}.pom
    done
	 cp -pL $(build-classpath commons-chain) .
popd
# Process manager webapp server/webapps/manager
pushd ${RPM_BUILD_ROOT}%{serverdir}/webapps/manager/WEB-INF/lib
    find . -name "*.jar" -not -name 'catalina-manager*' | xargs -t %{__rm} -f
    for i in catalina-manager; do
        %{__mv} ${i}.jar \
            ${RPM_BUILD_ROOT}%{_javadir}/%{name}/${i}-%{version}.jar
        pushd ${RPM_BUILD_ROOT}%{_javadir}/%{name}
            %{__ln_s} -f ${i}-%{version}.jar ${i}.jar
        popd
        %add_to_maven_depmap tomcat ${i} %{version} JPP/tomcat5 ${i}
        %{__install} -m 644 \
            ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/${i}-%{version}.pom \
            $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP.tomcat5-${i}.pom
    done
	 cp -pL $(build-classpath commons-fileupload) .
popd
# Process host-manager webapp server/webapps/host-manager
pushd ${RPM_BUILD_ROOT}%{serverdir}/webapps/host-manager/WEB-INF/lib
    find . -name "*.jar" -not -name 'catalina-host-manager*' \
        | xargs -t %{__rm} -f
    for i in catalina-host-manager; do
        %{__mv} ${i}.jar \
            ${RPM_BUILD_ROOT}%{_javadir}/%{name}/${i}-%{version}.jar
        pushd ${RPM_BUILD_ROOT}%{_javadir}/%{name}
            %{__ln_s} -f ${i}-%{version}.jar ${i}.jar
        popd
        %add_to_maven_depmap tomcat ${i} %{version} JPP/tomcat5 ${i}
        %{__install} -m 644 \
            ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/${i}-%{version}.pom \
            $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP.tomcat5-${i}.pom
    done
popd
# Process common/lib
pushd ${RPM_BUILD_ROOT}%{commondir}/lib
    find . -name "*.jar" -not -name "%{jname}*" \
        -not -name "naming*" | xargs -t %{__rm} -f
    # jasper's jars will be installed in a public repository
    for i in %{jname}-compiler %{jname}-runtime; do
        j="`echo $i | %{__sed} -e 's|%{jname}-|%{jname}5-|'`"
        %{__mv} ${i}.jar ${RPM_BUILD_ROOT}%{_javadir}/${j}-%{version}.jar
        pushd ${RPM_BUILD_ROOT}%{_javadir}
            %{__ln_s} -f ${j}-%{version}.jar ${j}.jar
        popd
        %add_to_maven_depmap tomcat ${i} %{version} JPP ${j}
        %{__install} -m 644 \
            ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/${i}-%{version}.pom \
            $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP-${j}.pom
    done
    # naming* jars will be installed in a public repository
    for i in naming-*.jar; do
        j="`echo $i | %{__sed} -e 's|\.jar$||'`"
        %{__mv} ${j}.jar \
            ${RPM_BUILD_ROOT}%{_javadir}/%{name}/${j}-%{version}.jar
        pushd ${RPM_BUILD_ROOT}%{_javadir}/%{name}
            %{__ln_s} -f ${j}-%{version}.jar ${j}.jar
        popd
        %add_to_maven_depmap tomcat ${j} %{version} JPP/tomcat5 ${j}
        %{__install} -m 644 \
            ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/${j}-%{version}.pom \
            $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP.tomcat5-${j}.pom
    done
	 cp -pL $(build-classpath mx4j/mx4j) .
	 cp -pL $(build-classpath mx4j/mx4j-impl) .
	 cp -pL $(build-classpath commons-pool) .
	 cp -pL $(build-classpath commons-dbcp) .
popd
# Process common/endorsed
pushd ${RPM_BUILD_ROOT}%{commondir}/endorsed
    find . -name "*.jar" | xargs -t %{__rm} -f
popd
# avoid duplicate servlet.jar
%{__rm} -f ${RPM_BUILD_ROOT}%{commondir}/lib/servlet.jar
# Add catalina-deployer
%{__install} -m 644 %{packdname}/build/deployer/lib/catalina-deployer.jar \
    ${RPM_BUILD_ROOT}%{_javadir}/%{name}/catalina-deployer-%{version}.jar
        pushd ${RPM_BUILD_ROOT}%{_javadir}/%{name}
            %{__ln_s} -f catalina-deployer-%{version}.jar catalina-deployer.jar
        popd

# Perform FHS translation
# (final links)
pushd ${RPM_BUILD_ROOT}%{homedir}
    [ -d bin ] || %{__ln_s} -f %{bindir} bin
    [ -d common ] || %{__ln_s} -f %{commondir} common
    [ -d conf ] || %{__ln_s} -f %{confdir} conf
    [ -d logs ] || %{__ln_s} -f %{logdir} logs
    [ -d server ] || %{__ln_s} -f %{serverdir} server
    [ -d shared ] || %{__ln_s} -f %{shareddir} shared
    [ -d webapps ] || %{__ln_s} -f %{appdir} webapps
    [ -d work ] || %{__ln_s} -f %{workdir} work
    [ -d temp ] || %{__ln_s} -f %{tempdir} temp
popd
%endif
# begin servlet api subpackage install
pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/servletapi
    %{__install} -m 644 jsr154/dist/lib/servlet-api.jar \
        ${RPM_BUILD_ROOT}%{_javadir}/%{name}-servlet-%{servletspec}-api-%{version}.jar
    pushd ${RPM_BUILD_ROOT}%{_javadir}
        %{__ln_s} -f %{name}-servlet-%{servletspec}-api-%{version}.jar \
            %{name}-servlet-%{servletspec}-api.jar
        # For backward compatibility with old JPP packages
        %{__ln_s} -f %{name}-servlet-%{servletspec}-api-%{version}.jar \
            servletapi5.jar
    popd
    # depmap frag for standard alternative
    %add_to_maven_depmap javax.servlet servlet-api %{servletspec} JPP servlet_2_4_api
    %add_to_maven_depmap tomcat servlet-api %{version} JPP %{name}-servlet-%{servletspec}-api
    %{__install} -m 644 \
            ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/servlet-api-%{version}.pom \
            $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP-%{name}-servlet-%{servletspec}-api.pom
    # javadoc servlet
    %{__install} -d -m 755 ${RPM_BUILD_ROOT}%{_javadocdir}/%{name}-servlet-%{servletspec}-api-%{version}
    %{__cp} -pr jsr154/build/docs/api/* \
        ${RPM_BUILD_ROOT}%{_javadocdir}/%{name}-servlet-%{servletspec}-api-%{version}
    %{__ln_s} -f %{name}-servlet-%{servletspec}-api-%{version} \
        ${RPM_BUILD_ROOT}%{_javadocdir}/%{name}-servlet-%{servletspec}-api
popd
# begin jsp api subpackage install
pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/servletapi
    %{__install} -m 644 jsr152/dist/lib/jsp-api.jar \
        ${RPM_BUILD_ROOT}%{_javadir}/%{name}-jsp-%{jspspec}-api-%{version}.jar
    pushd ${RPM_BUILD_ROOT}%{_javadir}
        %{__ln_s} -f %{name}-jsp-%{jspspec}-api-%{version}.jar \
            %{name}-jsp-%{jspspec}-api.jar
        # For backward compatibility with old JPP packages
        %{__ln_s} -f %{name}-jsp-%{jspspec}-api-%{version}.jar \
            jspapi.jar
    popd
    %add_to_maven_depmap javax.servlet jsp-api %{jspspec} JPP jsp_2_0_api
    %add_to_maven_depmap tomcat jsp-api %{version} JPP %{name}-jsp-%{jspspec}-api
    %{__install} -m 644 \
            ${RPM_BUILD_DIR}/%{name}-%{version}/tomcat5-poms/jsp-api-%{version}.pom \
            $RPM_BUILD_ROOT/%{_datadir}/maven2/poms/JPP-%{name}-jsp-%{jspspec}-api.pom
    # javadoc jsp
    %{__install} -d -m 755 ${RPM_BUILD_ROOT}%{_javadocdir}/%{name}-jsp-%{jspspec}-api-%{version}
    %{__cp} -pr jsr152/build/docs/api/* \
        ${RPM_BUILD_ROOT}%{_javadocdir}/%{name}-jsp-%{jspspec}-api-%{version}
    %{__ln_s} %{name}-jsp-%{jspspec}-api-%{version} \
        ${RPM_BUILD_ROOT}%{_javadocdir}/%{name}-jsp-%{jspspec}-api
popd
%if %{without_apisonly}
# begin jasper subpackage install
pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/%{jname}
    %{__install} -m 755 src/bin/jspc.sh \
        ${RPM_BUILD_ROOT}%{_bindir}/jspc5.sh
    %{__install} -m 755 src/bin/%{jname}.sh \
        ${RPM_BUILD_ROOT}%{_bindir}/%{full_jname}.sh
popd
pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/container
    %{__install} -m 755 catalina/src/bin/setclasspath.sh \
        ${RPM_BUILD_ROOT}%{_bindir}/%{full_jname}-setclasspath.sh
popd
# javadoc
%{__install} -d -m 755 ${RPM_BUILD_ROOT}%{_javadocdir}/%{jname}-%{version}
pushd ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/%{jname}
    %{__cp} -pr build/javadoc/* \
        ${RPM_BUILD_ROOT}%{_javadocdir}/%{jname}-%{version}
    %{__ln_s} %{jname}-%{version} ${RPM_BUILD_ROOT}%{_javadocdir}/%{jname}
popd
%endif

%if %{with_ecj}
%{__install} -d -m 755 ${RPM_BUILD_ROOT}%{_datadir}/eclipse/plugins
%{__cp} -p org.apache.jasper_5.5.17.v200706111724.jar ${RPM_BUILD_ROOT}%{_datadir}/eclipse/plugins
%endif

%if %{gcj_support}
# Remove non-standard jars from the list for aot compilation 
%{_bindir}/aot-compile-rpm \
    --exclude var/lib/%{name}/webapps/tomcat-docs/appdev/sample/sample.war \
    --exclude var/lib/%{name}/webapps/servlets-examples/WEB-INF/classes \
    --exclude var/lib/%{name}/webapps/jsp-examples/WEB-INF/classes \
    --exclude var/lib/%{name}/webapps/jsp-examples/plugin/applet \
    --exclude var/lib/%{name}/server/lib/servlets-cgi.renametojar \
    --exclude var/lib/%{name}/server/lib/servlets-ssi.renametojar
%endif

%if %{with_repolib}
	install -d -m 755 $RPM_BUILD_ROOT%{repodir}
	install -d -m 755 $RPM_BUILD_ROOT%{repodirlib}
	install -p -m 0644 %{SOURCE6} $RPM_BUILD_ROOT%{repodir}/component-info.xml
        tag=`echo %{name}-%{version}-%{release} | sed 's|\.|_|g'`
        sed -i "s/@TAG@/$tag/g" $RPM_BUILD_ROOT%{repodir}/component-info.xml
	install -d -m 755 $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE0} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE3} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE4} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE5} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE6} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE7} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE8} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE9} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE10} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE11} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE12} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE13} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{SOURCE14} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH0} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH1} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH2} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH3} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH4} $RPM_BUILD_ROOT%{repodirsrc}
#	install -p -m 0644 %{PATCH5} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH7} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH8} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH9} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH10} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH12} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH13} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH14} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH16} $RPM_BUILD_ROOT%{repodirsrc}
# not used
#	install -p -m 0644 %{PATCH17} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH18} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH20} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH21} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH25} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH28} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH33} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH34} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH35} $RPM_BUILD_ROOT%{repodirsrc}
# 36-39 contained in 5.5.31
#	install -p -m 0644 %{PATCH36} $RPM_BUILD_ROOT%{repodirsrc}
#	install -p -m 0644 %{PATCH37} $RPM_BUILD_ROOT%{repodirsrc}
#	install -p -m 0644 %{PATCH38} $RPM_BUILD_ROOT%{repodirsrc}
#	install -p -m 0644 %{PATCH39} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH40} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH41} $RPM_BUILD_ROOT%{repodirsrc}
#	install -p -m 0644 %{PATCH42} $RPM_BUILD_ROOT%{repodirsrc}
	install -p -m 0644 %{PATCH43} $RPM_BUILD_ROOT%{repodirsrc}
   install -p -m 0644 %{PATCH44} $RPM_BUILD_ROOT%{repodirsrc}
   install -p -m 0644 %{PATCH45} $RPM_BUILD_ROOT%{repodirsrc}
#   install -p -m 0644 %{PATCH46} $RPM_BUILD_ROOT%{repodirsrc}
   install -p -m 0644 %{PATCH47} $RPM_BUILD_ROOT%{repodirsrc}
   install -p -m 0644 %{PATCH48} $RPM_BUILD_ROOT%{repodirsrc}
   install -p -m 0644 %{PATCH49} $RPM_BUILD_ROOT%{repodirsrc}
   install -p -m 0644 %{PATCH50} $RPM_BUILD_ROOT%{repodirsrc}
   install -p -m 0644 %{PATCH51} $RPM_BUILD_ROOT%{repodirsrc}
   install -p -m 0644 %{PATCH52} $RPM_BUILD_ROOT%{repodirsrc}

	cp -p $RPM_BUILD_ROOT%{_javadir}/tomcat5/catalina-manager.jar $RPM_BUILD_ROOT%{repodirlib}
	cp -p $RPM_BUILD_ROOT%{_javadir}/tomcat5/catalina.jar $RPM_BUILD_ROOT%{repodirlib}
	cp -p $RPM_BUILD_ROOT%{_javadir}/tomcat5/tomcat-apr.jar $RPM_BUILD_ROOT%{repodirlib}
	cp -p $RPM_BUILD_ROOT%{_javadir}/tomcat5/tomcat-ajp.jar $RPM_BUILD_ROOT%{repodirlib}
	cp -p $RPM_BUILD_ROOT%{_javadir}/tomcat5/naming-resources.jar $RPM_BUILD_ROOT%{repodirlib}
	cp -p $RPM_BUILD_ROOT%{_javadir}/tomcat5/tomcat-coyote.jar $RPM_BUILD_ROOT%{repodirlib}
	cp -p $RPM_BUILD_ROOT%{_javadir}/jasper5-compiler.jar $RPM_BUILD_ROOT%{repodirlib}/jasper-compiler.jar
	cp -p $RPM_BUILD_ROOT%{_javadir}/tomcat5/tomcat-util.jar $RPM_BUILD_ROOT%{repodirlib}
	cp -p $RPM_BUILD_ROOT%{_javadir}/tomcat5/servlets-webdav.jar $RPM_BUILD_ROOT%{repodirlib}
	cp -p $RPM_BUILD_ROOT%{_javadir}/tomcat5/servlets-default.jar $RPM_BUILD_ROOT%{repodirlib}
	cp -p $RPM_BUILD_ROOT%{_javadir}/jasper5-runtime.jar $RPM_BUILD_ROOT%{repodirlib}/jasper-runtime.jar
	cp -p $RPM_BUILD_ROOT%{_javadir}/tomcat5/servlets-invoker.jar $RPM_BUILD_ROOT%{repodirlib}
	cp -p $RPM_BUILD_ROOT%{_javadir}/tomcat5/catalina-optional.jar $RPM_BUILD_ROOT%{repodirlib}
	cp -p $RPM_BUILD_ROOT%{_javadir}/tomcat5/tomcat-http.jar $RPM_BUILD_ROOT%{repodirlib}
	cp -p $RPM_BUILD_DIR/%{name}-%{version}/%{packdname}/build/jasper-compiler-jdt-home/jasper-compiler-jdt-home/jasper-compiler-jdt.jar $RPM_BUILD_ROOT%{repodirlib}
%endif

%if %{with_zips}
install -dm 755 $RPM_BUILD_ROOT%{_javadir}/jbossas-fordev
# Copy over zip for the zip subpackage
install -p -m 0644 $RPM_BUILD_DIR/%{name}-%{version}/%{packdname}/build/release/v%{version}/bin/apache-tomcat-%{version}-examples.zip $RPM_BUILD_ROOT%{_javadir}/jbossas-fordev/tomcat5-%{version}-examples.zip
install -p -m 0644 $RPM_BUILD_DIR/%{name}-%{version}/%{packdname}/build/release/v%{version}/bin/apache-tomcat-%{version}.zip $RPM_BUILD_ROOT%{_javadir}/jbossas-fordev/tomcat5-%{version}.zip
install -p -m 0644 $RPM_BUILD_DIR/%{name}-%{version}/%{packdname}/build/release/v%{version}/bin/apache-tomcat-%{version}-admin.zip $RPM_BUILD_ROOT%{_javadir}/jbossas-fordev/tomcat5-%{version}-admin.zip
install -p -m 0644 $RPM_BUILD_DIR/%{name}-%{version}/%{packdname}/build/release/v%{version}/src/%{packdname}.zip $RPM_BUILD_ROOT%{_javadir}/jbossas-fordev/tomcat5-%{version}-src.zip
%endif

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%if %{without_apisonly}
%post
%update_maven_depmap
# install tomcat5 (but don't activate)
/sbin/chkconfig --add %{name}
# Remove old automated symlinks
for repository in %{bindir} ; do
    find $repository -name '*.jar' -type l | xargs %{__rm} -f
done
for repository in %{commondir}/endorsed ; do
    find $repository -name '\[*\]*.jar' -not -type d | xargs %{__rm} -f
done
for repository in %{commondir}/lib ; do
    find $repository -name '\[*\]*.jar' -not -type d | xargs %{__rm} -f
done
for repository in %{serverdir}/lib ; do
    find $repository -name '\[*\]*.jar' -not -type d | xargs %{__rm} -f
done
# Create automated links - since all needed extensions may not have been
# installed for this jvm output is muted
%{__rm} -f %{bindir}/commons-daemon.jar
%{__ln_s} $(build-classpath commons-daemon) %{bindir}  2>&1
#leave them as files as they were in 5.5.23, otherwise, the symlinks get
#removed during upgrade
#%{__rm} -f %{bindir}/commons-logging-api.jar
#%{__ln_s} $(build-classpath commons-logging-api) %{bindir}  2>&1
%{__rm} -f %{bindir}/tomcat-juli.jar
%{__ln_s} $(build-classpath tomcat5/tomcat-juli) %{bindir}  2>&1

build-jar-repository %{commondir}/endorsed jaxp_parser_impl \
    xml-commons-apis 2>&1
build-jar-repository %{commondir}/lib \
	 ant commons-collections-tomcat5 \
    commons-dbcp-tomcat5 commons-el commons-pool-tomcat5 jaf \
	 javamail tomcat5-jsp-2.0-api \
    %{name}/naming-factory %{name}/naming-resources tomcat5-servlet-2.4-api \
    %{jname}5-compiler %{jname}5-runtime \
	 commons-chain commons-collections commons-logging regexp \
	 commons-logging-api jta 2>&1
%if %{with_ecj}
    build-jar-repository %{commondir}/lib ecj 2>&1
%endif
build-jar-repository %{serverdir}/lib catalina-ant5 commons-modeler \
    %{name}/catalina-ant-jmx %{name}/catalina-cluster %{name}/catalina \
    %{name}/catalina-optional %{name}/catalina-storeconfig \
    %{name}/servlets-default %{name}/servlets-invoker %{name}/servlets-webdav \
    %{name}/tomcat-ajp %{name}/tomcat-apr %{name}/tomcat-coyote \
    %{name}/tomcat-http %{name}/tomcat-util commons-beanutils \
	 commons-digester 2>&1
# commons-chain
# jkstatus-ant is no longer in distro as of tc5.5.31
#    %{name}/tomcat-http %{name}/tomcat-jkstatus-ant %{name}/tomcat-util 2>&1
%if %{gcj_support}
    if [ -x %{_bindir}/rebuild-gcj-db ]; then %{_bindir}/rebuild-gcj-db || true ; fi
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]; then %{_bindir}/rebuild-gcj-db || true ; fi
%endif

%if %{gcj_support}
%post common-lib
if [ -x %{_bindir}/rebuild-gcj-db ]; then %{_bindir}/rebuild-gcj-db || true ; fi
%endif

%if %{gcj_support}
%postun common-lib
if [ -x %{_bindir}/rebuild-gcj-db ]; then %{_bindir}/rebuild-gcj-db || true ; fi
%endif

%if %{gcj_support}
%post server-lib
if [ -x %{_bindir}/rebuild-gcj-db ]; then %{_bindir}/rebuild-gcj-db || true ; fi
%endif

%if %{gcj_support}
%postun server-lib
if [ -x %{_bindir}/rebuild-gcj-db ]; then %{_bindir}/rebuild-gcj-db || true ; fi
%endif

%post admin-webapps
# Remove old automated symlinks
find %{serverdir}/webapps/admin/WEB-INF/lib -name '\[*\]*.jar' -type d \
    | xargs %{__rm} -f
# Create automated links - since all needed extensions may not have been
# installed for this jvm output is muted
build-jar-repository %{serverdir}/webapps/admin/WEB-INF/lib \
    commons-beanutils commons-collections commons-digester struts12-1.2.9 \
    %{name}/catalina-admin 2>&1
build-jar-repository %{serverdir}/webapps/host-manager/WEB-INF/lib \
    %{name}/catalina-host-manager 2>&1
build-jar-repository %{serverdir}/webapps/manager/WEB-INF/lib \
    commons-io %{name}/catalina-manager 2>&1
# commons-fileupload
	 cp $(build-classpath commons-chain) %{serverdir}/webapps/admin/WEB-INF/lib/commons-chain.jar
	 cp $(build-classpath commons-fileupload) %{serverdir}/webapps/manager/WEB-INF/lib/commons-fileupload.jar

%if %{gcj_support}
    if [ -x %{_bindir}/rebuild-gcj-db ]; then %{_bindir}/rebuild-gcj-db || true ; fi
%endif

%if %{gcj_support}
%postun admin-webapps
    if [ -x %{_bindir}/rebuild-gcj-db ]; then %{_bindir}/rebuild-gcj-db || true ; fi
%endif
%endif

%post servlet-%{servletspec}-api
%{_sbindir}/update-alternatives --install %{_javadir}/servlet.jar servlet \
    %{_javadir}/%{name}-servlet-%{servletspec}-api.jar 20400
%{_sbindir}/update-alternatives --install %{_javadir}/servlet_2_4_api.jar servlet_2_4_api \
    %{_javadir}/%{name}-servlet-%{servletspec}-api.jar 20400
%if %{gcj_support}
    if [ -x %{_bindir}/rebuild-gcj-db ]; then %{_bindir}/rebuild-gcj-db || true ; fi
%endif

%post servlet-%{servletspec}-api-javadoc
%{__rm} -f %{_javadocdir}/servletapi # legacy symlink

%postun servlet-%{servletspec}-api
if [ "$1" = "0" ]; then
    %{_sbindir}/update-alternatives --remove servlet \
        %{_javadir}/%{name}-servlet-%{servletspec}-api.jar
    %{_sbindir}/update-alternatives --remove servlet_2_4_api \
        %{_javadir}/%{name}-servlet-%{servletspec}-api.jar
fi
%if %{gcj_support}
    if [ -x %{_bindir}/rebuild-gcj-db ]; then %{_bindir}/rebuild-gcj-db || true ; fi
%endif

%post jsp-%{jspspec}-api
%{_sbindir}/update-alternatives --install %{_javadir}/jsp.jar jsp \
    %{_javadir}/%{name}-jsp-%{jspspec}-api.jar 20000
%{_sbindir}/update-alternatives --install %{_javadir}/jsp_2_0_api.jar jsp_2_0_api \
    %{_javadir}/%{name}-jsp-%{jspspec}-api.jar 20000
%if %{gcj_support}
    if [ -x %{_bindir}/rebuild-gcj-db ]; then %{_bindir}/rebuild-gcj-db || true ; fi
%endif

%post jsp-%{jspspec}-api-javadoc
%{__rm} -f %{_javadocdir}/jsp-api # legacy symlink

%postun jsp-%{jspspec}-api
if [ "$1" = "0" ]; then
    %{_sbindir}/update-alternatives --remove jsp \
        %{_javadir}/%{name}-jsp-%{jspspec}-api.jar
    %{_sbindir}/update-alternatives --remove jsp_2_0_api \
        %{_javadir}/%{name}-jsp-%{jspspec}-api.jar
fi
%if %{gcj_support}
    if [ -x %{_bindir}/rebuild-gcj-db ]; then %{_bindir}/rebuild-gcj-db || true ; fi
%endif

%if %{without_apisonly}
%preun
# Always clean up workdir and tempdir on upgrade/removal
%{__rm} -fr %{workdir}/* %{tempdir}/*
if [ $1 = 0 ]; then
    [ -f /var/lock/subsys/%{name} ] && %{_initrddir}/%{name} stop
    [ -f %{_initrddir}/%{name} ] && /sbin/chkconfig --del %{name}
    # Remove automated symlinks
    for repository in %{commondir}/endorsed; do
        find $repository -name '\[*\]*.jar' -not -type d | xargs %{__rm} -f
    done
    for repository in %{commondir}/lib ; do
        find $repository -name '\[*\]*.jar' -not -type d | xargs %{__rm} -f
    done
    for repository in %{serverdir}/lib ; do
        find $repository -name '\[*\]*.jar' -not -type d | xargs %{__rm} -f
    done
fi

%preun admin-webapps
if [ $1 = 0 ]; then
    find %{serverdir}/webapps/admin/WEB-INF/lib  \
         -name '\[*\]*.jar' \
         -not -name 'catalina-admin*' -not -type d | xargs rm -f
fi

%pre
# Add the "tomcat" user and group
# we need a shell to be able to use su - later
%{_sbindir}/groupadd -g %{tcuid} -r tomcat 2> /dev/null || :
%{_sbindir}/useradd -c "Tomcat" -u %{tcuid} -g tomcat \
    -s /bin/sh -r -d %{homedir} tomcat 2> /dev/null || :
%endif

%if %{without_apisonly}
%files
%defattr(0664,root,tomcat,0775)
%doc %{packdname}/{LICENSE,RELE*,RUNNING.txt,BENCHMARKS.txt}
# symlinks
%{_datadir}/%{name}/common
%{_datadir}/%{name}/temp
%{_datadir}/%{name}/logs
%{_datadir}/%{name}/conf
%{_datadir}/%{name}/server
%{_datadir}/%{name}/shared
%{_datadir}/%{name}/work
%{_datadir}/%{name}/webapps
# Normal directories
%dir %{homedir}
%dir %{bindir}
%dir %{_var}/lib/%{name}
%dir %{_var}/cache/%{name}
%dir %{commondir}
%dir %{commondir}/classes
%dir %{commondir}/lib
%dir %{commondir}/endorsed
%dir %{commondir}/i18n
%dir %{serverdir}
%dir %{serverdir}/classes
%dir %{serverdir}/lib
%{serverdir}/lib/*.renametojar
%dir %{shareddir}
%dir %{shareddir}/classes
%dir %{shareddir}/lib
# Directories with special permissions
%attr(0775,tomcat,root) %dir %{appdir}
%attr(0775,tomcat,root) %dir %{confdir}
%attr(0775,tomcat,root) %dir %{tempdir}
%attr(0770,tomcat,root) %dir %{workdir}
%attr(0775,root,tomcat) %dir %{logdir}
%attr(0664,tomcat,tomcat) %{logdir}/catalina.out
%attr(0775,root,tomcat) %dir %{confdir}/Catalina
%attr(0775,root,tomcat) %dir %{confdir}/Catalina/localhost
%attr(0755,root,root) %{_bindir}/*
%attr(0755,root,root) %{bindir}/relink
%attr(0644,root,root) %{bindir}/*.jar
%attr(0644,root,root) %{bindir}/*.xml
%attr(0755,root,root) %{_initrddir}/%{name}
%attr(0664,tomcat,root) %config(noreplace) %{confdir}/catalina.policy
%attr(0664,tomcat,root) %config(noreplace) %{confdir}/JBossPublicKey.RSA
%attr(0664,tomcat,root) %config(noreplace) %{confdir}/catalina.properties
%attr(0664,tomcat,root) %config(noreplace) %{confdir}/logging.properties
%attr(0664,tomcat,root) %config(noreplace) %{confdir}/tomcat-users.xml
%attr(0664,tomcat,root) %config(noreplace) %{confdir}/%{name}.conf
%attr(0664,tomcat,root) %config(noreplace) %{confdir}/server-minimal.xml
%attr(0664,tomcat,root) %config(noreplace) %{confdir}/server.xml
%attr(0664,tomcat,root) %config(noreplace) %{confdir}/web.xml
%attr(0664,tomcat,root) %config(noreplace) %{confdir}/context.xml
#%config(noreplace) %{confdir}/uriworkermap.properties
#%config(noreplace) %{confdir}/workers.properties
#%config(noreplace) %{confdir}/workers.properties.minimal
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{commondir}/i18n/*
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/bootstrap*
%attr(-,root,root) %{_libdir}/gcj/%{name}/commons-daemon*
%attr(-,root,root) %{_libdir}/gcj/%{name}/commons-logging-api*
#%attr(-,root,root) %{_libdir}/gcj/%{name}/tomcat-juli*
# No longer shipped with tc 5.5.31
#%attr(-,root,root) %{_libdir}/gcj/%{name}/tomcat-jkstatus-ant*
%endif

%files parent
%defattr(0644,root,root,0755)
%{_datadir}/maven2/poms/JPP.tomcat5-parent.pom
%{_mavendepmapfragdir}/tomcat5

%files common-lib
%defattr(0644,root,root,0755)
#%{commondir}/lib/jaf.jar
#%{commondir}/lib/jta.jar
#%{commondir}/lib/javamail.jar
#%{commondir}/lib/commons-collections-tomcat5.jar
#%{commondir}/lib/commons-dbcp-tomcat5.jar
#%{commondir}/lib/commons-pool-tomcat5.jar
#%{commondir}/endorsed/jaxp_parser_impl.jar
#%{commondir}/endorsed/xml-commons-apis.jar
%{commondir}/lib/commons-pool.jar
%{commondir}/lib/commons-dbcp.jar
%{commondir}/lib/mx4j.jar
%{commondir}/lib/mx4j-impl.jar
%dir %{_javadir}/%{name}
%{_javadir}/%{name}/naming*.jar
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-naming-factory.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-naming-resources.pom
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}/naming-*
%endif

%files server-lib
%defattr(0644,root,root,0755)
%{_javadir}/catalina*.jar
%dir %{_javadir}/%{name}
%{_javadir}/%{name}/catalina-ant-jmx*.jar
%{_javadir}/%{name}/catalina-cluster*.jar
%{_javadir}/%{name}/catalina-deployer*.jar
%{_javadir}/%{name}/catalina.jar
%{_javadir}/%{name}/catalina-%{version}.jar
%{_javadir}/%{name}/catalina-optional*.jar
%{_javadir}/%{name}/catalina-storeconfig*.jar
%{_javadir}/%{name}/servlets*.jar
%{_javadir}/%{name}/tomcat*.jar
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.catalina-ant5.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-catalina-ant-jmx.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-catalina-cluster.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-catalina.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-catalina-optional.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-catalina-storeconfig.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-servlets-default.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-servlets-invoker.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-servlets-webdav.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-tomcat-ajp.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-tomcat-apr.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-tomcat-coyote.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-tomcat-http.pom
# Not in the community distro as of tc 5.5.31
# %attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-tomcat-jkstatus-ant.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-tomcat-juli.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-tomcat-util.pom
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}/catalina-ant*
%attr(-,root,root) %{_libdir}/gcj/%{name}/catalina-cluster*
%attr(-,root,root) %{_libdir}/gcj/%{name}/catalina-optional*
%attr(-,root,root) %{_libdir}/gcj/%{name}/catalina-storeconfig*
%attr(-,root,root) %{_libdir}/gcj/%{name}/catalina-%{version}.jar*
%attr(-,root,root) %{_libdir}/gcj/%{name}/servlets-default*
%attr(-,root,root) %{_libdir}/gcj/%{name}/servlets-invoker*
%attr(-,root,root) %{_libdir}/gcj/%{name}/servlets-webdav*
%attr(-,root,root) %{_libdir}/gcj/%{name}/tomcat-ajp*
%attr(-,root,root) %{_libdir}/gcj/%{name}/tomcat-apr*
%attr(-,root,root) %{_libdir}/gcj/%{name}/tomcat-coyote*
%attr(-,root,root) %{_libdir}/gcj/%{name}/tomcat-http*
%attr(-,root,root) %{_libdir}/gcj/%{name}/tomcat-util*
%endif

%files webapps
%defattr(0644,root,tomcat,0775)
%dir %{appdir}/servlets-examples
%{appdir}/servlets-examples/*
%dir %{appdir}/jsp-examples
%{appdir}/jsp-examples/*
%dir %{appdir}/ROOT
%{appdir}/ROOT/*
%dir %{appdir}/tomcat-docs
%{appdir}/tomcat-docs/*
%dir %{appdir}/webdav
%{appdir}/webdav/*
%if %{gcj_support}
%ifnarch ppc64 s390x
%attr(-,root,root) %{_libdir}/gcj/%{name}/catalina-root*
%endif
%endif

%files admin-webapps
%defattr(0640,root,tomcat,0750)
%attr(0660,root,tomcat) %{confdir}/Catalina/localhost/manager.xml
%attr(0660,root,tomcat) %{confdir}/Catalina/localhost/host-manager.xml
%{confdir}/Catalina/localhost/admin.xml
%dir %{appdir}/balancer
%{appdir}/balancer/*
%dir %{serverdir}/webapps
%{serverdir}/webapps/*
%attr(0644,root,root) %{_javadir}/%{name}/catalina-admin*.jar
%attr(0644,root,root) %{_javadir}/%{name}/catalina-manager*.jar
%attr(0644,root,root) %{_javadir}/%{name}/catalina-host-manager*.jar
%attr(0644,root,root) %{serverdir}/webapps/admin/WEB-INF/lib/commons-chain.jar
%attr(0644,root,root) %{serverdir}/webapps/manager/WEB-INF/lib/commons-fileupload.jar
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-catalina-admin.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-catalina-host-manager.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP.tomcat5-catalina-manager.pom
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}/catalina-admin*
%attr(-,root,root) %{_libdir}/gcj/%{name}/catalina-balancer*
%attr(-,root,root) %{_libdir}/gcj/%{name}/catalina-host-manager*
%attr(-,root,root) %{_libdir}/gcj/%{name}/catalina-manager*
%attr(-,root,root) %{_libdir}/gcj/%{name}/commons-fileupload*
%endif

%files %{jname}
%defattr(0644,root,root,0755)
%doc ${RPM_BUILD_DIR}/%{name}-%{version}/%{packdname}/%{jname}/doc/jspc.html
%{_javadir}/%{jname}5-*.jar
%attr(0755,root,root) %{_bindir}/%{jname}*.sh
%attr(0755,root,root) %{_bindir}/jspc*.sh
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP-jasper5-compiler.pom
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP-jasper5-runtime.pom
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{jname}5-*
%endif

%files %{jname}-javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{jname}-%{version}
%{_javadocdir}/%{jname}
%endif

%files servlet-%{servletspec}-api
%defattr(0644,root,root,0755)
%doc %{packdname}/LICENSE
%{_javadir}/%{name}-servlet-%{servletspec}-api*.jar
%{_javadir}/servletapi5.jar
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP-tomcat5-servlet-2.4-api.pom
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{name}-servlet-%{servletspec}-api*
%endif

%files servlet-%{servletspec}-api-javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-servlet-%{servletspec}-api-%{version}
%{_javadocdir}/%{name}-servlet-%{servletspec}-api

%files jsp-%{jspspec}-api
%defattr(0644,root,root,0755)
%doc %{packdname}/LICENSE
%{_javadir}/%{name}-jsp-%{jspspec}-api*.jar
%{_javadir}/jspapi.jar
%attr(0644,root,root) %{_datadir}/maven2/poms/JPP-tomcat5-jsp-2.0-api.pom
%if %{gcj_support}
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{name}-jsp-%{jspspec}-api*
%endif

%files jsp-%{jspspec}-api-javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-jsp-%{jspspec}-api-%{version}
%{_javadocdir}/%{name}-jsp-%{jspspec}-api


%if %{with_repolib}
%files repolib
%defattr(0644,root,root,0755)
%{_javadir}/repository.jboss.com
%endif

%if %{with_zips}
%files zip
%defattr(-,root,root,-)
%dir %{_javadir}/jbossas-fordev
%{_javadir}/jbossas-fordev/tomcat5-%{version}.zip
%{_javadir}/jbossas-fordev/tomcat5-%{version}-admin.zip
%{_javadir}/jbossas-fordev/tomcat5-%{version}-examples.zip

%files src-zip
%defattr(-,root,root,-)
%dir %{_javadir}/jbossas-fordev
%{_javadir}/jbossas-fordev/tomcat5-%{version}-src.zip
%endif

%if %{with_ecj}
%files jasper-eclipse
%defattr(0644,root,root,0755)
%dir %{_datadir}/eclipse
%dir %{_datadir}/eclipse/plugins
%{_datadir}/eclipse/plugins/org.apache.jasper_*
%endif

%changelog
* Thu Feb 17 2012 David Knox <dknox@redhat.com> 0:5.5.33-22_patch_07
- Resolves CVE-2012-0022

* Mon Dec 19 2011 David Knox <dknox@redhat.com> 0:5.5.33-21_patch_06
- Resolves: ownership of files in zip changed to root:root to 
- tomcat:tomcat to avoid permission problems

* Thu Dec 15 2011 David Knox <dknox@redhat.com> 0:5.5.33-20_patch_06
- Resolves: Copy commons-chain and commons-fileupload instead of linking
- in b-j-r to avoid "file not found" errors during install. 
- Symlinks in post need to stay for now

* Fri Dec 2 2011 David Knox  <dknox@redhat.com> 0:5.5.33-19_patch_06
- Resolves: CVE-2011-1184
- Resolves: CVE-2011-3190

* Thu Sep 15 2011 David Knox <dknox@redhat.com> 0:5.5.33-18_patch_05
- Resolves: JBPAPP-4873,JBPAPP-6133,JBPAPP-3630 Security manager issues

* Mon Jul 18 2011 David Knox <dknox@redhat.com> 0:5.5.33-17_patch_05
- Resolves CVE-2011-2526
- Resolves CVE-2011-2204 - Makes changes that affect the admin webapp.
- During testing it was found that access to the admin webapp results
- in a invalid path /login. For more info see https://issues.apache.org/bugzilla/show_bug.cgi?id=38484


* Thu Jun 23 2011 David Knox <dknox@redhat.com> 0:5.5.33-16_patch_04
- jbpapp-4873 can't start with default catalina.policy

* Wed Jun 8 2011 David Knox <dknox@redhat.com> 0:5.5.33-15_patch_04
- jbpapp-3900 library inconsistancies

* Thu May 20 2011 David Knox <dknox@redhat.com> 0:5.5.33-14_patch_04
- jbpapp-6553 - jasper-[compiler,runtime].jar, catalina-ant

* Fri May 13 2011 David Knox <dknox@redhat.com> 0:5.5.33-13_patch_04
- jbpapp-6464 unsigned i18n jars

* Mon May 09 2011 David Knox <dknox@redhat.com> 0:5.5.33-12_patch_04
- jbpapp-3669 stable log name for initscript
- jbpapp-3654 orig files in archives
- jbpapp-6437 NoClassDefFoundError looking for datasource

* Tue Apr 05 2011 David Knox <dknox@redhat.com> 0:5.5.33-11_patch_04
- Directory permission, TOMCAT_LOG, and initd.log

* Tue Mar 29 2011 David Knox <dknox@redhat.com> 0:5.5.33-10_patch_4
- JBPAPP-6122 conf hints for JON

* Thu Mar 24 2011 David Knox <dknox@redhat.com> 0:5.5.33-9_patch_3
- JBPAPP-3654 remove orig files from src distribution too

* Thu Mar 24 2011 David Knox <dknox@redhat.com> 0:5.5.33-8_patch_3
- JBPAPP-3669 initd scripts ouput to catalina.out
- JBPAPP-3654 remove orig files from distribution

* Tue Mar 22 2011 David Knox <dknox@redhat.com> 0:5.5.33-7_patch_3
- JBPAPP-3644 - tomcat enable security manager in sysconfig

* Wed Mar 16 2011 David Knox <dknox@redhat.com> 0:5.5.33-6_patch_2
- JBPAPP-3749 - cannot resolve user database
- EWS zip package requires the javax.sql property also. The zip package 
- doesn't use the tomcat5.conf file (only the rpm install does). Rather than 
- two places, this setting can be found in (zip) catalina.sh;
- (rpm) /usr/sbin/dtomcat5 which is a copy of catalina.sh

* Mon Mar 14 2011 David Knox <dknox@redhat.com> 0:5.5.33-5_patch_2
- Resolves JBPAPP-3749 for zip package

* Tue Mar 08 2011 David Knox <dknox@redhat.com> 0:5.5.33-4_patch_1
- Fix R: to include first bit of release tag
- Run sign-unsigned-jars before zips are created

* Tue Mar 01 2011 David Knox <dknox@redhat.com> 0:5.5.33-3_patch_1
- Resolves: JBPAPP-3749 - cannot resolve user database, found
- typo in conf.

* Wed Feb 23 2011 David Knox <dknox@redhat.com> 0:5.5.33-2_patch_1
- Required additional patch for failonerror copyig tomcat-native

* Thu Feb 10 2011 David Knox <dknox@redhat.com> 0:5.5.33-1_patch_1
- update to tomcat 5.5.33

* Tue Feb 1 2011 David Knox <dknox@redhat.com> 0:5.5.32-1
- update to tomcat 5.5.32

* Fri Jan 7 2011 David Knox <dknox@redhat.com> 0:5.5.31-0
- Update to tomcat5.5.31
- JBPAPP-3749 cannot resolve user database
- JBPAPP-3878 verified tomcat5 init.d script sets ownership

* Thu Jan 6 2011 David Knox <dknox@redhat.com> 0:5.5.28-12
- Fixed Buildrequires typo
- Added BR for zip package for consistancy with packaging 
  guidelines

* Tue Jan 4 2011 David Knox <dknox@redhat.com> 0:5.5.28-11
- Resolves: JIRA JBPAPP-3627

* Thu Nov 18 2010 David Knox <dknox@redhat.com> 0:5.5.28-10-patch_1
- Resolves: JIRA JBPAPP-3626

* Wed Aug 4 2010 David Knox <dknox@rehat.com> - 0:5.5.28-9-patch_1.1
- Fixed bug in CVE-2009-2902 patch that caused a stack overflow

* Tue Jul 13 2010 David Knox <dknox@redhat.com> - 0:5.5.28-9
- Add CVE-2010-2227
- 

* Wed Apr 28 2010 Permaine Cheung <pcheung@redhat.com> - 0:5.5.28-8
- Add missing patches, sources to repolib, and fix repolib location

* Wed Feb 10 2010 Permaine Cheung <pcheung@redhat.com> - 0:5.5.28-7
- Add patch for CVE-2009-3555 (from dknox@redhat.com)

* Wed Feb 10 2010 Permaine Cheung <pcheung@redhat.com> - 0:5.5.28-6
- Add patch for CVE-2009-2693, CVE-2009-2901, CVE-2009-2902 (from dknox@redhat.com)

* Wed Feb 10 2010 Permaine Cheung <pcheung@redhat.com> - 0:5.5.28-5
- Add commons-dbcp,pool,collections-tomcat5 to commonlib dir in zip
- Uncomment library path in config file and add lib64
- Leave commons-logging-api.jar as a real file instead of a symlink
  to avoid upgrade issue

* Tue Jan 26 2010 Permaine Cheung <pcheung@redhat.com> - 0:5.5.28-4
- Add patch for loading tomcat native

* Wed Jan 20 2010 Permaine Cheung <pcheung@redhat.com> - 0:5.5.28-3
- Separate tomcat-parent pom into its own subpackage

* Thu Jan 14 2010 Permaine Cheung <pcheung@redhat.com> - 0:5.5.28-2
- Fix post admin-webapp

* Wed Jan 13 2010 Permaine Cheung <pcheung@redhat.com> - 0:5.5.28-1
- Merge with upstream

* Tue Jan 05 2010 Permaine Cheung <pcheung@redhat.com> - 0:5.5.28-0.3
- BR: and R: jboss-transaction instead of geronimo-jta
- Fix patches 

* Fri Dec 18 2009 Permaine Cheung <pcheung@redhat.com> - 0:5.5.28-0.2
- Add struts-taglib and commons-chain, commons-io jars to admin.zip

* Wed Dec 16 2009 Permaine Cheung <pcheung@redhat.com> - 0:5.5.28-0.1
- Upgrade to 5.5.28
- Add admin.zip to the -zip subpackage
- Update some patches
- Remove patches for CVE-2008-5515, CVE-2009-0033, CVE-2009-0580, CVE-2009-0783
  which are fixed in 5.5.28
- Remove patches for CVE-2008-1232, CVE-2008-1947, CVE-2008-2370, CVE-2008-2938
  which are fixed in 5.5.27
- Remove patches for CVE-2007-5342, CVE-2007-5461 which are fixed in 5.5.26
- Remove patches for CVE-2007-2449, CVE-2007-2450, CVE-2007-3382, CVE-2007-3385
  which are fixed in 5.5.25
 
* Wed Sep 22 2009 Marc Schoenefeld <mschoene@redhat.com> - 0:5.5.23-1.patch07.19
- Fixed NVR to 19 , necessary for CVE-2009-0783 fix 

* Wed Sep 15 2009 David Knox <dknox@redhat.com> - 0:5.5.23-1.patch07.1
- Spinning Errata 8692 CVE-2009-0783 

* Wed Aug 19 2009 David Knox <dknox@redhat.com> - 0:5.5.23-1.patch07.1t
- Merging CVE-2009-0783. Was not advised for patch05.18

* Mon Jul 13 2009 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.18
- Merge CVE fixes from JBoss_4_0_5 branch
- add patch for CVE-2007-5333
  Resolves: rhbz#427766
- add patch for CVE-2008-5515
  Resolves: rhbz#504753
- add patch for CVE-2009-0033
  Resolves: rhbz#493381
- add patch for CVE-2009-0580
  Resolves: rhbz#503978

* Wed Mar 25 2009 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.17
- Remove quotes around $_RUNJAVA in catalina.sh and tool-wrapper.sh

* Wed Mar 25 2009 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.16
- Rebuild

* Wed Mar 25 2009 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.15
- Fix src zip

* Thu Mar 12 2009 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.14
- Fix sed command

* Thu Mar 12 2009 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.13
- Remove %%post webapps
- Move content of the READMEs for the CVE to index.html to avoid broken links
- Add examples-zip for QE

* Fri Feb 27 2009 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.12
- BR jta from geronimo-specs

* Mon Feb 23 2009 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.11
- Fix zip content

* Mon Feb 23 2009 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.10
- Fix zip
- Use new struts

* Fri Jan 23 2009 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.9
- Fix %%post webapps and %%preun webapps
- Add jsvc.tar.gz to zip
- Use glassfish-jaf and glassfish-javamail instead of the classpathx ones

* Thu Jan 22 2009 David Walluck <dwalluck@redhat.com> 0:5.5.23-1.patch05.8
- build zip using upstream release process
- own directories in zip subpackages
- fix path to update-alternatives

* Tue Dec 09 2008 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.7
- Fix zip content

* Thu Dec 04 2008 David Walluck <dwalluck@redhat.com> 0:5.5.23-1.patch05.6
- set jdt.jar to ecj
- fix component-info.xml TAG replacement
- fix repolib file ownership
- rediff catalina.sh.patch so that it applies with --fuzz=0
- change ecj version to >= 1:3.3.1.1

* Tue Dec 02 2008 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.5
- BR and R ecj instead of eclipse-ecj

* Tue Dec 02 2008 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.4
- Fix content of zip

* Tue Nov 25 2008 Permaine Cheung <pcheung@redhat.com> - 0:5.5.23-1.patch05.3
- Add -zip and -src-zip optional subpackages

* Fri Nov 14 2008 Fernando Nasser <fnasser@redhat.com> - 0:5.5.23-1.patch05.2
- Rebuild with Java5

* Tue Nov 04 2008 Fernando Nasser <fnasser@redhat.com> - 0:5.5.23-1.patch05.1
- Rebuild for EWS

* Tue Aug 19 2008 Permaine Cheung <pcheung@redhat.com> 0:5.5.23-1.patch05.0jpp.1jb
- Add patch for CVE-2008-1232, CVE-2008-1947, CVE-2008-2370, CVE-2008-2938

* Fri Apr 11 2008 David Walluck <dwalluck@redhat.com> 0:5.5.23-1.patch04.0jpp.4jb
- dereference symlinks when copying to repodirlib

* Fri Apr 11 2008 David Walluck <dwalluck@redhat.com> 0:5.5.23-1.patch04.0jpp.3jb
- add build-build-properties-default.patch to repodirsrc

* Fri Apr 11 2008 David Walluck <dwalluck@redhat.com> 0:5.5.23-1.patch04.0jpp.2jb
- fix location of repodir using macro for patch level

* Thu Apr 10 2008 David Walluck <dwalluck@redhat.com> 0:5.5.23-1.patch04.0jpp.1jb
- patch for CVE-2007-5342 (ASPATCH-343)
- fix for CVE-2007-1355 (ASPATCH-343)
- patch for IT #168408
- copy correct patch for CVE-2007-5461 to repolib directory
- install repolib sources as mode 0644 and preserve timestamps
- don't build outside of $RPM_BUILD_DIR
- update description in component-info.xml

* Wed Nov 07 2007 Fernando Nasser <fnasser@redhat.com> - 0:5.5.23-1.patch03.0jpp.1jb
- Patch for CVE-2007-5461

* Thu Aug 30 2007 Fernando Nasser <fnasser@redhat.com> - 0:5.5.23-1.patch02.0jpp.2jb
- Fix repolib directory path
- Copy new patches to src directory

* Thu Aug 30 2007 Fernando Nasser <fnasser@redhat.com> - 0:5.5.23-1.patch02.0jpp.1jb
  From jean-frederic clere <jclere@redhat.com>:
- Patch for CVE-2007-3382 and CVE-2007-3385
- Patch for CVE-2007-3386

* Thu Jul 26 2007 Vivek Lakshmanan <vivekl@redhat.com> - 0:5.5.23-0jpp.3.jb.4
- Add tag placeholder back in component-info file

* Thu Jul 26 2007 Vivek Lakshmanan <vivekl@redhat.com> - 0:5.5.23-0jpp.3.jb.3
- Add the new patches to repolib package

* Thu Jul 26 2007 Vivek Lakshmanan <vivekl@redhat.com> - 0:5.5.23-0jpp.3.jb.2
- Remove unnecesary backups of patches

* Thu Jul 26 2007 Vivek Lakshmanan <vivekl@redhat.com> - 0:5.5.23-0jpp.3.jb.1
- Merge spec changes from 0:5.5.23-0jpp.3 over (cosmetic/Examples related fixes)
  which we dont ship in JBoss but less stressful on the eyes with the diff)
- patch for ASPATCH-234

* Sat Apr 28 2007 Vivek Lakshmanan <vivekl@redhat.com> - 0:5.5.23-0jpp.1.jb.1
- Import to JBossAS-4_0_5 branch and modify to build for JBoss 4.0.x
- Add repolib support (on by dafult)
- Modify patch2 and add patch20 to allow for building of 
  jasper-compiler-jdt.jar

* Mon Apr 23 2007 vivek Lakshmanan <vivekl@redhat.com> - 0:5.5.23-0jpp.1
- Resolves: bug 237089 
- Merge 0:5.5.17-8jpp.2 with sources/patches from 5.5.23

* Thu Jan 18 2007 Rafael Schloming <rafaels@redhat.com> - 0:5.5.17-8jpp.2
- Changed PreReq to Requires(pre)

* Wed Oct 4 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-8jpp.1
- Merge with upstream

* Wed Oct 4 2006 Permaine Cheung <pcheung@redhat.com> 0:5.5.17-8jpp
- Fix condrestart in init script and location of init script in the spec file.

* Mon Oct 2 2006 Permaine Cheung <pcheung@redhat.com> 0:5.5.17-7jpp
- Add the new config file, and add the CONNECTOR_PORT variable in it.

* Mon Oct 2 2006 Permaine Cheung <pcheung@redhat.com> 0:5.5.17-6jpp
- Add the ability to start multiple instances of tomcat on the same machine.

* Wed Aug 30 2006 Deepak Bhole <dbhole@redhat.com> 5.5.17-6jpp.2
- Rebuilding.

* Mon Aug 21 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-6jpp.1
- Merge with upstream

* Mon Aug 21 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-6jpp
- Rebuild

* Mon Aug 21 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-5jpp
  From Andrew Overholt <overholt@redhat.com>:
- Silence post common-lib and server-lib.

* Thu Jul 27 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-3jpp_5fc
- Fix regression in relink with patch from Matt Wringe

* Sat Jul 22 2006 Jakub Jelinek <jakub@redhat.com> - 0:5.5.17-3jpp_4fc
- Rebuilt

* Thu Jul 13 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-3jpp_3fc
- Rebuild in full

* Wed Jul 05 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-3jpp_2fc
- Re-enable ppc64 and s390x
- Disable JSP pre-compilation on ppc64 and x390x (FIXME)
- Bootstrap mode (with apisonly) build

* Wed Jul 05 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-3jpp_1fc
- Full build
- Do not build on ppc64 and s390x
- Fix servlet-api.jar path
- Add version to catalina .so
From Ralph Apel <rapel@redhat.com>:
- Re-add patch to add rt.jar
- Add mx4j JMX API and struts to classpath

* Wed Jul 05 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-3jpp_0fc
- Upgrade
- Use any JTA for now
- Try and remove exclude for sample.war
- Bootstrap build with apisonly

* Wed Jul 05 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-3jpp_1rh
- Merge with upstream

* Fri Jun 30 2006 Ralph Apel <r.apel@r-apel.de> 0:5.5.17-3jpp
- Create option --with apisonly to build just tomcat5-servlet-2.4-api,
  tomcat5-jsp-2.0-api and its -javadoc subpackages
- Create option --without ecj to build even when eclipse-ecj not available
- Drop several unnecessary export CLASSPATH=

* Sat Jun 17 2006 Deepak Bhole <dbhole@redhat.com> - 0:5.5.15-1jpp_7fc
- Re-enable ppc64, s390 and s390x architectures now that eclipse is built there

* Mon May 15 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-2jpp_1rh
- Merge with upstream for upgrade to 5.5.17

* Mon May 15 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-2jpp
- Requires on post things that are linked to at post
  Merge changes from downstream:
- Fix line breaks in the tomcat5 init script
- Split preun section among main package and the two new subpackages
- Move catalina-ant*.jar to the server-lib subpackage to avoid circular
  dependency with the main package
- Remove leading zero from alternative priorities
- Rebuild with new classpath-mail as javamail alternative
- Update versions of dependencies and move them to library subpackages
- Use only jta from geronimo-specs

* Mon May 15 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-1jpp
- Upgrade to 5.5.17
- Remove jasper2 subdirectory of jasper from patches and this spec file

* Wed Apr 19 2006 Ralph Apel <r.apel@r-apel.de> 0:5.5.16-3jpp
- Drop jdtCompilerAdapter from build-jar-repository
- Use ant-trax in static webapp build
- Duplicate admin-webapps jars in _javadir and make them world readable
- Direct install of common-lib and server-lib to _javadir and symlink for TC5

* Tue Apr 04 2006 Ralph Apel <r.apel@r-apel.de> 0:5.5.16-2jpp
- Require eclipse-ecj >= 3.1.1 and adapt to it

* Fri Mar 24 2006 Ralph Apel <r.apel@r-apel.de> 0:5.5.16-1jpp
- Upgrade to 5.5.16

* Mon Mar  6 2006 Jeremy Katz <katzj@redhat.com> - 0:5.5.15-1jpp_6fc
- stop scriptlet spew

* Fri Mar  3 2006 Thomas Fitzsimmons <fitzsim@redhat.com> - 0:5.5.15-1jpp_5fc
- Require java-gcj-compat for post and postun sections of
  servlet-%{servletspec}-api, jsp-%{jspspec}-api-javadoc and
  server-lib sub-packages, since these three packages call
  %{_bindir}/rebuild-gcj-db in their post and/or postun sections.

* Wed Mar  1 2006 Rafael Schloming <rafaels@redhat.com> - 0:5.5.15-1jpp_4fc
- Disabled juli logging as a workaround for a number of classpath bugs
- in java.util.logging.*

* Thu Feb 23 2006 Rafael Schloming <rafaels@redhat.com> - 0:5.5.15-1jpp_3fc
- Added jasper-foo symlinks for jars.

* Wed Feb 22 2006 Rafael Schloming <rafaels@redhat.com> - 0:5.5.15-1jpp_2fc
- Exclude ppc64 s390 s390x

* Wed Feb 22 2006 Rafael Schloming <rafaels@redhat.com> - 0:5.5.15-1jpp_1fc
- Updated to 5.5.15

* Tue Feb 14 2006 Ralph Apel <r.apel@r-apel.de> 0:5.5.12-2jpp
- Fix jta.jar location

* Fri Nov 11 2005 Fernando Nasser <fnasser@redhat.com> 0:5.5.12-1jpp
- Place jsp in its own subpackage
- Fix alternative links to jsp and servlet
- Fix alternative priorities to jsp and servlet
- Create library subpackages: common-lib and server-lib
  From Vadim Nasardinov <vadimn@redhat.com> 0:5.5.12-1jpp
- Upgrade to 5.5.12
  From Deepak Bhole <dbhole@redhat.com>
- Fix init script so it works with SELinux

* Wed Jun 08 2005 Fernando Nasser <fnasser@redhat.com> 0:5.5.9-1jpp
- Merge for upgrade
- Change the user to tomcat from tomcat4
- Relax permissions on appdir directory so jonas package can build
- Remove spurious links to log4j.jar from common and server/lib
- Remove spurious dependency on tyrex (only needed for tomcat4)
- Make sure the main package installs first so user tomcat is created
- Reinstate ssl code changes so that tomcat can be built with other SDKs
  and not only with Sun's or BEA's.

* Mon May 09 2005 Fernando Nasser <fnasser@redhat.com> 0:5.5.9-1jpp
- Upgrade to 5.5.9
- Add jmx to bindir and lower requirement to java 1.4.2

* Fri Feb 04 2005 Jason Corley 0:5.5.7-2jpp
- Add provides servletapi5 in addition to obsoletes servletapi5 (Martin Grotzke)

* Thu Feb 03 2005 Jason Corley 0:5.5.7-1jpp
- Upgrade to current stable release, 5.5.7

* Fri Jan 31 2005 Jason Corley 0:5.5.4-17jpp
- Use new eclipse-ecj package to remove old jasper-compiler-jdt.jar hack

* Thu Jan 27 2005 Jason Corley 0:5.5.4-16jpp
- Attempt to replace non-free jta with free geronimo-specs

* Thu Jan 27 2005 Jason Corley 0:5.5.4-15jpp
- Clean rebuild

* Thu Dec 16 2004 Jason Corley 0:5.5.4-14jpp
- First attempt at jasper subpackages

* Thu Dec 16 2004 Jason Corley 0:5.5.4-13jpp
- Yet another "servletapi" naming scheme change

* Tue Dec 14 2004 Jason Corley 0:5.5.4-12jpp
- Update the servletapi and servletapi-javadoc subpackages to the way proposed
  by Gary Benson (based on work by Ralph Apel) in the 5.0.30 RPMs

* Wed Dec 08 2004 Jason Corley 0:5.5.4-10jpp
- Incorporate Fernando Nasser's javaxssl patch from the tomcat 5.0.28 RPM
- Replace find ... -exec's with find | xargs

* Tue Dec 07 2004 Jason Corley 0:5.5.4-9jpp
- First attempt at the whole servletapi issue
- Replace jmxri references with mx4j
- Build with JDK 1.4 and require a 1.4 JDK to run
- Remove cruft
- Clearly lost track of some stuff between changelog entries ;-)

* Fri Dec 03 2004 Jason Corley 0:5.5.4-1jpp
- First attempt at building 5.5

* Fri Sep 10 2004 Fernando Nasser <fnasser@redhat.com> 0:5.0.27-4jpp
- Rebuild using Tyrex 1.0.1

* Sat Sep 04 2004 Fernando Nasser <fnasser@redhat.com> 0:5.0.27-3jpp
- Rebuild with Ant 1.6.2

* Fri Jul 16 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.27-2jpp
- Oops, don't require mx4j 2.0.1. 1.1.1 or later should be enough.
  jmxri won't work anymore since tc5 needs mx4j-tools.

* Fri Jul 16 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.27-1jpp
- Update to 5.0.27 (stable)
- Don't remove tomcat4 user/group on uninstall see the mailing list
  for discussion
- build w/ xml-apis.jar instead of xmlParserAPIs.jar (release notes 5.0.27)
- Require junit 3.8.1 or newer (release notes 5.0.26)
- Require jakarta-commons-dbcp 1.2.1 or newer (release notes 5.0.27)
- Require jakarta-commons-logging 1.0.4 or newer (release notes 5.0.27)
- Require jakarta-commons-pool 1.1 or newer (release notes 5.0.27)

* Wed Jun 09 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.24-3jpp
- Change default webapps file permissions from 0640 -> 0644

* Tue Jun 08 2004 Fernando Nasser <fnasser@redhat.com> 0:5.0.24-2jpp
- Allow browsing of webapps directory so that JOnAS can build.

* Mon May 17 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.24-1jpp
- Update to 5.0.24
- Require xerces-j2 2.6.2 (release notes 5.0.21), also require ant < 1.6
  as tomcat5 doesn't seem to build cleanly with 1.6 yet.

* Fri Mar 19 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.19-2jpp
- Set JAVA_ENDORSED_DIRS by default in tomcat5.conf, it is otherwise empty
  Suggestion from Aleksander Adamowski <aleksander.adamowski@altkom.pl>  

* Wed Feb 25 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.19-1jpp
- Update to 5.0.19

* Fri Jan 23 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.18-1jpp
- Update to 5.0.18
- Build catalina before connectors
- Hack connectors build
- Require xerces-j2 2.6.0 (release notes 5.0.17)

* Sat Jan 17 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.16-4jpp
- Create TC4 user and group separately, lets TC5 work out of the box
  on Trustix (Patch from Iain Arnell)

* Sat Jan 10 2004 Kaj J. Niemi <kajtzu@fi.basen.net> - 0:5.0.16-3jpp
- servletapi5 is required
- move confdir/Catalina from admin-webapps to main package
  (otherwise we end up requiring tomcat5-admin-webapps for struts-webapps)

* Sat Jan 10 2004 Kaj J. Niemi <kajtzu@fi.basen.net> - 0:5.0.16-2jpp
- Fix conflict with tomcat4 catalina-ant.jar in %%_javadir by renaming it
  catalina-ant5.jar for now.

* Fri Jan  9 2004 Kaj J. Niemi <kajtzu@fi.basen.net> - 0:5.0.16-1jpp
- First build for JPackage

* Mon Dec 29 2003 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.16-0.11
- Merge changes from tomcat4.init to tomcat5.init

* Mon Dec 22 2003 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.16-0.10
- Some jsp-examples require jakarta-taglibs-standard to work

* Mon Dec 22 2003 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.16-0.9.1
- Struts should be 1.1 or later according to the release notes
- The /admin webapp works now as well
- manager.xml needs to be group writeable, otherwise tomcat complains

* Fri Dec 19 2003 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.16-0.7
- Accept an older version of xerces-j2 as well.

* Fri Dec 19 2003 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.16-0.6
- Require xerces-j2 instead of just jaxp_parser_impl
- Require jpackage commons-logging instead of internal version

* Wed Dec 17 2003 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.16-0.5
- Tomcat5 isn't beta anymore

* Wed Dec 17 2003 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.16-0.beta.4
- Place jspapi, jmxri, commons-el in common/lib as mentioned in the
  upstream RELEASE-NOTES.txt. This makes jsps actually work.

* Wed Dec 17 2003 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.16-0.beta.3
- Separated jakarta-commons-el from tomcat
- Require servletapi5 and jakata-commons-el
- Added Patch #4 (tomcat5-5.0.16-cluster-pathelement.patch) which fixes
  build failure when servlet-api is renamed something else than the default
- Added Patch #5 (tomcat5-5.0.16-skip-build-on-install.patch) which corrects
  servletapi/jspapi related build snafu on install. They're already built so
  it's OK to skip.

* Thu Dec  4 2003 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.16-0.beta.1
- 5.0.16
- jakarta-commons-el included here instead of somewhere else for now,
  packaging unfinished
- Patch #3 removes dependency to jsvc.tar.gz which doesn't seem to be anywhere

* Tue Aug  5 2003 Kaj J. Niemi <kajtzu@fi.basen.net> 0:5.0.12-0.beta.1
- Based on JPackage.org's tomcat4 .spec
- No compat stuff anymore.
- First build

------------------------------------------------------------------------
Source: rpm2cpio
/mnt/redhat/brewroot/packages/tomcat5/5.5.33/22_patch_07.ep5.el4/src/tomcat5-5.5.33-22_patch_07.ep5.el4.src.rpm
| cpio --quiet -i --to-stdout '*.spec'
