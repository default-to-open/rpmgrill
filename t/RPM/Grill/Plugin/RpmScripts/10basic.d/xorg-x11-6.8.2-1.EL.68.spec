Name: xorg-x11
Version: 6.8.2
Release: 1.EL.68

ExclusiveOS: linux

# allow 'make prep' on rawhide
%define _default_patch_fuzz 2

%define _projectroot		/usr/X11R6
%define _x11dir			%{_projectroot}
%define _x11bindir		%{_x11dir}/bin
%define _x11datadir		%{_x11dir}/lib
%define _x11includedir		%{_x11dir}/include
%define _x11localedir		%{_x11datadir}/X11/locale
%define _x11libdir		%{_x11dir}/%{_lib}
%define _x11mandir		%{_x11dir}/man
%define _x11fontdir		%{_x11datadir}/X11/fonts

%define with_archexec		1

%define with_icons_in_datadir	1
%if %{with_icons_in_datadir}
%define _x11icondir		%{_datadir}/icons
%else
%define _x11icondir		%{_x11datadir}/X11/icons
%endif

# Makes 'make World' build significantly faster
%define with_fastbuild		1
# parallel_build speeds up building on SMP systems, but is broken in
# xorg-x11 6.7.0, 6.8.0, 6.8.1
%define parallel_build		0
%define verbose_build		1
# Builds X with debug symbol info.  This results in *FRECKIN* *HUGE* packages.
# Enable this if you want to debug the modular X server.  As of gdb 5.1.1, this
# requires patches to gdb to be completely useful.  I MEAN HUGE, ie 2-3 times
# the size!  Don't complain - you've been warned!  gdb for X is
# available for download from ftp://people.redhat.com/mharris/gdb-xfree86
%define DebuggableBuild         0
# If enabled, this makes the libraries contain debug info.  In the future I
# would like to either have xorg-x11 debuginfoized or build both sets of libs.
%define with_debuglibs		0
# Pass -save-temps to gcc for debugging purposes
%define with_savetemps		0
%define Glide3version           20010520

%ifarch %{ix86} alpha
%define Glide3Require           1
%else
%define Glide3Require           0
%endif

# Now that rpm mostly handles multilib so to speak, give or take, sortof, we
# don't need to package the libs data stuff in a separate subpackage anymore.
%define with_libs_data		0

%define with_new_savage_driver	0

# s390 doesn't have video hardware.  xorg-x11 support for PPC64 is very very
# new and experimental.  We ship libs only as PPC64 has we ship the PPC 32bit
# X server.  When PPC64 is supported much better in xorg-x11, and we actually
# support 64bit xorg-x11 installations on PPC64 we might enable the X server.
%ifarch s390 s390x ppc64
%define with_Xserver		0
%else
%define with_Xserver		1
%endif

# Enable DRI on supported architectures, but only on Fedora Core 2/3
# variants, ie: only enable PPC DRI on Fedora Core.
%define with_DRI		0
%ifarch %{ix86} x86_64 ia64 alpha
%define with_DRI		1
%endif
%ifarch ppc
%define with_DRI		0
%endif

# libGL version:
# We specify the libGL version here for multiple reasons.  Firstly, so that
# we can add a versioned virtual provide in the subpackage that libGL gets
# included in, so that 3rd party apps needing to Require libGL can require
# libGL in an implementation neutral manner.  We want to ensure that the
# virtual provide version ALWAYS matches the shipping libGL version however,
# and by making an rpm macro, we can easily ensure that the virtual provide
# always matches the version of the file included in the file lists.  If
# a libGL update occurs during development, rpm will fail to package libGL
# due to the version number being bumped, and when the spec file is examined
# to determine the problem, the macro here just needs to be adjusted, and then
# both the virtual provide and the included libGL .so version will be
# guaranteed to always match.
%define libGL_version	1.2
# Same thing for libGLU as for libGL above
%define libGLU_version	1.3

# Set enable_sdk to 1 to enable the SDK when an Xserver is built, or 0 to disable
%define enable_sdk		1
%if %{with_Xserver}
%define with_sdk                %{enable_sdk}
%else
%define with_sdk                0
%endif

%ifarch s390 s390x
%define with_docs		0
%else
%define with_docs		1
%endif

# xf86cfg only works on x86, and alpha, so we ifarch, however xf86cfg is now
# disabled, as we've moved to our own GTK+ config tool redhat-config-xfree86,
# which has been renamed to system-config-display in Fedora Core 2
%ifarch %{ix86} alpha
%define with_xf86cfg            0
%define with_xf86config		0
%else
%define with_xf86cfg            0
%define with_xf86config		0
%endif

%define with_xcalc		1
%define with_xedit		0
%define with_xman		0
%define with_xmh		0

%define with_rstart		0
%define with_xprint		0

# Build fontconfig and package it instead of using external fontconfig
%define with_fontconfig		0
# Eventually we want to build fonts in a separate subpackage, so this option
# toggles font building and subpackage inclusion
%define with_fonts		0

%define with_whiteglass		0
%define with_redglass		0
%define with_handhelds		0

%define with_libxrx		0
# FIXME: Never ship xterm as part of xorg-x11.  This option will be removed
#        entirely in the future as we always will ship xterm separately.
%define with_xterm		0
%define with_sis_dri		0

%define with_dll_modules	0

%define with_bail_on_undef_syms	0

# The following, are post build checks performed in %%check section
# Test for dead symlinks after build and install sections are done?
%define with_dead_symlink_test	1
# Use ldd -r to test for undef syms.  Xorg isn't clean enough for this to be
# enabled except for developmental testing purposes.
%define with_undef_sym_test	0

# with_fortify_source is used to manually enable gcc's fortify source support
# available in newer gcc releases.  It causes "-D_FORTIFY_SOURCE=2" to be
# added to the gcc CFLAGS when building.  Currently, our RHEL4 and FC3 gcc
# have support for this but rpm does not enable it globally by default, so
# this macro causes it to be enabled on those builds.  FC4 has it enabled
# by default in the stock rpm configuration, so it doesn't need to be enabled
# here.  NOTE:  bcopy(), bzero(), vfprintf() are redefined in the X sources,
# causing FORTIFY_SOURCE to be useless for those functions.  Additionally the
# libc_wrapper causes the benefits of using fortify source to be lost for
# those functions wrapped by the wrapper.  Xorg needs some enhancements to
# fully benefit from FORTIFY_SOURCE.
%define with_fortify_source	0

# We don't ship the wacom driver as part of the xorg-x11 package, but
# ship the driver from linuxwacom.sourceforge.org.
%define with_wacom_driver       0

# Command macros
%define __mkfontdir	umask 133; which mkfontdir &> /dev/null && mkfontdir
%define __mkfontscale	umask 133; which mkfontscale &> /dev/null && mkfontscale
# Use this macro to call fc-cache throughout the specfile.
%define __fccache	umask 133; which fc-cache &> /dev/null && fc-cache

# Disable rpm from stripping xorg-x11's modules, or they explode
#if %{DebuggableBuild}
%define __spec_install_post /usr/lib/rpm/redhat/brp-compress
%define debug_package %{nil}
#endif

%define rhbsys  %([ -r /etc/beehive-root ] && echo 1 || echo 0)


######################################################################
######################################################################

Summary: The basic fonts, programs and docs for an X workstation.
License: MIT/X11, and others
Group: User Interface/X
URL: http://xorg.freedesktop.org
BuildRoot: %{_tmppath}/%{name}-%{version}-root

BuildRequires: flex >= 2.5.4a
# Perl is used both by xorg-x11 during build (bdftruncate.pl) and by my specfile
BuildRequires: perl
BuildRequires: bison, zlib-devel, ncurses-devel, utempter, expat-devel
BuildRequires: pam-devel, libpng-devel
# sh-utils needed for 'whoami' in spec file
BuildRequires: sh-utils
# Needed for correct man page compression, since we override the default
# -- Bill Nottingham <notting@redhat.com>
BuildRequires: redhat-rpm-config
BuildRequires: openmotif-devel

%if %{with_fontconfig}
# FIXME: Apparently fontconfig requires ed or ex to build.  We don't want to
# build fontconfig however, so this can go away when we can get rid of
# fontconfig weirdness
BuildRequires: ed
%endif
# Requires rpm 4.0.4 or higher to build or else modules will get stripped
BuildRequires: rpm >= 4.0.4
# xorg-x11 comes with freetype 2.1.7, however our freetype 2.1.7 stock has an
# aliasing which is fixed with -fno-strict-aliasing in our 2.1.7-3 rpm.
BuildRequires: freetype-devel >= 2.1.7-3

%if ! %{with_fontconfig}
BuildRequires: fontconfig-devel >= 2.1
%endif

Prereq: /bin/ln, %{_sbindir}/chkfontpath, %{_x11bindir}/mkfontdir

Requires: %{name}-xfs, %{name}-libs
# Don't make the base-fonts dependancy ver-rel as that is a bit problematic.
# We no longer use "xorg-x11-base-fonts" dep, but instead "base-fonts" virtual
# dep, so that fonts-xorg can provide the dependancy for us, or something else
# in the future.
Requires: base-fonts, utempter
# xinitrc is required as per bug #81424 in Red Hat bugzilla
Requires: xinitrc
Requires: %{_sysconfdir}/pam.d/system-auth
# FIXME: xrdb needs /lib/cpp at runtime (should be changed to use /usr/bin/cpp)
Requires: %{_bindir}/cpp, %{_x11bindir}/xauth
# kernel-drm requirement is so DRI works properly.  The kernel RPM package
# should have a "Provides: kernel-drm = 4.2.0".  Future kernels that provide
# new kernel-drm, should list all supported DRM interfaces with multiple
# Provides: lines.  The 4.2.0 DRM is backward compatible with XFree86 4.1.0
# also.                                                 <mharris@redhat.com>
%if %{with_DRI}
Requires: kernel-drm = 4.3.0
%endif

# Obsolete all old XFree86 3.3.x packages, and other legacy packages
Obsoletes: XFree86-ATI, XFree86-Alliance, XFree86-ChipsTechnologies
Obsoletes: XFree86-Cirrus, XFree86-Cyrix, XFree86-i740, XFree86-i810, XFree86-mga
Obsoletes: XFree86-NeoMagic, XFree86-NVidia, XFree86-Rage128, XFree86-Rendition
Obsoletes: XFree86-SiS, XFree86-3dfx, XFree86-Trident, XFree86-Tseng
Obsoletes: tdfx_dri, X11R6-contrib, XFree86-V4L, XFree86-Setup
Obsoletes: XFree86-3DLabs, XFree86-8514, XFree86-AGX, XFree86-FBDev
Obsoletes: XFree86-Mach32, XFree86-Mach64, XFree86-Mach8, XFree86-Mono
Obsoletes: XFree86-P9000, XFree86-S3, XFree86-S3V, XFree86-SVGA
Obsoletes: XFree86-VGA16, XFree86-W32, XFree86-compat-modules, XFree86-compat-libs
# This one was only on Alpha
Obsoletes: XFree86-TGA
# XFree86-{xtrap-clients,cursors} are integrated into other subpackages now
Obsoletes: XFree86-xtrap-clients, XFree86-cursors
%if ! %{with_xf86cfg}
Obsoletes: XFree86-xf86cfg
%endif

Obsoletes: XFree86

Conflicts: XFree86-sdk < 4.2.99.3-20030115.0

# What archive format to use for main tarball.  ".gz" is preferred because it
# uncompresses twice as fast, which knocks off about 10% of the build time on
# faster machines.  Disk space is cheap.
%define zipext	tar.gz

# Main source tarball for official releases created using the following:
# cvs -d :pserver:anoncvs@cvs.freedesktop.org:/cvs/xorg export -r XORG-6_8_1 xc
# tar zcf xorg-x11-%{version}.tar.gz
Source:   %{name}-%{version}.%{zipext}

Source1:  host.def
Source2:  xserver.pamd
# This file is for FC3/FC4 builds, where the new audit system is not included
# in our pam implementation yet.
Source3:  xdm-pre-audit-system.pamd
# This file is for RHEL4/FC5 builds, which include the new audit system
Source4:  xdm.pamd
Source5:  xfs.init
Source6:  xfs.config
Source7:  xdm.init
%if %{with_archexec}
Source10: archexec
%endif
#Source14: http://www.probo.com/timr/savage-1.1.27t.tgz
Source23: mkxauth
Source24: mkxauth.1x

Source50: xf86-input-evdev-1.0.0.5.tar.bz2
Source51: evdev-Imakefile

# X.org stable branch patch, created using:
# FIXME: These instructions need to be updated to X.org relevance.
# cvs rdiff -u -r xo-6_8_0 -r xo-6_8-branch xc > xorg-x11-6.8.0-xo-6_8-branch-$(/bin/date +"%Y-%m-%d").patch
#Patch0:   XFree86-4.3.0-xf-4_3-branch-2003-11-03.patch

Patch9:   XFree86-4.3.0-makefile-fastbuild.patch

# Patches: 800-829 - xkb keyboard symbol files
# 6000-6049 xkb related patches
Patch800: xorg-x11-6.8.2-sorted-xkbcomp-dirs.patch

##### DRIVER PATCHES #################################################
# Patches 1000-1024: apm driver patches
# Patches 1050-1099: ark driver patches
# Patches 1100-1149: ati driver patches

# Patches 1150-1199: ATI Rage 128
# Patches 1200-1299: radeon driver patches 
Patch1213: XFree86-4.3.0-radeon-ia64-preint10.patch
Patch1214: XFree86-4.3.0-radeon-disable-VideoRAM-option.patch

Patch1215: xorg-x11-6.8.1-ati-radeon-disable-dri.patch
Patch1216: xorg-x11-6.8.2-ati-radeon-7000-disable-dri.patch

Patch1217: xorg-x11-6.8.2-ati-radeon-rn50.patch
Patch1218: xorg-x11-6.8.1-ati-radeon-RV100-bus-master-fix.patch
Patch1219: xorg-x11-6.8.2-ati-radeon-disable-mc-clients-bug.patch
Patch1220: xorg-x11-6.8.2-ati-radeon-rn50-pixel-clock.patch
Patch1221: xorg-x11-6.8.2-ati-radeon-ddc-mode.patch
Patch1222: ati-rn50-disable-render.patch
Patch1223: add-rs482.patch
Patch1224: xorg-x11-6.8.3-radeon-default-mergedfb-ranges.patch

# Patches 1300-1319: chips driver patches 
Patch1300: XFree86-4.2.99.901-chips-default-to-noaccel-on-69000.patch
# For bugzilla https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=82438
Patch1301: XFree86-4.2.99.901-chips-default-to-swcursor-on-65550.patch

# Patches 1320-1339: cirrus driver patches 
# Patches 1340-1359: cyrix driver patches
# Patches 1360-1379: fbdev driver patches
Patch1360: xorg-x11-6.8.2-fbdev-32fbbpp.patch
Patch1361: xorg-x11-6.8.2-fbdev-no16bpp.patch
# Patches 1380-1399: glint driver patches
# Patches 1400-1419: i128 driver patches
# Patches 1420-1439: i740 driver patches
# Patches 1600-1624: Intel i810 / i830 patches
Patch1600: xorg-x11-6.8.2-add-i945-support.patch

# Patches 1625-1649: mga driver patches
Patch1625: xorg-x11-6.8.2-mga-g200se-support.patch
Patch1626: xorg-x11-6.8.2-mga-g200se-update.patch
Patch1627: xorg-x11-6.8.2-mga-g200se-a-updates.patch
Patch1628: xorg-x11-6.8.2-g200-ev-wb.patch
Patch1629: xorg-x11-6.8.2-mga-g200se-dont-force-16bpp.patch
# Patches 1650-1674: neomagic driver patches

# Patches 1675-1699: nv driver patches
Patch1675: xorg-x11-6.8.2-nv-1.2.2-backport.patch
Patch1676: nv34-tweaks.patch
Patch1677: nv-g80-support.patch
Patch1678: nv-g80-lvds.patch

# Patches 1700-1719: rendition driver patches
# Patches 1720-1739: s3 driver patches
# Patches 1740-1759: s3virge driver patches
# Patches 1760-1779: savage driver patches
# Patches 1780-1799: siliconmotion driver patches
# Patches 1800-1824: sis driver patches
# Patches 1825-1849: tdfx driver patches
# Patches 1850-1859: tga driver patches
# Patches 1860-1879: trident driver patches
# Patches 1880-1899: tseng driver patches
# Patches 1900-1919: v4l driver patches
# Patches 1920-1939: vesa driver patches
Patch1920: xorg-x11-6.8.2-vesa-vbe-clear.patch
# Patches 1940-1959: vga driver patches
# Patches 1960-1979: via driver patches
# Patches 1980-1999: vmware driver patches

# Patch2000, add the stand-alone XGI driver. Bug 196785.
#
# Note that this driver has never been released as a tarball, so the patch below adds the
# GIT snapshot as of Jan 25, 2007, where the following modifications have been made:
#
#  - All instances of // comments were changed to /* */ comments to get it to compile
#
#  - The unlibc-wrap patch was reverted, since the libc-wrapper was still used in 6.8.2
#
#  - I commented out a piece of code in xgi-video.c that used symbols RegionsEqual()
#    and XAAFillSolidRectangles(), since these are not available in 6.8.2.
#
Patch2000: add-xgi-driver.patch
Patch2001: xorg-x11-6.8.2-xgi-amd64.patch
Patch2005: xorg-x11-6.8.2-AMD64-override-default-driverlist.patch

Patch2010: add-ast-driver.patch

### Non-video driver patches #########################################
# Patches 2000-2019: xc/nls/{locale.dir,locale.alias,compose.dir} patches
# Manpage fixup  Mike A. Harris <mharris@redhat.com>
# load agpgart for DRM
Patch2022: XFree86-4.1.0-agpgart-load.patch

Patch9007: XFree86-4.2.99.2-netmouse.patch
Patch9008: xorg-x11-6.8.2-dev-input-mice.patch

Patch9013: xorg-Imake-make-icondir-configurable.patch
# These two can be merged into one later.
Patch9015: XFree86-4.2.99.4-IncludeSharedObjectInNormalLib.patch
Patch9016: XFree86-4.3.0-libfontenc-IncludeSharedObjectInNormalLib.patch

# Minor version fixup from debian for manpage strings
Patch9028: XFree86-4.2.99.901-028_fbdev_depth24_support.patch
# Recommendation of Keith Packard
Patch9031: XFree86-4.2.99.901-dont-install-Xcms.txt.patch

Patch9111: XFree86-4.3.0-disable-building-apps-we-do-not-ship.patch

Patch9120: XFree86-4.3.0-ia64-new-elfloader-relocations.patch

Patch9163: XFree86-4.3.0-XRes-IncludeSharedObjectInNormalLib.patch
Patch9181: XFree86-4.3.0-keyboard-disable-ioport-access-v3.patch
Patch9184: xorg-x11-6.8.0-Xserver-increase-max-pci-devices.patch
Patch9189: bug-198266.patch

# ia64 section
Patch9208: XFree86-4.3.0-ia64-drm-locking.patch

# New X.org patches from after Fedora Core integration

# This patch is submitted upstream in the following URLs:
# https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=119032
# http://pdx.freedesktop.org/cgi-bin/bugzilla/show_bug.cgi?id=368 (marked as
# rel-blocker, not committed as of Apr 5, 2004)
# http://bugs.xfree86.org/show_bug.cgi?id=991
Patch9306: xorg-x11-6.7.0-fix-BuildXFree86ConfigTools.patch
Patch9307: xorg-x11-6.7.0-xterm-make-optional.patch
Patch9309: xorg-x11-6.7.0-libxf86config-monitor-freq-fix.patch
Patch9310: xorg-x11-6.8.0-Imake-add-BuildFontDevelUtils-macro.patch

Patch9312: xorg-x11-6.8.0-libXdmcp-build-with-PIC.patch

Patch9317: xorg-x11-6.8.1-init-origins-fix.patch
Patch9319: xorg-x11-6.8.1-nls-indic-locales.patch
Patch9320: xorg-x11-6.8.1-battle-libc-wrapper.patch
Patch9321: xorg-x11-6.8.1.902-ia64-hp-zx2-support-bug-119364.patch
Patch9323: xorg-x11-6.8.1.902-lnxLib-tmpl-sharedlibreq-fixes.patch

Patch9324: xorg-x11-6.8.1-composite-gravity.patch
Patch9325: xorg-x11-6.8.2-gcc4-fix.patch
Patch9326: xorg-x11-6.8.2-ati-radeon-disable-broken-renderaccel-by-default.patch
Patch9327: xorg-x11-6.8.2-ati-radeon-gcc4-fix.patch
Patch9328: xorg-x11-6.8.2-fix-font-crash.patch
Patch9329: xorg-x11-6.8.2-xnest-shape-fix.patch
Patch9331: xorg-x11-6.8.2-XScreenSaverQueryInfo-crash-fix.patch
Patch9332: xorg-x11-6.8.2-cursor-flicker.patch
Patch9333: XFree86-4.1.0-xpm-security-fix-CAN-2005-0605.patch
Patch9334: xorg-x11-6.8.1-ati-radeon-dynamic-clocks-fix-2.patch
Patch9336: xorg-x11-6.8.2-ati-ragexl-ia64-avoidcpiofix.patch
Patch9337: xorg-x11-6.8.2-use-linux-native-pciscan-by-default.patch
Patch9338: xorg-x11-6.8.2-ia64-elfloader-cache-flush.patch
Patch9339: xorg-x11-6.8.2-xkb-dutch-keyboard-layout-fixes.patch
Patch9340: XFree86-4.3.0-security-CAN-2005-2495.patch 
Patch9341: xorg-x11-6.8.2-shadow-framebuffer-leak.patch
Patch9342: XFree86-4.1.0-fdo-7535.patch
Patch9343: xorg-x11-server-CVE-2006-6101.patch

Patch9800: xorg-x11-6.8.2-xkb-segv-bug-168145.patch
Patch9801: xorg-x11-6.8.2-im-lockup-bug-166068.patch
Patch9802: xorg-x11-6.8.2-Xserver-render-unaligned-access-168416.patch
Patch9803: xorg-x11-6.8.2-fstobdf-corrupted-bdf-167699.patch
Patch9804: xorg-x11-6.8.2-gb18030-20020207.patch
Patch9805: xorg-x11-6.8.2-gb18030-enc.patch
Patch9806: xorg-x11-6.8.2-gb18030-locale-alias.patch
Patch9807: xorg-x11-6.8.2-Xserver-pci-infinite-loop.patch
Patch9808: xorg-x11-6.8.2-xconsole-devpts-support-bug-165021.patch
Patch9809: xorg-x11-6.8.2-xkbdata-sun6-keys.patch
Patch9811: xorg-x11-6.8.2-vesa-driver-memory-leak-bug172091.patch
Patch9812: xorg-x11-6.8.2-mesa-i915-squelch-debug-spew.patch
Patch9813: xorg-x11-6.8.2-libXcursor-memleak-fix.patch
Patch9814: xorg-x11-6.8.2-Xnest-xkb-fix-bug177927.patch
Patch9815: xim-deadlock-bug-189849.patch
Patch9816: xorg-x11-6.8.2-xfs-segfault-fix.patch

Patch9820: xorg-x11-6.8.2-render-tris-CVE-2006-1526.patch
Patch9821: xorg-x11-6.8.2-ia64-hp-zx2-pcie-fix.patch
Patch9822: byte-swap-pid.patch
Patch9823: xorg-x11-6.8.2-libGLw-use-system-motif-headers.patch
Patch9824: setuid-fixes.patch
Patch9825: vesa-1.2.1-blank-on-init.patch
Patch9826: xorg-x11-6.8.2-cve-2006-3740-cid-fonts.patch
Patch9827: xorg-x11-6.8.2-int10-update.patch
Patch9828: cve-2007-1003.patch
Patch9829: int-overflow.patch
Patch9830: cve-2007-1351.patch
Patch9831: fx4600-limited-save-restore.patch
Patch9832: xorg-x11-6.8.2-xkb-ca-enhcanced.patch
Patch9833: xorg-x11-6.8.2-libXrandr-swap-coordinates.patch
Patch9834: cve-2007-4568.patch
Patch9835: cve-2007-4730.patch
Patch9836: cve-2007-5760.patch
Patch9837: cve-2007-5958.patch
Patch9838: cve-2007-6427.patch
Patch9839: cve-2007-6428.patch
Patch9840: cve-2007-6429.patch
Patch9841: cve-2008-0006.patch
Patch9842: cve-2008-1377.patch
Patch9843: cve-2008-1379.patch
Patch9844: cve-2008-2360.patch
Patch9845: cve-2008-2361.patch
Patch9846: xorg-x11-6.8.2-xkbcomp-add-ibm_spacesaver.patch
Patch9847: xorg-x11-6.8.2-fix-powerpc-fonts.patch
Patch9848: cve-2011-0465.patch

######################################################################
# Red Hat customizations, not intended for submission upstream
Patch10000: xorg-x11-6.8.0-redhat-custom-startup.patch
Patch10001: XFree86-4.2.99.2-redhat-custom-modelines.patch
# Disable the ugly checkerboard pattern that X starts up with.  We're in the
# year 2002 now, and this pattern just has to go.  No really.  <mharris>
Patch10002: xorg-redhat-die-ugly-pattern-die-die-die.patch
# Parallel make patch, designed specifically to hog all CPU's on all the
# build system boxes and make kernel builds take longer.  <evil grin>
Patch10003: XFree86-4.2.99.901-parallelmake.patch
#XFree86-4.2.99.901-parallelmake-this-time-its-personal.patch
Patch10005: XFree86-4.3.0-redhat-bug-report-address-update.patch
Patch10007: ia64-disable-offscreen-pixmaps.patch


# John Dennis's libGL fixes for exec-shield
# FIXME: This needs to be ported to Mesa head, and submitted by John for
#        discussion/integration in upstream Mesa CVS.
Patch10012: xorg-x11-6.8.0-redhat-libGL-exec-shield-fixes.patch
Patch10015: XFree86-4.3.0-redhat-nv-riva-videomem-autodetection-debugging.patch
# Red Hat Xft enhancements 9009/9010 are dependant on 9008
Patch10020: XFree86-4.3.0-redhat-fontconfig-2.1-slighthint.patch
Patch10022: xorg-redhat-embeddedbitmap.patch
Patch10023: XFree86-4.3.0-redhat-exec-shield-GNU-stack.patch
Patch10024: xorg-x11-6.8.2-pci-remap.patch

# cheating
Source15000: absolute-coords-2758.patch

# Patches in the 20000+ section are Red Hat specific patches that are 
# not intended to be sent upstream in their current state, or are Red Hat
# specific things not intended to be sent upstream at all.  Some are temporary
# workarounds unsuitable for upstream submission, some others are works in
# progress.

# FIXME: This patch makes sessreg work with highuid Linux systems.  It was
# originally submitted to XFree86 a long time ago, but was rejected as being
# non-portable.  This works good enough for us for the time being, until
# proper highuid support is implemented throughout the X.Org source tree.
Patch20002: XFree86-4.2.0-sessreg-highuid.patch
# Disable DRI on 16Mb cards in high res (Mike A. Harris <mharris@redhat.com>)
Patch20004: XFree86-4.2.0-tdfx-disable-dri-on-16Mb-cards-in-hires.patch
# Force mkfontdir to make fonts.dir and encodings.dir, etc. mode 0644 Mike A. Harris <mharris@redhat.com>
# FIXME: This should be updated, and resubmitted upstream to X.Org for 6.9.0
# or X11R7
Patch20005: XFree86-4.2.99.2-mkfontdir-perms.patch
Patch20007: XFree86-4.3.0-redhat-xcursorgen-do-not-build-included-cursors.patch
Patch20008: xorg-x11-6.8.2-maxclients.patch
Patch20009: xorg-x11-6.8.2-blank-at-exit.patch
Patch20010: xorg-x11-6.8.2-keyboard-leds.patch
Patch20011: xorg-x11-6.8.2-gc-max-formats.patch
Patch20012: xorg-x11-6.8.2-drm-device-permissions.patch
Patch20013: xorg-x11-6.8.2-fb-traps-crash.patch
Patch20014: xorg-6.8.2-libglu-pic-build.patch
Patch20015: xorg-x11-6.8.2-backing-store-validategc.patch

Patch30000: xorg-x11-6.8-option-max-clients.patch
Patch30001: xorg-x11-6.8-option-max-clients-fix.patch

# EXPERIMENTAL patches (disabled except for development)

######################################################################
%description
X.org X11 is an open source implementation of the X Window System.  It
provides the basic low level functionality which full fledged
graphical user interfaces (GUIs) such as GNOME and KDE are designed
upon.
######################################################################
%package devel
Summary: X Window System application development package
Group: Development/Libraries
Requires: %{name}-libs = %{version}-%{release}
Obsoletes: xpm-devel, Mesa-devel
Obsoletes: Xft-devel
Provides: xpm-devel, Mesa-devel
%if %{with_archexec}
# archexed moved from "xorg-x11" to "xorg-x11-devel" in the 6.8.0-1 rpm for
# bug #132121
Conflicts: %{name} < 6.8.0
%endif
%if ! %{with_fontconfig}
Requires: fontconfig-devel >= 2.1
%endif
Requires: pkgconfig
Obsoletes: XFree86-devel
Provides: XFree86-devel = 4.4.0
# Virtual provides for libGL and libGLU
# Provide for libGL major version
Provides: libGL-devel = 1
# Provide libGL specific version
Provides: libGL-devel = %{libGL_version}
# Provide for libGLU major version
Provides: libGLU-devel = 1
# Provide libGLU specific version
Provides: libGLU-devel = %{libGLU_version}

%description devel
This development package includes the libraries, header files and
documentation needed for developing applications for the X window system.
######################################################################
%package deprecated-libs-devel
Summary: Deprecated X Window System developmental libraries
Group: Development/Libraries
Requires: %{name}-deprecated-libs = %{version}-%{release}
Requires: %{name}-devel = %{version}-%{release}
# libXp used to be in the 'libs' subpackage, but we moved it in 6.7.99.901
Conflicts: xorg-x11-libs <= 6.7.99.901
Provides: libXp-devel = 6.2

%description deprecated-libs-devel
This package contains shared library runtimes which have been deprecated,
but are provided still for compatibilty with existing applications that link
to them.  Software projects which use these libraries, should port their
code to current alternatives.
######################################################################
%package font-utils
Summary: Font utilities required for installing fonts
Group: User Interface/X
# mkfontdir, ttmkfdir and other util were moved here so this conflict is needed
Conflicts: XFree86 < 4.2.0-5.2,
# ucs2any moved from xorg-x11-tools to xorg-x11-font-utils in 6.7.99.903-3
Conflicts: xorg-x11-base-fonts <= 6.7.99.903-3
# The fonts/util subdir moved from xorg-x11-base-fonts to xorg-x11-font-utils
# in 6.7.99.903-3
Conflicts: xorg-x11-base-fonts <= 6.7.99.903-3
Obsoletes: XFree86-font-utils
Provides: XFree86-font-utils = 4.4.0
Provides: font-utils

%description font-utils
Includes mkfontdir, and other font related utilities which are required when
installing font packages.
######################################################################
%package xfs
Summary: A font server for the X Window System.
Group: System Environment/Daemons
Prereq: fileutils sed shadow-utils initscripts
# chkconfig is needed for %post %postun
Prereq: /sbin/chkconfig, %{_x11bindir}/mkfontdir, %{_bindir}/ttmkfdir
Requires: %{name}-libs = %{version}-%{release}
# xfs rpm scripts that use /sbin/service
Requires(preun,postun): /sbin/service
Requires: base-fonts
Obsoletes: XFree86-xfs
Provides: xfs

%description xfs
This package contains the X Window System xfs font server and related
utilities, which is used to serve legacy core fonts to a local or remote
X server.
######################################################################
%package twm
Summary: A simple window manager
Group: User Interface/X
%if ! %{with_xterm}
Requires: xterm
%endif
Provides: windowmanager
# The twm.1 manpage was moved from the XFree86 package to the twm package
# to fix bug #70025 on July 29 2002 - Mike A. Harris
Conflicts: XFree86 <= 4.2.0-57.1
Obsoletes: XFree86-twm
Provides: twm

%description twm
A simple and lightweight window manager
######################################################################
%package xdm
Summary: X Display Manager
Requires: %{name} = %{version}, /etc/pam.d/system-auth
# pam requires were added for bug #159332 for new audit system.  It really
# should be a virtual provide in the pam package, to avoid odd version-release
# games, but this is the way it was done so we have to live with it.
Requires: pam >= 0.77-66.8

# xinitrc requirement on 3.13 for user login shell enhancement to Xsession
Requires: xinitrc >= 3.13
Group: User Interface/X
Obsoletes: XFree86-xdm
Provides: xdm

%description xdm
X Display Manager.
######################################################################
%package libs
Summary: Shared libraries needed by the X Window System
Group: System Environment/Libraries
# Now that Xft2 is part of XFree86 4.3.0, we obsolete the old standalone one
Obsoletes: Xft
Requires: freetype >= 2.1.7-3
Obsoletes: xpm
Provides: xpm
%if %{with_libs_data}
Requires: %{name}-libs-data = %{version}-%{release}
%else
Obsoletes: xorg-x11-libs-data < %{version}-%{release}
Obsoletes: XFree86-libs-data
# Files moved from these packages to XFree86-libs-data, and now to
# xorg-x11-libs-data, so we conflict them
Conflicts: XFree86 <= 4.2.99.2-0.20021105.0, XFree86-libs <= 4.2.99.2-0.20021105.0
%endif
#Requires(post,postun,verify): /sbin/ldconfig grep textutils
Prereq: /sbin/ldconfig grep textutils
Obsoletes: XFree86-libs
# FIXME: Currently the same libs are present, but that's soon to change
Provides: XFree86-libs = 4.4.0

%description libs
This package contains the shared libraries required for running X
applications.
######################################################################
%package deprecated-libs
Summary: Deprecated X Window System shared libraries 
Group: System Environment/Libraries

%description deprecated-libs
This package contains shared library runtimes which have been deprecated,
but are provided still for compatibilty with existing applications that link
to them.  Software projects which use these libraries, should port their
code to current alternatives.
######################################################################
%if %{with_libs_data}
%package libs-data
Summary: Architecture independent data required by X Window System libraries
Group: System Environment/Libraries
Obsoletes: XFree86-libs-data
# Files moved from these packages to XFree86-libs-data, and now to
# xorg-x11-libs-data, so we conflict them
Conflicts: XFree86 <= 4.2.99.2-0.20021105.0, XFree86-libs <= 4.2.99.2-0.20021105.0

%description libs-data
Architecture independent data files required by the X11 runtime libraries,
including locale and compose database files, XErrorsDB, rgb.txt, etc.
%endif
######################################################################
# Font subpackages
%if %{with_fonts}
%package base-fonts
Summary: Base fonts required by the X Window System
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir
# Required so upgrades work, since base fonts moved here from main pkg
Conflicts: XFree86 <= 4.2.0-3.1
# The fonts.* files from truetype and syriac moved from those pkgs to base
Conflicts: XFree86-truetype-fonts < 4.2.99.901-20030209.2
Conflicts: XFree86-syriac-fonts < 4.2.99.901-20030209.2
Obsoletes: XFree86-base-fonts
# Added to force removal of XFree86-ISO8859-2-Type1-fonts and 
# fonts-ISO8859-2-Type1 on upgrades, as this was renamed to the latter in
# RHL 7.2 and then removed entirely around RHL 8.0.  These fonts were removed
# because they are very broken, among other reasons, so we do not support them
# at all.  By forcing their removal, we can have better guarantees that people
# do not experience problems with these broken fonts when upgrading their OS.
# Adding it back now to fix (#129523)
Obsoletes: XFree86-ISO8859-2-Type1-fonts, fonts-ISO8859-2-Type1
Provides: base-fonts

%description base-fonts
This package provides the base fonts that are required by the X Window System.
######################################################################
%package truetype-fonts
Summary: TrueType fonts provided by the X Window System
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir, %{_bindir}/ttmkfdir
Obsoletes: XFree86-truetype-fonts

%description truetype-fonts
A collection of truetype fonts which are part of the core X Window System
distribution.
######################################################################
%package syriac-fonts
Summary: Syriac TrueType fonts by Beth Mardutho
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir, %{_bindir}/ttmkfdir
Obsoletes: XFree86-syriac-fonts

%description syriac-fonts
A collection of Syriac truetype fonts from Beth Mardutho, which are part
of the core X Window System distribution.
######################################################################
%package 75dpi-fonts
Summary: A set of 75dpi resolution fonts for the X Window System.
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir
Obsoletes: XFree86-75dpi-fonts

%description 75dpi-fonts
A set of 75 dpi fonts used by the X window system.
######################################################################
%package 100dpi-fonts
Summary: A set of 100dpi resolution fonts for the X Window System.
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir
Obsoletes: XFree86-100dpi-fonts

%description 100dpi-fonts
A set of 100 dpi fonts used by the X window system.
######################################################################
%package ISO8859-2-75dpi-fonts
Summary: A set of 75dpi Central European language fonts for X.
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir
Obsoletes: XFree86-ISO8859-2-75dpi-fonts

%description ISO8859-2-75dpi-fonts
Contains a set of 75dpi fonts for Central European languages.
######################################################################
%package ISO8859-2-100dpi-fonts
Summary: A set of 100dpi Central European language fonts for X.
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir
Obsoletes: XFree86-ISO8859-2-100dpi-fonts

%description ISO8859-2-100dpi-fonts
Contains a set of 100dpi fonts for Central European languages.
######################################################################
%package ISO8859-9-75dpi-fonts
Summary: ISO8859-9-75dpi-fonts
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir
Obsoletes: XFree86-ISO8859-9-75dpi-fonts

%description ISO8859-9-75dpi-fonts
Contains a set of 75dpi fonts for the Turkish language.
######################################################################
%package ISO8859-9-100dpi-fonts
Summary: ISO8859-9-100dpi-fonts
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir
Obsoletes: XFree86-ISO8859-9-100dpi-fonts

%description ISO8859-9-100dpi-fonts
Contains a set of 100dpi fonts for the Turkish language.
######################################################################
%package ISO8859-14-75dpi-fonts
Summary: ISO8859-14-75dpi-fonts
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir
Obsoletes: XFree86-ISO8859-14-75dpi-fonts

%description ISO8859-14-75dpi-fonts
Contains a set of 75dpi fonts in the ISO8859-14 encoding which
provide Welsh support.
######################################################################
%package ISO8859-14-100dpi-fonts
Summary: ISO8859-14-100dpi-fonts
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir
Obsoletes: XFree86-ISO8859-14-100dpi-fonts

%description ISO8859-14-100dpi-fonts
Contains a set of 100dpi fonts in the ISO8859-14 encoding which
provide Welsh support.
######################################################################
%package ISO8859-15-75dpi-fonts
Summary: ISO8859-15-75dpi-fonts
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir
Obsoletes: XFree86-ISO8859-15-75dpi-fonts

%description ISO8859-15-75dpi-fonts
Contains a set of 75dpi fonts in the ISO8859-15 encoding which
provide Euro support.
######################################################################
%package ISO8859-15-100dpi-fonts
Summary: ISO8859-15-100dpi-fonts
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir
Obsoletes: XFree86-ISO8859-15-100dpi-fonts

%description ISO8859-15-100dpi-fonts
Contains a set of 100dpi fonts in the ISO8859-15 encoding which
provide Euro support.
######################################################################
%package cyrillic-fonts
Summary: Cyrillic fonts for X.
Group: User Interface/X
Prereq: /usr/sbin/chkfontpath, %{_x11bindir}/mkfontdir
Obsoletes: XFree86-cyrillic-fonts

%description cyrillic-fonts
Contains a set of Cyrillic fonts.
%endif
# End of font subpackages ############################################
######################################################################
%if %{with_docs}
%package doc
Summary: Documentation on various X11 programming interfaces.
Group: Documentation
Obsoletes: XFree86-doc

%description doc
This package contains various documentation in PostScript format on
the various X APIs, libraries, and other interfaces.  If you need
low level X documentation, you will find it here.  Topics include
the X protocol, the ICCCM window manager standard, ICE session management,
the font server API, etc.
%endif
######################################################################
%package Xdmx
Summary: Distributed Multihead X Server and utilities
Group: User Interface/X
Requires: %{name} = %{version}-%{release}
Provides: Xdmx

%description Xdmx
Xdmx is proxy X server that provides multi-head support for multiple displays
attached to different machines (each of which is running a typical X server).
When Xinerama is used with Xdmx, the multiple displays on multiple machines
are presented to the user as a single unified screen.  A simple application
for Xdmx would be to provide multi-head support using two desktop machines,
each of which has a single display device attached to it.  A complex
application for Xdmx would be to unify a 4 by 4 grid of 1280x1024 displays
(each attached to one of 16 computers) into a unified 5120x4096 display.
######################################################################
%package Xnest
Summary: A nested server.
Group: User Interface/X
Requires: %{name} = %{version}-%{release}
Obsoletes: XFree86-Xnest
Provides: Xnest

%description Xnest
Xnest is an X server, which has been implemented as an ordinary
X application.  It runs in a window just like other X applications,
but it is an X server itself in which you can run other software.  It
is a very useful tool for developers who wish to test their
applications without running them on their real X server.
######################################################################
%package tools
Summary: Various X Window System tools
Group: User Interface/X
Obsoletes: X11R6-contrib
Requires: %{name}
Obsoletes: XFree86-tools

%description tools
Various tools for X, including listres, xcalc, and xload among others.

This package contains all applications that used to be in X11R6-contrib
in older releases.
######################################################################
%package xauth
Summary: X authority file utility
Group: User Interface/X
Conflicts: XFree86 < 4.2.0-50.11
Obsoletes: mkxauth
Provides: mkxauth
Obsoletes: XFree86-xauth
Provides: xauth

%description xauth
The xauth program is used to edit and display the authorization information
used in connecting to the X server.
######################################################################
%package Mesa-libGL
Summary: A 3D graphics library which uses an OpenGL-like API
Group: System Environment/Libraries
# FIXME: These should be versioned to the Mesa version
Obsoletes: Mesa
Provides: Mesa
Obsoletes: XFree86-Mesa-libGL
# Conflict is due to this package being split out from XFree86-libs a long time ago
Conflicts: XFree86-libs < 4.2.0-50.5

%description Mesa-libGL
The Mesa 3D graphics library is a powerful and generic toolset for
creating hardware assisted computer graphics. To the extent that Mesa
utilizes the OpenGL command syntax or state machine, it is being used
with authorization from Silicon Graphics, Inc. However, the author
(Brian Paul) makes no claim that Mesa is in any way a compatible
replacement for OpenGL or associated with Silicon Graphics, Inc. Those
who want a licensed implementation of OpenGL should contact a licensed
vendor. Mesa is very similar to OpenGL and you might find Mesa to be a
valid alternative to OpenGL.
######################################################################
%package Mesa-libGLU
Summary: Commonly used GL utility library
Group: System Environment/Libraries
Obsoletes: XFree86-Mesa-libGLU
# Conflict is due to this package being split out from XFree86-libs a long time ago
Conflicts: XFree86-libs < 4.2.0-50.5

%description Mesa-libGLU
libGLU is a utility library used by a lot of OpenGL applications
######################################################################
%if %{with_xf86cfg}
%package xf86cfg
Summary: X server configuration program
Group: User Interface/X
Obsoletes: XFree86-XF86Setup
Requires: %{name} = %{version}-%{release}
# Removed dep on Xconfigurator and changed to the actual Cards file instead
Requires: %{_x11datadir}/X11/Cards
# /usr/X11R6/include/X11/pixmaps/* moved from XFree86-devel to XFree86-xf86cfg
# in 4.3.0-3.8 so we need a Conflicts, however we don't build or ship it anyway
Conflicts: XFree86-devel < 4.3.0-3.8
Obsoletes: XFree86-xf86cfg

%description xf86cfg
X server configuration tool
%endif
######################################################################
%package Xvfb
Summary: A X Windows System virtual framebuffer X server.
Group: User Interface/X
Requires: %{name} = %{version}-%{release}
Obsoletes: XFree86-Xvfb
Provides: Xvfb

%description Xvfb
Xvfb (X Virtual Frame Buffer) is an X server that is able to run on
machines with no display hardware and no physical input devices.
Xvfb simulates a dumb framebuffer using virtual memory.  Xvfb does
not open any devices, but behaves otherwise as an X display.  Xvfb
is normally used for testing servers.
######################################################################
%if %{with_sdk}
%package sdk
Summary: SDK for X server driver module development
Group: User Interface/X
#Prereq: no idea what prereqs we need yet.
Obsoletes: XFree86-sdk
#Provides: XFree86-sdk = 4.4.0

%description sdk
The SDK package provides the developmental files which are necessary for
developing X server driver modules, and for compiling driver modules
outside of the standard X11 source code tree.  Developers writing video
drivers, input drivers, or other X modules should install this package.
%endif
##########  PREP  ###################################################
%prep
%setup -q -c

##########  PATCH  ##################################################
chmod 444 xc/config/cf/xfree86.cf
# xc/config/cf/xfree86.cf.OBSOLETE-USE-xorg.cf-INSTEAD
#%patch0 -p0 -b .xf-4_3-branch

%if %{with_new_savage_driver}
{
   echo "Updating SAVAGE driver with %{SOURCE14}"
   pushd xc/programs/Xserver/hw/xfree86/drivers
   mv savage savage-4.3.0
   tar zxvf %{SOURCE14}
   popd
}
%endif

# Pull evdev driver into the tree.  This is a little more tricky than
# it could be but we try to use the same setup as the RHEL-5
# standalone driver.  Same tarball, same patches.
{
  pushd xc/programs/Xserver/hw/xfree86/input
  mkdir evdev
  tar jxf %{SOURCE50} xf86-input-evdev-1.0.0.5/src/evdev.c -O > evdev/evdev.c
  cp %{SOURCE51} evdev/Imakefile
  patch -d evdev -b -z .absolute-coords-2758 < %{SOURCE15000}
  popd
}

%if %{with_fastbuild}
%patch9 -p0 -b .makefile-fastbuild
%endif

%patch800 -p1 -b .sorted-xkbcomp

%patch1213 -p0 -b .radeon-ia64-preint10
%patch1214 -p0 -b .radeon-disable-VideoRAM-option

%patch1216 -p0 -b .ati-radeon-7000-disable-dri
%patch1217 -p0 -b .ati-radeon-rn50
# Disabled and replaced by patch 1219 xorg-x11-6.8.2-ati-radeon-disable-mc-clients-bug.patch
#%patch1218 -p0 -b .ati-radeon-RV100-bus-master-fix
%patch1219 -p0 -b .ati-radeon-disable-mc-clients-bug
%patch1220 -p0 -b .ati-rn50-pixel-clock
%patch1221 -p1 -b .ati-radeon-ddc-mode
%patch1222 -p1 -b .ati-rn50-disable-render.patch
%patch1223 -p1 -b .add-rs482
%patch1224 -p1 -b .mergedfb-ranges

# FIXME: Chips & technologies -  Disable these two for now, to see if the
# problems are resolved that these two worked around.
# mharris - Jul 15, 2004
#%patch1300 -p0 -b .chips-default-to-noaccel-on-69000
#%patch1301 -p0 -b .chips-default-to-swcursor-on-65550

# backport fix for fbdev fbbpp needed for xenfb (#204117)
%patch1360 -p1 -b .fbbpp
%patch1361 -p1 -b .xen-16bpp

# Backport i945 support from Xorg CVS.
%patch1600 -p0 -b .add-i945-support

# Bug #183686: Matrox G200SE support
%patch1625 -p0 -b .g200se
%patch1626 -p1 -b .g200se-update
%patch1627 -p1 -b .g200se-a-update
%patch1628 -p1 -b .g200-ev-wb
%patch1629 -p1 -b .g200-no-16bpp

# nv updates
%patch1675 -p1 -b .nv-1.2.2-backport
%patch1676 -p1 -b .nv34-tweaks
# remove g80 support for 4.7
#%patch1677 -p1 -b .g80
#%patch1678 -p0 -b .g80-lvds

# Add Option "ModeSetClearScreen" to vesa(4) (#205361)
%patch1920 -p1 -b .vbe-clear

# Bug #196785 - XGI Z7 support
%patch2000 -p1 -b .add-xgi-driver
%patch2001 -p1 -b .add-amd64-driver

%patch2005 -p0 -b .AMD64-override-default-driverlist

# Bug #261621 - AST2000 driver
%patch2010 -p0 -b .add-ast-driver

######################################################################
%patch2022 -p1 -b .agpgart-load

# FIXME: patch doesn't apply to xorg-x11.  It may be that it is not needed
# anymore due to being fixed in an alternate way, or it may still be needed,
# and needs a minor tweak to apply. We disable it for now until we find
# someone with a netmouse affected by this problem.
#%patch9007 -p0 -b .netmouse
%patch9008 -p1 -b .dev-input-mice
%patch9013 -p0 -b .make-icondir-configurable

# These two can be merged into one later.
%patch9015 -p0 -b .IncludeSharedObjectInNormalLib
%patch9016 -p0 -b .libfontenc-IncludeSharedObjectInNormalLib

# Fixes from Daniel Stone's Debian debs
# FIXME: This needs to be investigated for xorg-x11 packaging and fixed/updated
#%patch9028 -p0 -b .028_fbdev_depth24_support
%patch9031 -p0 -b .dont-install-Xcms.txt
# Don't build these apps if all of them are disabled
%if ! %{with_xedit}%{with_xman}%{with_xmh}
# FIXME: This needs to be investigated for xorg-x11 packaging and fixed/updated
#%patch9111 -p0 -b .disable-building-apps-we-do-not-ship
%endif
# FIXME: This needs to be investigated for xorg-x11 packaging and fixed/updated
#%patch9120 -p0 -b .ia64-new-elfloader-relocations

%patch9163 -p0 -b .XRes-IncludeSharedObjectInNormalLib
# FIXME: This needs to be investigated for xorg-x11 packaging and fixed/updated
#%patch9181 -p0 -b .keyboard-disable-ioport-access-v3
%patch9184 -p0 -b .Xserver-increase-max-pci-devices
%patch9189 -p1 -b .bug198266.patch

# FIXME: This needs to be investigated for xorg-x11 packaging and fixed/updated
#%patch9208 -p0 -b .ia64-drm-locking

%patch9306 -p0 -b .fix-BuildXFree86ConfigTools
# FIXME: No longer applies to 6.8.0 cvs development.  Not important patch,
# so no major urge to port it forward.
#%patch9307 -p0 -b .xterm-make-optional
%patch9309 -p0 -b .libxf86config-monitor-freq-fix
%patch9310 -p0 -b .Imake-add-BuildFontDevelUtils-macro
%patch9312 -p0 -b .libXdmcp-build-with-PIC
%patch9317 -p0 -b .init-origins-fix
%patch9319 -p0 -b .nls-indic-locales

%patch9321 -p0 -b .ia64-hp-zx2-support-bug-119364
%patch9323 -p0 -b .lnxLib-tmpl-sharedlibreq-fixes

%patch9324 -p0 -b .composite-gravity.patch
%patch9326 -p0 -b .ati-radeon-disable-broken-renderaccel-by-default
%patch9327 -p0 -b .ati-radeon-gcc4-fix
%patch9328 -p0 -b .fix-font-crash.patch
%patch9329 -p0 -b .xnest-shape-fix.patch
%patch9331 -p0 -b .XScreenSaverQueryInfo-crash-fix

%patch9333 -p0 -b .xpm-security-fix-CAN-2005-0605
%patch9334 -p0 -b .ati-radeon-dynamic-clocks-fix-2
%patch9336 -p0 -b .ati-ragexl-ia64-avoidcpiofix
# FIXME: This patch is intended for RHEL4_U2, so is disabled for RHEL4_U1 for
# now.
%patch9337 -p0 -b .use-linux-native-pciscan-by-default

%patch9338 -p0 -b .ia64-elfloader-cache-flush
%patch9339 -p0 -b .xkb-dutch-keyboard-layout-fixes
%patch9340 -p0 -b .security-CAN-2005-2495.patch 
%patch9341 -p0 -b .shadow-framebuffer-leak.patch
%patch9342 -p1 -b .fdo-7535.patch
%patch9343 -p1 -b .CVE-2006-6101

%patch9800 -p0 -b .xkb-segv-bug-168145
%patch9801 -p0 -b .im-lockup-bug-166068
%patch9802 -p0 -b .Xserver-render-unaligned-access-168416
%patch9803 -p0 -b .fstobdf-corrupted-bdf-167699
%patch9804 -p0 -b .gb18030-20020207.patch
%patch9805 -p0 -b .gb18030-enc.patch
%patch9806 -p0 -b .gb18030-locale-alias.patch
%patch9807 -p0 -b .Xserver-pci-infinite-loop
%patch9808 -p0 -b .xconsole-devpts-support-bug-165021
%patch9809 -p0 -b .xkbdata-sun6-keys
%patch9811 -p0 -b .vesa-driver-memory-leak-bug172091
%patch9812 -p0 -b .mesa-i915-squelch-debug-spew
%patch9813 -p0 -b .libXcursor-memleak-fix
%patch9814 -p0 -b .Xnest-xkb-fix-bug177927
%patch9815 -p1 -b .fix-xim-deadlock-bug-189849
%patch9816 -p1 -b .xfs-segfault-fix

%patch9820 -p0 -b .render-tris-CVE-2006-1526
%patch9821 -p0 -b .ia64-hp-zx2-pcie-fix
%patch9822 -p1 -b .byte-swap-pid
%patch9823 -p1 -b .libGLw-use-system-motif-headers
%patch9824 -p1 -b .setuid-fixes
#%patch9825 -p1 -b .blank-on-init
%patch9826 -p1 -b .cid-fonts
%patch9827 -p1 -b .x86emu-update
%patch9828 -p1 -b .cve-2007-1003
%patch9829 -p1 -b .int-overflow
%patch9830 -p1 -b .cve-2007-1351
%patch9831 -p1 -b .fx4600
%patch9832 -p0 -b .xkb-ca-enhcanced
%patch9833 -p1 -b .coordinates
%patch9834 -p1 -b .cve-2007-4568
%patch9835 -p1 -b .cve-2007-4730
%patch9836 -p1 -b .cve-2007-5760
%patch9837 -p1 -b .cve-2007-5958
%patch9838 -p1 -b .cve-2007-6427
%patch9839 -p1 -b .cve-2007-6428
%patch9840 -p1 -b .cve-2007-6429
%patch9841 -p1 -b .cve-2008-0006
%patch9842 -p0 -b .cve-2008-1377
%patch9843 -p0 -b .cve-2008-1379
%patch9844 -p0 -b .cve-2008-2360
%patch9845 -p0 -b .cve-2008-2361
%patch9846 -p1 -b .xkbcomp-ibm
%patch9847 -p1 -b .ppc-font
%patch9848 -p1 -b .cve-2011-0465

########################################################################
# Red Hat custom patches
%patch10000 -p0 -b .redhat-custom-startup
%patch10001 -p0 -b .redhat-custom-modelines
# By default, we remove the default X server grey stipple pattern.
%patch10002 -p0 -b .redhat-die-ugly-pattern-die-die-die
# FIXME The parallel make patch might patch stuff that is fixed in a different
# way now, but that doesn't conflict with the patch.  Disabled to be safe.
%if %{parallel_build}
#%patch10003 -p0 -b .parallelmake
%endif
# FIXME: This needs to be investigated for xorg-x11 packaging and fixed/updated
#%patch10005 -p0 -b .redhat-bug-report-address-update
%patch10007 -p1 -b .ia64-disable-offscreen-pixmaps

# FIXME: These need to be updated for Xorg-x11 at some point
#%patch10007 -p0 -b .redhat-version-change-notification

# FIXME: This patch needs to be ported to *MESA* CVS, and included there
#        *FIRST*, before being submitted to X.Org at all.
#%patch10012 -p0 -b .redhat-libGL-exec-shield-fixes
%patch10015 -p0 -b .redhat-nv-riva-videomem-autodetection-debugging

#%patch10020 -p0 -b .redhat-fontconfig-2.1-slighthint
%patch10022 -p0 -b .redhat-embeddedbitmap
# FIXME: This needs to be investigated for xorg-x11 packaging and fixed/updated
#%patch10023 -p0 -b .redhat-exec-shield-GNU-stack
%patch10024 -p1 -b .pci-remap

%patch20002 -p0 -b .sessreg-highuid
# FIXME: This may not be needed any more.  We can leave it disabled and get
#        some tdfx users to hammer on it.  If no problems arise, we'll leave
#        it disabled.
#%patch20004 -p0 -b .tdfx-disable-dri-on-16Mb-cards-in-hires
# FIXME: This needs to be investigated for xorg-x11 packaging and fixed/updated
#        Also, mkfontscale, and possibly other utilities should be examined as well.
#%patch20005 -p0 -b .mkfontdir-perms
# Do not build the xcursor cursors as we do not ship them anyway
%if %([ '%{with_whiteglass}' -eq '0' -a '%{with_redglass}' -eq '0' -a '%{with_handhelds}' -eq '0' ] && echo 1 || echo 0)
%patch20007 -p0 -b .redhat-xcursorgen-do-not-build-included-cursors
%endif

%patch20008 -p1 -b .maxclients
%patch20009 -p1 -b .blank-at-exit
%patch20010 -p1 -b .keyboard-leds
%patch20011 -p0 -b .gc-max-format
%patch20012 -p1 -b .drm-device-permissions
%patch20013 -p1 -b .fbtraps
%patch20014 -p1 -b .glu-pic
%patch20015 -p1 -b .validategc

%patch30000 -p1 -b .max-client-option
%patch30001 -p1 -b .max-client-option-fix

######################################################################
#####  CREATE host-$arch.def  ##############################################
pwd
%define rhstr Red Hat Enterprise Linux 4

%if %{rhbsys}
%define vendorstring %{rhstr}
%else
%define vendorstring Unsupported Custom Build by %(whoami)
%endif

# FIXME: Hack to remove -g from RPM_OPT_FLAGS until XFree86 can be built
# with new rpm/gdb -debuginfo goodness
export RPM_OPT_FLAGS=${RPM_OPT_FLAGS//-g/}
%if %{with_fortify_source}
export RPM_OPT_FLAGS="${RPM_OPT_FLAGS} -D_FORTIFY_SOURCE=2"
%endif

# Copy our static architecture independant host.def into place
cp %{SOURCE1} xc/config/cf/
echo -e "\n\nGenerating architecture specifc host-%{_arch}.def file.\n\n"

cat > xc/config/cf/host-%{_arch}.def << EOF
#define XFree86CustomVersion "%vendorstring: %{version}-%{release}"
/* Experimental custom messages */
#define XFree86RedHatCustom	YES

#define BuilderString "Build Host: %(hostname -f)\n"
#define LinuxDistribution	LinuxRedHat
    
#define BuildDebug		%{DebuggableBuild}
/* #define XFree86Devel		%{DebuggableBuild} */

%if %{with_debuglibs}
#define DebuggableLibraries	YES
%endif

#define BootstrapCFlags         $RPM_OPT_FLAGS -pipe

/* Add -Wa,--noexecstack to AsCmd, in order to force all assembler files to
 * use GNU stacks.  This was accomplished in an alternative way in our XFree86
 * packaging via XFree86-4.3.0-redhat-exec-shield-GNU-stack.patch, which
 * patched every assembler file to add a .note.GNU-stack section, which is
 * considered a superior solution, but our patch was non-portable to non-GNU
 * systems.  This is a cleaner hack for now.
 *      -- Mike A. Harris <mharris@redhat.com>
 */
#define AsCmd                   CcCmd -c -x assembler -Wa,--noexecstack

/* FIXME: Remove -fno-strength-reduce and GccAliasingArgs after confirming
 * upstream that they are not needed for anything on Linux
 */
%if %{with_savetemps}
#define DefaultGcc2i386Opt      $RPM_OPT_FLAGS GccAliasingArgs -save-temps
#define DefaultGcc2x86_64Opt    $RPM_OPT_FLAGS GccAliasingArgs -save-temps
#define DefaultGcc2AxpOpt       $RPM_OPT_FLAGS GccAliasingArgs -save-temps -Wa,-m21164a
#define DefaultGcc2PpcOpt       $RPM_OPT_FLAGS GccAliasingArgs -save-temps
#define DefaultGcc2Ppc64Opt     $RPM_OPT_FLAGS GccAliasingArgs -save-temps
%else
#define DefaultGcc2i386Opt      $RPM_OPT_FLAGS GccAliasingArgs -pipe
#define DefaultGcc2x86_64Opt    $RPM_OPT_FLAGS GccAliasingArgs -pipe
#define DefaultGcc2AxpOpt       $RPM_OPT_FLAGS GccAliasingArgs -pipe -Wa,-m21164a
#define DefaultGcc2PpcOpt       $RPM_OPT_FLAGS GccAliasingArgs -pipe
#define DefaultGcc2Ppc64Opt     $RPM_OPT_FLAGS GccAliasingArgs -pipe
%endif

/* We need StaticNeedsPicForShared on all architectures so that static
 * libraries getting linked into shared libs works properly. (#163909)
 */
#define StaticNeedsPicForShared YES

#define MakeDllModules		%{with_dll_modules}

%if %{parallel_build}
#define ParallelMakeFlags	-j%(getconf _NPROCESSORS_ONLN)
/* This one seems to not work properly on GLU gosh darned it, possibly a
 * conflict with HJL's patch */
/* #define HasParallelMake	YES */
%endif

%if ! %{with_Xserver}
#define XorgServer			NO
%endif
#define BuildServer			YES
#define XVirtualFramebufferServer	YES
#define XnestServer			YES

/* Make xtrans fail gracefully by default, for bug #129622 and others */
#define XtransFailSoft		YES

/* We want includes in %{_includedir}/GL, so we move them there later on
 * because the LinkGLToUsrInclude option makes the GL subdirectory a symlink,
 * which is bad for RPM packaging as other packages may place files there,
 * plus there's the whole rpm replacing a symlink with a dir, etc. thing.
 */
#define LinkGLToUsrInclude	NO

/* The OpenGL ABI on Linux standard states libGL and libGLU must be present in
 * /usr/lib either directly, or as symlinks.  The supplied Imake config option
 * LinkGLToUsrLib makes absolute symlinks rather than relative ones, so it is
 * not suitable for us to use.
 */
#define LinkGLToUsrLib		NO
/* LinkGLToUsrInclude makes an absolute symlink to the _x11includedir, which
 * essentially makes %{_libdir}/GL a symlink, which is messy, and may conflict
 * with other package's files that may be installed in the GL include dir for
 * whatever reason.  We disable this option for now, and handle things
 * ourselves with a bit of scripting in the spec file.
 */
#define LinkGLToUsrInclude	NO
#define BuildGLwLibrary		YES
#define ForceNormalLib		YES

/* Disable joystick support because it is totally broken */
#define JoystickSupport		NO


/* FIXME: MOST of the HasXXXXXX defines below can be discarded when we update
 * to the X.org X11 tree, because linux.cf sets defaults for them on the
 * Linux platform.  I need to check and ensure the new defaults match what
 * we expect.   -- mharris
 */

/* FIXME: This should be defaulted upstream correctly, or patched and sent
 * upstream, and then removed from our specfile.
 */
%ifarch s390 s390x ppc64
#define HasAgpGart              NO
%else
#define HasAgpGart              YES
%endif

/* FIXME: HasFontconfig is broken so we have to use UseFontconfig
 * Update: This appears to work now (4.3.0-11.2), so HasFontconfig is being used
 * experimentally in rawhide now.  HasExpat can probably be removed if this works out.
 */
%if ! %{with_fontconfig}
#define HasFontconfig		YES
%endif

/* Expat is only needed by fontconfig (4.3.0) */
#define HasExpat		YES
#define HasFreetype2		YES
#define HasPam			YES
#define HasPamMisc		YES
#define HasZlib			YES

%if %{with_bail_on_undef_syms}
/* FIXME: This should be more configureable in stock Imake configs.  The
 * default SharedLibraryLoadFlags in 4.3.0 is merely "-shared", however
 * I'm adding "-Wl,-z,defs" upon Jakub's recommendation as it should cause
 * ld to bail if there are undefined symbols at link time.
 *
 * Additional information:  This is useful for test builds, to find missing
 * deps over time and fix them, however there are some really screwed up
 * things in the tree, which have never listed deps right as far as I can
 * see.  Also, the X server doesn't like being built like this I'm told by
 * Gentoo developers who have tried this before too.  Hopefully we can work
 * towards a sane build with this enabled at some point.  Here is a reference
 * bug from Gentoo:  http://bugs.gentoo.org/show_bug.cgi?id=49038
 */
#define SharedLibraryLoadFlags	-shared -Wl,-z,defs
%endif

#define HasDevRandom            YES
#define HasLinuxInput		YES

#define HasGlide3		%{Glide3Require}
%if %{Glide3Require}
#define Glide3LibName		glide3
#define Glide3IncDir		%{_includedir}/glide3
%endif

%if %{with_fonts}
#define BuildFonts              YES
#define BuildSpeedoFonts        NO
#define BuildCyrillicFonts      YES
#define BuildBethMarduthoFonts	YES
/* #define BuildISO8859_1Fonts     YES */
#define BuildISO8859_2Fonts	YES
#define BuildISO8859_3Fonts	NO
#define BuildISO8859_4Fonts	NO
#define BuildISO8859_5Fonts	BuildCyrillicFonts
/* #define BuildISO8859_6Fonts	NO  */
#define BuildISO8859_7Fonts	YES 
/* #define BuildISO8859_8Fonts	NO  */
#define BuildISO8859_9Fonts	YES
#define BuildISO8859_10Fonts	NO
#define BuildISO8859_11Fonts	NO
#define BuildISO8859_12Fonts	NO
#define BuildISO8859_13Fonts	NO
#define BuildISO8859_14Fonts	YES
#define BuildISO8859_15Fonts	YES
#define BuildISO8859_16Fonts	NO
%else
#define BuildFonts              NO
/* ucs2any and bdftruncate */
#define BuildFontDevelUtils	YES
%endif

#define InstallXcmsTxt          NO
#define BuildXF86MiscExt        YES
#define BuildHtmlManPages       NO

/* FIXME: This is commented out, in order to test XFree86's Imake DRI defaults
 * for each architecture.  Once confirmed all DRI capable archs build, we can
 * remove this, for a cleaner environmentally friendly host.def
 * YES=1 in Imake.tmpl and NO=0 so we can just use with_DRI here
 */
#define BuildXF86DRI		%{with_DRI}
#define BuildXF86DRM            NO

/* Do not build config tools if we are not shipping them anyway */
%if ! %{with_xf86cfg}%{with_xf86config}
#define BuildXFree86ConfigTools NO
%endif

/* This disables building of libXaw 8, since we only ship Xaw 6 and 7 for
 * legacy application compatibility.
 */
#define BuildXaw		NO

%if ! %{with_xprint}
#define BuildXprint		NO
#define BuildXprintClients	NO
/* OpenMotif and Java currently use libXp, as well as some other stuff.  We
 * are currently shipping libXp for compatibility, but consider it deprecated,
 * and we plan to remove it entirely in a future OS release, after a
 * reasonable migration period to give 3rd parties time to migrate their apps
 * to libgnomeprint and libgnomeprintui.
 */
#define BuildXprintLib		YES
%endif

#define BuildXterm		%{with_xterm}

/* FIXME: We don't need this anymore? */
#define UseXserverWrapper       YES

#define UseUtempter             YES
#define UseInternalMalloc       NO
#define UseMatroxHal            NO

/* FIXME: Other distros set these to yes.  Should we do this soon too?  */
#define UseConfDirForXkb           NO
#define UseConfDirForAppDefaults   NO

#undef  DefaultUserPath
#define DefaultUserPath		/usr/local/bin:/bin:/usr/bin
#undef  DefaultSystemPath
#define DefaultSystemPath	/usr/local/sbin:/sbin:/usr/sbin:/bin:/usr/bin

/* We default to the Red Hat Bluecurve(TM) cursor theme, but if it isn't
 * installed, X will fallback to core cursors, so no forced dependancy is
 * required.
 */
#define DefaultCursorTheme	Bluecurve

/* FIXME: Check and see if we actually need this junk still, or if Imake
 * defaults are ok now. */
#define AdmDir              /var/log
#define LbxproxyDir         /etc/X11/lbxproxy
#define ProxyManagerDir     /etc/X11/proxymngr
#define ServerConfigDir     /etc/X11/xserver
#define XdmDir              /etc/X11/xdm
#define XConfigDir          /etc/X11
#define XinitDir            /etc/X11/xinit

/* Do not override video drivers for Alpha architecture any more, because
 * we do not have officially supported Red Hat OS products for Alpha.  Let's
 * just use the default driverset instead.
 * %ifarch alpha
 * #define XF86CardDrivers mga nv tga sis rendition \
 *			i740 tdfx cirrus tseng \
 *			fbdev ati vga v4l glint
 * %endif
 */

/* https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=112175
 * This should probably be ifnarch %{ix86} instead of ifarch ia64, but we'll
 * leave it this way for the time being.   mharris@redhat.com
 */
%ifarch ia64
#define ATIAvoidNonPCI YES
%endif

%ifarch ia64
#define XF86CardDrivers mga nv tdfx v4l fbdev glint ati vga cirrus
%endif

#define DriverManDir    \$(MANSOURCEPATH)4
#define DriverManSuffix 4x /* use just one tab or cpp will die */
#define MiscManDir      \$(MANSOURCEPATH)7
#define MiscManSuffix   7x /* use just one tab or cpp will die */

EOF

##########  BUILD  ##################################################
%build
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT
# Speed up script processing
export LANG=C
# Make sure RPM_BUILD_DIR/%{name}-%{version} does not contain any CVS dirs
# prior to building
find "$RPM_BUILD_DIR/%{name}-%{version}" -name CVS -type d | xargs rm -rf

%if %{DebuggableBuild}
makeg World -C xc FAST=1
%else
make World -C xc FAST=1
%endif

##########  INSTALL  #################################################
%install
# Speed up script processing
export LANG=C

# Enable set -x if verbose_build is enabled
%{!?verbose_build:set -x}
make -C xc DESTDIR=$RPM_BUILD_ROOT install install.man
%if %{with_sdk}
make -C xc DESTDIR=$RPM_BUILD_ROOT install.sdk
%endif
# install the host-$arch.def config file
install -m 644 xc/config/cf/host-%{_arch}.def $RPM_BUILD_ROOT%{_x11datadir}/X11/config/

# FIXME: These mkdirs might be removable now
mkdir -p $RPM_BUILD_ROOT%{_bindir}
mkdir -p $RPM_BUILD_ROOT%{_includedir}
# Install pam related files
{
    mkdir -p $RPM_BUILD_ROOT/etc/{pam.d,security/console.apps}
    install -c -m 644 %{SOURCE2} $RPM_BUILD_ROOT/etc/pam.d/xserver
    install -c -m 644 %{SOURCE4} $RPM_BUILD_ROOT/etc/pam.d/xdm
    touch $RPM_BUILD_ROOT/etc/security/console.apps/xserver
}
# Move OpenGL includes in %{_includedir}/GL instead of the default location,
# because the OpenGL ABI for Linux dictates that the OpenGL includes must be
# in /usr/include/GL.  The Imake LinkGLToUsrInclude would theoretically work,
# however that makes /usr/include/GL a symlink to the default X directory,
# which isn't particularly useful, and can cause rpm directory/symlink upgrade
# problems when switching from one OpenGL implementation to another.  The
# best longer term fix for this, is to add a new InstallGLToUsrInclude Imake
# option which does exactly what we're doing below, as there's no useful
# reason to have the includes in 2 locations really, especially on Linux
# systems.  Additionally InstallGLToUsrInclude once implemented, should be
# enabled by default.
# FIXME: Implement imake InstallGLToUsrInclude option
{
    mkdir -p $RPM_BUILD_ROOT/%{_includedir}/GL
    mv $RPM_BUILD_ROOT%{_x11includedir}/GL/* $RPM_BUILD_ROOT/%{_includedir}/GL/
    rmdir $RPM_BUILD_ROOT%{_x11includedir}/GL
}
# Explicitly create XDM authdir
mkdir -m 700 -p $RPM_BUILD_ROOT/var/lib/xdm/authdir

mkdir -p $RPM_BUILD_ROOT%{_libdir}/pkgconfig

# Install the Red Hat xfs config file and initscript
mkdir -p $RPM_BUILD_ROOT/etc/{X11/fs,rc.d/init.d}
install -c -m 644 %{SOURCE6} $RPM_BUILD_ROOT/etc/X11/fs/config
install -c -m 755 %{SOURCE5} $RPM_BUILD_ROOT/etc/rc.d/init.d/xfs

# FIXME: Can Imake do this?  Fix up symlinks
{
    ln -sf ../X11R6/include/X11 $RPM_BUILD_ROOT%{_includedir}/X11
    ln -sf ../X11R6/include/DPS $RPM_BUILD_ROOT%{_includedir}/DPS
}
# Backward compatibility symlink
ln -sf ../..%{_x11datadir}/X11/xkb $RPM_BUILD_ROOT/etc/X11

# Create ld.so.conf include file
mkdir -p $RPM_BUILD_ROOT/etc/ld.so.conf.d
echo %{_x11libdir} > $RPM_BUILD_ROOT/etc/ld.so.conf.d/xorg-x11-%{_arch}.conf

# Symlink shared libs
{
    pushd $RPM_BUILD_ROOT%{_x11libdir}
    for lib in *.so.*; do ln -sf $lib ${lib%.so*}.so ; done
    popd
    for lib in libGL.so libGL.so.1 libGLU.so libGLU.so.1 ; do
        ln -sf ../..%{_x11libdir}/$lib $RPM_BUILD_ROOT%{_libdir}/$lib
    done
}

# Create various ghost files, needed by RPM when packaging
{
    # Make ghost X server config files
    # FIXME: The XF86Config and XF86Config-4 files are for legacy compat with
    # XFree86, and may cease to function or be removed at any time.
    for configfile in xorg.conf XF86Config XF86Config-4 ; do
        touch $RPM_BUILD_ROOT/etc/X11/$configfile
    done
%if %{with_fonts}
    # Make ghost fonts.alias, fonts.dir, encodings.dir files
    FONTDIR=$RPM_BUILD_ROOT%{_x11fontdir}
    touch $FONTDIR/{OTF,TTF}/fonts.alias
    for subdir in 100dpi 75dpi CID local misc Type1 TTF cyrillic ; do
        rm -f $FONTDIR/$subdir/{encodings,fonts}.dir
        touch $FONTDIR/$subdir/{encodings,fonts}.dir
        chmod 0644 $FONTDIR/$subdir/{encodings,fonts}.dir
    done
%endif

    # Remove fonts which contain bad codepoints, as documented in bug #97591
    rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMCtesiphon.otf
    rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMKharput.otf
    rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMMalankara.otf
    rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMMidyat.otf
    rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMQenNeshrin.otf
    rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMTurAbdin.otf
    rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMUrhoyBold.otf
    rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMUrhoy.otf
}

# Make sure all manpage dirs exist
mkdir -m 755 -p $RPM_BUILD_ROOT%{_x11mandir}/man{1,2,3,4,5,6,7,8} || :

# Fix permissions on locale/common/*.so libs
# FIXME: (CVS X doesn't have this dir, it is locale/lib/common now
#chmod 755 $RPM_BUILD_ROOT%{_x11localedir}/common/*.so.*

# Install mkxauth
{
    install -m 755 %{SOURCE23} $RPM_BUILD_ROOT%{_x11bindir}/
    install -m 644 %{SOURCE24} $RPM_BUILD_ROOT%{_x11mandir}/man1/
}
# Ugly hack to architecturally genericize xft-config and gccmakedep using
# my archexec script
{
    pushd $RPM_BUILD_ROOT/%{_x11bindir}
    # install archexec
%if %{with_archexec}
    install -m 755 %{SOURCE10} .
%endif

    for script in gccmakedep xft-config ; do
        mv $script $script-%{_arch}
        ln -s archexec $script
    done
    popd
}
# Copy CHANGELOG document into place for %%doc directive to find
cp xc/programs/Xserver/hw/xfree86/CHANGELOG .
# Create file list for SDK, because the list of files/dirs differs greatly
# depending on architecture, and RPM doesn't allow nested conditionals.
# FIXME: This should probably move up to where make install.sdk is called
%if %{with_sdk}
{
   SDKDIR=$RPM_BUILD_ROOT/%{_x11libdir}/Server
   # Find the directories first
   find $SDKDIR -type d | sort | \
      sed -e "s#.*$RPM_BUILD_ROOT/%{_x11libdir}#%dir %%{_x11libdir}#g" > filelist.sdk
   # Append the files
   find $SDKDIR ! -type d | sort | \
      sed -e "s#.*$RPM_BUILD_ROOT/%{_x11libdir}#%%{_x11libdir}#g" >> filelist.sdk
   # Add the filelist.sdk itself to itself and install it
   echo %%{_x11libdir}/Server/filelist.sdk >> filelist.sdk
   cp filelist.sdk $RPM_BUILD_ROOT/%{_x11libdir}/Server/filelist.sdk
}
%endif
# FIXME: This needs to be fixed up to only ship on supported architectures
{
   touch filelist.%{name}
   # Include new I/O utils for architectures that they work on
   for file in inb inl inw ioport outb outl outw ; do
      if [ -x $RPM_BUILD_ROOT/%{_x11bindir}/$file ] ; then
         echo %%{_x11bindir}/$file >> filelist.%{name}
      fi
   done
}

# Move pkgconfig files to proper location in _libdir
# FIXME: Redo this with Imake and submit patch upstream
{
   mv $RPM_BUILD_ROOT%{_x11libdir}/pkgconfig/* $RPM_BUILD_ROOT%{_libdir}/pkgconfig/
   rmdir $RPM_BUILD_ROOT%{_x11libdir}/pkgconfig
}


######################################################################
# STRIP SECTION - must come just before DELETE UNWANTED FILES section
# strip the stuff that's safe to strip
%if ! %{DebuggableBuild}
{
#    set +x
    # Strip ELF binary executables of debug symbols and .comment section
    for file in $(find $RPM_BUILD_ROOT -type f -perm +0111 -exec file {} \; | \
                    grep -v ' shared object,' | \
                    sed -n -e 's/^\(.*\):[  ]*ELF.*, not stripped/\1/p')
    do
	# strip wont take both of these on one commandline for some reason
        strip --strip-debug $file || :
        strip -R .comment $file || :
    done
    # Strip shared libraries of .comment section, and all unneeded symbols
    # strip wont take both of these on one commandline for some reason
    strip --strip-unneeded	$RPM_BUILD_ROOT%{_x11libdir}/*.so.* || :
    strip -R .comment		$RPM_BUILD_ROOT%{_x11libdir}/*.so.* || :
    strip --strip-unneeded	$RPM_BUILD_ROOT%{_libdir}/*.so.* || :
    strip -R .comment		$RPM_BUILD_ROOT%{_libdir}/*.so.* || :
# Enable this only after testing and verifying it works properly
    strip --strip-unneeded $RPM_BUILD_ROOT%{_x11localedir}/%{_lib}/common/*.so.* || :
    strip -R .comment $RPM_BUILD_ROOT%{_x11localedir}/%{_lib}/common/*.so.* || :
}
%endif

######################################################################
# DELETE UNWANTED FILES SECTION - must come after all else
# error: Installed (but unpackaged) file(s) found:
{
%if ! %{with_redglass}
   rm -rf $RPM_BUILD_ROOT/%{_x11icondir}/redglass
%endif
%if ! %{with_whiteglass}
   rm -rf $RPM_BUILD_ROOT/%{_x11icondir}/whiteglass
%endif
%if ! %{with_handhelds}
   rm -rf $RPM_BUILD_ROOT/%{_x11icondir}/handhelds
%endif
%if ! %{with_fontconfig}
   rm -rf $RPM_BUILD_ROOT/etc/fonts $RPM_BUILD_ROOT/%{_x11includedir}/fontconfig
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/{fc-cache,fc-list,fontconfig-config}
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/{fc-cache,fc-list}.1*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man3/fontconfig.3*
   rm -f $RPM_BUILD_ROOT%{_x11libdir}/libfontconfig.*
%endif
%if ! %{with_rstart}
   rm -rf $RPM_BUILD_ROOT/etc/X11/rstart
   rm -rf $RPM_BUILD_ROOT%{_x11datadir}/X11/rstart 
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/rstart*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/rstart*.1*
%endif
%if ! %{with_xedit}
   rm -rf $RPM_BUILD_ROOT%{_x11datadir}/X11/xedit
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/xedit
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/xedit.1*
%endif
%if ! %{with_xman}
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/xman
   rm -f $RPM_BUILD_ROOT%{_x11datadir}/X11/xman*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/xman.1*
%endif
%if ! %{with_xf86cfg}
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/xf86cfg
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/xf86cfg.1*
%endif
%if ! %{with_xf86config}
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/xf86config
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/xf86config.1*
%endif
%if ! %{with_xmh}
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/xmh
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/xmh.1*
%endif
# FIXME: Fix this by patching Imake configs and submit upstream (hack fix bug #49990)
%if ! %{with_libxrx}
   rm -f $RPM_BUILD_ROOT%{_x11libdir}/libxrx.*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/libxrx.1*
%endif
%if ! %{with_sis_dri}
   rm -f $RPM_BUILD_ROOT/%{_x11libdir}/modules/dri/sis_dri.so
%endif
%if ! %{with_Xserver}
   rm -f $RPM_BUILD_ROOT/etc/X11/xorg.conf*
   rm -f $RPM_BUILD_ROOT/etc/X11/XF86Config*
   rm -r $RPM_BUILD_ROOT/etc/X11/xserver
   rm $RPM_BUILD_ROOT/%{_x11datadir}/X11/xserver
   # Added to remove X11/etc stuff on RHL 9 ppc/s390/s390x builds because we
   # don't ship products on those platforms anyway.
   rm -rf $RPM_BUILD_ROOT/%{_x11datadir}/X11/etc
   rm $RPM_BUILD_ROOT%{_x11bindir}/startx
   rm $RPM_BUILD_ROOT%{_x11bindir}/xinit
   rm $RPM_BUILD_ROOT%{_x11mandir}/man1/startx.1*
   rm $RPM_BUILD_ROOT%{_x11mandir}/man1/Xserver.1*
   rm $RPM_BUILD_ROOT%{_x11mandir}/man1/xinit.1*
%endif

# Remove i810 XvMC client library driver on architectures the video hardware
# doesn't exist on, only ship it on those it is.
%ifnarch %{ix86} ia64 x86_64
   rm -f $RPM_BUILD_ROOT%{_x11libdir}/libI810XvMC.*
%endif

%ifarch s390 s390x ppc ppc64
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/mmapr
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/mmapw
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/pcitweak
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/scanpci
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/pcitweak.1*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/scanpci.1*
%endif

{
# rm/unlink example config files that we do not ship
   rm -f $RPM_BUILD_ROOT%{_x11datadir}/X11/XF86Config.{98,eg,indy}
   # The following are uncommented for the time being as I'm lazy.
   rm -f $RPM_BUILD_ROOT/etc/X11/xdm/GiveConsole
   rm -f $RPM_BUILD_ROOT/etc/X11/xdm/TakeConsole
   rm -f $RPM_BUILD_ROOT/etc/X11/xdm/Xaccess
   rm -f $RPM_BUILD_ROOT/etc/X11/xdm/Xsession
   rm -f $RPM_BUILD_ROOT/etc/X11/xdm/Xsetup_0
   rm -f $RPM_BUILD_ROOT/etc/X11/xdm/xdm-config
   rm -f $RPM_BUILD_ROOT/etc/X11/xinit/xinitrc
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/ccmakedep
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/ccmakedep.1*
   # FIXME: X.org CVS includes the XDarwin manpage in Linux, duh
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/XDarwin.1*
   # Remove DRM sources from installed tree (new to xorg-x11)
   rm -rf $RPM_BUILD_ROOT%{_x11dir}/src
}

%ifarch ppc64 s390 s390x
   # XOrg X11 started including these on s390 for some odd reason
   rm -f $RPM_BUILD_ROOT%{_x11datadir}/X11/doc/PostScript/RX.ps
   rm -f $RPM_BUILD_ROOT%{_x11datadir}/X11/doc/PostScript/XKBlib.ps
   rm -f $RPM_BUILD_ROOT%{_x11datadir}/X11/doc/PostScript/XKBproto.ps
   rm -f $RPM_BUILD_ROOT%{_x11datadir}/X11/doc/PostScript/dtprint_fspec.ps
   rm -f $RPM_BUILD_ROOT%{_x11datadir}/X11/doc/Xprint_FAQ.txt
   rm -f $RPM_BUILD_ROOT%{_x11datadir}/X11/doc/html/Xprint_FAQ.html
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man4/aiptek.4x*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man4/glide.4x*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man4/newport.4x*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man4/sunbw2.4x*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man4/suncg14.4x*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man4/suncg3.4x*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man4/suncg6.4x*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man4/sunffb.4x*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man4/sunleo.4x*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man4/suntcx.4x*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man4/ur98.4x*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man4/v4l.4x*
%endif
%if ! %{with_xprint}
   rm -f $RPM_BUILD_ROOT%{_x11includedir}/X11/XprintAppUtil/xpapputil.h
   rm -f $RPM_BUILD_ROOT%{_x11includedir}/X11/XprintUtil/xprintutil.h
   rm -f $RPM_BUILD_ROOT%{_x11libdir}/libXprintAppUtil.a
   rm -f $RPM_BUILD_ROOT%{_x11libdir}/libXprintUtil.a
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man7/Xprint.7x*
%endif
 {
   # Remove some legacy Xaw/Xt apps
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/xbiff
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/xditview
   rm -f $RPM_BUILD_ROOT%{_x11bindir}/xeyes
#   rm -f $RPM_BUILD_ROOT%{_x11bindir}/xmessage
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/xbiff.*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/xditview.*
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/xeyes.*
#   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man1/xmessage.*
 }
 {
   # We ship bitstream vera in separate packaging.  This should probably be
   # turned off with an Imake define in the future, perhaps something like
   # "#define BuildFontsBitsreamVera NO" in host.def, will have to investigate.
   # FIXME
   rm -f $RPM_BUILD_ROOT%{_x11fontdir}/TTF/Vera*.ttf
   # Remove various Syriac fonts which contain bad codepoints (bug #97951)
   rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMCtesiphon.otf
   rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMKharput.otf
   rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMMalankara.otf
   rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMMidyat.otf
   rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMQenNeshrin.otf
   rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMTurAbdin.otf
   rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMUrhoyBold.otf
   rm -f $RPM_BUILD_ROOT%{_x11fontdir}/OTF/SyrCOMUrhoy.otf
 }

%if ! %{with_wacom_driver}
   rm -f $RPM_BUILD_ROOT%{_x11libdir}/modules/input/wacom_drv.o
   rm -f $RPM_BUILD_ROOT%{_x11mandir}/man4/wacom.4x.gz
%endif
}
###  DO NOT PUT ANYTHING PAST THIS POINT #############################

%check
# Post build integrity checks section

# Find dead symlinks and fail the build if there are any
%if %{with_dead_symlink_test}
echo "Checking for broken symlinks ... "
{
    pushd $RPM_BUILD_ROOT
    BROKEN_LINK=0
    for link in $(find . -type l) ; do
        if test ! -e $link ; then
            echo Broken symlink $link found
            BROKEN_LINK=1
        fi
    done
    if [ $BROKEN_LINK = 1 ] ;then
        echo 'Broken symlink(s) detected in build, aborting ...'
        exit 1
    fi
    popd
}
%endif

# Scan the RPM_BUILD_ROOT for applications and shared libs that are
# not properly linked to all of their dependancies.
%if %{with_undef_sym_test}
echo "Checking for undefined symbols in shared libs ... "
{
    EXIT_STATUS=0
    # Use ldd's -u option only if supported on this system
    LDD_OPTS="-r$(ldd -u 2>&1 | grep 'unrecognized option' &> /dev/null|| echo ' -u')"
    echo LDD_OPTS=$LDD_OPTS

    pushd $RPM_BUILD_ROOT%{_x11libdir}
    for file in $(find . -type f -maxdepth 1 -name "lib*.so.*") ; do
        echo "Checking $file for undefined references ... "
        if ldd $LDD_OPTS "$file" 2>&1 | grep undefined ; then
            echo -e "\n*** WARNING: $file contains undefined references, listed above ***"}
            EXIT_STATUS=1
        fi
    done
    popd

    [ $EXIT_STATUS -eq 1 ] && echo -e "\nERROR: Undefined symbols detected above, failing build."
    exit $EXIT_STATUS
}
%endif

#if {with_check_buildroot_for_CVS_dirs}
#echo "Checking RPM_BUILD_ROOT for accidentally installed CVS metadata directories ... "
#{
#    
#}
#endif

######################################################################
#########  SCRIPT SECTION  ###########################################
######################################################################
%if %{with_rstart}
%define symlinkdirs	lbxproxy proxymngr rstart
%else
%define symlinkdirs	lbxproxy proxymngr
%endif

%pre
{ 
  pushd /etc/X11

  # Massage pre-existing config files to work properly with X.org X11
  # - Remove xie and pex5 modules from the config files, as they are long
  #   since obsolete, and not provided since XFree86 4.2.0
  # - Remove Option "XkbRules" "xfree86" to help work around upgrade problems
  #   such as https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=120858
  {
    for configfile in xorg.conf XF86Config XF86Config-4 ; do
      # FIXME: rewrite this all to use perl, if the XkbRules stuff below works out ok.
      if [ -r $configfile -a -w $configfile ]; then
	# Remove module load lines from the config file for obsolete modules
        perl -p -i -e 's/^.*Load.*"(pex5|xie|xtt).*\n$"//gi' $configfile
        # Change the keyboard configuration from the deprecated "keyboard"
	# driver, to the newer "kbd" driver.
        perl -p -i -e 's/Driver(.*)"keyboard"/Driver\1"kbd"/gi' $configfile
	# Remove any Options "XkbRules" lines that may be present
        perl -p -i -e 's/^.*Option.*"XkbRules".*\n$//gi' $configfile
      fi
    done
  }

  # Migrate any pre-existing XFree86 4.x config file to xorg.conf if it
  # doesn't already exist, and rename any remaining XFree86 4.x congig files
  # to have .obsoleted file extensions, to help avoid end user confusion for
  # people unaware of the config file name change between server
  # implementations, and avoid bug reports.  If this turns out to confuse
  # users, I can modify it to add comments to the top of the obsoleted files
  # to point users to xorg.conf   <mharris@redhat.com>
  {
    for configfile in XF86Config-4 XF86Config ; do
      if [ -r $configfile ]; then
          if [ -r xorg.conf ]; then
              mv -f $configfile $configfile.obsoleted
          else
              mv -f $configfile xorg.conf
          fi
      fi
    done
  }
  popd

  # Do this for upgrades or installs
  XKB_DIR=%{_x11datadir}/X11/xkb/compiled
  if [ ! -L $XKB_DIR -a -d $XKB_DIR ]; then
    mkdir -p /var/lib/xkb
    mv -f $XKB_DIR /var/lib/xkb/
    ln -sf ../../../../../var/lib/xkb $XKB_DIR
  fi
} &> /dev/null || :

%post
{
%if %{with_Xserver}
  for dir in %{symlinkdirs} ; do
%else
  for dir in %{symlinkdirs} xserver ; do
%endif
    [ ! -L %{_x11datadir}/X11/$dir -a ! -d %{_x11datadir}/X11/$dir ] && \
      ln -snf ../../../../etc/X11/$dir %{_x11datadir}/X11/$dir || :
  done
} &> /dev/null || :

%pre xdm
{
  # The dir /etc/X11/xdm/authdir moved to /var/lib/xdm/authdir and was replaced
  # by a symlink.  Upgrades from Red Hat Linux 6.x and earlier to any new
  # release with XFree86-4.0.x fail without the following. (fixes bug #32574)
  if [ ! -L /etc/X11/xdm/authdir -a -d /etc/X11/xdm/authdir ]; then
    mkdir -p /var/lib/xdm && \
    mv -f /etc/X11/xdm/authdir /var/lib/xdm/  && \
       ln -sf ../../../var/lib/xdm/authdir /etc/X11/xdm/authdir || :
  fi
} &> /dev/null || :
         
%post libs
/sbin/ldconfig

%postun libs
/sbin/ldconfig

%post deprecated-libs
/sbin/ldconfig

%postun deprecated-libs
/sbin/ldconfig

%post Mesa-libGL
/sbin/ldconfig

%postun Mesa-libGL
/sbin/ldconfig

%post Mesa-libGLU
/sbin/ldconfig

%postun Mesa-libGLU
/sbin/ldconfig

##### xfs scripts ####################################################
# Work around a bug in the XFree86-xfs postun script, which results in the
# special xfs user account being inadvertently removed, causing xfs to run as
# the root user, and also resulting in xfs not being activated by chkconfig,
# This trigger executes right after the XFree86-xfs postun script, and ensures
# that the xfs user exists, and that the xfs initscript is properly chkconfig
# activated (#118145,118818)
%triggerpostun xfs -- XFree86-xfs
{
  # Conditionalized to work on RHL 7.1 and 7.2 which do not have /sbin/nologin
  LOGINSHELL=$([ -e /sbin/nologin ] && echo /sbin/nologin || echo /bin/false)
  /usr/sbin/useradd -c "X Font Server" -r -s $LOGINSHELL -u 43 -d /etc/X11/fs xfs || :
  /sbin/chkconfig --add xfs
  /sbin/service xfs condrestart || :
} &> /dev/null || :

%pre xfs
{
  # Conditionalized to work on RHL 7.1 and 7.2 which do not have /sbin/nologin
  LOGINSHELL=$([ -e /sbin/nologin ] && echo /sbin/nologin || echo /bin/false)
  /usr/sbin/useradd -c "X Font Server" -r -s $LOGINSHELL -u 43 -d /etc/X11/fs xfs || :
} &> /dev/null || : # Silence output, and ignore errors (Bug #91822)

%post xfs
{
  /sbin/chkconfig --add xfs
# FIXME: What an unmaintainable mess.  ;o) There almost has to be a cleaner
# way of doing this.  If not, it needs to be figured out and documented to
# avoid confusion.
  use_unix=
  for config in /etc/X11/xorg.conf /etc/X11/XF86Config /etc/X11/XF86Config-4 ; do
    if [ -f $config ] && grep -q "unix/:" $config &> /dev/null; then
      use_unix=1
    fi
    if [ -f $config ] && grep -q "unix/:-1" $config &> /dev/null; then
      rm -f $config.new $config.rpmsave
      sed "s#unix/:-1#unix/:7100#g" $config > $config.new
      cp -f $config $config.rpmsave
      cat $config.new > $config
      rm -f $config.new
    fi
    if [ -f $config ] && grep -q "unix/:" $config &> /dev/null && \
      grep -q "%{_x11fontdir}/TrueType" $config &> /dev/null ; then \
      sed "s|FontPath[ ]*\"%{_x11fontdir}/TrueType\"|#FontPath \"%{_x11fontdir}/TrueType\"|g" $config > $config.new
      cat $config.new > $config
      rm -f $config.new
    fi
  done
  # If the font server config is using UNIX sockets, disable TCP listen by default
  if [ -n "$use_unix" ] && ! grep -q "no-listen" /etc/X11/fs/config &> /dev/null;then
    echo -e "# don't listen on tcp by default\nno-listen = tcp\n" >> /etc/X11/fs/config
  fi
}

%preun xfs
{
  if [ "$1" = "0" ]; then
    /sbin/service xfs stop &> /dev/null || :
# FIXME: The chkconfig call below works properly if uninstalling the package,
#        but it will cause xfs to be de-chkconfig'd if upgrading from one X11
#        implementation to another, as witnessed in the transition from
#        XFree86 to Xorg X11.  If this call is removed however, then xfs will
#        remain visible in ntsysv and similar utilities even after xfs is
#        uninstalled from the system in non-upgrade scenarios.  Not sure how
#        to fix this yet.
    /sbin/chkconfig --del xfs || :
# userdel/groupdel removed because they cause the user/group to get destroyed
# when upgrading from one X11 implementation to another, ie: XFree86 -> Xorg
#    /usr/sbin/userdel xfs 2>/dev/null || :
#    /usr/sbin/groupdel xfs 2>/dev/null || :
  fi
}

%postun xfs
{
  if [ "$1" -ge "1" ]; then
    /sbin/service xfs condrestart &> /dev/null || :
  fi
} 

%if %{with_fonts}
%post base-fonts
{
# FIXME: Make it only run mkfontdir in dirs that have fonts in them.
# Build fonts.dir files for all font dirs in this package.
# (exclude the local and CID dirs as they do not have fonts currently)
  for fontdir in 100dpi 75dpi misc Type1 ;do
    %__mkfontdir %{_x11fontdir}/$fontdir || :
  done
  /usr/sbin/chkfontpath -qa %{_x11fontdir}/75dpi:unscaled || :
  /usr/sbin/chkfontpath -qa %{_x11fontdir}/100dpi:unscaled || :
  /usr/sbin/chkfontpath -qa %{_x11fontdir}/misc:unscaled || :
  /usr/sbin/chkfontpath -qa %{_x11fontdir}/Type1 || :
  # Remove the Speedo directory from xfs config as X.Org no longer provides
  # Speedo font support.
  /usr/sbin/chkfontpath -qr %{_x11fontdir}/Speedo || :
# Only run fc-cache in the Type1 dir, gzipped pcf's take forever
  %__fccache %{_x11fontdir}/Type1 || :
} &> /dev/null || :

%postun base-fonts
{
  # Rebuild fonts.dir when uninstalling package. (exclude the local, CID dirs)
  if [ "$1" = "0" ]; then
    for fontdir in 100dpi 75dpi misc Type1 ;do
      %__mkfontdir %{_x11fontdir}/$fontdir || :
    done
# Only run fc-cache in the Type1 dir, gzipped pcf's take forever
    %__fccache %{_x11fontdir}/Type1 || :
  fi
} &> /dev/null || :

%post truetype-fonts
{
  FONTDIR=%{_x11fontdir}/TTF
  ttmkfdir -d $FONTDIR -o $FONTDIR/fonts.scale
  %__mkfontdir $FONTDIR
  %__fccache $FONTDIR
  /usr/sbin/chkfontpath -q -a $FONTDIR
} &> /dev/null || :

%postun truetype-fonts
{
  FONTDIR=%{_x11fontdir}/TTF
  if [ "$1" = "0" ]; then
    ttmkfdir -d $FONTDIR -o $FONTDIR/fonts.scale
    %__mkfontdir $FONTDIR
    %__fccache $FONTDIR
  fi
} &> /dev/null || :

%post syriac-fonts
{
  FONTDIR=%{_x11fontdir}/OTF
  %__mkfontscale $FONTDIR 
  %__mkfontdir $FONTDIR
  %__fccache $FONTDIR
  /usr/sbin/chkfontpath -q -a $FONTDIR
} &> /dev/null || :

%postun syriac-fonts
{
  FONTDIR=%{_x11fontdir}/OTF
  if [ "$1" = "0" ]; then
    %__mkfontscale $FONTDIR 
    %__mkfontdir $FONTDIR
    %__fccache $FONTDIR
  fi
} &> /dev/null || :

%post 75dpi-fonts
{
    %__mkfontdir %{_x11fontdir}/75dpi
#    %__fccache %{_x11fontdir}/75dpi
    /usr/sbin/chkfontpath -q -a %{_x11fontdir}/75dpi:unscaled
} &> /dev/null || :

%post 100dpi-fonts
{
    %__mkfontdir %{_x11fontdir}/100dpi
#    %__fccache %{_x11fontdir}/100dpi
    /usr/sbin/chkfontpath -q -a %{_x11fontdir}/100dpi:unscaled
} &> /dev/null || :

%post ISO8859-2-75dpi-fonts
{
    %__mkfontdir %{_x11fontdir}/75dpi
#    %__fccache %{_x11fontdir}/75dpi
    /usr/sbin/chkfontpath -q -a %{_x11fontdir}/75dpi:unscaled
} &> /dev/null || :

%post ISO8859-2-100dpi-fonts
{
    %__mkfontdir %{_x11fontdir}/100dpi
#    %__fccache %{_x11fontdir}/100dpi
    /usr/sbin/chkfontpath -q -a %{_x11fontdir}/100dpi:unscaled
} &> /dev/null || :

%post ISO8859-9-75dpi-fonts
{
    %__mkfontdir %{_x11fontdir}/75dpi
#    %__fccache %{_x11fontdir}/75dpi
    /usr/sbin/chkfontpath -q -a %{_x11fontdir}/75dpi:unscaled
} &> /dev/null || :

%post ISO8859-9-100dpi-fonts
{
    %__mkfontdir %{_x11fontdir}/100dpi
#    %__fccache %{_x11fontdir}/100dpi
    /usr/sbin/chkfontpath -q -a %{_x11fontdir}/100dpi:unscaled
} &> /dev/null || :

%post ISO8859-14-75dpi-fonts
{
    %__mkfontdir %{_x11fontdir}/75dpi
#    %__fccache %{_x11fontdir}/75dpi
    /usr/sbin/chkfontpath -q -a %{_x11fontdir}/75dpi:unscaled
} &> /dev/null || :
    

%post ISO8859-14-100dpi-fonts
{
    %__mkfontdir %{_x11fontdir}/100dpi
#    %__fccache %{_x11fontdir}/100dpi
    /usr/sbin/chkfontpath -q -a %{_x11fontdir}/100dpi:unscaled
} &> /dev/null || :

%post ISO8859-15-75dpi-fonts
{
    %__mkfontdir %{_x11fontdir}/75dpi
#    %__fccache %{_x11fontdir}/75dpi
    /usr/sbin/chkfontpath -q -a %{_x11fontdir}/75dpi:unscaled
} &> /dev/null || :
    

%post ISO8859-15-100dpi-fonts
{
    %__mkfontdir %{_x11fontdir}/100dpi
#    %__fccache %{_x11fontdir}/100dpi
    /usr/sbin/chkfontpath -q -a %{_x11fontdir}/100dpi:unscaled
} &> /dev/null || :

%post cyrillic-fonts
{
    %__mkfontdir %{_x11fontdir}/cyrillic
#    %__fccache %{_x11fontdir}/cyrillic
    /usr/sbin/chkfontpath -q -a %{_x11fontdir}/cyrillic:unscaled
} &> /dev/null || :

%postun 75dpi-fonts
{
  if [ "$1" = "0" ]; then
    %__mkfontdir %{_x11fontdir}/75dpi
#    %__fccache %{_x11fontdir}/75dpi
  fi
}

%postun 100dpi-fonts
{
  if [ "$1" = "0" ]; then
    %__mkfontdir %{_x11fontdir}/100dpi
#    %__fccache %{_x11fontdir}/100dpi
  fi
}

%postun ISO8859-2-75dpi-fonts
{
  if [ "$1" = "0" ]; then
    %__mkfontdir %{_x11fontdir}/75dpi
#    %__fccache %{_x11fontdir}/75dpi
  fi
}

%postun ISO8859-2-100dpi-fonts
{
  if [ "$1" = "0" ]; then
    %__mkfontdir %{_x11fontdir}/100dpi
#    %__fccache %{_x11fontdir}/100dpi
  fi
}

%postun ISO8859-9-75dpi-fonts
{
  if [ "$1" = "0" ]; then
    %__mkfontdir %{_x11fontdir}/75dpi
#    %__fccache %{_x11fontdir}/75dpi
  fi
}

%postun ISO8859-9-100dpi-fonts
{
  if [ "$1" = "0" ]; then
    %__mkfontdir %{_x11fontdir}/100dpi
#    %__fccache %{_x11fontdir}/100dpi
  fi
}

%postun ISO8859-15-75dpi-fonts
{
  if [ "$1" = "0" ]; then
    %__mkfontdir %{_x11fontdir}/75dpi
#    %__fccache %{_x11fontdir}/75dpi
  fi
}

%postun ISO8859-15-100dpi-fonts
{
  if [ "$1" = "0" ]; then
    %__mkfontdir %{_x11fontdir}/100dpi
#    %__fccache %{_x11fontdir}/100dpi
  fi
}

%postun cyrillic-fonts
{
  if [ "$1" = "0" ]; then
    %__mkfontdir %{_x11fontdir}/cyrillic
#    %__fccache %{_x11fontdir}/cyrillic
  fi
}
%endif

########## FILES SECTION #############################################
# FIXME: Move this to a separate README.specfile document
#
# IMPORTANT NOTE:  All fonts.dir, fonts.scale files are created during package
# installation time, and as such need to be flagged as ghost files, also their
# content is variable while installed as new fonts can be installed in the same
# directories potentially at any time, so they need to be flagged with %verify
# also.  They should not be flagged with %config however as they are not
# considered to be user editable, and should not be preserved.  Any case of a
# user wanting to edit these files by hand for ANY REASON, indicates a bug
# in the mkfontdir/ttmkfdir tools which should be fixed instead.
#
# encodings.dir files also should be flagged with %ghost and %verify, since
# the same applies to them, the only difference is that it may not actually
# exist unless the user creates it for some reason.  These files are deprecated
# and will be removed in a future upstream release entirely.
#
# fonts.alias should be flagged with %verify as it is modifyable.  For directories
# in which we supply a fonts.alias file, it should be flagged %config(noreplace)
# and for dirs which we do not supply one it should be flagged as both %ghost
# and %config(noreplace) so that the files are actually owned by the package,
# just not supplied by default, and they are preserved across upgrades.

######################################################################
# XFree86 package

%files -f filelist.%{name}
%defattr(-,root,root)
%doc CHANGELOG
%dir /etc/X11/lbxproxy
%config /etc/X11/lbxproxy/AtomControl
%dir /etc/X11/proxymngr
%config /etc/X11/proxymngr/pmconfig

# rstart stuffola
%if %{with_rstart}
%dir /etc/X11/rstart
%dir /etc/X11/rstart/commands
/etc/X11/rstart/commands/@List
/etc/X11/rstart/commands/ListContexts
/etc/X11/rstart/commands/ListGenericCommands
/etc/X11/rstart/commands/x
/etc/X11/rstart/commands/x11
%dir /etc/X11/rstart/commands/x11r6
%dir /etc/X11/rstart/contexts
/etc/X11/rstart/contexts/@List
/etc/X11/rstart/contexts/default
/etc/X11/rstart/contexts/x
/etc/X11/rstart/contexts/x11
%dir /etc/X11/rstart/contexts/x11r6
%config /etc/X11/rstart/config
/etc/X11/rstart/rstartd.real
%endif

%if %{with_Xserver}
%dir /etc/X11/xinit
# %config /etc/X11/xinit/xinitrc We have a separate xinitrc package
%dir /etc/X11/xserver
%config /etc/X11/xserver/*
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) /etc/X11/xorg.conf
# FIXME: The XF86Config* files are deprecated and not supported.  Included here
# only to ease the transition to xorg.conf for an OS release or so.
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) /etc/X11/XF86Config
%ghost %config(missingok,noreplace) %verify(not md5 size mtime) /etc/X11/XF86Config-4
%endif

%dir /etc/X11/xsm
%config /etc/X11/xsm/system.xsm
%ghost %{_x11datadir}/X11/lbxproxy
%ghost %{_x11datadir}/X11/proxymngr
%if %{with_rstart}
%ghost %{_x11datadir}/X11/rstart
%endif
%if %{with_Xserver}
%ghost %{_x11datadir}/X11/xserver
%endif
%dir %{_x11datadir}/X11/xkb
%config %{_x11datadir}/X11/app-defaults/*
%dir /var/lib/xkb
%config %attr(0644,root,root) /etc/pam.d/xserver
%config(missingok) /etc/security/console.apps/xserver
/var/lib/xkb/README
# SuperProbe is obsolete %{_x11bindir}/SuperProbe
%if %{with_Xserver}
%{_x11bindir}/X
%attr(4711,root,root) %{_x11bindir}/Xorg
%endif
%{_x11bindir}/Xmark
%ifnarch s390 s390x ppc ppc64
%{_x11bindir}/pcitweak
%{_x11bindir}/scanpci
%{_x11bindir}/mmapr
%{_x11bindir}/mmapw
%endif
%{_x11bindir}/appres
%{_x11bindir}/atobm
%{_x11bindir}/bitmap
%{_x11bindir}/bmtoa
%{_x11bindir}/cleanlinks
%{_x11bindir}/dga
%{_x11bindir}/dpsexec
%{_x11bindir}/dpsinfo
%{_x11bindir}/editres
%{_x11bindir}/iceauth
%if %{with_Xserver}
%{_x11bindir}/getconfig
%{_x11bindir}/getconfig.pl
%{_x11datadir}/X11/getconfig/cfg.sample
%{_x11datadir}/X11/getconfig/xorg.cfg
%{_x11bindir}/gtf
%endif
%{_x11bindir}/lbxproxy
%{_x11bindir}/lndir
%{_x11bindir}/luit
%{_x11bindir}/makepsres
%{_x11bindir}/makestrs
%{_x11bindir}/mergelib
%{_x11bindir}/mkcfm
%{_x11bindir}/mkdirhier
%{_x11bindir}/proxymngr
%if %{with_xterm}
%{_x11bindir}/resize
%endif
# Xresource extension client app
%{_x11bindir}/revpath
%if %{with_rstart}
%{_x11bindir}/rstart
%{_x11bindir}/rstartd
%endif
%{_x11bindir}/sessreg
%{_x11bindir}/setxkbmap
%{_x11bindir}/showrgb
%{_x11bindir}/smproxy
%if %{with_Xserver}
%{_x11bindir}/startx
%endif
%{_x11bindir}/texteroids
%if %{with_xterm}
%{_x11bindir}/uxterm
%endif
%{_x11bindir}/xcmsdb
%{_x11bindir}/xconsole
%{_x11bindir}/xcursor-config
%{_x11bindir}/xcursorgen
%{_x11bindir}/xcutsel
%{_x11bindir}/xdpyinfo
%{_x11bindir}/xdriinfo
%if %{with_xf86config}
# This has been removed from build 4.2.99.2-0.20021110.8 and later.  The
# supported X configuration tool in Red Hat Linux is system-config-display
# now, and we expect people to use it, and report bugs if there are any,
# and make requests for any missing features.  <mharris@redhat.com>
%{_x11bindir}/xf86config
%endif
%{_x11bindir}/xfindproxy
%{_x11bindir}/xfwp
%{_x11bindir}/xgamma
%{_x11bindir}/xhost
%if %{with_Xserver}
%{_x11bindir}/xinit
%endif
%{_x11bindir}/xkbbell
%{_x11bindir}/xkbcomp
%{_x11bindir}/xkbevd
%{_x11bindir}/xkbprint
%{_x11bindir}/xkbvleds
%{_x11bindir}/xkbwatch
%{_x11bindir}/xlsatoms
%{_x11bindir}/xlsclients
%{_x11bindir}/xlsfonts
%if %{with_xmh}
# xmh is obsolete
%{_x11bindir}/xmh
%endif
%{_x11bindir}/xmodmap
%{_x11bindir}/xon
%{_x11bindir}/xprop
%{_x11bindir}/xrandr
%{_x11bindir}/xrdb
%{_x11bindir}/xrefresh
%{_x11bindir}/xset
%{_x11bindir}/xsetmode
%{_x11bindir}/xsetpointer
%{_x11bindir}/xsetroot
%{_x11bindir}/xsm
%{_x11bindir}/xstdcmap
%if %{with_xterm}
%{_x11bindir}/xterm
%endif
%{_x11bindir}/xtrapchar
%{_x11bindir}/xtrapin
%{_x11bindir}/xtrapinfo
%{_x11bindir}/xtrapout
%{_x11bindir}/xtrapproto
%{_x11bindir}/xtrapreset
%{_x11bindir}/xtrapstats
%{_x11bindir}/xvidtune
%{_x11bindir}/xwd
%{_x11bindir}/xwud

%if %{with_Xserver}
# Provided by the Xconfigurator package in RHL 7.x, and in the hwdata
# currently in rawhide.
#%{_x11datadir}/X11/Cards
%{_x11datadir}/X11/Options
#%{_x11datadir}/X11/XF86Config
%dir %{_x11datadir}/X11/doc
%{_x11datadir}/X11/doc/*
# X server modules
%dir %{_x11libdir}/modules
%{_x11libdir}/modules/*.*
%dir %{_x11libdir}/modules/extensions
%{_x11libdir}/modules/extensions/*
%dir %{_x11libdir}/modules/fonts
%{_x11libdir}/modules/fonts/*
%dir %{_x11libdir}/modules/input
%{_x11libdir}/modules/input/*
%dir %{_x11libdir}/modules/linux
%{_x11libdir}/modules/linux/*
%dir %{_x11libdir}/modules/drivers
%{_x11libdir}/modules/drivers/*
%endif
%if %{with_DRI}
%dir %{_x11libdir}/modules/dri
%{_x11libdir}/modules/dri/*_dri.so
%endif
%dir %{_x11datadir}/X11/app-defaults
# FIXME: this doesn't build right on RHL9 - s390/s390x/ppc64 but... who CARES
%if %{with_Xserver}
%dir %{_x11datadir}/X11/etc
%{_x11datadir}/X11/etc/*
%{_x11datadir}/X11/xinit
%endif
%{_x11datadir}/X11/xkb/*
/etc/X11/xkb
%dir %{_x11datadir}/X11/x11perfcomp
%{_x11datadir}/X11/x11perfcomp/*
%{_x11datadir}/X11/xsm
%if %{with_Xserver}
%{_x11mandir}/man1/Xorg.1*
%{_x11mandir}/man1/Xserver.1*
%endif
%{_x11mandir}/man1/Xmark.1*
%{_x11mandir}/man1/appres.1*
%{_x11mandir}/man1/atobm.1*
%{_x11mandir}/man1/bitmap.1*
%{_x11mandir}/man1/bmtoa.1*
%{_x11mandir}/man1/cleanlinks.1*
%{_x11mandir}/man1/dga.1*
%{_x11mandir}/man1/dpsexec.1*
%{_x11mandir}/man1/dpsinfo.1*
%{_x11mandir}/man1/dumpkeymap.1*
%{_x11mandir}/man1/editres.1*
%{_x11mandir}/man1/iceauth.1*
%if %{with_Xserver}
%{_x11mandir}/man1/getconfig.1*
%{_x11mandir}/man1/gtf.1*
%endif
%{_x11mandir}/man1/lbxproxy.1*
%if %{with_libxrx}
%{_x11mandir}/man1/libxrx.1*
%endif
%{_x11mandir}/man1/lndir.1*
%{_x11mandir}/man1/luit.1*
%{_x11mandir}/man1/makedepend.1*
%{_x11mandir}/man1/makepsres.1*
%{_x11mandir}/man1/makestrs.1*
%{_x11mandir}/man1/mergelib.1*
%{_x11mandir}/man1/mkcfm.1*
%{_x11mandir}/man1/mkdirhier.1*
%{_x11mandir}/man1/oclock.1*
%ifnarch s390 s390x ppc ppc64
%{_x11mandir}/man1/pcitweak.1*
%{_x11mandir}/man1/scanpci.1*
%endif
%{_x11mandir}/man1/proxymngr.1*
%if %{with_xterm}
%{_x11mandir}/man1/resize.1*
%endif
%{_x11mandir}/man1/revpath.1*
%if %{with_rstart}
%{_x11datadir}/X11/rstart
%{_x11bindir}/rstart
%{_x11mandir}/man1/rstart.1*
%{_x11mandir}/man1/rstart.1*
%{_x11mandir}/man1/rstartd.1*
%endif
%{_x11mandir}/man1/sessreg.1*
%{_x11mandir}/man1/setxkbmap.1*
%{_x11mandir}/man1/showrgb.1*
%{_x11mandir}/man1/smproxy.1*
%if %{with_Xserver}
%{_x11mandir}/man1/startx.1*
%endif
%{_x11mandir}/man1/texteroids.1*
%{_x11mandir}/man1/xcmsdb.1*
%{_x11mandir}/man1/xconsole.1*
%{_x11mandir}/man1/xcursorgen.1*
%{_x11mandir}/man1/xcutsel.1*
%{_x11mandir}/man1/xdpyinfo.1*
%{_x11mandir}/man1/xdriinfo.1*
%if %{with_xf86config}
%{_x11mandir}/man1/xf86config.1*
%endif
%{_x11mandir}/man1/xfindproxy.1*
%{_x11mandir}/man1/xfwp.1*
%{_x11mandir}/man1/xgamma.1*
%{_x11mandir}/man1/xhost.1*
%if %{with_Xserver}
%{_x11mandir}/man1/xinit.1*
%endif
%{_x11mandir}/man1/xkbcomp.1*
%{_x11mandir}/man1/xkbevd.1*
%{_x11mandir}/man1/xkbprint.1*
%{_x11mandir}/man1/xkill.1*
%{_x11mandir}/man1/xlogo.1*
%{_x11mandir}/man1/xlsatoms.1*
%{_x11mandir}/man1/xlsclients.1*
%{_x11mandir}/man1/xlsfonts.1*
%if %{with_xmh}
# xmh is obsolete 
%{_x11mandir}/man1/xmh.1*
%endif
%{_x11mandir}/man1/xmodmap.1*
%{_x11mandir}/man1/xon.1*
%{_x11mandir}/man1/xprop.1*
%{_x11mandir}/man1/xrandr.1*
%{_x11mandir}/man1/xrdb.1*
%{_x11mandir}/man1/xrefresh.1*
%{_x11mandir}/man1/xset.1*
%{_x11mandir}/man1/xsetmode.1*
%{_x11mandir}/man1/xsetpointer.1*
%{_x11mandir}/man1/xsetroot.1*
%{_x11mandir}/man1/xsm.1*
%{_x11mandir}/man1/xstdcmap.1*
%if %{with_xterm}
%{_x11mandir}/man1/xterm.1*
%endif
%{_x11mandir}/man1/xtrap.1*
%{_x11mandir}/man1/xtrapchar.1*
%{_x11mandir}/man1/xtrapin.1*
%{_x11mandir}/man1/xtrapinfo.1*
%{_x11mandir}/man1/xtrapout.1*
%{_x11mandir}/man1/xtrapproto.1*
%{_x11mandir}/man1/xtrapreset.1*
%{_x11mandir}/man1/xtrapstats.1*
%{_x11mandir}/man1/xvidtune.1*
%{_x11mandir}/man1/xwd.1*
%{_x11mandir}/man1/xwud.1*
%if %{with_Xserver}
%{_x11mandir}/man4/*
%{_x11mandir}/man5/*
%endif
%{_x11mandir}/man7/*
%if ! %{with_icons_in_datadir}
%dir %{_x11icondir}
%endif
%dir %{_x11icondir}/default
%config(noreplace) %verify(not md5 size mtime) %{_x11icondir}/default/index.theme
%if %{with_handhelds}
%dir %{_x11icondir}/handhelds
%dir %{_x11icondir}/handhelds/cursors
%{_x11icondir}/handhelds/cursors/*
%endif
%if %{with_redglass}
%dir %{_x11icondir}/redglass
%dir %{_x11icondir}/redglass/cursors
%{_x11icondir}/redglass/cursors/*
%endif
%if %{with_whiteglass}
%dir %{_x11icondir}/whiteglass
%dir %{_x11icondir}/whiteglass/cursors
%{_x11icondir}/whiteglass/cursors/*
%endif

%files devel
%defattr(-,root,root)
# Changed GL include dir, on Mar 17, 2002 for 4.2.0-6.48 release
%dir %{_includedir}/GL
%{_includedir}/GL/*
%{_includedir}/X11
%{_includedir}/DPS
%{_libdir}/libGL.so
%{_libdir}/libGLU.so
%dir %{_x11includedir}
%dir %{_x11includedir}/DPS
%dir %{_x11includedir}/X11
%dir %{_x11includedir}/X11/ICE
# PEX is obsolete %dir %{_x11includedir}/X11/PEX5
%dir %{_x11includedir}/X11/PM
%dir %{_x11includedir}/X11/SM
%dir %{_x11includedir}/X11/Xaw
%dir %{_x11includedir}/X11/Xcursor
%dir %{_x11includedir}/X11/Xft
%dir %{_x11includedir}/X11/Xmu
%dir %{_x11includedir}/X11/bitmaps
%{_x11includedir}/X11/bitmaps/*
%dir %{_x11includedir}/X11/extensions
%{_x11includedir}/X11/extensions/*.h
%exclude %{_x11includedir}/X11/extensions/Print.h
%exclude %{_x11includedir}/X11/extensions/Printstr.h
%if %{with_fontconfig}
%dir %{_x11includedir}/fontconfig
%{_x11includedir}/fontconfig/*
%endif
%dir %{_x11includedir}/X11/fonts
%{_x11includedir}/X11/fonts/*.h
# FIXME: these are no longer present in 6.8.0, not sure why yet, so just
# commenting out rather than removing.  -- mharris
#%dir %{_x11includedir}/X11/fonts/codeconv
#%{_x11includedir}/X11/fonts/codeconv/*.h
%dir %{_x11datadir}/X11/config
%if %{with_archexec}
%{_x11bindir}/archexec
%endif
%{_x11bindir}/cxpm
%if %{with_fontconfig}
%{_x11bindir}/fontconfig-config
%endif
%{_x11bindir}/gccmakedep
%{_x11bindir}/gccmakedep-%{_arch}
%{_x11bindir}/imake
%{_x11bindir}/makedepend
%{_x11bindir}/makeg
%{_x11bindir}/pswrap
%{_x11bindir}/rman
%{_x11bindir}/sxpm
%{_x11bindir}/xft-config
%{_x11bindir}/xft-config-%{_arch}
%{_x11bindir}/xmkmf
%if %{with_Xserver}
%{_x11includedir}/*.h
%endif
%{_x11includedir}/DPS/*.h
%{_x11includedir}/X11/*.h
%{_x11includedir}/X11/ICE/*.h
# PEX is obsolete %{_x11includedir}/X11/PEX5/*.h
%{_x11includedir}/X11/PM/*.h
%{_x11includedir}/X11/SM/*.h
%{_x11includedir}/X11/Xaw/*
%{_x11includedir}/X11/Xcursor/*
###%if ! %{with_new_fontconfig_Xft}
%{_x11includedir}/X11/Xft/*
###%endif
%{_x11includedir}/X11/Xmu/*.h
%{_x11libdir}/libFS.a
%{_x11libdir}/libGL.a
%{_x11libdir}/libGLU.a
%{_x11libdir}/libGLw.a
%ifarch %{ix86} ia64 x86_64
%{_x11libdir}/libI810XvMC.a
%endif
%{_x11libdir}/libICE.a
%{_x11libdir}/libOSMesa.a
%{_x11libdir}/libSM.a
%{_x11libdir}/libX11.a
%{_x11libdir}/libXRes.a
%{_x11libdir}/libXTrap.a
%{_x11libdir}/libXau.a
#%{_x11libdir}/libXaw.a
%{_x11libdir}/libXcomposite.a
%{_x11libdir}/libXcursor.a
%{_x11libdir}/libXdamage.a
%{_x11libdir}/libXdmcp.a
%{_x11libdir}/libXext.a
%{_x11libdir}/libXevie.a
%{_x11libdir}/libXfixes.a
%{_x11libdir}/libXfont.a
# FIXME: this is no longer present in 6.8.0, not sure why yet, so just
# commenting out rather than removing.  -- mharris
#%{_x11libdir}/libXfontcache.a
%{_x11libdir}/libXft.a
%{_x11libdir}/libXi.a
%{_x11libdir}/libXinerama.a
%{_x11libdir}/libXmu.a
%{_x11libdir}/libXmuu.a
%{_x11libdir}/libXpm.a
%{_x11libdir}/libXrandr.a
%{_x11libdir}/libXrender.a
%{_x11libdir}/libXss.a
%{_x11libdir}/libXt.a
%{_x11libdir}/libXtst.a
%{_x11libdir}/libXv.a
%{_x11libdir}/libXvMC.a
%{_x11libdir}/libXxf86dga.a
%{_x11libdir}/libXxf86misc.a
%{_x11libdir}/libXxf86rush.a
%{_x11libdir}/libXxf86vm.a
%{_x11libdir}/libdmx.a
%{_x11libdir}/libdps.a
%{_x11libdir}/libdpstk.a
%{_x11libdir}/libfntstubs.a
%{_x11libdir}/libfontenc.a
%{_x11libdir}/liboldX.a
%{_x11libdir}/libpsres.a
%if %{with_Xserver}
%{_x11libdir}/libxf86config.a
%endif
%{_x11libdir}/libxkbfile.a
%{_x11libdir}/libxkbui.a
# Shared library symlinks
%{_x11libdir}/libGL.so
%{_x11libdir}/libGLU.so
%ifarch %{ix86} ia64 x86_64
%{_x11libdir}/libI810XvMC.so
%endif
%{_x11libdir}/libICE.so
%{_x11libdir}/libOSMesa.so
%{_x11libdir}/libSM.so
%{_x11libdir}/libX11.so
%{_x11libdir}/libXRes.so
%{_x11libdir}/libXTrap.so
%{_x11libdir}/libXaw.so
%{_x11libdir}/libXcomposite.so
%{_x11libdir}/libXcursor.so
%{_x11libdir}/libXdamage.so
%{_x11libdir}/libXext.so
%{_x11libdir}/libXevie.so
%{_x11libdir}/libXfixes.so
%{_x11libdir}/libXfont.so
# FIXME: these are no longer present in 6.8.0, not sure why yet, so just
# commenting out rather than removing.  -- mharris
#%{_x11libdir}/libXfontcache.so
%{_x11libdir}/libXft.so
%{_x11libdir}/libXi.so
%{_x11libdir}/libXinerama.so
%{_x11libdir}/libXmu.so
%{_x11libdir}/libXmuu.so
%{_x11libdir}/libXpm.so
%{_x11libdir}/libXrandr.so
%{_x11libdir}/libXrender.so
%{_x11libdir}/libXss.so
%{_x11libdir}/libXt.so
%{_x11libdir}/libXtst.so
%{_x11libdir}/libXv.so
%{_x11libdir}/libXvMC.so
%{_x11libdir}/libXxf86dga.so
%{_x11libdir}/libXxf86misc.so
%{_x11libdir}/libXxf86rush.so
%{_x11libdir}/libXxf86vm.so
%{_x11libdir}/libdps.so
%{_x11libdir}/libdpstk.so
%{_x11libdir}/libfontenc.so
%{_x11libdir}/libpsres.so
%{_x11libdir}/libxkbfile.so
%{_x11libdir}/libxkbui.so
%if %{with_libxrx}
%{_x11libdir}/libxrx.so
%endif
%if %{with_fontconfig}
%{_x11libdir}/libfontconfig.a
%{_x11libdir}/libfontconfig.so
%{_libdir}/pkgconfig/fontconfig.pc
%endif
# %{_x11libdir}/pkgconfig dir is unnecessary, just use the /usr/lib/pkgconfig dir
#%dir %{_x11libdir}/pkgconfig
%{_libdir}/pkgconfig/xcomposite.pc
%{_libdir}/pkgconfig/xcursor.pc
%{_libdir}/pkgconfig/xdamage.pc
%{_libdir}/pkgconfig/xevie.pc
%{_libdir}/pkgconfig/xfixes.pc
%{_libdir}/pkgconfig/xft.pc
%{_libdir}/pkgconfig/xrender.pc
# render.pc disabled because they do not get created properly
#%{_libdir}/pkgconfig/render.pc
%{_x11datadir}/X11/config/*
%{_x11mandir}/man1/cxpm.1*
%{_x11mandir}/man1/gccmakedep.1*
%{_x11mandir}/man1/imake.1*
%{_x11mandir}/man1/makeg.1*
%{_x11mandir}/man1/pswrap.1*
%{_x11mandir}/man1/rman.1*
%{_x11mandir}/man1/sxpm.1*
%{_x11mandir}/man1/xmkmf.1*
%{_x11mandir}/man3/*
%if %{with_fontconfig}
%{_x11mandir}/man3/fontconfig.3*
%endif


%files font-utils
%defattr(-,root,root)
%{_x11bindir}/bdftopcf
%{_x11mandir}/man1/bdftopcf.1*
%{_x11bindir}/bdftruncate
%{_x11mandir}/man1/bdftruncate.1*
#%{_x11bindir}/fonttosfnt
#%{_x11mandir}/man1/fonttosfnt.1*
%if %{with_fontconfig}
%{_x11bindir}/fc-cache
%{_x11bindir}/fc-list
%{_x11mandir}/man1/fc-cache.1*
%{_x11mandir}/man1/fc-list.1*
%endif
%{_x11bindir}/mkfontdir
%{_x11mandir}/man1/mkfontdir.1*
%{_x11bindir}/mkfontscale
%{_x11mandir}/man1/mkfontscale.1*
# The 'util' subdir is used by ucs2any, mkfontdir et al.
%dir %{_x11fontdir}/util
%{_x11fontdir}/util/*
# FIXME: ucs2any should be moved to %{name}-font-utils
%{_x11bindir}/ucs2any
# FIXME: ucs2any should be moved to font-utils subpackage
%{_x11mandir}/man1/ucs2any.1*


%files tools
%defattr(-,root,root)
%{_x11bindir}/beforelight
%{_x11bindir}/glxinfo
%{_x11bindir}/glxgears
%{_x11bindir}/ico
%{_x11bindir}/listres
%{_x11bindir}/mkhtmlindex
%{_x11bindir}/oclock
%{_x11bindir}/showfont
%{_x11bindir}/viewres
%{_x11bindir}/x11perf
%{_x11bindir}/x11perfcomp
%if %{with_xcalc}
%{_x11bindir}/xcalc
%endif
%{_x11bindir}/xclipboard
%{_x11bindir}/xclock
%if %{with_xedit}
%{_x11bindir}/xedit
%endif
%{_x11bindir}/xev
%{_x11bindir}/xfd
%{_x11bindir}/xfontsel
%{_x11bindir}/xgc
# XIE is obsolete %{_x11bindir}/xieperf
# xload has no need to be SUID root
%attr(755,root,root) %{_x11bindir}/xload
%{_x11bindir}/xmag
%if %{with_xman}
%{_x11bindir}/xman
%endif
%{_x11bindir}/xmessage
%{_x11bindir}/xvinfo
%{_x11bindir}/xwininfo
%{_x11bindir}/xlogo
%{_x11bindir}/xkill
%if %{with_xedit}
%dir %{_x11datadir}/X11/xedit
%dir %{_x11datadir}/X11/xedit/lisp
%{_x11datadir}/X11/xedit/lisp/*.lsp
%dir %{_x11datadir}/X11/xedit/lisp/progmodes
%{_x11datadir}/X11/xedit/lisp/progmodes/*.lsp
%endif
%if %{with_xman}
%{_x11datadir}/X11/xman.help
%endif
%{_x11mandir}/man1/beforelight.1*
%{_x11mandir}/man1/glxinfo.1*
%{_x11mandir}/man1/glxgears.1*
%{_x11mandir}/man1/ico.1*
%{_x11mandir}/man1/listres.1*
%{_x11mandir}/man1/mkhtmlindex.1*
%{_x11mandir}/man1/showfont.1*
%{_x11mandir}/man1/viewres.1*
%{_x11mandir}/man1/x11perf.1*
%{_x11mandir}/man1/x11perfcomp.1*
%if %{with_xcalc}
%{_x11mandir}/man1/xcalc.1*
%endif
%{_x11mandir}/man1/xclipboard.1*
%{_x11mandir}/man1/xclock.1*
%if %{with_xedit}
%{_x11mandir}/man1/xedit.1*
%endif
%{_x11mandir}/man1/xev.1*
%{_x11mandir}/man1/xfd.1*
%{_x11mandir}/man1/xfontsel.1*
%{_x11mandir}/man1/xgc.1*
# XIE is obsolete %{_x11mandir}/man1/xieperf.1*
%{_x11mandir}/man1/xload.1*
%{_x11mandir}/man1/xmag.1*
%if %{with_xman}
%{_x11mandir}/man1/xman.1*
%endif
%{_x11mandir}/man1/xmessage.1*
%{_x11mandir}/man1/xvinfo.1*
%{_x11mandir}/man1/xwininfo.1*


%files twm
%defattr(-,root,root)
%dir %{_sysconfdir}/X11/twm
%config %{_sysconfdir}/X11/twm/system.twmrc
%{_x11bindir}/twm
%{_x11datadir}/X11/twm
%{_x11mandir}/man1/twm.1*


%files xauth
%defattr(-,root,root)
%{_x11bindir}/xauth
%{_x11bindir}/mkxauth
%{_x11mandir}/man1/xauth.1*
%{_x11mandir}/man1/mkxauth.1*


%files xdm
%defattr(-,root,root)
%dir %{_sysconfdir}/X11/xdm
%{_sysconfdir}/X11/xdm/authdir
%dir %{_sysconfdir}/X11/xdm/pixmaps
%{_sysconfdir}/X11/xdm/pixmaps/*
# We ship these in the xinitrc package
#%config /etc/X11/xdm/GiveConsole
#%config /etc/X11/xdm/TakeConsole
#%config /etc/X11/xdm/Xaccess
%config /etc/X11/xdm/Xservers
# We ship these in the xinitrc package
#/etc/X11/xdm/Xsession
#/etc/X11/xdm/Xsetup_0
%config /etc/X11/xdm/Xresources
%config /etc/X11/xdm/Xwilling
# FIXME: chooser is an ELF executable, should not be in /etc really
/etc/X11/xdm/chooser
%config  %attr(0644,root,root) /etc/pam.d/xdm
%{_x11bindir}/xdm
%{_x11datadir}/X11/xdm
%{_x11mandir}/man1/xdm.1*
%dir /var/lib/xdm
%dir %attr(0700,root,root) /var/lib/xdm/authdir


%files xfs
%defattr(-,root,root)
%dir /etc/X11/fs
# Changed back to 'noreplace' to fix bug #53103
%config(noreplace) %verify(not md5 size mtime) %{_sysconfdir}/X11/fs/config
%config %{_sysconfdir}/rc.d/init.d/xfs
%{_x11bindir}/xfsinfo
%{_x11bindir}/fslsfonts
%{_x11bindir}/fstobdf
%{_x11bindir}/xfs
%{_x11datadir}/X11/fs
%{_x11mandir}/man1/xfs.1*
%{_x11mandir}/man1/xfsinfo.1*
%{_x11mandir}/man1/fslsfonts.1*
%{_x11mandir}/man1/fstobdf.1*

### %{name}-libs-data ################################################
# libs-data includes files which used to be in "libs" but which were moved
# here so that both x86, and x86_64 libs packages may be installed simultaneously.
%if %{with_libs_data}
%files libs-data
%defattr(-,root,root)
%dir %{_x11datadir}
%dir %{_x11datadir}/X11
%dir %{_x11localedir}
%{_x11localedir}/*
%{_x11datadir}/X11/rgb.txt
# Xcms.txt should be banished from the face of the earth with extreme
# hostility
#%{_x11datadir}/X11/Xcms.txt
%{_x11datadir}/X11/XErrorDB
%{_x11datadir}/X11/XKeysymDB
# Exclude i18n DSOs as they're arch specific
%exclude %dir %{_x11localedir}/%{_lib}
%exclude %dir %{_x11localedir}/%{_lib}/common
%exclude %{_x11localedir}/%{_lib}/common/*
%dir %{_x11mandir}
%dir %{_x11mandir}/man1
%dir %{_x11mandir}/man2
%dir %{_x11mandir}/man3
%dir %{_x11mandir}/man4
%dir %{_x11mandir}/man5
%dir %{_x11mandir}/man6
%dir %{_x11mandir}/man7
%dir %{_x11mandir}/man8
%endif

%files libs
%defattr(-,root,root)
# On x86 and other architectures _x11libdir and _x11datadir are the same dir,
# so listing them both generates a "file included twice" error.  Since these
# dirs are different on x86_64, we ifarch it here.
# All manpage dirs owned by libs package to guarantee they are owned by some
# installed package because everything pretty much depends on libs being there
%if ! %{with_libs_data}
%dir %{_x11datadir}
%dir %{_x11datadir}/X11
#%dir %{_x11localedir}
#%dir %{_x11localedir}/*/
#%{_x11localedir}/*/*
#%{_x11localedir}/compose.dir
#%{_x11localedir}/locale.alias
#%{_x11localedir}/locale.dir
%{_x11datadir}/X11/rgb.txt
# Xcms.txt should be banished from the face of the earth with extreme
# hostility
#%{_x11datadir}/X11/Xcms.txt
%{_x11datadir}/X11/XErrorDB
%{_x11datadir}/X11/XKeysymDB
%dir %{_x11mandir}
%dir %{_x11mandir}/man1
%dir %{_x11mandir}/man2
%dir %{_x11mandir}/man3
%dir %{_x11mandir}/man4
%dir %{_x11mandir}/man5
%dir %{_x11mandir}/man6
%dir %{_x11mandir}/man7
%dir %{_x11mandir}/man8
%endif # ! %{with_libs_data}

%dir %{_x11localedir}
%dir %{_x11localedir}/C
%dir %{_x11localedir}/armscii-8
%dir %{_x11localedir}/el_GR.UTF-8
%dir %{_x11localedir}/en_US.UTF-8
%dir %{_x11localedir}/georgian-*
%dir %{_x11localedir}/ibm-cp1133
%dir %{_x11localedir}/is*
%dir %{_x11localedir}/ja*
%dir %{_x11localedir}/ko*
%dir %{_x11localedir}/microsoft-cp125?
%dir %{_x11localedir}/mulelao-1
%dir %{_x11localedir}/nokhchi-1
%dir %{_x11localedir}/tatar-cyr
%dir %{_x11localedir}/th_TH*
%dir %{_x11localedir}/tscii-0
%dir %{_x11localedir}/vi_VN.*
%dir %{_x11localedir}/zh*
%dir %{_x11localedir}/%{_lib}
%dir %{_x11localedir}/%{_lib}/common
%{_x11localedir}/compose.dir
%{_x11localedir}/locale.alias
%{_x11localedir}/locale.dir
%{_x11localedir}/C/*
%{_x11localedir}/armscii-8/*
%{_x11localedir}/el_GR.UTF-8/*
%{_x11localedir}/en_US.UTF-8/*
%{_x11localedir}/georgian-*/*
%{_x11localedir}/ibm-cp1133/*
%{_x11localedir}/is*/*
%{_x11localedir}/ja*/*
%{_x11localedir}/ko*/*
%{_x11localedir}/microsoft-cp125?/*
%{_x11localedir}/mulelao-1/*
%{_x11localedir}/nokhchi-1/*
%{_x11localedir}/pt_BR.UTF-8/*
%{_x11localedir}/tatar-cyr/*
%{_x11localedir}/th_TH*/*
%{_x11localedir}/tscii-0/*
%{_x11localedir}/vi_VN.*/*
%{_x11localedir}/zh*/*
#%{_x11localedir}/%{_lib}/*
%{_x11localedir}/%{_lib}/common/*
%ifarch x86_64
%dir %{_x11libdir}
%endif
# Shared libraries:  %{_x11libdir}/lib*.so.* might be better in the long run
# except for arch specific stuff, but it shouldn't be built in the first place.
/etc/ld.so.conf.d/xorg-x11-%{_arch}.conf
%{_x11libdir}/libFS.so.6
%{_x11libdir}/libFS.so.6.0
%{_x11libdir}/libGLw.so.1
%{_x11libdir}/libGLw.so.1.0
%ifarch %{ix86} ia64 x86_64
%{_x11libdir}/libI810XvMC.so.1
%{_x11libdir}/libI810XvMC.so.1.0
%endif
%{_x11libdir}/libICE.so.6
%{_x11libdir}/libICE.so.6.3
%{_x11libdir}/libOSMesa.so.4
%{_x11libdir}/libOSMesa.so.4.0
%{_x11libdir}/libSM.so.6
%{_x11libdir}/libSM.so.6.0
%{_x11libdir}/libX11.so.6
%{_x11libdir}/libX11.so.6.2
%{_x11libdir}/libXRes.so.1
%{_x11libdir}/libXRes.so.1.0
%{_x11libdir}/libXTrap.so.6
%{_x11libdir}/libXTrap.so.6.4
%{_x11libdir}/libXaw.so.6
%{_x11libdir}/libXaw.so.6.1
%{_x11libdir}/libXaw.so.7
%{_x11libdir}/libXaw.so.7.0
%{_x11libdir}/libXcomposite.so.1
%{_x11libdir}/libXcomposite.so.1.0
%{_x11libdir}/libXcursor.so.1
%{_x11libdir}/libXcursor.so.1.0.2
%{_x11libdir}/libXdamage.so.1
%{_x11libdir}/libXdamage.so.1.0
%{_x11libdir}/libXext.so.6
%{_x11libdir}/libXext.so.6.4
%{_x11libdir}/libXevie.so.1
%{_x11libdir}/libXevie.so.1.0
%{_x11libdir}/libXfixes.so.3
%{_x11libdir}/libXfixes.so.3.0
%{_x11libdir}/libXfont.so.1
%{_x11libdir}/libXfont.so.1.5
# FIXME: these are no longer present in 6.8.0, not sure why yet, so just
# commenting out rather than removing.  -- mharris
#%{_x11libdir}/libXfontcache.so.1
#%{_x11libdir}/libXfontcache.so.1.2
%{_x11libdir}/libXft.so.1
%{_x11libdir}/libXft.so.1.1
%{_x11libdir}/libXft.so.2
%{_x11libdir}/libXft.so.2.1.2
%{_x11libdir}/libXi.so.6
%{_x11libdir}/libXi.so.6.0
%{_x11libdir}/libXinerama.so.1
%{_x11libdir}/libXinerama.so.1.0
%{_x11libdir}/libXmu.so.6
%{_x11libdir}/libXmu.so.6.2
%{_x11libdir}/libXmuu.so.1
%{_x11libdir}/libXmuu.so.1.0
%{_x11libdir}/libXpm.so.4
%{_x11libdir}/libXpm.so.4.11
%{_x11libdir}/libXrandr.so.2
%{_x11libdir}/libXrandr.so.2.0
%{_x11libdir}/libXrender.so.1
%{_x11libdir}/libXrender.so.1.2.2
%{_x11libdir}/libXss.so.1
%{_x11libdir}/libXss.so.1.0
%{_x11libdir}/libXt.so.6
%{_x11libdir}/libXt.so.6.0
%{_x11libdir}/libXtst.so.6
%{_x11libdir}/libXtst.so.6.1
%{_x11libdir}/libXv.so.1
%{_x11libdir}/libXv.so.1.0
%{_x11libdir}/libXvMC.so.1
%{_x11libdir}/libXvMC.so.1.0
%{_x11libdir}/libXxf86dga.so.1
%{_x11libdir}/libXxf86dga.so.1.0
%{_x11libdir}/libXxf86misc.so.1
%{_x11libdir}/libXxf86misc.so.1.1
%{_x11libdir}/libXxf86rush.so.1
%{_x11libdir}/libXxf86rush.so.1.0
%{_x11libdir}/libXxf86vm.so.1
%{_x11libdir}/libXxf86vm.so.1.0
%{_x11libdir}/libdps.so.1
%{_x11libdir}/libdps.so.1.0
%{_x11libdir}/libdpstk.so.1
%{_x11libdir}/libdpstk.so.1.0
%{_x11libdir}/libfontenc.so.1
%{_x11libdir}/libfontenc.so.1.0
%{_x11libdir}/libpsres.so.1
%{_x11libdir}/libpsres.so.1.0
%{_x11libdir}/libxkbfile.so.1
%{_x11libdir}/libxkbfile.so.1.0
%{_x11libdir}/libxkbui.so.1
%{_x11libdir}/libxkbui.so.1.0
%if %{with_fontconfig}
%{_x11libdir}/libfontconfig.so.*
%endif
%if %{with_libxrx}
# FIXME: need to do test build to get .so version
%{_x11libdir}/libxrx.so.
%endif

%files deprecated-libs
%defattr(-,root,root)
# Even when with_xprint is 0, we still need the libs for legacy compat
%{_x11libdir}/libXp.so.6
%{_x11libdir}/libXp.so.6.2

%files deprecated-libs-devel
%defattr(-,root,root)
%{_x11includedir}/X11/extensions/Print.h
%{_x11includedir}/X11/extensions/Printstr.h
%{_x11libdir}/libXp.a
%{_x11libdir}/libXp.so

%files Mesa-libGL
%defattr(-,root,root)
%{_x11libdir}/libGL.so.1
%{_x11libdir}/libGL.so.%{libGL_version}
%{_libdir}/libGL.so.1
#%{_libdir}/libGL.so.1.2

%files Mesa-libGLU
%defattr(-,root,root)
%{_x11libdir}/libGLU.so.1
%{_x11libdir}/libGLU.so.%{libGLU_version}
%{_libdir}/libGLU.so.1

######################################################################
# Fonts
%if %{with_fonts}
%files base-fonts
%defattr(-,root,root)
%dir %{_x11fontdir}
# base 100dpi fonts
%dir %{_x11fontdir}/100dpi
%ghost %verify(not md5 size mtime) %{_x11fontdir}/100dpi/encodings.dir
%config(noreplace) %verify(not md5 size mtime) %{_x11fontdir}/100dpi/fonts.alias
%ghost %verify(not md5 size mtime) %{_x11fontdir}/100dpi/fonts.dir
%ghost %verify(not md5 size mtime) %{_x11fontdir}/100dpi/fonts.scale
# base 75dpi fonts
%dir %{_x11fontdir}/75dpi
%ghost %verify(not md5 size mtime) %{_x11fontdir}/75dpi/encodings.dir
%config(noreplace) %verify(not md5 size mtime) %{_x11fontdir}/75dpi/fonts.alias
%ghost %verify(not md5 size mtime) %{_x11fontdir}/75dpi/fonts.dir
%ghost %verify(not md5 size mtime) %{_x11fontdir}/75dpi/fonts.scale
# base CID fonts
%dir %{_x11fontdir}/CID
%ghost %verify(not md5 size mtime) %{_x11fontdir}/CID/encodings.dir
%ghost %verify(not md5 size mtime) %{_x11fontdir}/CID/fonts.dir
%ghost %verify(not md5 size mtime) %{_x11fontdir}/CID/fonts.scale
# Encoding files
%dir %{_x11fontdir}/encodings
%{_x11fontdir}/encodings/*
#%dir %{_x11fontdir}/encodings/large
#%{_x11fontdir}/encodings/large/*
# local, and misc do not currently contain fonts, but we want to own the dir
%dir %{_x11fontdir}/local
%ghost %verify(not md5 size mtime) %{_x11fontdir}/local/encodings.dir
%ghost %verify(not md5 size mtime) %{_x11fontdir}/local/fonts.dir
# base misc files
%dir %{_x11fontdir}/misc
%{_x11fontdir}/misc/*.pcf.gz
%ghost %verify(not md5 size mtime) %{_x11fontdir}/misc/encodings.dir
%config(noreplace) %verify(not md5 size mtime) %{_x11fontdir}/misc/fonts.alias
%ghost %verify(not md5 size mtime) %{_x11fontdir}/misc/fonts.dir
%ghost %verify(not md5 size mtime) %{_x11fontdir}/misc/fonts.scale

# base Speedo fonts
#%dir %{_x11fontdir}/Speedo
#%{_x11fontdir}/Speedo/*.spd
#%ghost %verify(not md5 size mtime) %{_x11fontdir}/Speedo/encodings.dir
#%ghost %verify(not md5 size mtime) %{_x11fontdir}/Speedo/fonts.dir
#%verify(not md5 size mtime) %{_x11fontdir}/Speedo/fonts.scale

# base Type1 fonts
%dir %{_x11fontdir}/Type1
%{_x11fontdir}/Type1/*.afm
%{_x11fontdir}/Type1/*.pfa
%{_x11fontdir}/Type1/*.pfb
%ghost %verify(not md5 size mtime) %{_x11fontdir}/Type1/encodings.dir
%ghost %verify(not md5 size mtime) %{_x11fontdir}/Type1/fonts.dir
%verify(not md5 size mtime) %{_x11fontdir}/Type1/fonts.scale
%ghost %verify(not md5 size mtime) %{_x11fontdir}/Type1/fonts.cache*
# Make base-fonts own the other font directories and auxilliary files
%dir %{_x11fontdir}/OTF
%ghost %verify(not md5 size mtime) %{_x11fontdir}/OTF/encodings.dir
%ghost %verify(not md5 size mtime) %config(noreplace) %{_x11fontdir}/OTF/fonts.alias
%ghost %verify(not md5 size mtime) %{_x11fontdir}/OTF/fonts.dir
%ghost %verify(not md5 size mtime) %{_x11fontdir}/OTF/fonts.scale
%ghost %verify(not md5 size mtime) %{_x11fontdir}/OTF/fonts.cache*
%dir %{_x11fontdir}/TTF
%ghost %verify(not md5 size mtime) %{_x11fontdir}/TTF/encodings.dir
%ghost %verify(not md5 size mtime) %config(noreplace) %{_x11fontdir}/TTF/fonts.alias
%ghost %verify(not md5 size mtime) %{_x11fontdir}/TTF/fonts.dir
%ghost %verify(not md5 size mtime) %{_x11fontdir}/TTF/fonts.scale
%ghost %verify(not md5 size mtime) %{_x11fontdir}/TTF/fonts.cache*

# Don't glob all TTF fonts with *.ttf as we wont detect newly added fonts in
# new releases, and may not want them all (ie: Vera we ship separately)
%files truetype-fonts
%defattr(-,root,root)
%dir %{_x11fontdir}/TTF
%{_x11fontdir}/TTF/luxi*.ttf

%files syriac-fonts
%defattr(-,root,root)
%dir %{_x11fontdir}/OTF
%{_x11fontdir}/OTF/Syr*.otf

%files 75dpi-fonts
%defattr(-,root,root)
%dir %{_x11fontdir}/75dpi
%exclude %{_x11fontdir}/75dpi/*-ISO8859-2.pcf.gz
%exclude %{_x11fontdir}/75dpi/*-ISO8859-9.pcf.gz
%exclude %{_x11fontdir}/75dpi/*-ISO8859-14.pcf.gz
%exclude %{_x11fontdir}/75dpi/*-ISO8859-15.pcf.gz
%{_x11fontdir}/75dpi/*.pcf.gz

%files 100dpi-fonts
%defattr(-,root,root)
%dir %{_x11fontdir}/100dpi
%exclude %{_x11fontdir}/100dpi/*-ISO8859-2.pcf.gz
%exclude %{_x11fontdir}/100dpi/*-ISO8859-9.pcf.gz
%exclude %{_x11fontdir}/100dpi/*-ISO8859-14.pcf.gz
%exclude %{_x11fontdir}/100dpi/*-ISO8859-15.pcf.gz
%{_x11fontdir}/100dpi/*.pcf.gz

%files ISO8859-2-75dpi-fonts
%defattr(-,root,root)
%{_x11fontdir}/75dpi/*-ISO8859-2.pcf.gz

%files ISO8859-2-100dpi-fonts
%defattr(-,root,root)
%{_x11fontdir}/100dpi/*-ISO8859-2.pcf.gz

%files ISO8859-9-75dpi-fonts
%defattr(-,root,root)
%{_x11fontdir}/75dpi/*-ISO8859-9.pcf.gz

%files ISO8859-9-100dpi-fonts
%defattr(-,root,root)
%{_x11fontdir}/100dpi/*-ISO8859-9.pcf.gz

%files ISO8859-14-75dpi-fonts
%defattr(-,root,root)
%{_x11fontdir}/75dpi/*-ISO8859-14.pcf.gz

%files ISO8859-14-100dpi-fonts
%defattr(-,root,root)
%{_x11fontdir}/100dpi/*-ISO8859-14.pcf.gz

%files ISO8859-15-75dpi-fonts
%defattr(-,root,root)
%{_x11fontdir}/75dpi/*-ISO8859-15.pcf.gz

%files ISO8859-15-100dpi-fonts
%defattr(-,root,root)
%{_x11fontdir}/100dpi/*-ISO8859-15.pcf.gz

%files cyrillic-fonts
%defattr(-,root,root)
%dir %{_x11fontdir}/cyrillic
%{_x11fontdir}/cyrillic/*.gz
%ghost %verify(not md5 size mtime) %{_x11fontdir}/cyrillic/encodings.dir
%config(noreplace) %verify(not md5 size mtime) %{_x11fontdir}/cyrillic/fonts.alias
%ghost %verify(not md5 size mtime) %{_x11fontdir}/cyrillic/fonts.dir
%ghost %verify(not md5 size mtime) %{_x11fontdir}/cyrillic/fonts.scale

%endif
# End of font subpackages
#######################################################################


%if %{with_docs}
%files doc
%defattr(-,root,root)
%doc xc/doc/hardcopy/*
%endif

%files Xdmx
%defattr(-,root,root)
%{_x11bindir}/Xdmx
%{_x11mandir}/man1/Xdmx.1*
%{_x11mandir}/man1/dmxtodmx.1*
%{_x11mandir}/man1/vdltodmx.1*
%{_x11mandir}/man1/xdmxconfig.1*

%files Xnest
%defattr(-,root,root)
%{_x11bindir}/Xnest
%{_x11mandir}/man1/Xnest.1*

%if %{with_xprint}
%files Xprint
%defattr(-,root,root)
/etc/X11/Xsession.d/92xprint-xpserverlist.sh
/etc/X11/xinit/xinitrc.d/92xprint-xpserverlist.sh
/etc/init.d/xprint
/etc/profile.d/xprint.csh
/etc/profile.d/xprint.sh
/etc/rc.d/init.d/xprint
/etc/rc.d/rc[0-6].d/K??xprint
/etc/rc.d/rc[0-6].d/S??xprint
%{_x11bindir}/Xprt
%endif

%files Xvfb
%defattr(-,root,root)
%{_x11bindir}/Xvfb
%{_x11mandir}/man1/Xvfb.1*

%if %{with_xf86cfg}
%files xf86cfg
%defattr(-,root,root)
%{_x11bindir}/xf86cfg
%{_x11mandir}/man1/xf86cfg.1*
# FIXME: This stuff should not be in any include directory, that is stupid
%dir %{_x11includedir}/X11/pixmaps
%{_x11includedir}/X11/pixmaps/*
%endif

%if %{with_sdk}
%files sdk -f filelist.sdk
%defattr(-,root,root)
%endif

%clean
[ "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT 

# WIP: https://bugzilla.redhat.com/bugzilla/show_bug.cgi?id=168834
#- Added xorg-x11-6.8.2-map-pci-bios-ierr-bug168834.patch to fix X server bug
#  which causes an IERR to occur on some Dell and other servers.  (#168834)
#- Disabled xorg-x11-6.8.2-Xserver-pci-infinite-loop.patch to test the
#  assumption that the map-pci-bios-ierr bug is the same issue as suspected,
#  as the patches also conflict with each other.


%changelog
* Wed Apr 13 2011 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.68
- cve-2011-0465.patch: Fix escaping and quoting logic to match upstream (#696317)

* Wed Mar 16 2011 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.67
- cve-2011-0465.patch: Sanitize cpp macro expansion. (CVE 2011-0465)

* Mon Jan 31 2011 Jerome Glisse <jglisse@redhat.com> 6.8.2-1.EL.66
- xorg-x11-6.8-option-max-clients-fix.patch #490951 export function
  for max client option changes

* Tue Jan 25 2011 Jerome Glisse <jglisse@redhat.com> 6.8.2-1.EL.65
- xorg-x11-6.8-option-max-clients.patch #490951 add max client options

* Fri Dec 17 2010 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.64
- xorg-x11-6.8.2-backing-store-validategc.patch: Fix GC validation in the
  backing store code. (#663056)

* Tue Mar 31 2009 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.63
- xorg-x11-6.8.2-mga-g200se-dont-force-16bpp.patch: Fix option parsing to
  work and memory sizing to work. (#469651)

* Thu Feb 12 2009 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.61
- xorg-x11-6.8.2-dev-input-mice.patch: Try /dev/input/mice when
  searching for automatic mouse device. (#485305)

* Thu Feb 12 2009 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.60
- xorg-x11-6.8.2-mga-g200se-dont-force-16bpp.patch: Do vram probe
  earlier, and fix inverted test sense. (#485156)

* Wed Jan 28 2009 Dave Airlie <airlied@redhat.com> 6.8.2-1.EL.59
- xorg-x11-6.8.2-fix-powerpc-fonts.patch  (#300911)

* Tue Jan 27 2009 Kristian Høgsberg <krh@redhat.com> 6.8.2-1.EL.58
- Fix segfault on xfs drone server exit path.
- Update Sun6 keyboard patch to not drop the \| key.

* Fri Jan 23 2009 Dave Airlie <airlied@redhat.com> 6.8.2-1.EL.57
- xorg-x11-6.8.2-xkbcomp-add-ibm_spacesaver.patch (#454831)
- xorg-x11-6.8.2-mga-g200se-dont-force-16bpp.patch (#469651)

* Mon Jan 12 2009 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.56
- xorg-x11-6.8.2-g200-ev-wb.patch: Add support for Maxim and Winbond
  variants. (#445498, #454780)

* Thu Jan 08 2009 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.55
- Fix libGLU.a build on x86_64. (#432087)

* Mon Dec 08 2008 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.54
- xorg-x11-6.8.2-fb-traps-crash.patch: Fix crash in trapezoid rendering
  triggered by Firefox, among other things. (#463137)

* Mon Dec 08 2008 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.53
- xorg-x11-6.8.2-drm-device-permissions.patch: Fix initial DRI device
  permissions. (#462106)

* Wed Jun 25 2008 Dave Airlie <airlied@redhat.com> 6.8.2-1.EL.52
- remove g80 support - too fragile for RHEL 4.

* Tue Jun 24 2008 Dave Airlie <airlied@redhat.com> 6.8.2-1.EL.51
- nv-g80-support.patch - fix linking against older system.
- nv-g80-lvds.patch - fix LVDS support to not break DVI.

* Thu Jun 12 2008 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.50
- xorg-x11-6.8.2-vesa-vbe-clear.patch: Fix wild pointer chase. (#205361)

* Wed Jun 11 2008 Dave Airlie <airlied@redhat.com> 6.8.2-1.EL.49
- cve-2008-1377.patch: Record and Security Extension Input validation
- cve-2008-1379.patch: MIT-SHM extension Input Validation flaw
- cve-2008-2360.patch: Render AllocateGlyph extension Integer overflows
- cve-2008-2361.patch: Render CreateCursor extension Integer overflows

* Wed Jun 04 2008 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.48
- Revert xorg-x11-6.8.2-vesa-vbe-clear.patch for the moment. (#205361)

* Thu Apr 10 2008 Kristian Høgsberg <krh@redhat.com> - 6.8.2-1.EL.44
- Update xorg-x11-6.8.2-xkbdata-sun6-keys.patch to also support
  Sun Type 7 keyboards (#194259).

* Wed Apr  9 2008 Kristian Hoegsberg <krh@redhat.com> 6.8.2-1.EL.43
- Backport evdev driver from RHEL4 (#392711).

* Thu Apr 03 2008 Dave Airlie <airlied@redhat.com> 6.8.2-1.EL.42
- nv-g80-lvds.patch: Attempt to backport LVDS support to pre-randr nv (#237122)

* Wed Apr 02 2008 Dave Airlie <airlied@redhat.com> 6.8.2-1.EL.41
- add-ast-driver.patch: Add the AST driver (#261621)
- xorg-x11-6.8.2-gc-max-formats.patch: Fix Xvfb crash caused by too many formats (#235383)

* Tue Apr 01 2008 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.40
- xorg-x11-6.8.2-vesa-vbe-clear.patch: Add Option "ModeSetClearScreen" to
  vesa driver. (#205361)

* Tue Apr 01 2008 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.39
- Reorder the nv patches in with the other driver patches, and re-enable
  the G80 backport. (#237122)

* Mon Mar 31 2008 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.38
- xorg-x11-6.8.2-mga-g200se-a-updates.patch: Fixes for G200SE-A. (#251140)
- Fix xgi build on AMD64 harder. (#248461)

* Thu Mar 27 2008 Dave Airlie <airlied@redhat.com> 6.8.2-1.EL.37
- Fix xgi build on AMD64 platform (#248461)

* Thu Feb 21 2008 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.36
- No change, just sync with 4.6 Z-stream.

* Fri Jan 18 2008 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.33.0.2
- cve-2007-6429.patch: Fix MIT-SHM pixmaps with bpp < 8.

* Mon Jan 14 2008 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.33.0.1
- cve-2007-4568.patch: XFS Integer Overflow Vulnerability
- cve-2007-5760.patch: XFree86-Misc Extension Invalid Array Index Vulnerability
- cve-2007-5958.patch: Xorg / XFree86 file existence disclosure vulnerability
- cve-2007-6427.patch: XInput Extension Memory Corruption Vulnerability
- cve-2007-6428.patch: TOG-CUP Extension Memory Corruption Vulnerability
- cve-2007-6429.patch: EVI and MIT-SHM Extension Integer Overflow Vulnerability
- cve-2008-0006.patch: libXfont PCF Parser Memory Corruption Vulnerability

* Tue Oct 09 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.33
- xorg-x11-6.8.2-keyboard-leds.patch: Fix keyboard LED handling across
  VT switch.  (#294521)

* Fri Sep 21 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.32
- xorg-x11-6.8.2-blank-at-exit.patch: Fix a thinko that would make the server
  crash at exit instead of blanking the screen. (#293221)
- Fix the core package to depend on arbitrary versions of xorg-x11-{libs,xfs}
  since the versioning really isn't that important.

* Wed Sep 12 2007 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.31
- Rebuild due to missing patch

* Tue Sep 11 2007 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.30
- Add patch9832 -p1 -b .cve-2007-4730 (#286081)

* Tue Sep 11 2007 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.28
- Add patch9832 -p1 -b .cve-2007-4730 (#286081)

* Thu Aug 02 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.27
- xorg-x11-6.8.3-radeon-default-mergedfb-ranges.patch: Expand the default sync
  ranges for radeon MergedFB to be big enough for 800x600 @ 60Hz. (#235889)

* Thu Aug 02 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.26
- xorg-x11-6.8.2-blank-at-exit: Yet another attempt to keep screen contents
  from showing up at server startup. (#205361)

* Wed Aug 01 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.25
- xorg-x11-6.8.2-maxclients.patch: Raise maximum client limit to 512.
  (#230217, #206955)

* Mon Jul 30 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.24
- xorg-x11-6.8.2-libXrandr-swap-coordinates.patch: Swap dimensions in randr
  ScreenChangeNotify events. (#224216)

* Mon Jul 30 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.23
- Enable building cirrus driver on ia64 for HVM's sake. (#237070)

* Mon Jul 30 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.22
- Re-enable RS482 backport. (#180384)

* Wed Jul 25 2007 Kristian Høgsberg <krh@redhat.com> - 6.8.2-1.EL.21
- Add patch for Canadian and French Canadian xkb layouts as secondary
  layouts (#235891).

* Wed Jul 25 2007 Kristian Høgsberg <krh@redhat.com> - 6.8.2-1.EL.20
- Add requires for base-fonts for xfs subpacakge (#215580).

* Fri Jun 15 2007 Kristian Høgsberg <krh@redhat.com> - 6.8.2-1.EL.19
- Fix root priv elevation bug (242903).  Just don't delete the
  directory and make sure when we create the directory, that we set
  the mode using mkdir -m.

* Thu Apr 19 2007 Kristian Høgsberg <krh@redhat.com> 6.8.2-1.EL.18
- Add more PCI IDs to the vesa G80 check (#226687).

* Wed Apr 18 2007 Kristian Høgsberg <krh@redhat.com> - 6.8.2-1.EL.17
- Back out G80 support, add vesa driver workaround (#226687).

* Tue Apr 17 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.16
- Backport G80 support from Xorg git. (#226687)

* Tue Apr 10 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.15
- Fix x86emu's JNL instruction. (#226687)

* Mon Apr 09 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.13.59
- Disable vesa blank-on-init patch. (#235372)

* Mon Apr 09 2007 Adam Jackson <ajax@redhat.com>
- Add cve-2007-1351.patch (#234056)
- Add cve-2007-1003.patch  (#233000)
- Add int-overflow.patch (#231693)

* Wed Apr 04 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.13.56
- Fix x86emu's BTS instruction. (#226687)

* Mon Feb 26 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.13.55
- Forcibly disable 16bpp in fbdev when under Xen. (#229788)

* Tue Feb 20 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.13.54
- Fix x86emu's BSF and BSR instructions. (#226687)

* Wed Feb  7 2007 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.13.53
- Add nv34-tweaks.patch to fix bug 175022.

* Thu Feb  1 2007 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.13.52
- Add xim-deadlock-bug-189849.patch to fix bug 189849.

* Thu Feb  1 2007 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.13.51
- Back out the rs482 patch as it was punted to 4.6.

* Thu Feb  1 2007 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.13.50
- Re-order the rn50 render and the add-rs482 patches

* Thu Feb  1 2007 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.13.50
- Add missing define in add-rs482.patch

* Wed Jan 31 2007 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.13.50
- Enable patch 1222

* Wed Jan 31 2007 Soren Sandmann <sandmann@redhat.com>
- Add patch 1222, add-rs482.patch (but don''t apply yet), which is a completely
  untested 'backport' of RS482 support. 

* Wed Jan 31 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.13.59
- xorg-x11-6.8.2-mga-g200se-update.patch: Fix G200SE lockups and timing
  issues. (#215003)

* Wed Jan 31 2007 Soren Sandmann <sandmann@redhat.com> - 6.8.2-EL.13.48
- Update ia64-disable-offscreen-pixmaps.patch to make it compile.

* Wed Jan 31 2007 Soren Sandmann <sandmann@redhat.com>
- Update ia64-disable-offscreen-pixmaps.patch to turn offscreen pixmaps off
  in the option processing code rather than in the default.

* Wed Jan 31 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.13.47
- xorg-x11-6.8.2-ati-radeon-ddc-mode.patch: Force radeon''s "DDCMode" to true
  on Dell server chipsets to fix cursor tracking. (#172250)

* Tue Jan 30 2007 Soren Sandmann <sandmann@redhat.com> - 6.8.2-1.EL.13.46
- Update ia64-disable-offscreen-pixmaps.patch so that it actually does
  something. (#198895)

* Mon Jan 29 2007 Soren Sandmann <sandmann@redhat.com> - 6.8.2-1.EL.13.45
- Update XGI driver patch so its symbols don't clash with the SiS drivers'.

* Mon Jan 29 2007 Soren Sandmann <sandmann@redhat.com> - 6.8.2-1.EL.13.44
- Add ia64-disable-offscreen-pixmaps.patch. (#198895).

* Fri Jan 26 2007 Soren Sandmann <sandmann@redhat.com>
- Add xf86-video-xgi driver. (#196785)

* Thu Jan 18 2007 Soren Sandmann <sandmann@redhat.com> - 6.8.2-1.EL.13.43
- Merge security fixes:
    xorg-x11-6.8.2-cve-2006-4740-cid-fonts.patch
    xorg-x11-server-CVE-2006-6101.patch
    xorg-x11-6.8.2-sorted-xkbcomp-dirs.patch

    ChangeLog:

    * Wed Jan 03 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.13.37.5
    - Add xorg-x11-6.8.2-sorted-xkbcomp-dirs.patch to fix rpmdiff multilib
        failure.

    * Tue Jan 02 2007 Adam Jackson <ajax@redhat.com> 6.8.2-1.EL.13.37.4
    - Add xorg-x11-server-CVE-2006-6101.patch. (#218871)

    * Wed Sep  6 2006 Adam Jackson <ajackson@redhat.com> 6.8.2-1.EL.13.37.2
    - Fix for CID font parser integer overflows. (CVE-2006-3470, #204548)

* Wed Jan 17 2007 Soren Sandmann <sandmann@redhat.com>
- Add patch to wait for the VT switch to complete on shutdown. #223074

* Wed Jan 17 2007 Soren Sandmann <sandmann@redhat.com>
- Remove obsolete .map-pci-bios-ierr-bug168834 patch. 

* Tue Jan 16 2007 Soren Sandmann <sandmann@redhat.com> - 6.8.2-1.EL.13.42
- Apply patch for bug 198266. (#198266).

* Wed Jan 10 2007 Soren Sandmann <sandmann@redhat.com> - 6.8.2-1.EL.13.41
- xorg-x11-6.8.2-pci-remap.patch
  Backport Egbert's patch from fdo bug 4139. (#168834).

* Tue Jan 9 2007 Soren Sandmann <sandmann@redhat.com> - 6.8.2-1.EL.13.40
- xorg-x11-6.8.2-nv-1.2.2-backport.patch
  Backport nv 1.2.2 driver (#198962, #175022)

* Tue Jan 9 2007 Soren Sandmann <sandmann@redhat.com>
- Add patch to vesa driver to blank framebuffer on init. (#205361)

* Mon Jan 8 2007 Soren Sandmann <sandmann@redhat.com>
- Add patch to check result of setuid() calls. (#195555)

* Mon Jan 8 2007 Soren Sandmann <sandmann@redhat.com>
- Add patch to disable render acceleration for rn50 (#192200).

* Mon Jan 8 2007 Soren Sandmann <sandmann@redhat.com> - 6.8.2-1.EL.13.39
- Add patch to make libGLw use system copies of Motif headers instead
  of its own internal ones. Add BuildRequires on openmotif-devel. (#178196).

* Mon Jan 8 2007 Soren Sandmann <sandmann@redhat.com>
- Add patch to fix byteswapping issue with ShmCreatePixmap. Bugs rh 203136,
  fdo 4730. 

* Fri Dec 22 2006 Jeremy Katz <katzj@redhat.com> - 6.8.2-1.EL.13.38
- add patch for fbdev driver to work with xenfb

* Fri Aug 25 2006 Adam Jackson <ajackson@redhat.com>
- Remove with_alternate_projectroot macros.

* Mon Aug 14 2006 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.13.37
- Add XFree86-4.1.0-fdo-7535. 
  Fix for FDO bug 7535, CVE-2006-3467, RH bug 202472

* Tue Jul 11 2006 Kristian Høgsberg <krh@redhat.com> 6.8.2-1.EL.13.36
- Update xorg-x11-6.8.2-xkbdata-sun6-keys.patch to add sun6 xkb symbol
  file to Imake install rule.

* Wed Jul  5 2006 Adam Jackson <ajackson@redhat.com> 6.8.2-1.EL.13.35
- Typo fixes to xorg-x11-6.8.2-ati-radeon-rn50-pixel-clock.patch.

* Wed Jul  5 2006 Adam Jackson <ajackson@redhat.com> 6.8.2-1.EL.13.34
- Removed xorg-x11-6.8.2-ati-radeon-rn50-pixelclock-limit-bug182511.patch.
- Forward-ported proper RN50 resolution limiting from XFree86-4.3.0-110.EL's
  XFree86-4.3.0-ati-RN50-limit-pixel-clock-bug189927.patch, named
  xorg-x11-6.8.2-ati-radeon-rn50-pixel-clock.patch.  (#194616, #195577,
  and #196891)

* Fri May 19 2006 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.33
- Added xorg-x11-6.8.2-ia64-hp-zx2-pcie-fix.patch to fix (#192191)
- Updated xorg-x11-6.8.2-Xnest-xkb-fix-bug177927.patch to really add XKEYBOARD
  support to Xnest this time (#177927)

* Tue May  9 2006 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.32
- Updated xorg-x11-6.8.2-xkbdata-sun6-keys.patch for (#165128)

* Fri May  5 2006 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.31
- Added xorg-x11-6.8.2-Xnest-xkb-fix-bug177927.patch to restore XKEYBOARD
  support to Xnest (#177927)

* Fri May  5 2006 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.30
- Merged in previously embargoed security fix for CVE-2006-1526, previously
  released as a security update in build 6.8.2-1.EL.13.25.1 from previous
  changelog entry.  (#189801)

* Mon May  1 2006 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.25.1
- Added xorg-x11-6.8.2-render-tris-CVE-2006-1526.patch to fix a
  buffer overflow documented in CVE-2006-1526.  (#189801)

* Tue Apr 25 2006 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.29
- Added xorg-x11-6.8.2-vesa-driver-memory-leak-bug172091.patch to fix a memory
  leak in the "vesa" driver. (#172091)

* Tue Apr 18 2006 Adam Jackson <ajackson@redhat.com> 6.8.2-1.EL.13.28
- Bump to appease beehive.

* Mon Apr 17 2006 Adam Jackson <ajackson@redhat.com> 6.8.2-1.EL.13.27
- Added xorg-x11-6.8.2-mga-g200se-support.patch to fix (#183686)

* Wed Mar 15 2006 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.26
- Added xorg-x11-6.8.2-ati-radeon-disable-mc-clients-bug.patch to fix
  (#177057, 182471)
- Disabled xorg-x11-6.8.1-ati-radeon-RV100-bus-master-fix.patch as the
  mc-clients patch is intended to resolve the same issue properly.
- Added xorg-x11-6.8.2-xkbdata-sun6-keys.patch to implement xkb support for
  Sun Type6 keyboards with extra keys.  (#165128)
- Added xorg-x11-6.8.2-ati-radeon-rn50-pixelclock-limit-bug182511.patch to
  limit the pixel clock on the ES1000, and any other cards based on the RN50
  chipset (#182511,180274,179886)
- Added xorg-x11-6.8.2-mesa-i915-squelch-debug-spew.patch to silence the
  extraneous debug spew in the i915 DRI driver (#181913,158016)
- Added xorg-x11-6.8.2-libXcursor-memleak-fix.patch to fix a memory leak in
  libXcursor (#172708)

* Mon Jan  9 2006 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.25
- Updated xorg-x11-6.8.2-ati-radeon-7000-disable-dri.patch with additional
  changes to resolve regressions in bug (#170008).

* Wed Nov 30 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.24
- Added xorg-x11-6.8.2-xconsole-devpts-support-bug-165021.patch which is
  a backport of UNIX98 pty support from CVS head for bug (#165021).
- Fixed freetype BuildRequires to be 2.1.7-3 instead of just 2.1.7 to match
  the comment above it, as the previous freetype builds have pointer aliasing
  bugs fixed ages ago.

* Wed Nov 30 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.23
- Added "StaticNeedsPicForShared YES" back to host.def to ensure that static
  libs with no shared counterpart get built PIC on *all* architectures
  including s390 and ppc64 to fix bug (#163909).
- Removed xorg-x11-6.8.2-config-StaticNeedsPicForShared.patch which is now
  obsoleted by the above change.  This reverts changes added in 6.8.2-11.
- Updated xorg-x11-6.8.2-add-i945-support.patch to activate Intel i945 PCI
  IDs for DRI support (#170517).
 
* Tue Nov 29 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.22
- Added xorg-x11-6.8.2-Xserver-pci-infinite-loop.patch, replacing previous
  workaround XFree86-4.3.0-ia64-pci-infinite-loop.patch which was
  conditionalized to ia64, which fixes bug (#166571).

* Mon Nov 28 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.21
- Added xorg-x11-6.8.2-xkb-segv-bug-168145.patch to fix xkb induced
  SEGV that occurs when using ALT-TAB to switch between apps (#168145).
- Added xorg-x11-6.8.2-im-lockup-bug-166068.patch to fix XIM bug in Xlib
  which causes IM to not work properly in Java and other stuff (#166068).
- Added xorg-x11-6.8.2-Xserver-render-unaligned-access-168416.patch to fix
  an unaligned memory access in the X server render support (#168416).
- Added xorg-x11-6.8.2-fstobdf-corrupted-bdf-167699.patch to fix (#167699).
- Remove the Speedo font files, as Xorg no longer supports Speedo fonts in
  6.8.0 onward but includes the fonts accidentally. (#166637,142744,154191)
- Changed base subpackage post script to remove the Speedo font path from xfs
  configuration to avoid warnings in /var/log/messages from xfs about bad
  font path elements. (#166637,142744,154191)
- Updated default xfs config to not contain Speedo FPE. (#166637)
- Renamed xorg-x11.6.8.1.903-AMD64-override-default-driverlist.patch to
  xorg-x11-6.8.2-AMD64-override-default-driverlist.patch to fix annoying
  patch naming inconsistency.
- Added xorg-x11-6.8.2-gb18030-20020207.patch, xorg-x11-6.8.2-gb18030-enc.patch,
  and xorg-x11-6.8.2-gb18030-locale-alias.patch, which are forward ports of
  GB18030 support from Yu Shao for bug (#168331).

* Mon Oct 10 2005 Mike A. Harris <mharris@redhat.com>
- Updated xorg-x11-6.8.2-ati-radeon-7000-disable-dri.patch to fix a typo
  present in initial patch, which fixes bug (#170008).

* Mon Sep 19 2005 Kristian Høgsberg <krh@redhat.com> 6.8.2-1.EL.13.20
- Fix broken byteswapping in the pci config patch (#168717).

* Tue Sep 13 2005 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.13.19
- Change version again.

* Tue Sep 13 2005 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.14
- Increase version.

* Tue Sep 13 2005 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.13.18
- Add xorg-x11-6.8.2-shadow-framebuffer-leak.patch to plug a leak in the
  shadow framebuffer code (bug 166696). 
- Update native pciscan patch to work correctly when accessing individual
  bytes in PCI memory.

* Fri Sep 2 2005 Soren Sandmann <sandmann@redhat.com> 6.8.2-1.EL.13.17
- Add XFree86-4.3.0-security-CAN-2005-2495.patch to fix various integer
  overflows.

* Thu Aug 18 2005 Kristian Høgsberg <krh@redhat.com> 6.8.2-1.EL.13.15
- Add xorg-x11-6.8.1-ati-radeon-RV100-bus-master-fix.patch to fix
  (#165179) and xorg-x11-6.8.2-add-i945-support.patch to fix (#156964).

* Wed Aug 17 2005 Kristian Høgsberg <krh@redhat.com> 6.8.2-1.EL.13.14
- Update xorg-x11-6.8.2-ati-radeon-rn50.patch to disable DRI entirely
  for RN50/ES1000 cards.

* Mon Aug  1 2005 Kristian Høgsberg <krh@redhat.com> 6.8.2-1.EL.13.13
- Update xorg-x11-6.8.2-use-linux-native-pciscan-by-default.patch with
  changes by Olivier Baudron from comment #28, bug #163331.

* Fri Jul 22 2005 Kristian Høgsberg <krh@redhat.com> 6.8.2-1.EL.13.12
- Bump release.
- Add xorg-x11-6.8.2-ati-radeon-rn50.patch to make the radeon driver
  recognize RN50/ES1000 cards (#162813).

* Mon Jul 12 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.11
- Added xorg-x11-6.8.2-ati-radeon-7000-disable-dri.patch to disable DRI on
  Radeon 7000/VE hardware by default, but allow override. (#150174)

* Thu Jun 30 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.10
- Added xorg-x11-6.8.2-xkb-dutch-keyboard-layout-fixes.patch as a proposed
  fix for Dutch keyboard layout issue (#135233)

* Thu Jun 23 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.9
- Updated xdm.pamd to work with new audit system. (#159332)
- Made copy of xdm.pamd named "xdm-pre-audit-system.pamd" for FC3/FC4 builds.
- Added xorg-x11-xdm "Requires: pam >= 0.77-66.8" for RHEL-4 builds, and
  "Requires: pam >= 0.79-10" for FC5 builds.  The audit functionality is
  disabled for FC3/FC4 builds.
- Merged new build target macro "build_fc5" from FC5 build, and updated spec
  file to use it where appropriate for nonstandard rebuilds of RHEL4 rpms.

* Mon May 30 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.8
- Added xorg-x11-6.8.2-ia64-elfloader-cache-flush.patch to fix cache flush
  issue on ia64 systems (#153103)
- Fix spec file to restrict removal of CVS metadata dirs at build time to
  the package, rather than the entire RPM_BUILD_DIR hierarchy.

* Mon May 30 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.7
- Re-enable xorg-x11-6.8.2-use-linux-native-pciscan-by-default.patch for
  RHEL4U2. (#156867)

* Fri May 13 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.6
- Temporarily disable xorg-x11-6.8.2-use-linux-native-pciscan-by-default.patch
  which was added for a test build in 6.8.2-1.EL.13.4, as it is intended for
  RHEL4_U2, not RHEL4_U1.  We will re-enable this for U2 once U1 is released.

* Fri May 13 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.5
- Added xorg-x11-6.8.2-ati-ragexl-ia64-avoidcpiofix.patch to workaround issue
  on ia64 with CPIO disabled in ati Mach64 driver (#155609,155610).  For
  future reference, this is also included in FC4 build 6.8.2-31.

* Mon May 2 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.13.4
- Added xorg-x11-6.8.2-use-linux-native-pciscan-by-default.patch to fix PCI
  config space contention issue by changing the X server to default to using
  Linux native PCI interfaces instead of directly banging on PCI space
  itself (#146386,152608).  Patch is from build 6.8.2-16 in FC4.

* Mon May 2 2005 Kristian Høgsberg <krh@redhat.com> 6.8.2-1.EL.13.3
- Dont install Xprint man page

* Wed Apr 20 2005 Kristian Høgsberg <krh@redhat.com> 6.8.2-1.EL.13.2
- Remove CVS directories from upstream tarball.

* Mon Apr 18 2005 Kristian Høgsberg <krh@redhat.com> 6.8.2-1.EL.13.1
- Add xorg-x11-6.8.1-ati-radeon-dynamic-clocks-fix-2.patch to revert
  radeon dynamic clock setup to what we had in 6.8.1.  The 6.8.2 code
  still causes lockups on some systems (#152648).

* Tue Mar 29 2005 Kristian Høgsberg <krh@redhat.com> 6.8.2-1.EL.13
- Rebuild 6.8.2-13 as 6.8.2-1.EL.13 for RHEL 4 security errata.

* Wed Mar 23 2005 Kristian Høgsberg <krh@redhat.com> 6.8.2-13
- Add XFree86-4.1.0-xpm-security-fix-CAN-2005-0605.patch (#150040).

* Wed Mar 16 2005 Soeren Sandmann <sandmann@redhat.com> 6.8.2-12
- Add xorg-x11-6.8.2-cursor-flicker.patch (#144022)
- Fix xorg-x11-6.8.2-XScreenSaverQueryInfo-crash-fix.patch so it will apply

* Tue Mar 15 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-11
- Added xorg-x11-6.8.2-config-StaticNeedsPicForShared.patch for (#108026)
- Removed StaticNeedsPicForShared from host.def section
- Added xorg-x11-6.8.2-XScreenSaverQueryInfo-crash-fix.patch to fix (#147890)

* Mon Mar 14 2005 Mike A. Harris <mharris@redhat.com>
- Search and destroy any CVS directories found in RPM_BUILD_DIR during rpm
  spec file build section prior to building.  This fixes a problem where the
  6.8.2 release was tarballed officially from a CVS checkout rather than a
  CVS export, causing the CVS metadata to be present, and some of it ends up
  getting installed in the final OS.

* Fri Mar 11 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.FC3.10test
- Rebuild 6.8.2-10 as 6.8.2-1.FC3.10test for Fedora Core 3 testing release

* Fri Mar 11 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-10
- Re-enable xorg-x11-6.8.2-xnest-shape-fix.patch which has been updated now
  for 6.8.2 by Mark McLoughlin (#148763,138482)

* Thu Mar 10 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-9
- Disable xorg-x11-6.8.2-xnest-shape-fix.patch added in 6.8.2-8, as it does
  not compile.

* Thu Mar 10 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.FC3.8test
- Rebuild 6.8.2-8 as 6.8.2-1.FC3.8test for Fedora Core 3 testing release

* Tue Mar  8 2005 Soeren Sandmann <sandmann@redhat.com> 6.8.2-8
- Add Patch9329: xorg-x11-6.8.2-xnest-shape-fix.patch (Patch by Mark
  McLoughlin). (#148763)

* Fri Mar  4 2005 Soeren Sandmann <sandmann@redhat.com> 6.8.2-7
- Added xorg-x11-6.8.2-fix-font-crash.patch to fix crash on fonts with NULL
  bits (#145546)

* Wed Mar  2 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.FC3.6test
- Rebuild 6.8.2-6 as 6.8.2-1.FC3.6test for Fedora Core 3 testing release

* Wed Mar  2 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-6
- Added xorg-x11-6.8.2-ati-radeon-gcc4-fix.patch to fix bug in radeon driver
  when building with gcc 4. (#150086)

* Tue Mar  1 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1.EL.5
- Rebuild 6.8.2-5 as 6.8.2-1.EL.5 for RHEL4

* Tue Mar  1 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-5
- Conditionalize the gcc4 patch for FC4 only for now.
- Disable FORTIFY_SOURCE on RHEL4/FC3 builds as it fails for some odd reason,
  yet it builds ok on FC4.
- Added xorg-x11-6.8.2-ati-radeon-disable-broken-renderaccel-by-default.patch
  to disable render acceleration by default in the "radeon" driver, as it is
  currently broken (#136065,136941,149907,143401,143234)

* Tue Mar  1 2005 Soeren Sandmann <sandmann@redhat.com> 6.8.2-4
- Fix somehow empty patch file

* Tue Mar  1 2005 Soeren Sandmann <sandmann@redhat.com> 6.8.2-3
- Add patch for gcc 4 build problem (#150042)

* Tue Mar  1 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-2
- Rebuild xorg-x11 with gcc 4 into FC4

* Thu Feb 10 2005 Mike A. Harris <mharris@redhat.com> 6.8.2-1
- Update main tarball to X.Org X11 6.8.2

* Tue Feb  8 2005 Mike A. Harris <mharris@redhat.com> 6.8.1.904-2
- [SECURITY] Added with_fortify_source option macro to spec file, to allow
  xorg-x11 to take partial advantage of the new gcc FORTIFY_SOURCE feature
  available in newer gcc releases.  This option is automatically enabled in
  FC4 builds by rpm by default via RPM_OPT_FLAGS, however while gcc in FC3
  and RHEL4 has this support also, it must be manually enabled in the spec
  file for it to get used.  "-D_FORTIFY_SOURCE=2" gets passed to gcc when
  this option is enabled.

* Fri Feb  4 2005 Mike A. Harris <mharris@redhat.com> 6.8.1.904-1
- Update main tarball to X.Org X11 6.8.1.904 (6.8.2 release candidate 4)
  via X.Org official tarball: xorg-x11-6.8.1.904.tar.gz
- Removed xorg-x11-6.8.1.903-nls-pt_BR.UTF-8-fix.patch, as it is integrated
  into 6.8.1.904 already.

* Fri Feb  4 2005 Mike A. Harris <mharris@redhat.com> 6.8.1.903-4
- Added new with_alternate_projectroot macro, which will eventually allow the
  parallel installation of multiple versions of xorg-x11 in rpm format without
  conflicting with each other (theoretically).  The feature is intended only
  for Red Hat X.Org developer usage, and will not be an officially supported
  installation method.  It is an incomplete experimental work in progress,
  and should not be used by mortals.  THIS WILL FRY YOUR SYSTEM, DO NOT USE
  IT.  :o)

* Wed Feb  2 2005 Soeren Sandmann <sandmann@redhat.com> 6.8.1.903-3
- Added patch to fix Composite gravity issue, recently added to xorg
  HEAD. (fdo#2230).

* Thu Jan 27 2005 Mike A. Harris <mharris@redhat.com> 6.8.1.903-2
- Added xorg-x11-6.8.1.903-nls-pt_BR.UTF-8-fix.patch from kem to fix broken
  pt_BR.UTF-8 support recently added to xorg cvs (fdo#2400)

* Thu Jan 27 2005 Mike A. Harris <mharris@redhat.com> 6.8.1.903-1
- Update main tarball to X.Org X11 6.8.1.903 (6.8.2 release candidate 3)
  via X.Org official tarball: xorg-x11-6.8.1.903.tar.gz
- Updated xorg-x11.6.8.1.903-AMD64-override-default-driverlist.patch as the
  "i810" is now included upstream by default, but not "vmware" for AMD64
- Removed the following patches, as they are integrated into CVS now:
    xorg-x11-6.8.1.902-xf86pcibus-PCIX-bar-64bit-fix.patch
- Added {_x11localedir}/pt_BR.UTF-8/* to file list to pick up new i18n files

* Thu Jan 27 2005 Mike A. Harris <mharris@redhat.com> 6.8.1.902-7
- Renamed build_maintainer macro to build_mharris as it is actually a personal
  macro and there are actually several developers maintaining the rpm for
  quite some time now.  In case anyone is curious, I use it to tweak the spec
  file on occasion to build on a customized OS install that does not quite
  match any of our supported OS configurations.  ;o)
- Added a %%check section to the spec file, to put post build/install sanity
  checks in place.
- Added new post-build sanity check "with_undef_sym_test", did a local test
  build to confirm it works correctly, fixed a few things, then disabled it
  by default because Xorg needs a lot of love in order for this to be default.

* Wed Jan 26 2005 Mike A. Harris <mharris@redhat.com> 6.8.1.902-6
- Added xorg-x11-6.8.1.902-lnxLib-tmpl-sharedlibreq-fixes.patch to fix
  many missing library dependancies in lnxLib.tmpl, detected by examining
  the build log of a "with_bail_on_undef_syms" build.
- Disabled with_bail_on_undef_syms, after determining that there is a bit of
  work that needs to be done upstream first in order for us to expect X to
  fully build with these linker options.

* Mon Jan 24 2005 Mike A. Harris <mharris@redhat.com> 6.8.1.902-5
- Removed dead unused i810 update patch.
- Enabled with_bail_on_undef_syms, to do a test build.

* Fri Jan 21 2005 Mike A. Harris <mharris@redhat.com> 6.8.1.902-4
- Renamed the xorg-x11-6.8.0-AMD64-enable-i810-driver.patch patch to
  xorg-x11-6.8.0-AMD64-override-default-driverlist.patch and added the "vmware"
  driver to the default list of drivers to be build on AMD64. (#145588)

* Thu Jan 20 2005 Mike A. Harris <mharris@redhat.com> 6.8.1.902-3
- Added xorg-x11-6.8.1.902-xf86pcibus-PCIX-bar-64bit-fix.patch to attempt to
  fix bugs (#140601, 143910)

* Mon Jan 17 2005 Mike A. Harris <mharris@redhat.com> 6.8.1.902-2
- Added xorg-x11-6.8.1.902-ia64-hp-zx2-support-bug-119364.patch to add support
  for new Hewlett Packard IA64 ZX2 chipset. (#119364)

* Thu Jan 13 2005 Mike A. Harris <mharris@redhat.com> 6.8.1.902-1
- Update main tarball to X.Org X11 6.8.1.902 (6.8.2 release candidate 2)
  via X.Org official tarball: xorg-x11-6.8.1.902.tar.gz

* Sat Dec 18 2004 Mike A. Harris <mharris@redhat.com> 6.8.1.901-1
- Update main tarball to X.Org X11 6.8.1.901 (6.8.2 release candidate 1)
  via CVS export of CVS tag XORG-6_8_1_901
- Removed the following patches, as they are integrated into CVS now:
    xorg-x11-6.8.1-ati-radeon-segv-130888.patch
    xorg-x11-6.8.1-ati-radeon-panel-timing-param-init-130888.patch
    xorg-x11-6.8.0-ia64-460gx-pci-typo.patch
    xorg-x11-6.8.1-ati-radeon-mobility-display-detection-fix2.patch
    xorg-x11-6.8.1-ati-radeon-dynamic-clocks-fix.patch
    xorg-x11-6.8.1-libX11-stack-overflow.patch
    xorg-x11-6.8.1-vidmode-change-verbosity.patch
    xorg-x11-6.8.1-disable-dri-option.patch
    xorg-x11-6.8.1-xmodmap-overflows.patch
    xorg-x11-6.8.1-xpm-security-fixes-CAN-2004-0914.patch
    xorg-x11-6.8.1-xpm-security-fixes-CAN-2004-0914-sec8-ammendment.patch
    xorg-x11-6.8.1-r128-logout-deadlock.patch
    xorg-x11-6.8.1-add-missing-lucidatypewriter-font.patch
- Disabled xorg-x11-6.8.1-i810-update.patch, but left it present, as only some
  hunks fail to apply.  This leads me to believe perhaps 6.8.2 has only part of
  the i810 CVS head code.  We need to explore this a bit before dropping the
  patch altogether.

* Sat Dec 18 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-25
- Tag CVS head of latest changes, to update to 6.8.2rc1 (6.8.1.901) for the
  next commit

* Mon Dec 13 2004 Kristian Høgsberg <krh@redhat.com>
- Rename xorg-x11.conf to xorg-x11-%{_arch}.conf so it works on
  multilib systems.

* Mon Dec 13 2004 Kristian Høgsberg <krh@redhat.com> 6.8.1-24
- Bump version.

* Sun Dec 12 2004 Kristian Høgsberg <krh@redhat.com>
- Drop xorg-libICE-remove-bogus-delay.patch as this was resolved in
  6.8.0 (https://bugs.freedesktop.org/show_bug.cgi?id=306)
- Drop XFree86-4.3.0-Xserver-xf86PciInfo-updates.patch, most of these
  #define's are present in the latest Xorg release.
- XFree86-4.3.0-redhat-xlib-linux-fix-avoiding-substance-abuse-job.patch
  is no longer needed since the unwanted code is only enabled when __sparcv9
  is defined.
- Remove XFree86-4.2.0-xtermresources.patch from cvs.
- Use /etc/ld.so.conf.d/xorg-x11.conf instead of editing
  /etc/ld.so.conf in %post (#124077).
- Remove XFree86-4.3.0-Xserver-dix-xkb-key-repeating-bug-CVS-backport.patch
  since the problem is now fixed upstream.
- Remove XFree86-4.3.0-xcursorgen-check-malloc-return.patch since it
  would only make xcursorgen fail differently in case of OOM.

* Thu Dec  9 2004 Soeren Sandmann <sandmann@redhat.com> 6.8.1-22.EL
- Better patch to Disable DRI on Radeon, workaround for bug #138348 .

* Thu Dec  9 2004 Soeren Sandmann <sandmann@redhat.com>
- Add disabled-by-default "dri" option to radeon driver.

* Mon Dec  6 2004 Mike A. Harris <mharris@redhat.com>
- Added "Obsoletes XFree86-ISO8859-2-Type1-fonts, fonts-ISO8859-2-Type1" to
  base-fonts subpackage, so that these ancient buggy font rpms get forcibly
  removed on OS upgrades from older OS releases that contained them.  We
  removed these fonts because they are very buggy among other reasons, however
  they do not get removed on upgrade without flagging them Obsoleted, which
  causes some problems when people use the buggy fonts in applications (#129523)

* Fri Dec  3 2004 Kristian Høgsberg <krh@redhat.com>
- Remove XFree86-4.3.0-Xserver-dix-xkb-key-repeating-bug-CVS-backport.patch
  since the problem is now fixed upstream.
- Remove XFree86-4.3.0-xcursorgen-check-malloc-return.patch since it
  would only make xcursorgen fail differently in case of OOM.

* Wed Dec  1 2004 Kristian Høgsberg <krh@redhat.com> 6.8.1-22
- Update xorg-x11-6.8.1-battle-libc-wrapper.patch to not break when
  some module also includes stdio.h.

* Tue Nov 30 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-21.EL
- Build 6.8.1-21 using build_fc3 target as 6.8.1-12.FC3.21 for FC3

* Tue Nov 30 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-21
- Added xorg-x11-6.8.1-ati-radeon-dynamic-clocks-fix.patch which now replaces
  xorg-x11-6.8.1-ati-radeon-7000-smp-lockup.patch as a fix for a lockup
  problem that occurs on some models of Radeon on SMP systems, related to the
  dynamic clocks code.  Fixes bugs: (#138108, 138348, 133526, 138539, 138779,
  fdo#1912)
- Merge to FC-3 branch and tag as 6.8.1-12.FC3.21, and to RHEL-4 branch and
  tag as 6.8.1-21.EL

* Mon Nov 29 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-20
- Disabled with_fonts again
- Added xorg-x11-6.8.1-xpm-security-fixes-CAN-2004-0914-sec8-ammendment.patch
  to fix bugs introduced into libXpm in the previous security patch for
  CAN-2004-0914 which cause gimp to fail to save Xpm files (#140815, 141047,
  fdo#1924)

* Mon Nov 29 2004 Kristian Høgsberg <krh@redhat.com>
- Update xorg-x11-6.8.1-ati-radeon-7000-smp-lockup.patch to the new
  patch from Alex Deucher <agd5f@yahoo.com>, provided in
  https://bugs.freedesktop.org/show_bug.cgi?id=1912.

* Tue Nov 23 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-19.with_fonts.0
- Enabled with_fonts for a single build, to update fonts-xorg package

* Tue Nov 23 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-19
- Updated a few patches to apply with -p0 for consistency
- Reordered some patches by patch number
- Change libI810XvMC inclusion to be ifarch ix86/ia64/x86_64 only, since we
  know Intel video exists on those arches.  This is better than excluding it
  on arches we know it is not available on, because the list is shorter this
  way, and exact.  Less maintenance this way.

* Tue Nov 23 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-18
- Remove libI810XvMC from PPC, as there is no Intel video hardware available
  for PPC architecture and this is an Intel video specific client side lib.
- Added xorg-x11-6.8.1-r128-logout-deadlock.patch to fix lockup on logout
  bug on Rage128 with DRI (#138822)
- Added xorg-x11-6.8.1-add-missing-lucidatypewriter-font.patch from upstream
  to fix bug with fonts that got inadvertently excluded from the X11 6.8.1
  release.  Our fonts-xorg package is being updated to include these additional
  fonts now as well (#139108, 139121, fdo#1560)
- Enable xorg-x11-6.8.1-i810-update.patch for all OS version builds now.

* Tue Nov 23 2004 Kristian Høgsberg <krh@redhat.com> 6.8.1-17
- Add libI810XvMC back on PPC filelists.
- Move xorg-x11-6.8.1-battle-libc-wrapper.patch into fc4_build section.

* Tue Nov 23 2004 Kristian Høgsberg <krh@redhat.com> 6.8.1-16
- Add xorg-x11-6.8.1-battle-libc-wrapper.patch to work around build
  error that pops up when system headers #define printf.

* Mon Nov 22 2004 Kristian Høgsberg <krh@redhat.com> 6.8.1-15
- Added xorg-x11-6.8.1-ati-radeon-7000-smp-lockup.patch to fix the
  hard lockup happening on SMP boxes with Radeon 7000 cards (#138108).

* Thu Nov 18 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-14
- Added xorg-x11-6.8.1-nls-indic-locales.patch to add support for some indic
  locales.  BLOCKER (#133880)
- Minor fix in application of vidmode verbosity patch
- Added build_fc4 and build_rhel4 spec file build targets
- Enabled DRI for PPC only on FC2/FC3/FC4 builds for Fedora/PPC users.
- Conditionalized i810-update patch to only apply for build_fc4 as it is
  currently experimental.

* Thu Nov 18 2004 Kristian Høgsberg <krh@redhat.com>
- Add xorg-x11-6.8.1-i810-update.patch which contain fixes for i810
  chipsets backported from CVS HEAD as of November 16th (#132267).

* Mon Nov 15 2004 Kristian Høgsberg <krh@redhat.com> 6.8.1-13
- Added xorg-x11-6.8.1-xpm-security-fixes-CAN-2004-0914.patch to fix a
  number of Xpm issues found by Thomas Biege <thomas@suse.de>
  (#136169)

* Fri Nov 12 2004 Kristian Høgsberg <krh@redhat.com>
- Remove xorg-x11-6.8.1-ati-radeon-mobility-display-detection-fix.patch
  since it has been replaced with the -fix2 patch, remove
  XFree86-4.3.0-redhat-version-change-detection.patch since it doesn't
  work for Xorg.
- Remove XFree86-4.3.0-remove-copyright-symbol-to-fix-UTF-8.patch
  since it is now fixed upstream.

* Thu Nov 11 2004 Kristian Høgsberg <krh@redhat.com>
- Drop XFree86-4.3.0-Xserver-common-fix-broken-MIN-macro-definition.patch
  since it's harmless and it's fixed in Xorg HEAD now.
- Removed commented out xbiff, xeyes and xditview files from file
  lists, they are in CVS if we need them.
- Updated xorg-x11-tools description so it doesn't advertise stuff it
  doesn't contain (xbiff and xeyes).
- Drop XFree86-4.3.0-xbiff-file-heirarchy-standard.patch as we don't
  ship xbiff.
- Drop XFree86-4.2.0-xtermresources.patch as we don't ship in tree
  xterm anymore.
- Drop XFree86-4.3.0-redhat-lock-version.patch as Xorg don't print
  scary warnings for betas.

* Wed Nov 10 2004 Kristian Høgsberg <krh@redhat.com> 
- Edit xorg-x11-6.8.1-xmodmap-overflows.patch to fix buffer overflow
  crash (#138743).

* Wed Oct 20 2004 Kristian Høgsberg <krh@redhat.com> 6.8.1-12
- Add NULL check in xorg-x11-6.8.1-init-origins-fix.patch to prevent
  crashes on single head setups.

* Tue Oct 19 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-11
- Added xorg-x11-6.8.1-ati-radeon-mobility-display-detection-fix2.patch to fix
  ATI Radeon Mobility display detection issue. (#132865, 133147, and upstream
  bugs: (fdo #1599, 1301, 1303, 1374, 1482, 1514, 1622, and 1631, and numerous
  others not on our lists))

* Tue Oct 19 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-10
- Set with_fonts based off build_fc2 macro, so it is enabled for FC2 builds
  but remains disabled for FC3 and other builds.  Makes it easier to rebuild
  for FC2/FC1.
- Fix to make Vera font really get deleted this time for real. ;o)
* Mon Oct 18 2004  <krh@redhat.com> 6.8.1-9
- Add xorg-x11-6.8.1-init-origins-fix.patch, which fixes a crash for
  some invalid xorg.conf combinations (#134967).

* Mon Oct 18 2004 Mike A. Harris <mharris@redhat.com>
- Do not include the Bitstream Vera fonts when doing builds with with_fonts
  enabled, as we ship Vera in separate packaging already.
- When doing with_fonts builds to generate the fonts-xorg tarball, remove
  various Syriac fonts which contain bad codepoints:  SyrCOMCtesiphon.otf
  SyrCOMKharput.otf, SyrCOMMalankara.otf, SyrCOMMidyat.otf, SyrCOMQenNeshrin.otf
  SyrCOMTurAbdin.otf, SyrCOMUrhoyBold.otf, SyrCOMUrhoy.otf (bug #97951)

* Mon Oct 18 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-8
- Added xorg-x11-6.8.1-ati-radeon-segv-130888.patch from Kevin Martin to fix
  linked list related SEGV for bug (#130888)
- Added xorg-x11-6.8.1-ati-radeon-panel-timing-param-init-130888.patch by
  Kevin Martin to fix panel timing issue in Radeon driver (#130888)

* Thu Oct 14 2004 Soren Sandmann <sandmann@redhat.com> 6.8.1-7
- Add xorg-x11-6.8.1-xmodmap-overflows.patch (#83720, #103161).

* Tue Oct 12 2004  <krh@redhat.com> 6.8.1-6
- Add xorg-x11-6.8.1-disable-dri-option.patch, which adds XF86Free-DRI
  to the list of extensions that can be disabled using the -extension
  command line switch (#135071).

* Wed Oct  6 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-5
- Added xorg-x11-6.8.1-vidmode-change-verbosity.patch which changes the
  default verbosity level of Xvidmode extension debugging log messages in
  the X server from "1" to "> DEFAULT_XF86VIDMODE_VERBOSITY" which is set
  to 3.  This fixes a power consumption problem on laptops running on battery
  power, where when a screensaver kicks in and calls xf86GetVidMode(), the
  X server generates excessive log messages which cause the hard disk to spin
  up if it was in powersave mode, thus reducing the battery life.  Since the
  currently logged messages are pretty useless generally speaking, this fixes
  the problem by increasing the verbosity level required before the messages
  end up in the log file. (#128305)

* Tue Oct  5 2004 Mike A. Harris <mharris@redhat.com>
- Added post/postun scripts to the deprecated-libs subpackage, copied versions
  of those in the libs subpackage (#134424)

* Fri Sep 24 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-4
- Implemented xorg-x11-6.8.1-libX11-stack-overflow.patch to fix stack
  overflow in libX11 which was discovered by new security features of
  gcc4 (#132885)

* Mon Sep 20 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-3
- Bump to 6.8.1 and rebuild to quell beehive complaining
- Disable "parallel_build", as it is still broken

* Mon Sep 20 2004 Mike A. Harris <mharris@redhat.com> 6.8.1-2
- Update main tarball to the final X.Org X11 6.8.1 release via CVS export of
  CVS tag XORG-6_8_1 - this obsoletes previous 6.8.1 tarball which was a
  upstream release mixup.
- Added xorg-x11-6.8.0-libXdmcp-build-with-PIC.patch to make libXdmcp.a
  build with PIC flags to fix (#131130)
- Fixed changelog dates and made changelog version-release strings
  consistent
- Re-enable "parallel_build 1" to test if it works currently, so we can take
  advantage of SMP machines better

* Wed Sep 15 2004 Kristian Høgsberg <krh@redhat.com> 6.8.1-1
- Update to xorg 6.8.1
- Change Source: to use xorg-%{version}.%{zipext} since that is what
  the tarball from http://freedesktop.org/~xorg/X11R6.8.1/src/single/
  is called.

* Tue Sep 14 2004 Mike A. Harris <mharris@redhat.com> 6.8.0-5
- Enable "#define HasDevRandom YES" in host-$arch.def for bug (#126205)
- Remove "Requires: %{name}, %{name}-libs = %{version}-%{release}" from twm
  subpackage, as the libs twm is linked to should automatically be picked up
  by rpm "find-provides", and xterm moved to a separate package a long time
  ago, so both of these should no longer be needed. (#123423)
- Added xorg-x11-6.8.0-ia64-460gx-pci-typo.patch to fix typo in Intel 460gx
  PCI handling code on ia64. (#126586)
- Remove "XtermWithI18N" from host.def as we build xterm externally
- Added SElinux fix to xfs initscript (#130421,130969)

* Tue Sep 14 2004 Bill Nottingham <notting@redhat.com> 6.8.0-4
- buildrequire redhat-rpm-config, use brp-compress from that (fixes file conflicts)

* Mon Sep 13 2004 Kristian Høgsberg <krh@redhat.com> 6.8.0-3
- Fix typo in test for xorg.conf (#127711).

* Mon Sep 13 2004 Kristian Høgsberg <krh@redhat.com> 6.8.0-2
- Add with_wacom_driver option and set it to 0 (#132438, #132440).

* Thu Sep  9 2004 Mike A. Harris <mharris@redhat.com> 6.8.0-1
- Update main tarball to the final X.Org X11 6.8.0 release via CVS export of
  CVS tag XORG-6_8_0
- Add "BuildXaw NO" to host-$arch.def to disable building of libXaw 8 library
- Add "XtransFailSoft YES" to host-$arch.def to fix (#129622)
- Moved "archexec" script from main xorg-x11 subpackage to xorg-x11-devel
  subpackage since it is only used by things in the devel subpackage and we
  do not want to have the devel subpackage have a forced dependancy on the
  main package.  (#132121)
- Added "Conflicts: xorg-x11 < 6.8.0-1" to xorg-x11-devel for archexec
  subpackage move, so upgrades work correctly
- Removed libXaw.a from file list, as 6.8.0 no longer builds static libXaw 7
  even when libXaw 8 is disabled by "BuildXaw NO"
- Rework the _x11localedir file lists to fix rpm build problems

* Mon Sep  6 2004 Mike A. Harris <mharris@redhat.com>
- Remove various Syriac fonts which contain bad codepoints:  SyrCOMCtesiphon.otf
  SyrCOMKharput.otf, SyrCOMMalankara.otf, SyrCOMMidyat.otf, SyrCOMQenNeshrin.otf
  SyrCOMTurAbdin.otf, SyrCOMUrhoyBold.otf, SyrCOMUrhoy.otf (bug #97951)

* Fri Sep  3 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.903-6
- Remove hard coded dependancy on Glide3 from xorg-x11 package, as the tdfx
  DRI driver has used dlopen() with Glide3 since XFree86 4.2.1 or so, and no
  longer has a build time or runtime dependancy on Glide3 being present.  If
  Glide3 is present, DRI will work (theoretically), but if it is not present,
  the tdfx driver should still function correctly, so we can get rid of this
  dependancy now, as we are removing Glide3 from some of our OS products.

* Thu Sep  2 2004 Bill Nottingham <notting@redhat.com> 6.7.99.903-5
- bump release again

* Tue Aug 31 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.903-4
- Bump release field and rebuild unmodified to handle an off-by-one error
  in release field of font-utils subpackage dependancy

* Tue Aug 31 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.903-3
- Enable "#define HasDevRandom YES" in host-$arch.def for bug (#126205)
- Remove driver list overrides for all architectures except ia64, as ppc was
  missing the "nv" driver.  In the future, we will use patches to the Imake
  config directory to disable individual drivers on particular architectures.
- Disable building of fonts by setting with_fonts 0, as we now provide the
  fonts from a separate src.rpm which builds noarch packages, so that we no
  longer regenerate fonts every single X build, and people do not have to 
  redownload fonts every single xorg-x11 update when the fonts never change
  anyway.
- Added xorg-x11-6.8.0-Imake-add-BuildFontDevelUtils-macro.patch to allow
  building and inclusion of ucs2any and bdftruncate when doing "with_fonts 0"
  builds, as "BuildFonts NO" causes these utils to be excluded.
- Change main package dependancy from xorg-x11-base-fonts to base-fonts which
  is a virtual provide in both the xorg-x11-base-fonts and fonts-xorg-base
  packages now, to maximize install/upgrade compatibility.
- Moved "ucs2any" from the xorg-x11-tools subpackage to the font-utils
  subpackage where it belongs, and added a Conflicts line to the font-utils
  package to handle upgrades.
- Moved "fonts/util" subdir from xorg-x11-base-fonts, to font-utils package,
  as the utilities that use it reside there, and it never made sense in the
  base-fonts package anyway really.  Added Conflicts line to font-utils to
  handle upgrades.

* Tue Aug 31 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.903-2
- Remove "xtt" module line from config file on upgrades, as X.Org no longer
  supplies that module, since the "freetype" module now includes the
  functionality that was only available in the "xtt" module before.

* Sat Aug 29 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.903-1
- Update main tarball to CVS export of CVS tag XORG-6_7_99_903 snapshot,
  a.k.a. 6.8.0 RC3
- Added "xmessage" back upon request (#131076)
- Updated file list to change libXevie.so.1.0.0 to libXevie.so.1.0 due to
  upstream .so versioning change.

* Wed Aug 25 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.902-8
- Add defattr flag to Xdmx subpackage (#130870)

* Tue Aug 24 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.902-7
- Added new rpm macro 'with_libs_data' to Conditionalize the libs-data
  subpackage.  This allows us to disable the "libs-data" subpackage now, as
  rpm multilib should properly handle both architectures sanely, so the
  workaround of having the library data in a separate package is no longer
  needed.  By setting 'with_libs_data' to 0, it will cause the libs-data files
  to be included in the "libs" subpackage as it was in the past, and the
  "libs-data" package will get obsoleted.  This will simplify the rpm
  packaging a slight bit for the future.

* Sun Aug 22 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.902-6
- Remove a bunch of legacy Xaw/Xt applications which really should not be
  part of X11 sources (xbiff,xditview,xeyes,xmessage)

* Sat Aug 21 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.902-5
- Update archexec with additional cleanups, and make host.def match the
  version of host.def backported to XFree86 4.3.0 for RHEL3-U3, to maximize
  upgrade compatibility.

* Sat Aug 21 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.902-4
- Added "archexec" script as a generic solution to the xft-config/gccmakedep
  problem.
- Renamed xft-config and gccmakedep to <name>-<arch>, and added symlinks from
  archexec to <name>, so these two files do not conflict when installed on
  multilib systems.

* Fri Aug 20 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.902-3
- Install the host-<arch>.def file where host.def gets installed.

* Fri Aug 20 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.902-2
- Initial attempt to make host.def architecture neutral, and split the
  architecture specific things onto host-<arch>.def specific files, to allow
  multiple xorg-devel packages to be installed on multilib systems, such as
  x86_64, ppc64, and s390x.

* Wed Aug 18 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.902-1
- Update main tarball to CVS export of CVS tag XORG-6_7_99_902 snapshot,
  a.k.a. 6.8.0 RC2
- Removed patches that are now included in upstream sources:
  - xorg-x11-6.8.0-glx-install-dri-modules-in-correct-place.patch

* Mon Aug 16 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.901-2
- Set "BuildXprint NO" "BuildXprintClients NO" "BuildXprintLib YES" so we get
  *only* the Xprint libraries for backward compatibility with existing
  dynamically linked applications.
- Added new "xorg-x11-deprecated-libs", and moved the Xprint runtimes to it
  for backward compatibility for now, until we remove libXp entirely at some
  point in the future.
- Replaced remaining spec file package description references of "XFree86" to
  something X11 implementation neutral.
- Exclude the two new Xprint libraries libXprintAppUtil.a, libXprintUtil.a
  as we do not ship anything that links to them, so do not need them for
  back compat.

* Mon Aug 16 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.901-1
- Update main tarball to CVS export of CVS tag XORG-6_7_99_901 snapshot,
  a.k.a. 6.8.0 RC1
- Removed patches that are now included in upstream sources:
  - xorg-x11-6.7.0-mga-storm-sync-fix.patch
  - xorg-x11-6.8.0-ppc64-XorgServer-not-XF86Server-fix.patch
- Update xorg-x11-6.8.0-redhat-custom-startup.patch due to Imakefile change
- Disabled xorg-6.8.0-redhat-libGL-exec-shield-fixes.patch for now, as Xorg
  changes have broken it again and I do not want to port it forward 10 times.
  Once 6.8.0 is finalized, we will port it forward to Mesa CVS and get it
  into the Mesa CVS head *first*, then we will backport it to 6.8.0.  This
  way we do not have to maintain and port this patch once a week.
- Removed unwanted xprint file deletion from specfile as "BuildXprint NO"
  actually works now.
- Added Xevie libraries to file lists.

* Thu Aug 12 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.2-5
- Remove unneeded pre-build of ucs2any.c as it is now part of xorg stock
- Various minor cleanups to specfile
- Remove 'restest' Xresource extension sample client, as we now have 'xrestop'
  which is way better.
- Update xorg-x11-6.8.0-glx-install-dri-modules-in-correct-place.patch to use
  MODULEDIR instead of BUILDMODULEDIR (fdo #1057)

* Thu Aug 12 2004 Jeremy Katz <katzj@redhat.com> - 6.7.99.2-4
- Nuke libXp.a as it is unneeded (libXp got enabled for libXaw)

* Thu Aug 12 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.2-3
- Added xorg-6.8.0-glx-install-dri-modules-in-correct-place.patch to correct
  the location where dri modules get installed on lib64 arches (#129668)
- Enable libXp.so.* temporarily as libXaw is cancerously attached to it

* Thu Aug 12 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.2-2
- Added code to the rpm pre script to munge the config file to change the
  "keyboard" driver to "kbd" driver on upgrades, as XOrg no longer supports
  the old "keyboard" driver.
- Use perl -p -i -e in pre rpm script for all config file munging instead of
  grep and temporary files.

* Wed Aug 11 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.2-1
- Update main tarball to CVS export of CVS tag XORG-6_7_99_2 snapshot
- Removed patches that are now included in upstream sources:
  - xorg-x11-6.8.0-ppc64-support-updates.patch
  - xorg-x11-6.8.0-fix-xprint-install.patch
  - xorg-x11-6.8.0-build-fix-for-non-dri-builds.patch
- Remove /etc/init.d/xprint, as we do not ship/support Xprint
- Set "#define BuildXprint NO" in host.def
- Add xorg-x11-6.8.0-fix-BuildXprint.patch to fix "BuildXprint NO"
- Add xorg-x11-6.8.0-ppc64-XorgServer-not-XF86Server-fix.patch to fix ppc64
  build issue due to upstream renaming of XF86Server to XorgServer
- Added "XorgServer NO" to host.def for non-server builds

* Tue Aug 10 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.1-1
- Update main tarball to CVS export of CVS tag XORG-6_7_99_1 snapshot
- Removed patches that are now included in upstream sources:
  - xorg-x11-6.7.0-xkb-sysreq.patch
  - xorg-x11-6.7.0-mga-enable-video-rom-before-using.patch
  - xorg-x11-6.7.0-xset-man-update.patch
  - xorg-libX11-zh_CN.UTF8-crash-fix.patch
  - xorg-x11-6.8.0-i810-remove-stale-sdk-header.patch
- Update xorg-x11-6.8.0-redhat-custom-startup.patch due to Imakefile change
- Fix glitch in macro that disables DRI on ppc builds for fc3/rhel4
- Implemented xorg-x11-6.8.0-build-fix-for-non-dri-builds.patch patch to fix
  a compile time bug in the Radeon driver render acceleration on non-DRI
  builds, where the driver tests if CPStarted is set before calling
  RADEONInit3DEngineForRender(), however CPStarted is not available in
  non-DRI builds.  Also, RADEONInit3DEngineForRender() already correctly
  handles both the DRI and non-DRI cases both at compile and runtime, and
  checks if CPStarted is set internally.  (xorg #1033)

* Sat Aug  7 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.0-0.2004_08_05.1
- Delete various X server driver manpages on ppc64 s390, s390x which are
  showing up now for some odd reason, even when servers are not being built.
- Do not include libI810XvMC on ppc/ppc64/s390/s390x filelists

* Thu Aug  5 2004 Mike A. Harris <mharris@redhat.com> 6.7.99.0-0.2004_08_05.0
- Updated to X.Org X11 CVS development and branched specfile.  Chose arbitrary
  version number of "6.7.99.0" as XOrg confusingly calls development builds
  "6.7.0" still, and we need differentiation for sanity.  Kevin mentioned he
  would tag 6.7.99.1 in CVS once the final version 6.8.0 is approved by the
  XOrg BOD, so everything should work out ok version-wise.
- Removed patches already included in new upstream snapshot:
  - xorg-x11-6.7.0-ati-driver-message-cleanups.patch
  - xorg-x11-6.7.0-ati-radeon-pagesize.patch
  - xorg-x11-6.7.0-ati-radeon-7000m-dell-server.patch
  - xorg-x11-6.7.0-siliconmotion-fboffset-fix-from-cvs-head.patch
  - xorg-double-cast.patch
  - XFree86-4.3.0-build-libXinerama-before-libGL-for-via-driver.patch
  - xorg-use-linux-pci-only.patch
  - xorg-x11-6.7.0-allow-XF86ExtraCardDrivers-on-AMD64.patch
  - xorg-r200-uninitialized-variable-used.patch
- Disabled ati-radeon-forcelegacycrt and xorg-x11-6.7.0-xterm-make-optional
  patches, as they need porting forward and are very low priority
- Removed voodoo driver tarballs, as a newer version of the driver is now
  included in stock Xorg
- Update xorg-x11-6.8.0-Xserver-increase-max-pci-devices.patch for 6.8.0,
  as the upstream default changed from 64 to 128, but we want it to be 256.
- Update xorg-x11-6.8.0-AMD64-enable-i810-driver.patch for 6.8.0, as upstream
  currently still does not enable the i810 driver on AMD64 arch for some
  reason.
- Update xorg-x11-6.7.0-ppc64-support-updates.patch for 6.8.0
- Updated xorg-6.8.0-redhat-libGL-exec-shield-fixes.patch for 6.8.0
- Commented out the codeconv dir - no longer present
- Commented libXfontcache out of file lists, no longer present
- Added new libraries to file lists: libXcomposite, libXdamage, libXfixes,
- Added pkg-config files xcomposite.pc, xdamage.pc, xfixes.pc, xrender.pc
- Added all of the new Xprint junk to the xprint exclusion list
- Created new xorg-x11-Xdmx subpackage to contain all of the DMX related files
  required to run DMX.
- Removed with_via_driver option as it is no longer needed
- Removed "WORLDOPTS=" from make World invocation as upstream defaults to
  this now for some time.
- Added xorg-x11-6.8.0-i810-remove-stale-sdk-header.patch as workaround for
  header file inclusion problem (Kristian Hogsberg, fdo-bz #995)
- Added xorg-x11-6.8.0-fix-xprint-install.patch (Kristian Hogsberg)

* Thu Aug  5 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-7.2
- Disabled XFree86-4.3.0-ia64-new-elfloader-relocations.patch as it fails the
  build on ia64.

* Thu Jul 15 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-7.1
- Disabled XFree86-4.2.99.901-chips-default-to-noaccel-on-69000.patch and
  XFree86-4.2.99.901-chips-default-to-swcursor-on-65550.patch for the time
  being at least in order to see if anyone still reports the problem, in
  which case we can narrow down the bad primative, report upstream with
  workaround patch that disables accel.  (#82438)
- Removed XFree86-4.0.1-nohardware.patch as it is ancient, undocumented, and
  probably not needed anymore.
- Removed unnecessary or no longer needed patches, including:
  - XFree86-4.3.0-ati-r128-chip-names-touchup.patch
  - XFree86-4.3.0-nls-cjk-utf8.patch, XFree86-4.0-xdm-servonly.patch
  - XFree86-4.2.99.4-x86_64-glx-nopic.patch
  - XFree86-4.3.0-xterm-can-2003-0063.patch
  - XFree86-4.3.0-SDK-add-missing-includes-for-synaptics.patch
  
* Thu Jul  8 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-7
- Updated and renamed following patches from XFree86-* to xorg-x11-* while
  cleaning up and documenting them for submission upstream:
  - xorg-x11-6.7.0-xset-man-update.patch
  - xorg-x11-6.7.0-xkb-sysreq.patch
  - xorg-x11-6.7.0-ati-driver-message-cleanups.patch
  - xorg-x11-6.7.0-ati-radeon-pagesize.patch
  - xorg-x11-6.7.0-ati-radeon-forcelegacycrt.patch
- Removed patches that are tested and confirmed to be no longer needed:
  - xorg-x11-6.7.0-cpp-s390x.patch
  - XFree86-4.2.99.3-locale-alias-gb18030.patch
  - XFree86-4.3.0-nls-compose-en_US.UTF8-lxo.patch
  - XFree86-4.3.0-ati-ia64-no-nonpci-ioport-access.patch
  - XFree86-4.3.0-ia64-slowbcopy.patch
  - XFree86-4.3.0-ia64-slowbcopy2.patch
- Disabled the sis DRI driver using with_sis_dri macro, as it is currently too
  experimental (#126821)
- Added xorg-x11-6.7.0-siliconmotion-fboffset-fix-from-cvs-head.patch taken
  from X.Org CVS head to try and fix bug (#127278)
  
* Thu Jul  8 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-6.2
- Test build with xorg-x11-6.7.0-cpp-s390x.patch disabled

* Thu Jul  8 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-6.1
- Updated and renamed following patches from XFree86-* to xorg-x11-* while
  cleaning up and documenting them for submission upstream:
  - xorg-x11-6.7.0-mga-enable-video-rom-before-using.patch
- Removed patches that are tested and confirmed to be no longer needed:
  - XFree86-4.3.0-r128-unresolved-symbols.patch
  - XFree86-4.3.0-ati-r128-Xv-ecp-divisor.patch
  - XFree86-4.3.0-gb18030-20020207.patch
  - XFree86-4.3.0-gb18030-xtt.patch, XFree86-4.3.0-gb18030-enc.patch
  - XFree86-4.3.0-nv-riva-dualhead-fixes.patch
  - XFree86-4.3.0-siliconmotion-Xv-stability-fix.patch
  - XFree86-4.2.99.901-007_fix_xfree86_man_version_string.patch
  - XFree86-4.2.99.901-008_doc_extensions_fix.patch
  - XFree86-4.3.0-Xserver-includes-ansify-prototypes.patch
  - XFree86-4.3.0-missing-SharedXfooReqs.patch
  - XFree86-4.3.0-libXrandr-missing-sharedreqs.patch
  - XFree86-4.3.0-libXpm-missing-sharedreqs.patch
  - XFree86-4.3.0-missing-lib-sharedreqs.patch
  - XFree86-4.3.0-Mesa-SSE-fixes-from-MesaCVS-v2.patch

* Sun Jul  4 2004 Mike A. Harris <mharris@redhat.com>
- Remove temporary config file left over after upgrade (#127187)
- Add libGL-devel and libGLU-devel virtual provides to xorg-x11-devel
  subpackage.  Both are provided for the major library version (1 in both
  cases), and for the major.minor (1.2 for libGL, 1.3 for libGLU).  This is
  being added to allow 3rd party packagers to add BuildRequires in an agnostic
  manner for apps that use libGL/libGLU, which allows any libGL/libGLU
  implementation devel package to be installed and meet the dependancy, as
  long as it also provides the same virtual provide mechanism.

* Wed Jun 30 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-6
- Added xorg-x11-6.7.0-AMD64-enable-i810-driver.patch to patch the i810
  driver into the default driver list instead (#126687)

* Wed Jun 30 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-5.1
- Enabled XF86ExtraCardDrivers on x86_64, and added i810 driver to it, to
  implement feature request from Intel (#126687)
- Added xorg-x11-6.7.0-Xserver-increase-max-pci-devices.patch to Increase
  the maximum number of PCI devices the X server scans, by changing the
  compiled in constant MAX_PCI_DEVICES from 64 to 256, as a lot of newer
  x86, ia64, ppc, ppc64, AMD64 hardware exists which may have more than 64
  devices. (#126164)  

* Fri Jun 25 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-5
- Fixed bug in mga driver which caused hangs on some Matrox Mystique boards
  of revision 0->2, which were caused by a previous upstream bugfix for
  another issue.  xorg-x11-6.7.0-mga-storm-sync-fix.patch (#124028)
- Added xorg-x11-6.7.0-ati-radeon-7000m-dell-server.patch to add support for
  custom ATI hardware made for Dell. (#122190)

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com> 6.7.0-4
- rebuilt

* Tue May 18 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-3
- Added rpm script munging of X server config file back to spec file, which
  got inadvertently left out of the 6.7.0-2 build.  This fixes #120858 and
  its bretheren.

* Fri May  8 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-2
- Add -Wa,--noexecstack to AsCmd, in order to force all assembler files to
  use GNU stacks.  This was accomplished in an alternative way in our XFree86
  4.3.0 packaging via XFree86-4.3.0-redhat-exec-shield-GNU-stack.patch which
  patched every assembler file to add a .note.GNU-stack section, which is
  considered a superior solution, but our patch was non-portable to non-GNU
  systems.  This is a cleaner hack for now. (FC2BLOCKER #122708)
- Modified main rpm pre script to massage the X server config file(s) to
  remove XkbRules lines to help avoid (FC2BLOCKER #120858 and a zillion
  duplicates), and to ensure that the only active X server config file is
  xorg.conf (if any is present), and any other XFree86 4.x config files are
  renamed to .obsolete, which will help to minimize config file name confusion,
  and provide some sanity on upgrades, as all users will use xorg.conf by
  default regardless now. (FC2BLOCKER #122454)  (Fix based on patch from wtogami)

* Thu May  7 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-1
- Added xorg-x11-6.7.0-libxf86config-monitor-freq-fix.patch to fix a problem
  caused by gratuitous upstream libxf86config changes which force the
  HorizSync and VertRefresh lines to always be written out to the config file
  in commented out form.  (FC2BLOCKER #120950, 122341, 122573, 122439, 122072,
  122461, 121946, 121717, others not yet duped)

* Thu Apr 15 2004 John Dennis <jdennis@redhat.com> 6.7.0-0.5
- add xorg-use-linux-pci-only.patch, fixes bugs #118130 & #120520

* Thu Apr  8 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-0.4
- Further package description cleanups to remove more references to "XFree86"
  and replace them with more neutral wording, and also fix (#119670)

* Thu Apr  8 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-0.3
- Fix pre script for loop error created by accidentally committing half worked
  code.

* Wed Apr  7 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-0.2
- Updated spec file package descriptions to remove references to "XFree86" and
  update them to "X Window System" or "Xorg X11" as appropriate.
- Updated the following patches to work with xorg.cf instead of xfree86.cf:
  - xorg-x11-0.6.6-allow-XF86ExtraCardDrivers-on-AMD64.patch
  - xorg-x11-0.6.6-fix-BuildXFree86ConfigTools.patch
  - xorg-x11-6.7.0-xterm-make-optional.patch
  - xorg-x11-6.7.0-ppc64-support-updates.patch

* Wed Apr  7 2004 Mike A. Harris <mharris@redhat.com> 6.7.0-0.1
- Updated file lists to handle upstream renaming of X server binary from
  "XFree86" to "Xorg", server manpage, and getconfig config file.
- Added new ghost files for new server config file /etc/X11/xorg.conf
- Removed legacy compatibility symlinks for the old XF86Config file from
  /usr/X11R6/lib/X11 as X.org X11 uses /etc/X11/xorg.conf and there is no
  legacy to be compatible with.
- Other specfile cleanups to use /etc/X11/xorg.conf as the config file, and
  flag all places of XF86Config files with FIXME warnings of deprecation

* Tue Apr  6 2004 Mike A. Harris <mharris@redhat.com>
- Update main tarball to official X11 Release 6.7.0 from CVS export of the
  upstream release tag "xo-6_7_0" off of the "XORG-RELEASE-1" branch of CVS
- Removed xorg-redhat-ia64-plt-prot-exec-fix.patch as it is merged in 6.7.0

* Tue Apr  6 2004 Mike A. Harris <mharris@redhat.com> 0.6.6-0.2004_03_30.5
- Removed build_psyche build target, renamed build_rawhide to build_fc2, and
  added new build_maintainer custom build target
- Various spec file cleanups, renamed macros to foo_bar format, etc.

* Tue Apr  6 2004 Mike A. Harris <mharris@redhat.com> 0.6.6-0.2004_03_30.4
- Updated our ppc64 support patch and submitted upstream to fix (FDO #303) 
- Renamed xorg-ppc64-support-updates.patch to xorg-x11-ppc64-support-updates.patch
  to establish consistency with the names my xdiff utility produces.
- Added xorg-x11-0.6.6-allow-XF86ExtraCardDrivers-on-AMD64.patch to allow
  add on drivers to be specified using XF86ExtraCardDrivers in host.def on
  AMD64 architecture, in order to enable the "voodoo" driver.
- Enable the "voodoo" driver for AMD64 in addition to x86.
- Removed build_shrike, build_yarrow, and build_taroon build target macros and
  usage, as the package is not designed or intended to be used on those OS
  releases, and there are various potential problems that could arise.
- Updated freetype and freetype-devel dependancies to require version 2.1.7, as
  that is what version ships in the upstream sources, and there have been some
  font display related bugs reported by people who have recompiled the SRPM on
  older OS releases, and we do not support that anyway.
- Fixed bugs in spec file command substitution '[' tests discovered while
  updating the build target macros.
- Disabled BuildRequires: Glide3, Glide3-devel dependancies as Glide is opened
  via dlopen() for a while now, so it should not be needed at compile time any
  more.

* Mon Apr  5 2004 Mike A. Harris <mharris@redhat.com>
- Updated xorg-ppc64-support-updates.patch with fix for endian related issue
  (FC2 BLOCKER #119045)
- Removed obsolete_xfree86 conditional and usage, we hard code the Obsoletes
  lines now.
- Restored "Conflicts" lines that I had previously removed in the transition
  from XFree86 to Xorg X11, as they seem to still be needed on upgrades, or
  it is possible there will be upgrade failure issues, in particular when
  upgrading from Red Hat Linux 7.x or older releases to FC2.
- Added xorg-libX11-zh_CN.UTF8-crash-fix.patch to fix (FC2 BLOCKER #119032)

* Fri Apr  2 2004 Mike A. Harris <mharris@redhat.com> 0.6.6-0.2004_03_30.3
- Fixed a bug in xorg-redhat-libGL-exec-shield-fixes.patch (FC2 BLOCKER #119818)
- John further updated above patch, and tagged the .3 release.

* Thu Apr  1 2004 Mike A. Harris <mharris@redhat.com> 0.6.6-0.2004_03_30.2
- Added new open source Nvidia DRI 3D driver today, and enabled it on x86,
  ia64, and x86_64 only, as those are the only architectures that have been
  tested.  It builds cleanly with xorg, but is totally untested so far.

* Wed Mar 31 2004 Mike A. Harris <mharris@redhat.com> 0.6.6-0.2004_03_30.1
- Added xorg-ppc64-support-updates.patch back, as PPC64 fixes were reverted
  upstream <sigh>.

* Tue Mar 30 2004 Mike A. Harris <mharris@redhat.com> 0.6.6-0.2004_03_30.0
- Updated main xorg tarball to CVS snapshot 2004_03_30 from today.
- Removed XFree86-4.3.0-radeon-dpms-on-dvi-v2.patch as it should no longer be
  needed with current Radeon driver.
- Removed patches already merged into new upstream tarball, including:
  - xorg-redhat-elfloader-linux-non-exec-stack.patch
  - xorg-x11-addrinuse.patch
  - xorg-x11-Xft-freetype-bitmap-font-fix.patch
- Split out xorg-redhat-ia64-plt-prot-exec-fix.patch from libGL-exec-shield
  patch, as it was unrelated to libGL-exec-shield fixes. (#119324)
- Removed fonttosfnt* from the file lists as it has been removed upstream now
- Updated file list for libXft.so.2.1.2

* Tue Mar 30 2004 Mike A. Harris <mharris@redhat.com> 0.0.6.6-0.0.2004_03_11.11
- Added xorg-r200-uninitialized-variable-used.patch to CVS, as my last commit
  neglected to include the file.

* Tue Mar 30 2004 John Dennis <jdennis@redhat.com> 0.0.6.6-0.0.2004_03_11.10
- reenable libGL exec shield patch
- also fix bug 119324 ia64 exec permissions on PLT in elfloader

* Thu Mar 25 2004 Mike A. Harris <mharris@redhat.com>
- Fixed uninitialized variable access in Radeon R200 driver, in r200_pixel.c
  with xorg-r200-uninitialized-variable-used.patch FC2t2 TARGET (#116661)

* Wed Mar 24 2004 Mike A. Harris <mharris@redhat.com> 0.0.6.6-0.0.2004_03_11.9
- Really added the xorg-x11-Xft-freetype-bitmap-font-fix.patch patch this time
  as it was inadvertently left out of 0.0.6.6-0.0.2004_03_11.8 by mistake

* Tue Mar 23 2004 Mike A. Harris <mharris@redhat.com> 0.0.6.6-0.0.2004_03_11.8
- Added xorg-x11-Xft-freetype-bitmap-font-fix.patch from Xft 2.1.6 to Xorg
  included Xft to fix - FC2t2 BLOCKER (#118587,118822)
- Remove the rpm pre scripts from the library subpackages as they did not end
  up solving the XFree86 -> xorg-x11 ld.so.conf upgrade problem.
- Disable userdel/groupdel in xfs preun script, as it is harmless to leave the
  xfs user/group around as it is a registered account ID anyway, and there is
  a rather unsolveable problem on upgrades from one package providing xfs to
  a new one otherwise. - FC2t2 BLOCKER (#118145)
- Added "triggerpostun xfs -- XFree86-xfs" script, to work around a bug in the
  XFree86-xfs postun script, which results in the special xfs user account
  being inadvertently removed, causing xfs to run as the root user, and also
  resulting in xfs not being activated by chkconfig.  This trigger executes
  right after the XFree86-xfs postun script, and ensures that the xfs user
  exists, and that the xfs initscript is properly added by chkconfig, however
  this problem will recur again if we ever rename the xorg-x11 package to
  something else, or switch to a different X11 implementation altogether, since
  the xfs postun still will remove chkconfig on "rpm -e" or "rpm -U" to a
  different package name, but that problem is not easily solved other than by
  adding a new trigger every time the package name changes, unless someone
  has a better idea - FC2t2 BLOCKER (#118145,118818)
- Added "triggerpostun libs -- XFree86-libs" script to work around a bug in
  the XFree86-libs postun script, which results in _x11libdir being removed
  from ld.so.conf when upgrading from XFree86 to xorg-x11.  This trigger
  executes right after the XFree86-libs postun script and puts _x11libdir back
  in ld.so.conf - FC2t2 BLOCKER (#118448,118851,118993)
- Use "/sbin/service" instead of "service" in rpm scripts.
- Add "Requires(preun,postun): /sbin/service" to xfs package
  dependancies.

* Mon Mar 22 2004 Mike A. Harris <mharris@redhat.com> 0.0.6.6-0.0.2004_03_11.7
- Fixed -libs subpackage postun script by commenting out the broken empty
  if block (#118890,118949)
- Added xorg-x11-addrinuse.patch to fix bug in X.org Xtrans code which causes
  bind() failures to fail as if errno was set to -EADDRINUSE (#118950)
- Set "LinkGLToUsrLib NO" because the symlinks Imake creates are absolute,
  and we want relative symlinks.  A user reported this bug, so I have added
  code to %%install section to create relative symlinks in a similar but
  cleaner way to our XFree86 4.3.0 packaging. 

* Wed Mar 17 2004 Mike A. Harris <mharris@redhat.com> 0.0.6.6-0.0.2004_03_11.6
- Added new rpm pre scripts for the libs, Mesa-libGL, and Mesa-libGLU packages
  which add _x11libdir to ld.so.conf if it is missing, and then run ldconfig,
  in order to work around a race condition in the XFree86-libs-4.3.0-64 and
  older XFree86-libs packaging which could cause _x11libdir to be removed
  from ld.so.conf when other packages are still using it, including xorg-x11,
  causing upgrades to fail (#118448)
- Removed the offending code from xorg-x11-libs postun script so that this
  problem is not preserved in xorg-x11 packaging.  Also updated our XFree86
  packaging in cvs, so future XFree86 erratum for Fedora Core 1 and other OS
  releases will help to reduce the chances of someone getting hit by this
  upgrade problem.
- Added initial support to spec file for using the CVS Revision of the spec
  file in the package Release field.  Graciously stolen from the kernel spec
  file.  This is currently unused, but may be used in the future.

* Wed Mar 17 2004 Mike A. Harris <mharris@redhat.com> 0.0.6.6-0.0.2004_03_11.5
- Added versions to some of the XFree86 compabitility virtual provides, which
  include "Provides: XFree86-devel = 4.4.0", "Provides: XFree86-font-utils = 4.4.0",
  "Provides: XFree86-libs = 4.4.0"
- Added virtual provides of xdm, base-fonts, Xnest, xauth, libGL, libGLU, to
  each relevant subpackage.  They are all intentionally unversioned, so that
  things that require xdm/Xnest/etc. in a version/implementation agnostic
  manner, should use "Requires: xdm" instead of requiring a specific
  implementation or version of xdm.  If some package really does require a
  specific implementation or version of xdm, then it should still use the
  full non-virtual package name, as it is going to be both implementation and
  version specific anyway, so versioning these particular virtual provides
  does not make sense.

* Tue Mar 16 2004 Mike A. Harris <mharris@redhat.com> 0.0.6.6-0.0.2004_03_11.4
- Removed a bunch of the virtual Provides I added previously as they create
  problems with previous usage of Conflicts lines in some subpackages, and
  likely with other software, since they were not versioned Provides.  The
  other option would be versioning the provides, but I am not convinced that
  is the right approach.  Instead, I have removed them and will add things
  for compatibility only as problems arise.
- Added virtual "Provides: foo" to the Xvfb, xfs, twm, and font-utils subpackages,
  where "foo" is the subpackage name with the "XFree86-" part stripped off
  so that apps can use for example "Requires: xfs" to get an xfs font server,
  instead of requiring the XFree86 implementation specifically.  This allows
  us to have X11 implementation agnostic dependancies, which makes it easier
  to switch X11 implementations without breaking a pile of package
  dependancies.
- Added ld_so_conf_add_x11libdir macro, to clean up the rpm scripts a bit

* Mon Mar 15 2004 Mike A. Harris <mharris@redhat.com> 0.0.6.6-0.0.2004_03_11.3
- Added Obsoletes: tags to each subpackage in order to be able to properly
  replace XFree86 on upgrades cleanly
- Added virtual Provides: to most subpackages for compatibility with XFree86
  packaging on upgrades for packages that hard code specific XFree86
  dependancies.  Note that this may change in the future depending on the
  problems and needs that arise.
- Remove {_libdir}/libGL.so.1.2 symlink from Mesa-libGL subpackage as unneeded
- Disable libGL exec-shield patch for libGL as it has a slightly elusive glitch
- Remove all old XFree86 Conflicts lines from packaging, as they should not be
  needed now since the package names have changed and the old ones are now
  fully obsoleted

* Sat Mar 13 2004 Mike A. Harris <mharris@redhat.com> 0.0.6.6-0.0.2004_03_11.2
- Removed with_vmware conditional, and now unconditionally include vmware_drv
- Removed both the with_new_xft and with_new_xrender macros and their usage
- Removed version from virtual Xft Provides, as it is probably unnecessary
- Ported redhat-libGL-exec-shield-fixes.patch from 4.3.0 and added it as
  xorg-redhat-libGL-exec-shield-fixes.patch

* Sat Mar 13 2004 Mike A. Harris <mharris@redhat.com> 0.0.6.6-0.0.2004_03_11.1
- Various spec file cleanups, and s/XFree86/X Window System/ etc.
- Use %%{name} instead of hard coded XFree86 in dependancies for xdm
- Remove triggerpostun -- XFree86, as that was for 3.3.6 compatibility only
- Fix dri module file lists to prevent double inclusion problem
- Disable TLS support for libGL and the DRI drivers until it is ported forward

* Fri Mar 12 2004 Mike A. Harris <mharris@redhat.com> 0.0.6.6-0.0.2004_03_11.0
- Removed with_new_render hacks from specfile because new Render is included
  now, and upstream imake can deal with 3 level .so versions
- Updated libXft/libXrender .so.* versions in rpm file lists
- Updated spec file bits for moving GL includes into OpenGL ABI for Linux
  mandated location
- Removed spec file hack to make libGL be visible in OpenGL ABI for Linux
  mandated location, and enabled LinkGLToUsrLib YES in host.def to accomplish
  the same instead.
- Replaced .so version specific spec file hack to make libGLU be visible in
  OpenGL ABI for Linux mandated location, with a new hack that is more robust
- Updated file list for libXcursor.so.1.0.2

* Thu Mar 11 2004 Mike A. Harris <mharris@redhat.com>
- Updated to CVS snapshot 2004_03_11
- Added missing .so symlinks to -devel subpackage file list that did not get
  detected by the rpm missing_files_terminate_build test, but were present in
  the RPM_BUILD_ROOT
- Fixed bad dates for last few entries in spec file changelog
- Applied the xorg-mharris-radeon-agp-detect-via-pci-cap-list.patch and
  libICE-remove-bogus-delay.patch to upstream CVS and removed patches
- Downgraded freetype-devel dependancy to 2.1.4 again, so the package builds
  more easily on older OS releases for anyone brave enough to do so (ok, ok,
  so it is for me ok!)
- Added xorg-Imake-make-icondir-configurable.patch, ported forward from our
  XFree86 4.3.0 patch
- Explicitly list each individual shared library in the file lists instead of
  using globs, as this makes it easier to know when .so versions change,
  perhaps accidentally and catch problems sooner.  Globs were used before
  mainly to ensure files did not get excluded accidentally, however rpm now
  checks for files in the buildroot that do not end up in the final packaging
- Remove XFree86-4.3.0-redhat-xft-loadtarget.patch as the Xft in xorg CVS
  now includes this functionality already, however it is conditionalized at
  build time on the definition of FC_HINT_STYLE being defined, so we need to
  ensure this is getting defined at build time for compatibility.
- Updated redhat-embeddedbitmap patch

* Wed Mar 10 2004 Mike A. Harris <mharris@redhat.com> 0.0.6.6-0.0.2004_03_09.1
- Added xorg-ppc64-support-updates.patch, a forward port of ppc64 support from
  our XFree86 4.3.0 packaging
- Made with_savetemps work on x86/alpha/ppc/ppc64/amd64, and remove -pipe
  when using -save-temps
- Builds were failing with an mkfontscale SEGV or SIGILL on ppc/ppc64/s390
  which has been tracked down to an aliasing bug in freetype 2.1.7.  I have
  rebuilt freetype 2.1.7-3 with -fno-strict-aliasing which seems to work around
  the problem in testing.  We will see if it fixes it once freetype is built.
- Updated freetype dep in libs subpackage to 2.1.4
- Temporarily updated freetype-devel dep to 2.1.7-3 to force beehive to
  install it, so I get the -fno-strict-aliasing build
- ifnarch ppc64/s390/s390x libI810XvMC.*

* Wed Mar 10 2004 Mike A. Harris <mharris@redhat.com> 0.0.6.6-0.0.2004_03_09.0
- Initial xorg-x11 package, forked from the XFree86-4.3.0-63 package
- Package name chosen as xorg-x11 due to lack of official upstream package
  name at this point.  Name may change in the future, so people should not
  hard code any dependancies on it.  Version and Release fields future proofed
  for similar reasons, as we do not know what upstream version will be.
- Renamed StudlyCaps rpm macros XFree86CVSDate and CVSBuild to cvs_date and
  cvs_build to be more consistent in macro naming throughout specfile
- Disabled the with_new_savage_driver, and with_via_driver options by default,
  as the included drivers are newer, although the via driver may lose DRI
  support temporarily which I may need to add back later
- Disabled with_new_xft, with_new_xrender by default to use the stuff included
  in the tree, or use external Xft/Xrender packaging instead.
- Force with_xterm to 0 for all builds as we have shipped xterm separately
  for a few OS releases now
- Updated spec file License field to be more accurate "MIT/X11/others"
- Updated freetype deps to "BuildRequires: freetype-devel >= 2.1.4", as 2.1.4
  is what is currently included in the xorg sources and is the minimum needed
  to build properly
- Replaced all hard coded Requires: XFree86-* with usage of %%{name} macro
  instead, so package renames are easier to deal with
- Dropped all patches that were previously backported from XFree86 CVS, or
  were already checked into XFree86 CVS since 4.3.0.
- Temporarily disabled many patches that fail to apply, or fail to apply
  cleanly, for future investigation and cleanup, just to get rpms building
- Ported the elfloader-linux-non-exec-stack patch to current xorg-x11
- Removed the Glide3 conditionalized BuildRequires hack that was previously
  implemented to work around Red Hat buildsystem problems
- Disable removal of XIE/PEX docs as they are no longer provided in sources
- Force the removal of _x11dir/src in %%install, as the new tree installs the
  DRM source code there by default, and we do not want it because our DRM is
  in our kernel rpm.  No sense confusing users with multiple DRMs.
- Added getconfig bits to main server package
- Added fonttosfnt to font-utils subpackage
- Moved bdftopcf and bdftruncate to font-utils subpackage
- All libraries are now supplied by default in upstream builds in both static
  and dynamic (.a and .so) formats.  Libraries which are now supplied in
  shared form that were not in the past include:  libFS.so, libGLw.so,
  libI810XvMC.so, libXRes.so, libXfontcache.so, libXinerama.so, libXss.so,
  libXvMC.so, libXxf86dga, libXxf86misc.so, libXxf86rush.so, libXxf86vm.so,
  libfontenc.so, libxkbfile.so, libxkbui.so
- Added %%ghost flagged fonts.scale files to 100dpi, 75dpi, cyrillic, and misc
  font directories, so that if these files are present, they are owned by the
  appropriate subpackages

* Sun Mar  7 2004 Mike A. Harris <mharris@redhat.com>
- Conditionalized with_voodoo_driver to not build under build_taroon

* Fri Mar  5 2004 Mike A. Harris <mharris@redhat.com>
- Removed kdrive subpackage, and all with_kdrive conditionalization, as it is
  just extra spec file noise currently, and we have never shipped it.  Anyone
  building kdrive should instead be using kdrive from the xserver project on
  freedesktop.org
- Removed all 'athlon' subarchitecture references from spec file as the rpm
  {ix86} macro includes it automatically.
- Added XFree86-4.3.0-remove-copyright-symbol-to-fix-UTF-8.patch quick 2
  second fix to correct manpage display under UTF-8 (#101243)

* Thu Mar  4 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-62.EL
- Built 4.3.0-62.EL with target build_taroon for Red Hat Enterprise Linux 3 erratum

* Fri Feb 27 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-62
- Added new 2D driver from Alan Cox for Voodoo 1/2 hardware that does not
  require Glide in order to function, and provides RENDER acceleration and
  various other improvements above and beyond the XFree86 supplied "glide"
  driver which we have not shipped in the past.  Driver version 1.0beta3.
- Use new macros via_driver_name and voodoo_driver_name to avoid complexities
  in host.def with XF86ExtraCardDrivers define.

* Fri Feb 27 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-61
- Added XFree86-4.3.0-keyboard-disable-ioport-access-v3.patch as a final patch
  without debug logging enabled, to fix (#115769)
- Added spec file macro 'with_savetemps' for debugging purposes, disabling it
  by default.  When used, it is set up to only get used on x86 for
  build_rawhide and build_psyche builds
- Added XFree86-4.3.0-ati-ia64-no-nonpci-ioport-access.patch to fix ati driver
  issue on ia64 which causes IBM x455 system to machine check.  Also added
  "#define ATIAvoidNonPCI YES" to host.def to activate this fix only on ia64
  builds (#112175)

* Wed Feb 25 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-60
- Added XFree86-4.3.0-keyboard-disable-ioport-access-v2.patch to try to
  fix (#115769)
- Changed mkxauth to call chown as foo:bar instead of foo.bar as the latter
  syntax has been deprecated
- Added XFree86-4.3.0-minor-typo.patch to fix a trivial typo that I spotted
  in an error message in linux int10 code.
- Remove Buildrequires kudzu-devel, pciutils-devel, both of which were added
  on Mar 21, 2001 when Glide3 was included in the XFree86 packaging, but are
  no longer necessary.  I detected this when the buildsystem failed my build
  due to being unable to meet the dependancy on kudzu-devel, and further
  investigation showed that dependancy is no longer necessary.
- Added XFree86-4.3.0-xcursorgen-check-malloc-return.patch to make xcursorgen
  check the return codes on malloc before referencing allocated memory
- Added XFree86-4.3.0-redhat-xcursorgen-do-not-build-included-cursors.patch to
  stop building the XFree86 supplied Xcursor cursors as we do not ship them

* Thu Feb 19 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-59
- Added XFree86-4.3.0-xrandr-manpage-typo-fix.patch to fix manpage (#83702)
- Added XFree86-4.3.0-radeon-9200-dvi-snow.patch to fix issue on Radeon 9200
  when using DVI panel and encountering snow and other artifacts (#112073)
- Updated XFree86-4.3.0-debug-logging-ioport-based-rate-setting.patch to have
  it patch both lnx_kbd.c and lnx_io.c because both files insanely contain
  identical cut and pasted copies of the exact same source code, so nothing
  shows up in the X server log when testing with previous patch as the calls
  never got invoked in lnx_kbd.c (#115769)

* Wed Feb 18 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-58
- Added XFree86-4.3.0-debug-logging-ioport-based-rate-setting.patch to get
  some useful debugging information as to why the X server seems to be unable
  to use the KDKBDREP ioctl(), and is falling back to direct I/O port bashing,
  which causes problems in the kernel (#115769)
- Removed /usr/X11R6/lib/X11/fonts/misc and /usr/X11R6/lib/X11/fonts/cyrillic
  from the default xfs font path, as /usr/X11R6/lib/X11/fonts/misc:unscaled is
  present by default, which is what we want, and the cyrillic one gets added
  automatically if cyrillic fonts get installed.
- Updated libXrender to the version 0.8.4 maintenance release, which fixes a
  problem in 0.8.3 that caused antialiased fonts to be inadvertently disabled
  in Qt/KDE, and also caused color mouse pointers to appear as outlines
  on Radeon 7500 using Xinerama (#109351,109897)
- Updated libXft to version 2.1.3 from freedesktop.org xlibs, and enabled it
  for build_rawhide and build_psyche just for testing purposes for now.
- Conditionalize the patches XFree86-4.3.0-fixes-for-freetype-2.1.7-v2.patch,
  and XFree86-4.3.0-redhat-xft-loadtarget.patch to only be applied when
  with_new_xft is 0, as it is not needed for Xft 2.1.3
- Added XFree86-4.3.0-SDK-add-missing-includes-for-synaptics.patch from
  Paul Nasrat, to fix the SDK so that 3rd party drivers such as "synaptics"
  can be built in external rpm packages (#99351,103498,114804)
- Comment out host.def supported driver list for alpha architecture, and just
  build the default drivers, as we no longer have official Alpha products, so
  there is no reason to restrict driver support to hardware that works or is
  reasonably considered to work.  Ship it all and see what breaks.
- Disabled tdfx driver DRI support in Fedora Core development, as we have
  at least temporarily deprecated Glide3 due to it no longer compiling
  properly.  Alan was working on fixing this, so we will probably re-enable
  tdfx DRI support once Glide3 is working again.
- Removed XFree86-4.3.0-fixes-for-freetype-2.1.7-v2.patch and replaced it
  with XFree86-4.3.0-general-fixes-for-freetype-2.1.7.patch which excludes
  Xft2 fixups, and XFree86-4.3.0-xft-2.1.2-fixes-for-freetype-2.1.7.patch
  which includes only Xft2 fixups needed for xft-2.1.2, as 2.1.3 includes
  this fix already

* Sun Feb 15 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-57
- Oops, now we change DevelDriDrivers to DevelDRIDrivers so that the via DRI
  driver actually builds this time.
- Oops, now we change '%%define DevelDRIDrivers' to '#define DevelDRIDrivers'
  so that the via DRI driver actually builds this time.
- Added XFree86-4.3.0-build-libXinerama-before-libGL-for-via-driver.patch
  because the via DRI driver links against libXinerama, and seems to be the
  only DRI driver which does so.  This patch causes libXinerama to be
  compiled before libGL to ensure the via driver will link properly.

* Sat Feb 14 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-56
- Happy VIAlentines Day Edition.  Feel the love.
- Updated the 'via' driver to latest driver from Alan Cox, which contains
  DRI support among other things.  Only enabled for build_rawhide and
  build_psyche for the time being, until it has been adequately tested.
- Added DevelDriDrivers to host.def with 'via' driver added, conditionalized
  to the with_via_dri_driver macro
- Conditionalize with_via_driver to only build on x86 architecture
- Added XFree86-4.3.0-i740-missing-symbol-vbeFree.patch to add a missing
  symbol to the i740 driver (#115676)
- Built 4.3.0-56 with target build_rawhide for Fedora Core development

* Thu Feb 12 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-55
- Added {x11datadir}/X11/xinit back to package list, which seems to have been
  inadvertently dropped during attempts to get package to compile on Red Hat
  Linux 9 s390 builds earlier this week.
- Built 4.3.0-55 with target build_yarrow for Fedora Core 1 erratum
- Built 4.3.0-55.EL with target build_taroon for Red Hat Enterprise Linux 3 erratum
- Built 4.3.0-2.90.55 with target build_shrike for Red Hat Linux 9 erratum

* Wed Feb 11 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-54
- Added XFree86-4.3.0-libXfont-security-CAN-2004-0083-CAN-2004-0084-CAN-2004-0106.patch
  to fix all recent security flaws in libXfont which are outlined in
  CAN-2004-0083, CAN-2004-0084, CAN-2004-0106, discovered by iDefense, David
  Dawes and others.  This patch replace all previous libXfont patches from
  XFree86 builds 4.3.0-49 through to present.
- Added XFree86-4.3.0-libXfont-security-CAN-2004-0083-CAN-2004-0084-CAN-2004-0106-v2.patch
  which is the same as the above patch, but modified to cleanly apply to 4.3.0,
  renamed to keep all patches present in src.rpm for comparative purposes.
- Built 4.3.0-54 with target build_yarrow for Fedora Core 1 erratum
- Built 4.3.0-54.EL with target build_taroon for Red Hat Enterprise Linux 3 erratum
- Built 4.3.0-2.90.54 with target build_shrike for Red Hat Linux 9 erratum

* Tue Feb 10 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-53
- Added XFree86-4.3.0-security-dirname-CAN-2004-0106.patch which replaces
  XFree86-4.3.0-security-fonts-alias-dirname3.patch, the new patch being the
  same but without the second hunk, as the patch Keith wrote for CAN-2004-0083
  and CAN-2004-0084 already handled that issue so there was a conflict.
- Built 4.3.0-53 with target build_yarrow for Fedora Core 1 erratum
- Built 4.3.0-53.EL with target build_taroon for Red Hat Enterprise Linux 3 erratum
- Built 4.3.0-2.90.53 with target build_shrike for Red Hat Linux 9 erratum

* Tue Feb 10 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-52
- Added XFree86-4.3.0-security-fonts-alias-dirname3.patch in order to fix 2
  additional buffer overflows in libXfont, discovered by iDefense and David
  Dawes.  No CVE assignment has been provided yet.
- Built 4.3.0-52 with target build_yarrow for Fedora Core 1 erratum
- Built 4.3.0-52.EL with target build_taroon for Red Hat Enterprise Linux 3 erratum
- Built 4.3.0-2.90.52 with target build_shrike for Red Hat Linux 9 erratum

* Tue Feb 10 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-51
- Added XFree86-4.3.0-security-dirname-CAN-2004-0083-CAN-2004-0084-keithp.patch
  alternative patch written by Keith Packard, to fix CAN-2004-0083 and
  CAN-2004-0084 security issues
- Added XFree86-4.3.0-security-fonts-alias-dirname-CAN-2004-0084.patch to the
  package, but disabled for now while we test the above patch from Keith
  Packard which addresses both security issues.
- Built 4.3.0-51 with target build_yarrow for Fedora Core 1 erratum
- Built 4.3.0-51.EL with target build_taroon for Red Hat Enterprise Linux 3 erratum
- Built 4.3.0-2.90.51 with target build_shrike for Red Hat Linux 9 erratum

* Mon Feb  9 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-50
- Fix issues detected in QA testing
- Built 4.3.0-50 with target build_yarrow for Fedora Core 1 erratum
- Built 4.3.0-50.EL with target build_taroon for Red Hat Enterprise Linux 3 erratum
- Built 4.3.0-2.90.50 with target build_shrike for Red Hat Linux 9 erratum

* Wed Feb  4 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-2.90.49
- Built 4.3.0-2.90.49 with target build_shrike for Red Hat Linux 9 erratum
- Split {_x11datadir}/X11/etc/* glob previously wrapped using with_Xserver into a
  with_xterm portion and with_Xterm portion with the dir being always included,
  in order to work around obscure build failure on s390 on RHL 9.  Yes this is
  an insane problem to have to fix because we do not ship an RHL 9 s390 product
  and never will.  But we seek perfection however, and who knows, maybe next
  week we will release a Red Hat Linux 9 port to s390 for consumer desktops or
  something.  <grin>
- Rename with_included_xterm macro to with_xterm for naming consistency with
  other options, as it threw me off.

* Wed Feb  4 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-49.EL
- Built 4.3.0-49.EL with target build_taroon for Red Hat Enterprise Linux 3 erratum

* Wed Feb  4 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-49
- Added XFree86-4.3.0-security-fonts-alias-dirname-CAN-2004-0083.patch to
  fix security issue in core fonts backend reported by iDefense in CAN-2004-0083
- Added build_maintainer_mode distribution version autodetection to simplify
  local build testing procedures, added dist_ver macro, dist_test parameterized
  macro (to keep jbj on his toes), and updated build_xxxx target autoconfig
  when build_auto_mode is enabled.  This only affects local builds, not any
  Red Hat builds.
- Enabled radeon-agp-detection-using-capability-list-walk patch on all builds,
  which was inadvertently left off on some due to misplaced macro conditional
- Built 4.3.0-49 with target build_yarrow for Fedora Core 1 erratum

* Sun Feb  1 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-45.0.2.EL.test
- Rebuilt with build_taroon for RHEL 3 testing

* Sat Jan 31 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-45.0.2
- Added XFree86-4.3.0-Xserver-dix-xkb-key-repeating-bug-CVS-backport.patch
  to fix a bug in DIX when xkb is being used that causes keys to repeat
  spuriously on some hardware under certain system loads.  This patch has been
  backported from the 4.3.0-48 developmental head package. (#76959,114635)
- Added XFree86-4.3.0-XRes-IncludeSharedObjectInNormalLib.patch to make
  libXRes get built PIC for bug (#114292)
- Updated XFree86-4.3.0-missing-lib-sharedreqs.patch to remove dependancy on
  libXt caused by improper dependancy listing in SharedXmuuReqs (#113336)

* Thu Jan 29 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-45.0.1.EL.test
- Build test release for RHEL3 U2 testing

* Wed Jan 28 2004 Mike A. Harris <mharris@redhat.com> 4.3.0-45.0.1
- Temporary fork of 4.3.0-45 to add some patches for test builds, until post
  4.3.0-45 (4.3.0-46 through 4.3.0-50) local-work-in-progress stuff is in
  clean enough shape for tree inclusion
- Added XFree86-4.3.0-fixes-for-freetype-2.1.7-v2.patch so that XFree86 will
  build properly against freetype 2.1.7 (#114343)

* Sun Nov 30 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-45
- Implemented new AGP/PCI autodetection in the Radeon driver by examining PCI
  configuration space and walking the PCI extended capabilities list in order
  to determine if the device implements the AGP capability.  This code should
  work on _any_ AGP/PCI hardware generically and should be factored out into
  generic X server code in future XFree86 releases so all drivers can benefit
  from it.  XFree86-4.3.0-radeon-agp-detection-using-capability-list-walk.patch
  should fix all Radeon PCI/AGP autodetection bugs, including (#111191).  Some
  AGP Radeon users may experience a performance boost with this new driver if
  their card was misdetected and treated as PCI before, as pcigart mode works
  on AGP hardware, but is slower than using AGP.
- Fixed build_rawhide to work the same as build_yarrow everywhere since the
  two are functionally identical for the time being.  

* Wed Nov 26 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-44.EL
- Rebuilt 4.3.0-44 as 4.3.0-44.EL for RHEL3 QU1 update

* Wed Nov 26 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-44
- Added XFree86-4.3.0-libfontenc-IncludeSharedObjectInNormalLib.patch to fix
  KDE build problem on AMD64 which links to the static libfontenc library and
  fails because it wasn't compiled with -fPIC, reported in bug (#111058)
- Enable the open source vmware_drv.o video driver that ships with XFree86 on
  all builds now, to supply this driver as-is to users as a convenience
  although it is still unsupported by Red Hat.  Users encountering video or
  other X related problems with this driver, need to report their problems
  directly to XFree86.org, or to VMware Inc.
- Rebuild in rawhide for FC2 development

* Fri Nov 14 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-43.1
- Added XFree86-4.3.0-nv-riva-videomem-autodetection-debugging.patch to be
  able to debug Riva TNT memory autodetection problems in the future (#109459)
- Added new build_rawhide flag to wrap experimental changes and test patches
  with for Rawhide builds
- Rename rpm macro from tlssubdir to _tlsdir, and enforce it's usage everywhere
  in the spec file

* Mon Nov  3 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-2.90.43
- Rebuild 4.3.0-43 for Red Hat Linux 9 erratum with build_shrike set

* Mon Nov  3 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-43
- Updated to XFree86-4.3.0-xf-4_3-branch-2003-11-03.patch to pick up latest
  fixes in the XFree86 4.3.x stable branch including:
  - Fix for crash on ia64 because of wrong setjmp buffer alignment (John Dennis)
  - Close freetype fontfile filehandle in mkfontscale, this prevents problems
    from limitation of simultaniously open files
  - Fixed erronous freeing of DisplayModeRec in xf86DeleteMode() when
    deleting the modePool in xf86PruneDriverModes() the 'prev' member has
    a different meaning for modePool modes than for ScrnInfoPtr->modes modes
    where it creates a doubly linked list
  - Fix some i830+ VT switch/exit crashes
  - Fix DRM_CAS on ia64 as used by the DRI (Bugzilla #778, John Dennis).
- Removed XFree86-4.3.0-Xlib-XIM-bugfix-from-XFree86-bugzilla.patch,
  XFree86-4.3.0-ia64-setjmp-alignment.patch
- Updated XFree86-4.3.0-ia64-drm-locking.patch as part of it is in the stable
  branch patch now.
- Updated some spec file comments, and other mostly cosmetic changes.
- Fixed some mistakes in spec file changelog dates.

* Wed Oct 29 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-42.2
- Enable new Radeon support patches for shrike builds also to support newer
  Radeon hardware, so future erratum picks up these enhancements.
- Backport XFree86-4.3.0-RandR-refresh-rate-rounding-error-fix-from-CVSHEAD.patch
  from CVS HEAD in order to fix bug (#108008)
- Added XFree86-4.3.0-vidmode-SEGV-fix-from-CVS-HEAD.patch, backported from
  CVS HEAD to fix a SEGV in the vidmode extension (#101276)
- Renamed build_cambridge target to build_yarrow to indicate the change from
  project name to final product name.
- Added XFree86-4.3.0-rendition-complete-driver-backport-CVS20031031.patch which
  is a backport of the rendition driver from CVS head, including a couple bug
  fixes and the rest of changes are cosmetic.  (#108693)
- Disabled XFree86-4.3.0-rendition-disable-cause-of-SEGV.patch which should now
  be obsolete from above rendition driver backport.

* Fri Oct 24 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-42
- This release is the long awaited answer to the meaning of life, the universe
  and everything.
- Added XFree86-4.3.0-redhat-exec-shield-GNU-stack.patch to make the complete
  XFree86 build including Mesa et al. exec-shield friendly (arjanv, mharris)
- Updated to new XFree86-4.3.0-Mesa-SSE-fixes-from-MesaCVS-v2.patch which
  should fix compatibility problems between DRI and 2.6.x kernels which were
  caused by the previous version of this patch.  Linus reported the fix for
  this with details of the problem, and explanation of the solution, which I
  extracted out of CVS (#107932,106566,107829)

* Mon Oct 20 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-41
- Added XFree86-4.3.0-ucs2any-C-implementation.patch which implements ucs2any
  in C, and is slightly faster than the ucs2any.pl perl script

* Mon Oct 13 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-40
- More xfs initscript cleanups
- Added XFree86-4.3.0-ia64-drm-locking.patch from John Dennis, to fix DRI
  locking deadlock on ia64 architecture (#104338,103936)

* Fri Oct 10 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-39
- Fixed brown paper bag bug - missing "; then" in if clause of xfs initscript

* Thu Oct  9 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-38.1
- Added conditional option with_bail_on_undef_syms which currently sets
  SharedLibraryLoadFlags to "-shared -Wl,-z,defs" in order to cause linking to
  fail completely when undefined symbols are found.  Mesa compilation blows
  up, so I've disabled this option for now until I have proper time to spend
  on an investigation sometime in the future.
  
* Wed Oct  8 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-38
- Updated xfs initscript to improve startup performance by not triggering the
  creation of fonts.dir due to new fonts.cache* files being found (#97240).
- Updated xfs initscript to handle Opentype (otf, otc) fonts by calling
  mkfontscale + mkfontdir on them.
- Updated xfs initscript to ignore all known font metadata file types when
  determining wether or not to trigger mkfontdir on non-truetype/non-opentype
  font file types.
- Updated xfs initscript to run fc-cache if fonts.dir files get updated in any
  way.  This is disabled for fc-cache version 1.0.2 which shipped on Red Hat
  Linux 8.0, as it SEGV's for some reason on that release, and 4.3.0 isn't
  officially supported for that release.
- Updated xfs initscript to use "grep -qs" instead of output redirection in
  all grep invocations, as it is a bit cleaner code, possibly even faster.
- Call mkfontscale in Syriac-fonts rpm post and postun scripts to properly
  generate fonts.scale and fonts.dir for these Opentype fonts.
- Added XFree86-4.3.0-missing-lib-sharedreqs.patch to make sure libDPS,
  libXmuu, libXfont, libXp, libXpm, libXrandr, and libXv get linked to their
  dependant libraries when building XFree86, so that undefined symbols do not
  prevent prelinking from working.  This solves other problems too, and now
  obsoletes the previous XFree86-4.3.0-missing-SharedXfooReqs.patch, and
  XFree86-4.3.0-libXrandr-missing-sharedreqs.patch patches as well (#106661)

* Mon Oct  6 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-37
- Added XFree86-4.3.0-radeon-autodetect-pci-or-agp-cards.patch which is a
  backport from CVS of new code to autodetect wether a given card is AGP or
  PCI by reading PCI config space.  This simplifies future updates to the
  radeon driver for future Radeon hardware.  Older driver update patches
  can further be simplified later on to remove some unnecessary cruft from
  them.
- Updated XFree86-4.3.0-radeon-support-backport-from-CVS-v2.patch to fix a few
  missing chip IDs in a section of radeon_driver.c
- Enabled DRI support for ppc for build_cambridge target

* Mon Oct  6 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-36.2
- This build contains conditionalized build changes for RHL 8.0, intended to
  allow pain free compilation and installation of 4.3.0 in RHL 8.0.  All
  changes are conditionalized to build_psyche to limit their effects strictly
  to RHL 8.0 builds unless the change is an obvious no-risk fix that wont
  harm current development or erratum.
- Renamed fontconfig-2.1-slighthint.patch due to a problem which was reported
  by a user recompiling XFree86 on Red Hat Linux 8.0, getting a fontconfig
  dependancy, recompiling and installing fontconfig, and then trying to
  recompile XFree86 from their previously installed XFree86 source rpm.  Both
  XFree86 and fontconfig contain a patch of the same name, and the fontconfig
  one overwrote the one from the XFree86 packaging.  The two patches are
  identical but the directory paths modified to match XFree86's fontconfig path.
  The new patch name is XFree86-4.3.0-redhat-fontconfig-2.1-slighthint.patch
- Added "Provides: Xft-devel = %%{xftver}" to XFree86-devel and "Provides:
  Xft = %%{xftver}" to XFree86-libs, both wrapped with build_psyche for Red Hat
  Linux 8.0 compatibilty as many packages brokenly hardcode Xft dependancies
- Disabled the Conflicts: Xft-devel and Conflicts: Xft lines from the -libs and
  -devel packages as they seem to prevent upgrades from working from XFree86
  4.2.x to 4.3.0 on RHL 8.0 systems as the package both provides, and obsoletes,
  Xft and Xft-devel, and the 'conflicts' line seems to make it conflict with
  itself.
- Fixed some broken with_fontconfig conditionalization for cases where XFree86
  supplied fontconfig is used for building, just so the option actually works
  if someone sets it.

* Fri Oct  3 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-36
- Added XFree86-4.3.0-ati-generic-shared-chip-data.patch to unify changes to
  atichip.h into a single harmless patch to avoid patch overlap and merge
  conflicts
- Updated XFree86-4.3.0-radeon-support-from-ATI-backport-from-CVS.patch to
  remove changes to atichip.h as they're merged into the above patch instead
- Added XFree86-4.3.0-radeon-support-backport-from-CVS.patch backport of 
  support for newer Radeon 9600/9800/IGP/Mobility hardware from CVS head,
  along with a few minor bug fixes for Mobility and IGP.  Very low risk change
  which is heavily audited, however currently configured to only build for
  cambridge and psyche until runtime tested sufficiently
- Renamed XFree86-4.3.0-ati-radeon-dpms-on-dvi-v2.patch for consistency, to
  XFree86-4.3.0-radeon-dpms-on-dvi-v2.patch
- Added XFree86-4.3.0-Xserver-xf86PciInfo-updates.patch which from now
  on will hold all xf86PciInfo updates.  Moved all Radeon, savage, and S3
  updates from other patches into this file.

* Fri Oct  3 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-35.EL
- Rebuilt 4.3.0-35 as 4.3.0-35.EL for RHEL

* Thu Oct  2 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-35
- Updated to XFree86-4.3.0-xf-4_3-branch-2003-10-02.patch to pick up latest
  fixes in the XFree86 4.3.x stable branch including:
  - xdm build fixes from previous security update
  - Use pam_strerror() to print an error message after pam_setcred() fails,
    C style unification
  - xdm portability fix
- Added XFree86-4.3.0-Xlib-XIM-bugfix-from-XFree86-bugzilla.patch to fix
  an XIM bug introduced into XFree86 CVS in late August, reported in XFree86
  bugzilla, fixed in the trunk but not the 4.3 branch yet. (#106058)
- The XIM bug above was introduced in XFree86-4.3.0-xf-4_3-branch-2003-09-11.patch
  which the spec file claims I added Sat Sep 6, 2003 in version 4.3.0-30, which
  would mean that release was affected also, however this isn't the case.  A
  deeper investigation shows that the changelog got the patch added, but the
  actual patch got misplaced somehow, so didn't get applied until 4.3.0-32. As
  such, I'm adding an updated comment to the 4.3.0-32 changelog entry to
  reflect this goofup.

* Mon Sep 29 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-34.2
- Made 'hostname' use -f in BuilderString, so that the FQDN of the buildhost
  is present in X server startup log info
- Updated server startup vendorstring for Fedora Core, RHEL, and to indicate
  Red Hat Linux distro releases 8.0 and 9

* Thu Sep 25 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-34.1
- Added XFree86-4.3.0-savage-scaling-bz274.patch to fix (XF86 #274)
- Added XFree86-4.3.0-savage-memleak-plug-bz278.patch to plug memory leak in
  the savage driver (XF86 #278)
- Added XFree86-4.3.0-savage-memleak-plug-bz279.patch to plug memory leak in
  the savage driver (XF86 #279)

* Thu Sep 25 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-34
- Updated to XFree86-4.3.0-xf-4_3-branch-2003-09-26.patch to pick up new
  security fixes from CVS
- Updated XFree86-4.3.0-redhat-libGL-exec-shield-fixes.patch to new patch
  XFree86-4.3.0-redhat-libGL-exec-shield-fixes-v2.patch which reorders some
  includes in mem.c so it builds.  Still cambridge only. (#104029)

* Fri Sep 19 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-33.1
- Added XFree86-4.3.0-redhat-libGL-exec-shield-fixes.patch experimental patch to
  cambridge only from John Dennis <jdennis@redhat.com> to fix libGL / DRI /
  exec-shield problems with executable page mappings (#104029,91784,101647)
- Added XFree86-4.3.0-redhat-libGL-TLS-buildfix.patch to fix the libGL opt
  patch Imake TLS stuff.  Cosmetic only.

* Fri Sep 19 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-33
- Created XFree86-4.3.0-Xserver-dualhead-segv-with-no-busid.patch to fix a
  problem that Roland McGrath was experiencing, where the X server will crash
  when starting on a system with one dualhead video card, with the config file
  omitting the BusID keywords.  The crash is due to a format string bug in
  xf86Helper.c during startup time in a codepath that is rarely executed.
- Moved new Xft/Xrender tarball unpacking and preparation from build section
  to prep section where it belongs, in order for patches we apply to xft et al
  to not get missed, and also so rpmbuild -bp results in something closer to
  the actual sources we are using.  There are a few more areas needing tidying
  in this regard also.

* Wed Sep 17 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-32.EL
- Rebuilt 4.3.0-32 with build_taroon set as 4.3.0-32.EL in order to pick up
  the libGL patch in Taroon

* Wed Sep 17 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-32
- Updated to XFree86-4.3.0-xf-4_3-branch-2003-09-17.patch to pick up latest
  xdm security fixes from CVS stable branch "xf-4_3-branch":
  - Backport xdm code from -current, including following changes:
    - use better pseudo-random generators to generate magic cookies,
      including EGD-like prng daemons support.
    - add support for LISTEN keyword in Xaccess
    - deal with small memory leaks
    - use SIOCGLIFCONF to query network interfaces where available
    - fix XDMCP bug that could cause localhost entries in /etc/X0.hosts
      to be lost
    - add xdm /dev/random handling for Solaris
    - fix XDMCP queries on systems using getifaddrs().
    - Fix for http://www.cve.mitre.org/cgi-bin/cvename.cgi?name=CAN-2003-0730
- Enabled the libGL optimization patch for Taroon, but disable TLS support as
  it is experimental and only intended for Cambridge builds.
- Updated XFree86-4.3.0-redhat-radeon-forcelegacycrt-for-alan.patch to remove
  CVS revision strings from the patch so it applies cleanly with new update
- Dropped XFree86-4.3.0-xaa-pixmap-cache-crash-clash.patch as the stable branch
  patch update now has this fix

* Mon Sep 15 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-31
- Added "export LANG=C" to the build and install sections of the spec file
  in hopes it will speed up all script processing during building.
- Added xrender.pc pkg-config support using an expansion disabled here-document
  with rpm macros

* Sat Sep  6 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-30.EL
- Rebuilt for Taroon

* Sat Sep  6 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-30
- [CHANGELOG UPDATE] - the XFree86-4.3.0-xf-4_3-branch-2003-09-11.patch
  referenced below originally, actually got left out of this build
  inadvertently, and the changes referenced did not get included until the
  4.3.0-32 build above.  <mharris@redhat.com>
- Updated to XFree86-4.3.0-xf-4_3-branch-2003-09-11.patch to pick up latest
  fixes from CVS stable branch "xf-4_3-branch", including:
  - Fix calculation of CRTC2 frame offset with page flipping in radeon driver
    (Michel Daenzer)
  - Fix an XAA pixmap cache server crash that can happen in some cases
    when the off-screen memory is heavily fragmented (David Dawes, based
    on #5752, Koike Kazuhiko, Chisato Yamauchi).
  - Fixed a crash when _XIMProtoOpenIM(), hich is called through XOpenIM()
    API when protocol IM is being set up,  fails (Bugzilla #618,
    Hisashi MIYASHITA).
  - Don't call FBIOPAN_DISPLAY ioctl with arguments that will cause a
    confusing if harmless error (Michel Daenzer)
  - Fixes for potential integer overflows in font libraries. (blexim,
    Matthieu Herrb).
  - For integer overflow tests, use SIZE_MAX which is more standard than
    SIZE_T_MAX, and default to ULONG_MAX for the case of LP64 systems. Based
    on reports by Matthias Scheler and Alan Coopersmith (Bugzilla #646).
- Created a new XFree86-modules-unsupported package, and moved some of the
  modules which are unsupported and provided totally as-is into this new
  subpackage
- Disabled SDK-add-missing-includes-for-vnc patch as it causes the X server
  build to fail, reverted to previous patch for synaptics.
- Added XFree86-4.3.0-ia64-setjmp-alignment.patch to fix an issue with setjmp
  on ia64 which results in an X server crash when using Sun Java.  Fixed by
  John Dennis <jdennis@redhat.com> for bug IDs (#103610,104191)
- Remove {_x11datadir}/X11/xserver on builds disabling with_Xserver, as a dead
  symlink was found by with with_dead_symlink_test.
- Modified with_dead_symlink_test to be cleaner.

* Sat Sep  6 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-29.1
- Enable libOSMesa on s390/s390x/ppc/ppc64, as it was disabled but some of the
  files were shipped anyway, and there's no really good reason to not supply it
  that I can think of.
- Add a new conditionalized test (with_dead_symlink_test) to test for dead
  symlinks to the end of the install section of the specfile and enable it by
  default.
- Added Requires: xterm to the XFree86-twm subpackage because twm configuration
  requires xterm by default.  This also will fix another problem where upgrading
  the XFree86 packages from from RHL 9 or earlier to XFree86 after xterm was
  split out into it's own package, will cause xterm to be lost unless the user
  manually installs the xterm package.  Now, as long as they have XFree86-twm
  installed, xterm will be dragged in as a dependancy, since it is one.  If
  anyone knows of similar xterm dependancies either in other XFree86 subpackages
  or in other Red Hat Linux packages, they should file a bug report and add me
  to the CC list.
- Added XFree86-4.3.0-SDK-add-missing-includes-for-vnc-and-synaptics.patch as
  an updated of the SDK patch for the GPL synaptics driver (#99351)

* Sat Sep  6 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-29
- Move perlification of xft.pc earlier so it has effect
- Fix broken symlinks for libXrender.so.2 similar to the prior broken Xft libs

* Fri Sep  5 2003 Karsten Hopp <karsten@redhat.de> 4.3.0-28
- fix typo in perl script

* Fri Sep  5 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-27
- Build 4.3.0-27, release name (Conquest)
- Added XFree86-4.3.0-SDK-add-missing-includes-for-vnc.patch, contributed by
  Paul Nasrat in order to help get VNC compiling with the SDK (#103824)
- Added XFree86-4.3.0-radeon-disable-VideoRAM-option.patch which causes the
  Radeon driver to ignore any user supplied VideoRAM option in the config file,
  as the radeon driver properly autodetects RAM on all supported video hardware,
  and the option to override it is misused by users who think they have more
  RAM than they do, resulting in the creation of a problem where none existed.
  In the unlikely case a model of radeon is found that does not autodetect the
  amount of videoram properly, we can easily fix that with information provided
  by ATI at that point in time.
- Fixed broken libXft symlinks, hopefully got it right this time.
- Fix xft.pc file by munging @VERSION@ into the proper version

* Thu Sep  4 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-26
- Build 4.3.0-26, release name (Brazil Nut)
- Added XFree86-4.3.0-xaa-pixmap-cache-crash-clash.patch to fix bug in XAA
  pixmap cache code which could cause a SEGV.  Patch by Thomas Winishhofer,
  submitted to me by Daniel Stone at Debian.
- Added XFree86-4.3.0-nls-cjk-utf8.patch fix for (#101377)
- Added XFree86-4.3.0-Mesa-SSE-fixes-from-MesaCVS.patch fix for SSE/3Dnow
  detection problem, backported from Mesa3D CVS tree, not present in XFree86
  CVS.
- Added XFree86-4.3.0-nls-compose-en_US.UTF8-lxo.patch to fix problem with
  us_intl keymap and funny i18n characters (#80244)
- The XFree86-4.3.0-redhat-xft-loadtarget.patch was getting applied to the Xft
  lib that ships with XFree86 during the patch phase, but we immediately
  replace Xft with the latest Xft2 in the build section thus losing the patch,
  so I've added code in the build section to re-patch the new Xft2
- Put the xft.pc pkg-config file back into the filelist
- Fix libXft.so.2 symlink to libXft.so.2.1.1 instead of libXft.so.2.1 (#103636)

* Tue Sep  2 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-25
- The Australian special edition release, codename (Jumbo Tiger Shrimp)
- Re-enabled with_new_xft_and_xrender, this time using Imake, dealing with
  limiations of Imake by renaming the generated libraries to 3 digit versions

* Mon Sep  1 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-24
- Disable Glide3 support on ia64 as it does not really work anyway
- Disable xkb-multilayout-modifier-fix-CVS11137 as the ALT-TAB problem is back
  now, and this is the next likely candidate cause

* Thu Aug 28 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-23.dbg
- Updated XFree86-4.3.0-redhat-libGL-opt.patch from Jakub <jakub@redhat.com>,
  so that libGL TLS support now works on all x86 class CPUs, rather than just
  i686 and higher.  New version is: XFree86-4.3.0-redhat-libGL-opt-v2.patch
- Disabled xkb-us_intl-and-other-fixes-CVS11216 and xkb-fix-sticky-modifiers
  patches since they fix one bug, to create another, and fix that bug to
  create several more.  The original problem was much less worse and affected
  far less people.
- Enabled with_debuglibs temporarily for debugging purposes

* Tue Aug 26 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-22.4
- Added --libdir=%%{_x11libdir} for Xft/Xrender stuff

* Tue Aug 26 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-22.3
- Change ./configure lines of Xft/Xrender to have --prefix=/usr/X11R6

* Tue Aug 26 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-22.2
- This package only compiles on Linux, and is not intended for use on other
  OSs.  Made explicit now.
- Test build with SDK enabled to try to troubleshoot

* Thu Aug 21 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-22.1
- Re-enabled new Xft/Xrender in order to try and debug why the builds are
  failing ONLY in the Red Hat buildsystem.

* Thu Aug 21 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-22
- Added XFree86-4.3.0-libGL-multitexture-defines.patch to fix bug where wine
  and various other OpenGL applications wont compile with Mesa from 4.3.0 due
  to a gl.h header file bug introduced in 4.3.0 (#97840)
- Added XFree86-4.3.0-libXrandr-missing-sharedreqs.patch to fix bug (#102924)
- Added XFree86-4.3.0-xkb-fix-sticky-modifiers.patch to fix problem in XFree86
  rpm releases 4.3.0-19 through 4.3.0-21 which cause ALT-TAB and some other
  modifier combinations to break.  Bug (#102668)
- Moved all xkb datafile patches to section 800-829 in specfile
- Added conditional BuildRequires: glibc >= 2.3.2-66 and Requires: lines if
  with_GL_TLS libGL optimization patch is enabled, to ensure the system has
  the required glibc installed. (#102175)
- Disabled the new Xft and Xrender code by toggling with_new_xft_and_xrender,
  because of an unexplainable build failure that has started occuring only in
  the Red Hat buildsystem, which I can not reproduce locally.  4.3.0-21 built
  perfectly fine in beehive, but the current rpm fails when compiling the new
  Xft, saying that ld can't find -lXrender.  I've absolutely no clue why this
  is occuring, all of the builds compile both on x86 and AMD64 locally here,
  and am unable to debug it on the systems it occurs on in the buildsystem.

* Tue Aug 19 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-21
- Added XFree86-4.3.0-libXpm-missing-header.patch from John Dennis to fix
  bug (#101017)
- Added XFree86-4.3.0-ia64-slowbcopy2.patch by John Dennis to replace the
  earlier patch XFree86-4.3.0-ia64-slowbcopy.patch which fixes a semi
  obscure problem in slowbcopy (#98139)
- Integrated Keith Packard's upstream Xft-2.1.2 and Xrender-0.8.3 bugfix
  packages from fontconfig.org into XFree86 4.3.0.  This fixes a variety of
  Xft/Xrender bugs scattered throughout bugzilla against many GNOME and other
  applications, etc. (#99468, 99469)

* Mon Aug 18 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-20
- Disabled patches XFree86-4.3.0-revert-en_US.UTF-8-Compose.patch and
  XFree86-4.3.0-en_US.UTF-8-Compose-safer.patch now to provide stock XFree86
  en_US.UTF-8 compose table.  It had been disabled days before Red Hat Linux 9
  went gold in order to minimize the risk factor of the change due to lack of
  widespread beta testing.  Upstream X has not received bug reports about any
  problems caused by the change so it seems safe.  It also should provide
  enhancements to some subset of users, and might fix some problems that have
  been reported to us, which might not be present in stock 4.3.0.  Now is a
  safer time to enable this change than 3 days before our gold release of
  RHL 9.  ;o)

* Thu Aug 14 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-19
- Added XFree86-4.3.0-xkb-broken-modifiers-be-am-CVS10956.patch to fix modifier
  bug in be and am keymap files (#87679)
- Added XFree86-4.3.0-xkb-it-keymap-update-CVS10957.patch to fix bugs in
  Italian keymap files (#88080)
- Added XFree86-4.3.0-xkb-hr-keymap-fixes-CVS10967.patch to fix a small issue
  in the hr keymap files, and add a new hr_US keymap.
- Added XFree86-4.3.0-xkb-broken-capslock-fix-CVS11006.patch to fix bug in
  DVORAK (and other) keymap files which breaks capslock. (#87494)
- Added XFree86-4.3.0-xkb-ru-group-number-fix-CVS11092.patch to fix broken
  group number in russian map
- Added XFree86-4.3.0-xkb-ua-add-missing-letters-fix-CVS11134.patch to add
  missing letters to Ukranian keyboard map
- Added XFree86-4.3.0-xkb-multilayout-modifier-fix-CVS11137.patch workaround
  for problems that arise when in multi-layout map different modifier keysyms
  share the same key
- Added XFree86-4.3.0-xkb-it-small-fix-CVS11150.patch which contains a small
  fix for the Italian layout
- Added XFree86-4.3.0-xkb-us_intl-and-other-fixes-CVS11216.patch to add Euro
  sign support to us_intl keyboard map.  Patch also fixes various other xkb
  bugs.  (#91630)

* Thu Jul 17 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-18
- Disabled SDK temporarily as it does not work on all architectures
- Added XFree86-4.3.0-mouse-draglock-fix-CVS10885.patch to fix mouse draglock
  issue with buttons greater than 4
- Added XFree86-4.3.0-restore-underline-position-in-freetype-CVS10891.patch
  which should fix some issues with mozilla in bugzilla
- Added XFree86-4.3.0-fbdev-mode-validation-segv-fix-CVS10893.patch to fix SEGV
  in fbdev's mode validation
- Added XFree86-4.3.0-vidmode-memleak-fixes-CVS10895.patch to fix various
  memory leaks and uninitialized struct fields in vidmode extension

* Mon Jul 14 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-17.1
- Enabled the XFree86-sdk subpackage conditional so we have the SDK

* Thu Jul 10 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-17
- Added Jakub Jelinek's libGL optimization patch, which allows parts of libGL
  to be built PIC without affecting performance, thus allowing apps linked to
  libGL to be prelinked (XFree86-4.3.0-redhat-libGL-opt.patch) as well as other
  optimizations
- Toggled with_debuglibs off so X doesn't take 10 years to compile

* Wed Jul 09 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-16.EL
- Rebuilt 4.3.0-16 as 4.3.0-16.EL for Red Hat Enterprise Linux development

* Wed Jul 09 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-16
- Updated to XFree86-4.3.0-xf-4_3-branch-2003-07-09.patch to pick up latest
  fixes from CVS stable branch "xf-4_3-branch", including:
  - Fix repeated image problem when using a vesa video mode before starting
    the Xserver on the S3 Trio3D cards
  - Fix for a crash if a scalable font has a bitmap entry in fonts.dir
    (#5687, Bugzilla #332, Juliusz Chroboczek).
  - Fix for xfs crashes in Freetype backend (Bugzilla #242, Juliusz Chroboczek).
  - Pull twm fixes (signal handler, empty windows menu) from CVS head
- Added XFree86-4.3.0-libXi-freeze-fix-CVS11329.patch to fix a deadlock in
  libXi where is called _XLockDisplay() twice when calling an Xi function that
  calls XGetExtensionVersion() (Bugzilla #260, Bastien Nocera, Owen Taylor)
- Added XFree86-4.3.0-ps2-mouse-resolution-fix-CVS11329.patch to change PS/2
  mouse resolution to 8 counts/mm as some broken mice have problems with other
  values (Windows uses 8)
- Added XFree86-4.3.0-xkbuse-avoid-roundtrip-CVS11329.patch to correct a
  precedence problem in test in xc/lib/X11/XKBUse.c XkbUseExtension(). This
  avoids an extra round trip during application startup (Bugzilla #473, Owen
  Taylor)
- Added XFree86-4.3.0-ia64-slowbcopy.patch by John Dennis <jdennis@redhat.com>
  to insert a short delay in the xf86SlowBcopy() routine and prevent PCI bus
  lockups on ia64 which were observed with the nv driver (#98139)

* Mon Jun  9 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-15.1
- Added XFree86-4.3.0-via-driver-cvs20030611.tar.bz2 snapshot from XFree86 CVS
  to add support for the VIA EPIA onboard Castlerock CLE266 video chipset

* Fri Jun  6 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-15
- Removed "#!/bin/bash" from top of specfile as midnight commander 4.6.0 now
  has built in rpm specfile highlighting!  YaY!
- Added XFree86-4.3.0-mga-enable-video-rom-before-using.patch to fix long
  standing bug in mga driver which causes an MCA on Alpha and likely other
  platforms as well (#91711)

* Tue Jun  3 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-14.EL
- Rebuild 4.3.0-14 as 4.3.0-14.EL for Red Hat Enterprise Linux development

* Tue Jun  3 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-14
- Added XFree86-4.3.0-ia64-pci-infinite-loop.patch fix for a problem that
  occurs while doing a pci scan on Intel Tigers which leaves pci data structure
  with multiple root buses (primary == -1) causing an infinite loop, for now
  exit the loop when primary < 0  -  John Dennis <jdennis@redhat.com>

* Wed May 28 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-13.1
- Remove X server symlink check from xfs initscript for bug (#54630)

* Wed May 28 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-13
- Updated to XFree86-4.3.0-xf-4_3-branch to pick up the latest fixes from the stable
  XFree86 4.3.0 branch including
  - Fix programming error in ix86 motherboard chipset determination
  - Workaround for broken devices that do not implement the header type field
    in their PCI configuration space
  - Fix infinite loop that occurs on systems whose PCI configuration space
    does not advertise a host bridge 
  - Fix to prevent PCI and CardBus resets when VT switching
  - Set Mesa hooks to flush vertices on state changes in Radeon 3D drivers,
    which I believe fixes (#91784)
  - Fix lockup on server reset in radeon driver
  - Check for NULL tObj in the i830 3D driver TexEnv function.  This
    fixes a FlightGear crash
  - Prevent a SIGFPE with the glint/pm3 driver when attempting to display
    an XVideo image less than 8 pixels wide
  - Fix a SEGV that can happen with Riva128 cards
  - Fix SiliconMotion driver for mode switching and SEGV problem when
    initializing Xv functionality (XF86 #50)
  - i810/815 depth buffer needs to be a multiple of the tile size.  This fixes
    3D corruption near the bottom of the screen at 800x600@16bpp (XF86 #283)
  - Fixed Imakefiles so the driver SDK builds again
  - Fix XDMCP queries in xdm on systems using getifaddrs() (XF86 #277)
- Fixed xfs rpm preinstall script to ingore errors and redirect all output
  to /dev/null.  This was accidentally removed in a prior build, and causes
  xfs installation to fail.  (#91822 & 91706,91707,91733,91756)
- Added XFree86-4.3.0-savage-bugfix-from-xf-4_3-branch-2003-05-28.patch which
  is extracted from xf-4_3-branch and reapplied on top of our 1.1.27mh driver
  since we have updated this driver but do not want to lose fixes coming from
  the stable branch.
- Dropped patches that are now included in the stable branch:
  XFree86-4.3.0-radeon-irq-gen-lockup-from-cvs.patch,
  XFree86-4.3.0-radeon-dualhead-cursor-crash-from-CVS.patch
- Disabled XFree86-4.3.0-siliconmotion-Xv-stability-fix.patch as it fails to
  apply now.  Pending future investigation as it is non-critical anyway.
- Added XFree86-4.3.0-redhat-lock-version.patch, enabled it, and locked down
  the version to 4.3.0 (currently stable branch is 4.3.0.1)

* Mon May 26 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-12
- Enabled with_debuglibs now so that the libraries are debuggable during
  development, since it is not possible to have .debuginfo packages for X for
  various complex technical reasons, and it wont likely be possible for quite
  some time unfortunately.  The XFree86-libs package will get much larger due
  to this change, so I may have to revert it if people complain, or if it slows
  down anything.  This is a *TEMPORARY* solution, and will be removed sometime.
- HasFontconfig seems to work now, so I am using it instead of UseFontconfig
  to see if anything breaks in rawhide
- Removed with_freetype2 macro, and all conditional code using it throughout
  the specfile, as we never want to include the XFree86 freetype2
- Added missing Provides: xpm back to XFree86-libs package which got sideswiped
  due to the conditionalized with_freetype2 junk during development
- Made triggerin script conditionalize referencing rstart dir

* Fri May 23 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-11.2
- Disabled rstart, as it is probably not even used nowadays.  People should
  be using ssh/rsh or some other modern mechanism for running remote X apps.
- Change UseFontconfig to HasFontconfig to test if it works

* Wed May  7 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-11
- Define "XF86Server NO" on s390, s390x, ppc64, as we do not ship X servers on
  these platforms.  We use a 32bit X server on ppc64.
- Wrap all X server modules, docs, config files, man[45]/*, include/*.h with
  with_Xserver in file lists so that things are properly packaged on the archs
  that we do not ship Xserver on (s390/s390x/ppc64)

* Tue May  6 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-10.1.EL
- Update XFree86-4.3.0-ppc64-support-v3.patch to -D__powerpc__ on ppc64 or
  Radeon driver explodes while building
- Remove -fno-strength-reduce from x86 and x86_64 host.def optimization flags
- Added ppc64, ia64 host.def optimization flag overrides, defaulting them to
  their existing settings

* Tue May  6 2003 Bill Nottingham <notting@redhat.com> 4.3.0-10
- Updated XFree86-4.3.0-elfloader-linux-non-exec-stack-v2.patch to fix elfloader
  to page align addresses it passes to mprotect

* Mon May  5 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-9
- Disable xterm from building, as it is now shipped in its own separate package
- Build 4.3.0-9 in rawhide and 4.3.0-9.0.EL for RHEL

* Fri May  2 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-8.3
- Added XFree86-4.3.0-Xserver-includes-ansify-prototypes.patch to ansify
  remaining function prototypes in the X server include dir
- Added XFree86-4.3.0-ppc64-support-v2.patch which contains some more complete
  updates from SuSE for PPC64, replacing XFree86-4.3.0-ppc64-support.patch
- Set HasAgpGart NO for ppc64
- Added new macro with_Xserver to conditionalize the inclusion of the X server,
  driver and extension modules, and define it to 0 for s390, s390x, ppc64
- Updated file lists to use with_Xserver macro instead of ifnarch s390/s390x

* Fri May  2 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-8.RHEL.1
- Do not install or ship mmapr, mmapw, pcitweak, scanpci, libOSMesa.so.4.0,
  pcitweak.1x.gz, or scanpci.1x.gz on ppc64, s390 or s390x

* Fri May  2 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-8
- Enable XFree86-4.3.0-elfloader-linux-non-exec-stack.patch again, and remove
  ifnarch x86_64 on XFree86-4.3.0-xlib-dual-malloc-memleak-lcPrTxt.c.patch and
  XFree86-4.3.0-craptastic-cast.patch
- Disable XFree86-4.3.0-missing-SharedXfooReqs.patch temporarily as it breaks
  xauth + ssh on s390, and thus requires deeper investigation
- Build 4.3.0-8 for rawhide, and 4.3.0-8.RHEL.0 for RHEL devel

* Thu May  1 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-7.el.1
- Replaced XFree86-4.3.0-ia64-new-elfloader-relocations.patch with a new
  version that John added to fix (#89976)
- Added XFree86-4.3.0-radeon-ia64-preint10.patch from John Dennis, to solve a
  problem which is yet to be announced. ;o)  Will update comment once I have
  details.

* Thu Apr 24 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-7.el.0
- Added XFree86-4.3.0-ia64-new-elfloader-relocations.patch for ia64 ELF
  relocations for http://bugs.xfree86.org/cgi-bin/bugzilla/show_bug.cgi?id=195
- Replaced XFree86-4.3.0-missing-SharedXfontReqs.patch with a new patch
  XFree86-4.3.0-missing-SharedXfooReqs.patch that solves similar problems for
  many other X libraries on Linux, and should fix (#89860)

* Thu Apr 24 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-6
- Apply XFree86-4.3.0-xf-4_3-branch-2003-04-26.patch to update to the latest
  fixes from the xf-4_3-branch stable branch of XFree86 CVS
- Removed XFree86-4.3.0-radeon-R300-fix-pll-value-from-cvs.patch as it is
  incorporated into the stable branch above:
- Added XFree86-4.3.0-libXfont-null-pointer-dereference-fix.patch which fixes
  a null pointer dereference in libXfont
- Added XFree86-4.3.0-siliconmotion-Xv-stability-fix.patch to fix siliconmotion
  driver for mode switching and SEGV problem when initializing Xv functionality
- Added XFree86-4.3.0-Xserver-non-pc-keyboard-fix.patch to fix problem on non-PC
  keyboards caused by changes to make SysRq generate the same keycode as PrtScrn
- Added XFree86-4.3.0-nv-graphic-engine-setup-reset-fix.patch to stabilize
  VT switching and server startup/shutdown
- Added XFree86-4.3.0-nv-new-chip-ids.patch which adds new PCI IDs for
  GeForce FX and Quadro FX
- Added XFree86-4.3.0-nv-riva-dualhead-fixes.patch to fix problems that can
  arise on newer chipsets on dualhead configurations
- Added XFree86-4.3.0-nv-filter-imagerect-pixel-range.patch to fix a problem
  where the HW filter would include pixels outside of the image rect being
  displayed.
- Added XFree86-4.3.0-nv-dpms-workaround-for-broken-monitors.patch
- Added XFree86-4.3.0-nv-unresolved-symbols.patch to add missing vgaHWUnmapMem
- Added XFree86-4.3.0-rendition-disable-cause-of-SEGV.patch
- Added XFree86-4.3.0-trident-half-a-jittered-screen.patch to fix bug in the
  trident driver that caused old cyber 9382/9385 chipsets to display a half
  jittered screen
- Added XFree86-4.3.0-Xserver-limit-440EX-440LX-to-32-pci-busses.patch
- Added XFree86-4.3.0-xaa-trapezoid-filling-bug.patch in a rare 8x8 pattern
  fill case in XAA generic code
- Added XFree86-4.3.0-Xserver-Xineramify-Xscreensaver-extension.patch to make
  screensavers work in dualhead Xinerama mode
- Added XFree86-4.3.0-Xlib-XOpenDisplay-SEGV-fix.patch to fix many places in
  Xlib which could segfault due to not checking to see if it has received as
  much data as needed, causing it to potentially read uninitialized memory
- Added XFree86-4.3.0-mga-manpage-overlay-option.patch which better documents
  the Matrox Overlay option as many people are confused by this
- Added XFree86-4.3.0-r128-unresolved-symbols.patch to add various symbols
  missing from symbol lists that generate errors when DRI is disabled

* Thu Apr 24 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-5
- Removed XFree86-4.0.1-alpha-pcibus-lemming.patch as it is not clear what it
  actually does, is not documented anywhere what if any bug it fixes, and
  nobody remembers what it was for, and we have not applied it for quite a
  while now either.
- Added XFree86-4.3.0-radeon-irq-gen-lockup-from-cvs.patch which works around
  a lockup that can occur on server shutdown/restart with the radeon driver due
  to bugs in DRM IRQ handling in the kernel
- Added XFree86-4.3.0-radeon-support-from-ATI-backport-from-CVS.patch which is
  an amalgamation of patches done by Hui Yu at ATI which implement:
  Radeon IGP320/330/340 support (2D only), RV280 (9200/M9+) support, Fix for
  some M9 laptop panels, Improved version of monitor detection code, Fixed bug
  for two or more radeon cards, Man page updates, Workaround for double scan
  modes problem at high resolutions, Overlay scaling problem when RMX is used,
  and also PPC updates for Radeon from Michel Daenzer
- Replaced XFree86-4.2.99.902-ati-radeon-alan-legacy-vga.patch with new
  XFree86-4.3.0-redhat-radeon-forcelegacyvga-for-alan.patch reimplementation
  around the new radeon driver code.  Needs testing by Alan.

* Tue Apr 22 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-4
- Enable _unpackaged_files_terminate_build & _missing_doc_files_terminate_build
  options and clean up remaining file failures so we are swooshy clean now
- Update %%install file deletion list for s390/s390x/ppc
- Moved DELETE FILES section after STRIP FILES section in specfile
- Added XFree86-4.3.0-redhat-xlib-linux-fix-avoiding-substance-abuse-job.patch
  as a hideous kludge to work around the even more ugly hideous Solaris
  broken weirdness junk triggering off _LP64 in XlcDL.c

* Sun Apr 20 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-3.9
- Renamed TinyX subpackage to kdrive
- Made all kdrive X servers setuid root in filelists

* Sat Apr 19 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-3.8
- Added XFree86-4.3.0-xbiff-file-heirarchy-standard.patch for FHS 2.2
  compliance of xbiff
- When not shipping config tools, defining "BuildXFree86ConfigTools NO" in
  host.def speeds up build
- Added XFree86-4.3.0-disable-building-apps-we-do-not-ship.patch to disable
  building applications we do not ship such as xedit, xman, xmh
- Moved include/pixmaps from XFree86-devel to XFree86-xf86cfg where it belongs,
  although this stuff really should not be in _x11includedir

* Fri Apr 18 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-3.7
- Added PPC64 support with XFree86-4.3.0-ppc64-support.patch

* Sat Apr 12 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-3.6
- Added XFree86-4.3.0-ati-radeon-dualhead-cursor-crash.patch to fix radeon
  dualhead crash problem when mouse cursor crosses screens (#87854,88748)

* Wed Apr  9 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-3.5
- Added XFree86-4.3.0-missing-SharedXfontReqs.patch to try and fix (#88355)

* Fri Apr  4 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-3.4
- Added XFree86-4.3.0-redhat-bug-report-address-update.patch which changes the
  X server bug report messages on where and how to file bug reports

* Fri Apr  4 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-3.3
- Added XFree86-4.3.0-ati-r128-Xv-ecp-divisor.patch which fixes a problem on
  Rage 128 in which high resolution images displayed with the XVideo extension
  have weird "green" noise in them (#88033)
- Added XFree86-4.3.0-makefile-fastbuild.patch to bypass the main Makefile
  clean and depend targets when make World is ran

* Fri Mar 14 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-3.2
- Added XFree86-4.3.0-xlib-dual-malloc-memleak-lcPrTxt.c.patch which fixes
  a memleak in Xlib caused by double malloc. Not being applied to x86_64 yet,
  waiting for approval to fix (#86108)
- Added XFree86-4.3.0-craptastic-cast.patch to non-x86_64, just a cosmetic
  casting fixup of (off_t)(off_t) to just (off_t)

* Sat Mar  8 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-3.1
- Updated XFree86-4.3.0-glint-unresolved-symbols.patch to add several more
  missing DRM symbols that another user reported when DRI is not used.  This
  compliments the existing symbol name additions with an even more complete
  list, and should fix the problems reported in bug (#85191) as well as
  adding to the bugfix for (#85805)
- Added XFree86-4.3.0-elfloader-linux-non-exec-stack.patch to patch the XFree86
  ELF loader to work properly on Linux with a kernel with a non-exec stack,
  however this patch is disabled on x86_64 and possibly other architectures for
  now

* Sat Mar  8 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-3
- Added XFree86-4.3.0-ati-radeon-R300-fix-pll-value.patch which fixes a bug
  in the Radeon driver (on all archs) that occurs only on R300 chips (Radeon
  9500/9700) due to a broken PLL define in radeon_regs.h (#85784)
- Re-enabled XFree86-4.3.0-glint-unresolved-symbols.patch on x86_64 as it is
  approved now by msw.

* Fri Mar 7 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-2.2
- Modified xdm.pamd and xserver.pamd to remove explicit paths with hard coded
  /lib dir, since it is in /lib64 on lib64 archs, and so pam console ownership
  is screwed without this change.  Similar problems were fixed in September in
  many other packages, but no bug reports were filed in bugzilla so I was aware
  of this problem, so it remained broken until I just discovered it myself
  while trying to debug a screensaver related issue (#85795)
- I have made the XFree86-4.3.0-glint-unresolved-symbols.patch patch added in
  4.3.0-2.1 ifnarch x86_64 to exclude this patch from x86_64 builds, even
  though it is an obviously correct and harmless bugfix on all architectures
  and should be applied (#85805)

* Sun Mar 2 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-2.1
- Added XFree86-4.3.0-glint-unresolved-symbols.patch to fix some unresolved
  drm symbols in the glint driver.  Possible fix for (#85191)?
- Removed unused patch - XFree86-4.0.99.3-Xwrapper.patch (#85336)
- Renamed xdm-4.0-servonly.patch to XFree86-4.0-xdm-servonly.patch

* Thu Feb 27 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-2
- Removed some junk comments from specfile, the commented out old cursors
  and xtrap-clients subpackage junk and a few other things
- Corrected a mistake in OTF font directory file list that was named TTF
  instead of OTF, causing a ghost file to be missed
- Verified all file lists to be accurate just to doublecheck the 4.3.0 release
  is not accidentally missing any files
- Removed mharris_noclean_mode developmental cruft from specfile, as I do not
  use it in my developmental builds anymore and wont need it after
  transitioning to _unpackaged_files_terminate_build mode
- Removed XFree86-4.2.99.901-012_r128_xv_btyeswap_fix.patch as current CVS
  fixes the problem in a different way, and this patch reverts that
- Removed the changes deemed potentially unsafe from en_US.UTF-8 compose
  table to have minimalistic changes

* Thu Feb 27 2003 Mike A. Harris <mharris@redhat.com> 4.3.0-1
- Updated to official XFree86 4.3.0 release via CVS export of xf-4_3_0

* Wed Feb 26 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030226.0
- Updated CVS snapshot to 4.2.99.902-20030226, manually checked each diff
  and verifying each code change is safe.  No questionable changes today.

* Tue Feb 25 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030225.0
- Updated CVS snapshot to 4.2.99.902-20030225, manually checked each diff,
  accept all documentation updates, verified each change.
- Added XFree86-4.3.0-revert-en_US.UTF-8-Compose.patch to back out changes
  made in CVS to en_US.UTF-8 Compose tables as they can not be easily
  verified to be 100% correct and regressionless at this point
- Removed XFree86-4.2.99.902-xft-version-bump.patch as it is in CVS update

* Mon Feb 24 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030224.2
- Added XFree86-4.2.99.902-xft-version-bump.patch to fix Xft library .so
  version from 2.0 to 2.1 since it had an addition of UTF-16 APIs.  This
  fixes http://bugzilla.mozilla.org/show_bug.cgi?id=175108

* Mon Feb 24 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030224.1
- Updated my radeon XFree86-4.2.99.902-ati-radeon-dpms-on-dvi-v2.patch patch
  to play things a bit safer by removing MT_LCD.  There is a more appropriate
  and robust way to do this that I will examine in the future.
- Removed unused WithNewCyrixDriver crud from specfile
- Removed unused with_bk crud from specfile
- [SECURITY] Added XFree86-4.3.0-xterm-can-2003-0063.patch to fix xterm
  titlebar issue reported in CAN-2003-0063 by disabling the feature that
  allows the problem.

* Mon Feb 24 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030224.0
- Updated CVS snapshot to 4.2.99.902-20030224, which makes another cursor
  glitch fix to generic code, and fixes an obvious vgaHW locking bug.  The
  rest are minor cosmetics and documentation updates.
- Add credit to GB18030 patches to Yu Shao and James Su, whom both worked on
  this support over time.

* Sun Feb 23 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030223.0
- Updated CVS snapshot to 4.2.99.902-20030223
- CVS checkin 946 fixes GL debugging junk printed to screen (#84347)
- More CVS fixes for Radeon ARGB cursor code from Keith and Michel Daenzer
  (#84691)
- CVS checkin 939 Check pScrn->vtSema before calling xf86SetCursor() from
  xf86CursorCloseScreen().  This avoids a segfault at exit with some
  drivers, and I believe should fix the problem reported in (#79678,84689)
- CVS checkin 938 fix adding FP native mode for Radeon (Hui Yu@ATI, 
  Kevin Martin).  - This should fix problems people have reported on various
  Radeon Mobility laptops of being unable to select video modes, etc.  I
  can not get into bugzilla to get the bug IDs currently.
- CVS checkin 937 - Initialize I2C when primary head has an invalid DDC type
  for the Radeon driver (Hui Yu@ATI).  This should fix some of the DDC probe
  related problems some users experience during installation which cause the
  installer to go bonkers.

* Fri Feb 21 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030220.3
- Bump kernel-drm requirement to 4.3.0

* Fri Feb 21 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030220.2
- Implemented XFree86-4.2.99.902-ati-radeon-dpms-on-dvi.patch for DPMS on
  LCD/DFP panels on Radeon driver (#80629)

* Fri Feb 21 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030220.1
- Removed Xft/Xft-devel goofup from bad specfile diff application
- Added XFree86-4.2.99.902-savage-revert-vbe-change-from-X-cvs.patch to back
  out a VBE change done in XFree86 CVS sometime in the last couple of months,
  which I believe causes the Savage MX probs (#72476,80278,80346,80423,82394)

* Fri Feb 21 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030220.0
- Updated CVS snapshot to 4.2.99.902-20030220
- Removed integraged now: XFree86-4.2.99.901-debian-dont_vtswitch_option.patch,
  XFree86-4.2.99.901-017_neomagic_manpage_fixes.patch, XFree86-4.2.99.901-018_fontenc_null_ptr_deref_fix.patch,
  XFree86-4.2.99.901-020_proxymgr_manpage_fixes.patch, XFree86-4.2.99.901-035_xim_memleak_fix.patch,
  XFree86-4.2.99.902-ati-radeon-buildfix.patch

* Thu Feb 20 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030218.3
- Ok, no kidding this time.  I really really mean it, the new savage driver
  is definitely in this build for sure for sure.  No kidding around this time.
- Created and added XFree86-4.2.99.902-savage-Imakefile-vbe-fixup.patch,
  XFree86-4.2.99.902-savage-1.1.26cvs-1.1.27t-fixups.patch,
  XFree86-4.2.99.902-savage-1.1.26cvs-1.1.27t-accel-fixup.patch
- Added XFree86-4.2.99.902-redhat-version-change-notification.patch which does
  not actually do anything except fail to apply cleanly when the XFree86
  version changes, thus alerting me to change the spec file Version field, and
  update the patch

* Thu Feb 20 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030218.2
- Actually ENABLE the new savage driver with rpm spec conditional, since I
  moronically did not enable it the first time

* Tue Feb 18 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030218.1
- Implemented a new radeon driver config file option "ForceLegacyCRT" in
  XFree86-4.2.99.902-ati-radeon-alan-legacy-vga.patch to allow Alan to use an
  ancient VGA mono monitor, and documented it in the radeon manpage (#69976)

* Tue Feb 18 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030218.0
- Updated CVS snapshot to 4.2.99.902-20030218
- Added Red Hat buildsystem BuildConflicts line to test for disk space
- Added Red Hat buildsystem BuildProvides line to hint that up to 8 CPUs can
  be used effectively when compiling XFree86
- Added XFree86-4.2.99.902-ati-radeon-buildfix.patch to fix ATI Radeon driver
  build problem

* Mon Feb 17 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030217.1
- Update savage driver to Tim Roberts tried and true faithful savage driver
  new release 1.1.27t (#72476,80278,80346,80423,82394)

* Mon Feb 17 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.902-20030217.0
- Updated CVS snapshot to 4.2.99.902-20030217 - Release Candidate 2
- Dropped XFree86-4.2.99.901-xlib-hang.patch, XFree86-4.2.99.901-argb-cursor-render-bugfix-keithp.patch,
  XFree86-4.2.99.901-xft-_XftSmoothGlyphMono-endless-loop-fix.patch,
  XFree86-4.2.99.901-xft-crash-with-non-render-server-from-keithp.patch

* Thu Feb 14 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030213.1
- Added XFree86-4.2.99.901-argb-cursor-render-bugfix-keithp.patch, yet another
  ARGB cursor bugfix.  This one is in the render code.  It should fix problems
  reported by msw and others of random blobs and stuff following the cursors
  around, in particular when using the 'core' cursor theme
- Added XFree86-4.2.99.901-xft-_XftSmoothGlyphMono-endless-loop-fix.patch
  patch to fix endless loop in libXft Nalin found while investigating (#80414)
- Added XFree86-4.2.99.901-xft-crash-with-non-render-server-from-keithp.patch
  to fix bug http://bugzilla.mozilla.org/show_bug.cgi?id=175108 reported to me
  by blizzard that crashes mozilla, which is also found in (#80414)

* Thu Feb 14 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030213.0
- Updated CVS snapshot to 4.2.99.901-20030213, fixing several critical bugs
- Disabled keiths argb radeon cursor patch as CVS has some other fix now
- New CVS also fixes the same problem on r128 and mach64 mouse cursor that
  the radeon had (#83284,83768)
- Disabled revert-xkb-patch-865 as the problem with VTswitching is fixed now
  in this snapshot (#84306)

* Thu Feb 13 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030212.0
- Updated CVS snapshot to 4.2.99.901-20030212

* Thu Feb 13 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030211.3
- Added XFree86-4.2.99.901-dont-install-Xcms.txt.patch to not install Xcms.txt
  by default, under recommendation of Keith Packard
- Added Conflicts: Xft to -libs, and Conflicts: Xft-devel to -devel, and
  removed <= 2.0 versioning off Obsoletes: Xft and Xft-devel to try and fix
  problem where if you upgrade an 8.0 system to 4.2.99.x the Xft2 library
  becomes unusable (#77838)
- Created XFree86-4.2.99.901-revert-xkb-patch-865.patch to revert the changes
  from Ivan Pascal that Daved Dawes checked into CVS in XFree86 CHANGELOG entry
  865 to fix autorepeat on keypad /*-+ and fix mouse-keys, and other things,
  which had the result of totally breaking VT switching from terminal to
  terminal after switching out of X

* Thu Feb 13 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030211.2
- Added XFree86-4.2.99.901-ati-radeon-argb-cursor-fix-from-keithp.patch from
  Keith, and disabled argb cursor patch for radeon (#83768)

* Thu Feb 13 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030211.1
- Added XFree86-4.2.99.901-debian-dont_vtswitch_option.patch which adds a new
  ServerFlags option "DontVTSwitch", to allow disabling of VT switching via
  CTRL-ALT-Fn written by Branden Robinson for Debian
- Added XFree86-4.2.99.901-ati-radeon-ia64-pagesize.patch which removes the
  hardcoded compile-time pagesize in the radeon and r128 drivers, replacing
  it with runtime detection with getpagesize() since platforms like ia64,
  alpha and others that can have different runtime page sizes will work
- Added XFree86-4.2.99.901-xlib-hang.patch that fixes a bug in _XEventsQueued()
  that causes an 'event reader lock' of another thread to be released which
  can cause a hang and keyboard lockup in KDE. For example, using KDE CVS and
  xine CVS, by playing a movie clip with Noatun (hang and keyboard lockup
  after playback has stopped).
- Update s3virge driver documentation for 4.3.0
- Added XFree86-4.2.99.901-007_fix_xfree86_man_version_string.diff to fix up
  XFree86 version string in manpages
- Added XFree86-4.2.99.901-008_doc_extensions_fix.diff to sanitize filename
  extensions of XFree86 documentation for consistency
- Added XFree86-4.2.99.901-012_r128_xv_btyeswap_fix.patch patch to fix Xvideo
  extention support for YUV2 and UYVY in r128 driver on big-endian processors
- Neomagic manpage update XFree86-4.2.99.901-017_neomagic_manpage_fixes.patch
- Added XFree86-4.2.99.901-018_fontenc_null_ptr_deref_fix.patch which fixes a
  null pointer dereference in the fontenc library
- Added XFree86-4.2.99.901-024_r128_and_radeon_vgahw_independence.patch to fix
  problem on some architectures that do not allow legacy VGA hardware access
- Added XFree86-4.2.99.901-027_ati_driver_message_cleanups.patch to fix up the
  formatting of a few ATI driver startup messages
- Added XFree86-4.2.99.901-028_fbdev_depth24_support.patch to fix fbdev 24bit
  depth support
- Added XFree86-4.2.99.901-035_xim_memleak_fix.patch to fix a memory leak in
  the XIM code

* Tue Feb 11 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030211.0
- Updated CVS snapshot to 4.2.99.901-20030211

* Tue Feb 11 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030209.2
- Moved TTF and OTF subpackage fonts.* and other auxilliary ghost files into
  the base-fonts subpackage so the dirs are always present, even if the
  truetype and/or syriac-fonts packages are not installed, and to prevent
  multiple packages from claiming ownership of the same files (#83913)
- Added Conflicts lines for the above change
- Added Buildrequires: ed  for fontconfig
- Removed unapplied ancient XFree86-4.1-xinerama.patch workaround
- Added XFree86-4.2.99.901-xauth-diskfull.patch which fixes a bug where xauth
  may write an incomplete .xauth file and delete the old one if there is
  insufficient disk space (Harald Hoyer - #84036)

* Mon Feb 10 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030209.1
- Added more with_foo buildtime conditionals for standardization
- Cleaned up post buildroot-install time file deletions of unpackaged files

* Mon Feb 10 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030209.0
- Updated CVS snapshot to 4.2.99.901-20030209
- Added XFree86-4.2.99.901-xkb-sysreq.patch to fix GNOME printscreen issue
  due to bad mapping of sysreq (#80373)
- Removed XFree86-4.2.99.4-ati-r128-full-chipset-support.patch as it got
  integrated into upstream sources
- Added XFree86-4.2.99.901-ati-r128-chip-names-touchup.patch to make R128 chips
  that we are not sure are AGP or not show up as "(AGP?)", to heighten the
  chance of a user noticing it and providing us with this information.
- Removed XFree86-4.2.99.4-ati-xf86PciInfo-chip-support-update.patch as it
  is integrated upstream now

* Thu Feb  6 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030206.0
- Updated CVS snapshot to 4.2.99.901-20030206
- New Intel i865 integrated video support is in this snapshot
- Made XFree86-4.2.99.901-ati-radeon-missing-symbol-drmScatterGatherAlloc.patch
  to fix a bug reported on devel@xfree86.org, also submitted it

* Wed Feb  5 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030205.0
- Updated CVS snapshot to 4.2.99.901-20030205
- Removed integrated patches XFree86-4.2.99.3-encodings-Imakefile-fix.patch
- Add XFree86-4.2.99.901-ati-radeon-fix-broken-argb-cursors.patch to hopefully
  fix all the Radeon Xcursor related weirdness (#78231,80445)

* Wed Feb  5 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030203.2
- Cleanups of specfile, host.def
- Ported parallelmake patch to current tree, and experimented with it but
  could not get it working properly so it is disabled again

* Tue Feb  4 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030203.1
- Added XFree86-4.2.99.901-chips-default-to-swcursor-on-65550.patch to
  default to swcursor on C&T 65550 for bug (#82438)
- Improved chips-default-to-noaccel-on-69000 patch to be more correct for (#74841)

* Tue Feb  4 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.901-20030203.0
- Updated CVS snapshot to 4.2.99.901-20030203
- Added BuildBethMarduthoFonts YES as XFree86 CVS somehow weirdly stopped
  building Syriac fonts
- Disable mga-xinerama-G450-issue fix as it is believed to be fixed in CVS now
  with CHANGELOG log entry 818.  Needs confirmation to be sure.

* Mon Feb  3 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.4-20030129.5
- Updated XFree86-4.2.99.4-ati-r128-full-chipset-support.2.patch to remove
  stupid ANSI trigraphs and escape them properly.

* Sat Feb  1 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.4-20030129.4
- Wrote XFree86-4.2.99.4-ati-r128-full-chipset-support.patch to add 2D and 3D
  support for 30 previously unsupported ATI Rage 128 chips including various
  Rage 128 Pro, Rage 128 Pro Ultra chips 

* Sat Feb  1 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.4-20030129.3
- Wrote XFree86-4.2.99.4-ati-xf86PciInfo-chip-support-update.patch to update
  the PCI ID list for further driver update patches to follow
- Wrote XFree86-4.2.99.4-ati-radeon-8500-9100-firegl-8700-8800-update.patch
  to add 2D and 3D support for 8 previously unsupported chips in the ATI R200
  chip family including various Radeon 8500, FireGL 8700/8800, and the new
  Powered by ATI Radeon 9100 from Sapphire
- Added XFree86-4.2.99.4-ati-radeon-TV_DAC_CNTL.patch minor code cleanup

* Thu Jan 30 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.4-20030129.2
- Added XFree86-4.2.99.4-locale-alias-openi18n.patch from Leon Ho, required
  for openi18n compliance
- Cleaned up post build/install file/dir deletions to move gradually towards
  being able to turn on _unpackaged_files_terminate_build

* Thu Jan 30 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.4-20030129.1
- Removed handhelds cursor theme
- Added XFree86-4.2.99.3-ati-chip-support-update.patch, partial support patch
  for ATI Rage 128, Radeon, etc. hardware previously unsupported

* Thu Jan 30 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.4-20030129.0
- Update CVS snapshot to 20030129
- Removed patches present upstream now:  XFree86-4.2.99.4-xkb-se-fix.patch
  XFree86-4.2.99.4-xkb-rules-xfree86-ca_enhanced.patch
- Updated XFree86-4.2.99.4-redhat-custom-startup.patch to work with latest

* Wed Jan 29 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.4-20030121.6
- Removed from host.def HasMMXSupport, Has3DNowSupport, HasKatmaiSupport,
  and HasSSESupport after manually verifying the current default Imake config
  files enable this properly on x86 and x86_64
- Removed -fPIC from global x86_64 flags again, and force StaticNeedsPicForShared
  to YES on all architectures in host.def, instead of just on x86
- Added XFree86-4.2.99.4-IncludeSharedObjectInNormalLib.patch to fix up
  remaining issues with StaticNeedsPicForShared (#78188,82954)
- Added XFree86-4.2.99.4-x86_64-glx-nopic.patch to build GLX nopic on x86_64
  for performance reasons - as it is on x86

* Fri Jan 24 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.4-20030121.4
- Rebuilt with -fPIC temporarily for anaconda et al. on hammer

* Fri Jan 24 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.4-20030121.3
- Rebuilt without -fPIC on hammer for debugging X server

* Fri Jan 24 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.4-20030121.2
- Added more complete XFree86-4.2.99.4xkb-se-fix.patch from David Dawes to
  replace XFree86-4.2.99.4-xkb-se-asciitilde.patch if it works properly
- Obsolete XFree86-Setup (#82674)
- Added XFree86-4.2.99.4-xkb-rules-xfree86-ca_enhanced.patch to fix (#80425)

* Wed Jan 22 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.4-20030121.1
- Added XFree86-4.2.99.4-xkb-se-asciitilde.patch to fix (#80922,82097)

* Tue Jan 21 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.4-20030121.0
- Update CVS snapshot to 20030121
- Drop patches now included upstream ati-radeon-mono-8x8-accel-fix,
  mga-vbe-dvi-ddc, xmag fix
- Added missing Conflicts: XFree86-sdk < 4.2.99.3-20030115.0

* Mon Jan 20 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20030118.3
- Flagged {_x11icondir}/defaults/index.theme file as config noreplace
- Disable building on ia64 due to compiler SEGV

* Sun Jan 19 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20030118.2
- Bump kernel-drm req up to 4.2.99.3 to match new kernel DRM
- Remove -fPIC from x86_64 default opt flags, and disable ELF loader patch
- Add XFree86-4.2.99.3-Imake-make-icondir-configurable.patch to make XFree86
  Xcursor ICONDIR and XCURSORPATH build time configurable and default the
  cursors to install into /usr/share/icons
- Added new specfile directory macro _x11icondir and use it everywhere
- Made default cursor theme Bluecurve
* Sat Jan 18 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20030118.1
- Added XFree86-4.2.99.3-ati-radeon-mono-8x8-accel-fix.patch to fix mono
  8x8 color expansion issue causing mirroring on RV200+

* Sat Jan 18 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20030118.0
- Update CVS snapshot to 20030118
- Add XFree86-4.2.99.3-xmag-segv-uninitialized-pointer.patch to fix (#81966)
- Major radeon driver updates and fixes:  Fix for Mono8x8 patterns on Radeon,
  Fix for Radeon mode validation, Workaround for flickering problem with
  switching between ARGB and mono cursors on Radeons, DDCMode fix for VidMode
  extension, Panel detection bug fix for Radeon, Add Xv overlay support for
  dual headed Radeons, Fix Radeon driver 24-bit support for flat panels,
  Add Radeon 9500/Pro support, Disable CGWorkaround for non-A11 rev R300s,
  Radeon solid/dashed line fix for RV200 and newer cards, Radeon overlay
  gamma fix, Radeon LG panel fix.
- Add XFree86-4.2.99.3-elf-loader-x86_64-relocation-fixups.patch and disabled
  dllmodules to try and fix ELF relocation problem reported in bug (#81984) 

* Wed Jan 15 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20030115.1
- Add XFree86-4.2.99.3-mga-vbe-dvi-ddc.patch to support for DDC probe of DVI
  panels on Matrox hardware
- Use MakeDllModules on x86_64 as ELF loader is currently problematic

* Wed Jan 15 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20030115.0
- Update CVS snapshot to 20030115
- Move syriac fonts from TTF subdir to new OTF subdir
- Move inb inl inw ioport outb outl outw commands to XFree86 pkg from sdk

* Wed Jan 15 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20021230.7
- Added XFree86-4.2.99.3-mga-unresolved-symbols.patch to fix unresolved
  DRM symbols in mga driver for bug (#80968)

* Tue Jan 14 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20021230.6
- Added fontconfig-slighthint patch from our fontconfig package as a hack to
  allow the embeddedbitmap and xft-loadtarget patches to build correctly.
- Added XFree86-4.2.99.3-embeddedbitmap.patch
- Added XFree86-4.2.99.3-encodings-Imakefile-fix.patch to fix (#81565)

* Thu Jan  9 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20021230.5
- Add Requires: xinitrc  (#81424)
- Remove placeholder redglass cursor theme
- Disable accel on C&T 69000 XFree86-4.2.99.3-chips-noaccel.patch for (#74841)

* Tue Jan  7 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20021230.4
- Disable fc-cache in post/postun scripts except for TTF/Type1 directories.
- Created XFree86-4.2.99.3-savage-pci-id-fixes.patch to fix up the Savage
  driver PCI IDs that were missing and/or incorrect.

* Tue Jan  7 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20021230.3
- Disabled the XFree86-4.2.99.3-xft-loadtarget.patch patch as it is broken.

* Mon Jan  6 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20021230.2
- Remove xman as there are other manpage viewers, and this one seems to be
  unmaintained upstream.  Conditionalized with with_xman (#81003)
- Update dependancy on freetype to version 2.1.3-4 which contains a patch that
  a patch we are applying to Xft requires.

* Fri Jan  3 2003 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20021230.1
- Added XFree86-4.2.99.3-xft-loadtarget.patch from Owen Taylor, which is a
  patch needed for our freetype 2.1.3 package, ported forward from the 8.0 Xft
  package

* Mon Dec 30 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.3-20021230.0
- Updated CVS snapshot to version 4.2.99.3 20021230
- Added XFree86-4.2.99.2-netmouse.patch to fix mouse protocol initialization
  problem reported on XFree86 bug report list
- Removed the gtf utility, its manpage, and libxf86config.a from s390/s390x
- Removed leading "0." from specfile RELEASE field as it is unnecessary

* Wed Dec 17 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021217.1
- Disabled and removed whiteglass cursor theme as it is broken and nobody
  is likely to fix it it seems.  We will be supplying our own theme in the end
  that does not suck (#75844)

* Tue Dec 17 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021217.0
- Updated CVS snapshot to 20021217, dropped unneeded patches
- Added XFree86-4.2.99.2-xinerama-G450-issue.patch to work around mga issues
  when RENDER is used with Xinerama due to faulty Render acceleration

* Sun Dec 15 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021215.0
- Updated CVS snapshot to 20021215, dropped unneeded patches
- Update BuildRequires freetype to >= 2.1.2-7
- Added ISO8859-14 fonts for Welsh for Alan
- Disable XFree86-sdk by default for now due to nsc driver sdk issue
- define debug_package %{nil} to disable -debuginfo packages for now

* Fri Dec 13 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021210.1
- Added Buildrequires: libpng-devel for bug (#79623)

* Tue Dec 10 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021210.0
- Updated CVS snapshot to 20021210, dropped unneeded patches
- Added XFree86-4.2.99.2-mga-unresolved-symbols.patch
- Added /usr/X11R6/lib/X11/Xcms.txt to libs-data
- Changed XFree86-devel requires from fontconfig to fontconfig-devel (#79183)
- Added alpha-domain and alpha-domain2 patches back (split original in 2, and
  updated)

* Mon Dec  9 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021209.0
- Updated CVS snapshot to 20021209, dropped unneeded patches
- Numerous bug fixes, stability, and correctness fixes for the Intel 830/845G
  2D, 3D, and Xvideo support
- Updated Korean font encoding tables XFree86-4.2.99.2-korean-encoding-table-fixes.patch
- Added XFree86-4.2.99.2-20021209-cvs-update.patch to further update to
  latest CVS as David checked in a lot more stuff
- Removed patches included upstream now: XFree86-4.2.99.2-more-lib64-fixes.patch
  XFree86-4.2.99.2-disable-DRI-on-s390-by-default.patch,
  XFree86-4.2.99.2-x86_64-has-SSE-MMX-3DNOW.patch

* Mon Dec  9 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021208.1
- Updated XFree86-4.2.99.2-redhat-custom-startup.patch to handle bug (#77930)
- Added XFree86-4.2.99.2-alpha-domain.patch to fix PCI domains on alpha, and
  re-enabled building on alpha.
- Removed with_ttmkfdir conditional, all ttmkfdir sources/patches and building

* Sun Dec  8 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021208.0
- Updated CVS snapshot to 20021208, dropped unneeded patches

* Fri Dec  6 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021126.10
- Fixed XFree86-4.2.99.2-mkfontdir-perms.patch to correctly chmod 0644 (#79119)
- Added XFree86-4.2.99.2-xkb-gb-backslash-and-bar.patch to fix missing
  backslash/vertical bar keys on gb keyboard

* Thu Dec  5 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021126.9
- Enabled StaticNeedsPicForShared YES in host.def for x86.  xfree86.cf defaults
  to YES for all archs except x86, which causes problems linking X .a only libs
  into KDE/GNOME .so libs and other problems like libxkbfile.a in (#78188)
- Disabled older temporary hack XFree86-4.1-xinerama.patch to see if it is needed

* Wed Dec  4 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021126.8
- Get rid of xtrap-clients and cursors subpackages, incorporating them into
  main XFree86 package and adding an Obsoletes tag for them
- Added missing syriac-fonts post/postun scripts
- Added XFree86-4.2.99.2-omGeneric-stop-app-crashes.patch to fix problems with
  apps crashing, due to some bad juju recently checked into upstream CVS

* Wed Dec  4 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021126.7
- REALLY fix VT switch this time by making patch20007 apply as 20007 and not
  as 20006 doofus

* Wed Dec  4 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021126.6
- Added XFree86-4.2.99.2-TEMPORARY-fix-for-broken-vt-switching.patch to fix
  broken VT switching, CTRL-ALT-BS, etc...

* Tue Dec  3 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021126.5
- Re-enabled the old manual stripping policy and disabled rpm stripping as it
  has shown to not strip everything that needs to be stripped.
- Added -fPIC to global compiler options for x86_64, as static libs need to
  be built with -fPIC to be linked into shared libs

* Fri Nov 29 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021126.3
- Added XFree86-4.2.99.2-fix-CppCmd-path.patch to change the location X looks
  for cpp from /lib/cpp to /usr/bin/cpp
  
* Thu Nov 28 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021126.2
- Added "-fno-strength-reduce GccAliasingArgs" to x86 and x86_64 default
  optimization flags, and "GccAliasingArgs" to default alpha and ppc flags,
  since we override XFree86 defaults, and they include these optimizations.

* Wed Nov 27 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021126.1axp
- Add XFree86-4.2.99.2-missing-carriage-return-before-endif.patch to fix
  Alpha build failure in axpPci.c due to one backspace too many...
- XFree86-4.2.99.2-build-fixes-for-alpha.patch

* Tue Nov 26 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021126.1
- Woohoo! We now let rpm strip the XFree86 build as it no longer fries X modules
- Added "BuildRequires: rpm >= 4.0.4" for safe rpm stripping, as older versions
  of rpm will strip XFree86 modules and make them unloadable
- Added new _x11localedir macro, did search and replace cleanup
- _includedir cleanup
- Got rid of the Imake defines (BuildXinerama, BuildXineramaLibrary,
  BuildXF86DGA, BuildXF86DRI) from host.def, as they should be set properly in
  stock XFree86 configs, and if not, patched and sent upstream
- Remove ancient BuildTdfx option that has not been used/needed for ages

* Tue Nov 26 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021126.0
- Update CVS snapshot to 20021126
- Removed patches that are now upstream: XFree86-4.2.99.2-redhat-xdm-pam.patch
  XFree86-4.2.0-xkb-french-canadian.patch, XFree86-4.2.0-xkb-is.patch,
  XFree86-4.2.0-manpage-document-nomtrr-option.patch,  
  XFree86-4.2.0-im-clientmessage-crash.patch
  
* Mon Nov 25 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021122.4
- Test build
 
* Sat Nov 23 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021122.3
- Test brp-compress out to see if we need to override it still

* Sat Nov 23 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021122.2
- Added XFree86-4.2.99.2-neomagic-2160-disable-broken-accel-for-bug55587.patch
  to try to resolve bug (#55587)
- Added XFree86-4.2.99.2-disable-DRI-on-s390-by-default.patch to disable DRI
  on s390 and s390x by default as X was defaulting to DRI=YES and s390 has no
  video hardware.
- Added XFree86-4.2.99.2-x86_64-has-SSE-MMX-3DNOW.patch to enable SSE/MMX/3DNOW
  on x86_64 by default
- Added XFree86-4.2.99.2-more-lib64-fixes.patch to cleanup Imake lib64ness
- Modified strip section to call strip once for strip-debug, and once for
  strip -R .comment, as apparently calling them together does not do what I
  expected it to do.  Thanks to Michael Fratoni for pointing this out.

* Sat Nov 23 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021122.1
- Reordered more patches to sections 10000/20000, and minor housekeeping
- Removed BuildRequires on pam header file, and replaced with pam-devel
- Removed XFree86-4.0.3-xaw-asciisink.patch, as a different solution was put
  into upstream sources

* Sat Nov 23 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021122.0
- Updated CVS snapshot to 20021122
- Updated XFree86-4.2.99.2-redhat-custom-modelines.patch as extramodes changed
- Removed Alan Cox's input drivers, as they're included upstream now
- Removed patches that are now included upstream: XFree86-4.2.0-minor-typo.patch,
  XFree86-4.2.0-hostname-stderr-fix.patch, XFree86-4.2.99.2-rename-Katmai-to-SSE.patch
  XFree86-4.2.99.2-new-alan-cox-input-drivers.patch, XFree86-4.2.99.2-Imake-lib64-fixups.patch
  XFree86-4.2.99.2-ati-r128-ppc-dri-buildfix.patch, XFree86-4.2.0-bad-mmap-check.patch
  XFree86-4.2.99.2-FontconfigFontsConfDir.patch, XFree86-4.2.99.2-Imakefile-fontconfig-build-dir-fixup.patch
- Removed XFree86-4.1.0-ppc-compiler-workaround.patch, we are building with
  gcc 3.2 now, so this hack for older gcc 2.96 on ppc is not needed anymore
- Submitted many of the remaining patches upstream in hopes they will be
  applied soon, and we can drop many more of them
- Re-ordered the patch section a bit, removed dead patches that were still
  being included but not applied.  Made 2 new sections for patches - range
  10000 is for Red Hat custom patches that are specific to Red Hat Linux, and
  which are not particularly relevant for upstream or other distros, and a
  second section for patches which are certified ugly hacks, but needed, and
  possibly refused by upstream (with commented reason hopefully).
- Added new gtf utility and manpage to main package for calculating new
  VESA GTF (General Timing Formula) modelines for creating new video modes

* Sat Nov 23 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021110.11
- Added BuildRequires: expat-devel (#78422)
- Removed s390 FreeType patch, as Than says it is no longer needed.

* Fri Nov 22 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021110.10
- Conditionalized with_sdk to exclude it on s390
- Do not build/include mmapr and mmapw on s390 and ppc platforms
- Conditionalized inclusion of libxrx and disabled it as it is a Netscape
  plugin apparently, and a potentially serious security risk, and upstream
  recommends not to ship it.

* Thu Nov 21 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021110.9
- Disable ati-r128-vtswitch-fix-busmaster-enable patch to see if the problem
  still exists or not.
- Explicitly list each .a and .so library in the -devel package, so that
  unwanted libs that show up due to XFree86 Imake bugs do not get packaged.
  If RPM is configured with _unpackaged_files_terminate_build == 1, these types
  of errors can get picked up and fixed before becoming a problem.
- Updated fontconfig-devel BuildRequires dependancy to version 2.1

* Thu Nov 21 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021110.8
- Disabled xf86config, as it is ancient, and unneeded.  Our supported config
  tool is redhat-config-xfree86 now, and we want people using it, testing it,
  reporting bugs and feature requests to us in bugzilla.
- Re-enabled input drivers from Alan Cox
- Moved pkgconfig files, from _x11libdir to _libdir (#77815,77858)
- Changed host.def to use HasFontconfig instead of UseFontconfig
- Added XFree86-4.2.99.2-Imakefile-fontconfig-build-dir-fixup.patch to fix a
  bug in xc/lib/Imakefile which caused "make clean" to fail during build time
  when HasFontconfig is defined.  The problem is due to the FontconfigLibDir
  being added to $SUBDIRS always, and all targets seeing it and barfing when it
  is /usr/lib.  I changed it to FONTCONFIGBUILDDIR instead, which only gets
  defined when HasFontconfig is not defined.
- Changed default cursor theme to whiteglass so that more people include with
  graphic art abilities see the graphic glitches and maybe one of them will fix
  the broken whiteglass theme
- Added XFree86-4.2.99.2-FontconfigFontsConfDir.patch to rename conflicting
  namespace in Imakefile
- Re-enabled the Imake-lib64-fixups patch for proper building on x86_64

* Fri Nov 15 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021110.7
- Enabled kernel DRM check to ensure user has a Red Hat rawhide kernel
  installed which supplies the version of DRM that is required for proper
  operation of DRI.
- Added rename-Katmai-to-SSE patch to rename the HasKatmaiSupport Imake
  define to be more correct as to what it is really doing.

* Tue Nov 12 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021110.6
- Added XFree86-4.1.0-ia64-vgaHW-memory-barrier2.patch which adds memory
  barriers to the vgaHW functions to guarantee memory ordering.  This resolves
  MCAs on ia64 and possibly other platforms
- Added memory barriers to nv driver in nv-ia64-memory-barrier.patch to solve
  HP Itanium 2 machine checks

* Tue Nov 12 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021110.5
- Added patch to fix Imake related lib64 issue on Hammer where any library
  chosen with HasSomelib results in Imake looking in /usr/lib rather than in
  /usr/LibDirName - XFree86-4.2.99.2-Imake-lib64-fixups.patch

* Tue Nov 12 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021110.4
- Removed glFrustum-fixie patch as it is unneeded in CVS X
- Removed various other patches that are no longer needed, were not being
  applied, but were still being included in spec file
- Updated redhat-custom-startup.patch to apply cleanly to 4.2.99.2
- Enabled HasFontconfig in host.def (duh duh duh)

* Mon Nov 11 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021110.3
- Specfile cleanups.  Removed stuff custom to my local environment that is now
  unneeded, and fixed some build issues.

* Sun Nov 10 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021110.2
- Simplified the XFree86-75dpi-fonts and XFree86-100dpi-fonts file lists by
  using %%exclude globs instead of individually listing a billion oddball
  globs, in order to shrink specfile, and improve maintainability.
- Reordered the files lists to be closer to package alphabetical order

* Sun Nov 10 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021110.1
- Added new __fccache macro for running fc-cache if it exists when installing
  or uninstalling font packages.  Added __fccache to all font packages
  post/postun scripts. (#77542)
- Conditionalized the new inb, inl, etc. commands to only be included on
  architectures that they build and work for.

* Sun Nov 10 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021110.0
- Updated CVS snapshot to Nov 10th
- Added new inb, inl, inw, ioport, outb, outl, outw commands to SDK subpackage
  as they are potentially useful for driver development on architectures that
  they work on.
- Added ownership of _x11includedir dir to XFree86-devel package

* Fri Nov  8 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021105.2
- Updated various Requires lines in subpackages that specified a dep on
  another XFree86 subpackage to require the same ver-rel instead of just ver.
- Reorganized font subpackages %%description near the %%package definition
- Made font subpackage inclusion conditional with the macro with_fonts with
  hopes to build the fonts in a separate noarch src.rpm in the future instead
  of being part of the XFree86 build process. (untested yet)
- Fixed bad Conflicts line missing a <= in XFree86-libs-data

* Thu Nov  7 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021105.1
- Enabled the restest Xresource client
- Disabled experimental building of kdrive/TinyX
- Created new XFree86-libs-data subpackage to hold architecture independent
  data files including locale/compose datafiles, XErrorsDb, rgb.txt and other
  files that should be installed with the X libraries, and not require the
  main XFree86 package to be installed.

* Tue Nov  5 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021105.0
- Updated CVS snapshot to Nov 5th
- Includes bug fix for i830/i845 hardware/software cursor issue (#76772,77213)

* Mon Nov  4 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021101.6
- Changed all occurances of /usr/X11R6/lib in all pre/post/postun/trigger/etc.
  scripts to use either _x11libdir or _x11datadir, whichever is appropriate,
  so that things work properly on x86_64 and other lib64 archs
- Replaced all occurances of {_x11datadir}/X11/fonts with {_x11fontdir}

* Sat Nov  2 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021101.5
- Removed Xterm3D from specfile.  There are enough terminal emulators in
  the distribution already.  xterm3D causes build dep loops, and is something
  that is more suited to its own RPM package IMHO.
- Added conditionalized Obsoletes: XFree86-xf86cfg
- Added XFree86-4.2.0-bad-mmap-check.patch to fix (#71783)

* Sat Nov  2 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021101.4
- Changed SDK to use a filelist instead, and added code to %%install to
  generate the filelist.sdk.  Hopefully this will work on all arches now.
- Added XFree86-4.2.99.2-ati-r128-ppc-dri-buildfix.patch to fix build problem
  on PPC when DRI is not being built in.

* Sat Nov  2 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021101.2
- Updated XFree86-sdk package to use _x11libdir instead of _x11datadir as
  the sdk gets installed to /usr/%{_lib} which is lib64 on Hammer.

* Fri Nov  1 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021101.1
- Updated CVS snapshot, includes DRI CVS merge with Radeon 8500 3D support,
  various RandR and Xcursor fixes.  Note: You need to compile DRM by hand
  from XFree86 CVS for DRI to work, and no I wont help, I am busy.  Mailing
  lists exist for people who need help compiling DRM kernel modules.
- Cleaned up cursors subpackage and added handheld cursors

* Wed Oct 23 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021023.2
- Added files to sdk filelist.  Probably a lot of them can be commented out
  as they dont really suit the purpose the subpackage is being added, but I
  have included them anyway for now.

* Wed Oct 23 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.2-0.20021023.0
- Updated CVS snapshot to 4.2.99.2

* Tue Oct 22 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021018.6
- Added new XFree86-sdk subpackage in order to allow X driver modules to be
  compiled in separate subpackages, and to facilitate driver development
  outside of a fully installed XFree86 source code tree.
- Fixed broken geode driver Imakefile SDK installation code

* Sat Oct 19 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021018.5
- Disabled kdrive on ia64 also, as it fails to build (dunno why because the
  buildsystem deleted the log).  No biggie as I doubt we will see ia64 based
  PDAs anytime soon.

* Fri Oct 18 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021018.4
- Completed the with_kdrive conditional build stuff.  TinyX kdrive etc. X
  servers can now be optionally enabled to be built.  WARNING: Note that this
  is not something which will be officially included or supported in
  Red Hat Linux, but rather it is intended solely for my own experimentation
  with kdrive.  Do not use this thinking or expecting that it will be enabled
  in official packages.  No guarantees, you have been warned.  Have fun with
  it for now, while I have it enabled anyway.
- Disabled the kdrive option on x86_64 and ppc because gcc exhibits an ICE
  when building XIgsServer on x86_64, and the build fails on XIgsServer due
  to a source bug it appears when building on ppc
- Added XFree86-4.2.99.1-kdrive-posix-sigaction.patch to fix sigaction issue
  in kdrive - sa_restore is obsolete and should not be used, POSIX does not
  require it, and it causes the build to fail on alpha.
- Disable kdrive build on alpha, due to build failures

* Fri Oct 18 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021018.1
- Updated file lists to conditionally include all freetype2 related files in
  the appropriate subpackages when with_freetype2 is defined

* Fri Oct 18 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021018.0
- Updated CVS snapshot to the latest bits
- Removed patches that are included in CVS code now:
  XFree86-4.2.1-xshm-header-file-fix.patch, XFree86-4.2.99.1-drm-device-dir-perms.patch

* Thu Oct 17 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021014.4
- Added Provides/Obsoletes for Xft/Xft-devel for obsolesense and compatibility

* Tue Oct 15 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021014.3
- Added new manpages for bdftruncate, cleanlinks, mergelib,
  mkhtmlindex, ucs2any
- Added mmapw binary

* Tue Oct 15 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021014.2
- Excluded fontconfig development files in the XFree86-devel subpackage when
  with_fontconfig is not defined, by using the rare rpm 'exclude' directive,
  both so that it does not conflict with existing fontconfig libs, and also
  to make people wonder what the exclude directive is and cause confusion and
  world unrest, just because.

* Tue Oct 15 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021014.1
- Added xc/programs/Xserver/hw/xfree86/CHANGELOG doc flagged to main
  XFree86 subpackage, so people can find the developmental CHANGELOG
  without installing the source code

* Mon Oct 14 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021014.0
- Updated CVS snapshot to 2002-10-14, which includes xfs updates and cleanups,
  APM suspend fixes, Radeon crash freeze fix, RandR extension updated to
  support refresh rate changes.
- Made XFree86-libs subpackage Obsolete: Xft (#75932)
- Fixed XFree86CVSDate in spec file to be correct.  Doh!
- Disabled xkb-fix-deadkey-quotedbl-us_intl patch as one hunk fails, and it
  looks like CVS includes these changes already.  I really wish people would
  file these type of change requests upstream FIRST so I do not have to
  maintain separate fork of them.
- Removed XFree86-4.2.0-xfs-syslog.patch, XFree86-4.2.0-sane-deadacc.patch,
  XFree86-4.2.1-lbxproxy-SEGV-fix.patch, XFree86-4.2.1-vidmode-manpage-fixes.diff,
  as they are included in CVS now.
- Updated drm-device-dir-perms.patch, xtt.patch, Wacom patch to account for
  changes in CVS update, and cleaned up patches a bit.
- Wrapped %%clean section of specfile with auto_mharris_mode check, so that
  the BUILD_ROOT files get left behind for me for doing rpmfilediff to check
  for new files.
- Removed .pl filename extensions from ucs2bdf.pl and bdftruncate.pl in file
  lists, to match the newly generated filenames.

* Sat Oct 12 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021012.0
- Updated CVS snapshot to 20021012
- Added changelog entries below for CVS updates.  ;o)
- Added /usr/X11R6/bin/xft-config to -devel pkg
- Made -libs package own the dirs _x11libdir, and _x11datadir
- Fixes and improvements for the en_US.UTF8 compose rules, and for some dead
  accents for iso8859-1 and iso8859-15 (Alexandre Oliva).
- Fix 24bpp displays with the fbdev driver when not using shadowfb
- New "kbd" keyboard driver module which will eventually replace the built in
  "keyboard" driver.
- New Natsemi geode video driver from Alan Hourihane

* Thu Oct 10 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021008.8
- Made specfile changes for x86_64 arch (AMD Hammer) for lib64 support, which
  involved adding a new macro _x11datadir and making all fonts, and other non
  executable data, etc. use the _x11datadir macro instead of _x11libdir.  On
  x86/alpha/ia64/ppc _x11datadir and _x11libdir are the same, however on x86_64
  architecture, _x11libdir=/usr/X11R6/lib64 and _x11datadir=/usr/X11R6/lib
- The package currently builds on x86/x86_64/alpha/ia64/ppc.  ppc64/s390/s390x
  to be tested soon, as will sparc/sparc64 if Tom Callaway gives it a shot.

* Thu Oct 10 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021008.5
- Updated file lists for new files in CVS.  Normally I would add details as
  to what new applications were added, but I am feeling lazy.  Basically,
  mmapr, new xcursor stuffs, and a few other things.  Blah blah blah.
- Created new subpackage XFree86-cursors for the new truecolor antialiased,
  alpha blended, animated, themeable mouse pointers in XFree86.  Go Keith go!
- Created new subpackage XFree86-syriac-fonts for the new Syriac fonts.
- Made various updates to _x11foodir macro usage throughout the specfile

* Wed Oct  9 2002 Mike A. Harris <mharris@redhat.com> 4.2.99.1-0.20021008.0
- Forked XFree86.spec and updated XFree86 to CVS snapshot from head of CVS
  dated 20021008
- Removed all patches from specfile which are now present in CVS, or otherwise
  made irrelevant.  There are still various patches disabled which are not yet
  known if they are needed or not, and might need porting work.

* Tue Oct  8 2002 Mike A. Harris <mharris@redhat.com> 4.2.1-8
- Updated Patch0 to current xf-4_2-branch, picking up a few security fixes
  and bugfixes, in particular for MIT-SHM, xdm
- Removed XFree86-4.0.3-xaw-freed-mem-deref.patch now as it _finally_ is in
  XFree86.org sources.  ;o)
- Removed XFree86-4.2.0-xdm-pam-conv-and-realloc.patch - it is integrated now

* Mon Oct  7 2002 Mike A. Harris <mharris@redhat.com> 4.2.1-7
- Various architectural cleanups for all-arch build

* Wed Sep 18 2002 Mike A. Harris <mharris@redhat.com> 4.2.1-6.2
- Added new input drivers from Alan Cox for "Fujitsu stylistic",
  Palmax PD1000/PD1100 Input driver, Union Reality UR-98 head tracker

* Wed Sep 18 2002 Mike A. Harris <mharris@redhat.com> 4.2.1-6.1
- Added new Cyrix driver 0.2 from Alan Cox, which fixes (#72297)

* Sat Sep 14 2002 Mike A. Harris <mharris@redhat.com> 4.2.1-6
- Updated savage driver to the upstream maintainer Tim Roberts new 1.1.25t
  version which solves various savage driver problems, which are fully
  documented at http://www.probo.com/timr/savage40.html (#71973)

* Wed Sep 11 2002 Mike A. Harris <mharris@redhat.com> 4.2.1-5.1
- Disabled DRI on ppc at streeters request

* Wed Sep 11 2002 Mike A. Harris <mharris@redhat.com> 4.2.1-5
- Added XFree86-4.2.1-lbxproxy-SEGV-fix.patch from Debian to fix a SEGV
  in lbxproxy
- Added XFree86-4.2.1-xshm-header-file-fix.patch from Debian
- Added XFree86-4.2.1-vidmode-manpage-fixes.diff from Debian

* Tue Sep 10 2002 Mike A. Harris <mharris@redhat.com> 4.2.1-4
- Added ati-r128-dri-dga and ati-radeon-dri-dga patches to fix bugs in the
  Radeon and Rage 128 drivers which cause crashes while using VMware with
  DGA when DRI is enabled (#73678)
- Fix up ttmkfdir to look for freetype in _libdir for AMD Hammer

* Sun Sep  8 2002 Mike A. Harris <mharris@redhat.com> 4.2.1-3.3
- Remove scanpci, pcitweak from ppc/ppc64 builds

* Sun Sep  8 2002 Mike A. Harris <mharris@redhat.com> 4.2.1-3.2
- (x86_64) Added Imake define to point Freetype2LibDir to _libdir

* Sat Sep  7 2002 Mike A. Harris <mharris@redhat.com> 4.2.1-3
- Replaced the BuildRequires on Glide3 and Glide3-devel that was
  conditionalized for x86/alpha/ia64 with some new shell script code in the
  prep section to ensure Glide3 is installed on the build system since
  some rpm based software freaks out with conditional BuildRequires, and I
  am a nice guy.

* Sat Sep  7 2002 Mike A. Harris <mharris@redhat.com> 4.2.1-2
- Did a search and replace on specfile to convert all locations of the X11
  font directory to _x11fontdir, /usr/X11R6/bin -> _x11bindir, and similar
  for _x11mandir, etc. throughout the specfile
  
* Sat Sep  7 2002 Mike A. Harris <mharris@redhat.com> 4.2.1-1
- Updated XFree86 to version 4.2.1.  This does not bring us anything new
  since 4.2.1 is merely 4.2.0 stable branch (which our 4.2.0 was already
  tracking all along) plus the latest X security patch, which 4.2.0-72
  contains.  This release is merely a cosmetic update to official 4.2.1 in
  order to quell all of the "Why doesnt Red Hat have 4.2.1" questions that
  are sure to abound.
- Removed patches present in 4.2.1:  XFree86-4.2.0-vesa-xf86SetDpi-fix.patch,
  XFree86-4.0.3-xaw-readtext.patch, XFree86-4.1.0-time-wraparound.patch,
  XFree86-4.2.0-mitshm.patch,  XFree86-4.2.0-xkb-us_intl-missing-commas.patch,
  XFree86-4.2.0-overlay-crash.patch

* Thu Sep  5 2002 Owen Taylor <otaylor@redhat.com>
- Fix zh_TW-xcinNEW patch which lost a couple of things in the merge 
  with the XLOCALEDIR patch

* Tue Sep  3 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-71
- Added xlib-security-fix-XLOCALEDIR to fix a security vulnerability in
  Xlib i18n code new to 4.2.0.  4.1.0 and earlier is not susceptible.
- XFree86.org has tagged a new release of XFree86 4.2.1 in CVS for this
  issue.  Red Hat current XFree86 4.2.0 is essentially 4.2.1 except for the
  cosmetic version number difference
- Updated the zh_TW-xcin patch to zh_TW-xcinNEW which handles a code area
  that overlapped with the new security patch
- Updated the _LP64 kludge patch on alpha/ia64 as it also overlapped the
  security patch

* Sun Sep  1 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-70
- Updated custom startup log patch to fix a few glitches
- Added -fPIC to x86_64 compiler flags until better solution is made in future
- Added XFree86-4.2.0-libXrender-bugfix.patch to fix showstopper (#73243)

* Thu Aug 29 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-69.1
- Added Obsoletes: XFree86-compat-libs to list of obsolete packages

* Thu Aug 29 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-69
- Rebuild with a few patches disabled that errored out on me and will be
  fixed in future build

* Thu Aug 29 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-68
- Pruned ia64 driver list based on unknown state of working order for these
  drivers on ia64 to minimalize support issues.  As hardware becomes available
  for testing, and drivers can be verified to be mostly sane/working, they
  can be re-enabled on a driver by driver basis.
- Added XFree86-4.2.0-im-clientmessage-crash.patch to fix CJK application
  crashing showstopper bug (#72236)

* Mon Aug 26 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-67.6
- Actually properly enable the maxxfbmem patch from 4.2.0-67.5 this time
- Fix unresolved symbols in SiS driver reported by Alan Cox

* Sun Aug 25 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-67.5
- Changed buildsys autodetect to use new beehive mechanism (#71055)
- Added kernel version string to X server startup messages for easier debugging
- Fixed SiS hardware cursor (hopefully) with XFree86-4.2.0-sis-cursor.patch
- Fixed SiS maxxfbmem driver comparison inversions

* Thu Aug 22 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-67.1
- Cleaned up 3.3.6 server Obsoletes lines et al. to be more compact

* Thu Aug 22 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-67
- Integrated PPC specfile changes
- Enable DRI on ppc, but not ppc64
- PPC using gcc 2.96 autodetection and compiler flag tweaks, etc.
- Added ppc64, s390x, x86_64 to conditionalized LP64 patch
- PPC - build pcitweak, scanpci on ppc, ppc64 now

* Mon Aug 19 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-66
- Added XFree86-4.2.0-elf-loader-empty-symbol-table.patch to fix gcc 3.2
  related issue in the X ELF loader (#70576)
- Re-enabled the Radeon DDA removal patch now that Null beta is released

* Thu Aug 15 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-65
- Due to a kernel bug breaking SuS compliance in the Alpha kernel, a change
  has been made to the install section so that fonts.dir, encodings.dir files
  are mode 644 before "touch" touches them.
- Modified stripping policy at end of install section to strip all ELF
  executable files in the buildroot instead of just the ones found in 
  /usr/bin and /usr/X11R6/bin.
- Modified shared library stripping policy for all libs found in /usr/X11R6/lib,
  /usr/lib, and now also /usr/X11R6/lib/X11/locale/common.  All .so.* libs are
  now stripped with "strip --strip-unneeded -R .comment" following the current
  RPM default for stripping shared libraries, and under the advice of Uli.
- Note:  XFree86 server modules are not stripped at all currently for safety.
  Once I determine what can be safely stripped, I will add stripping of the
  modules also.

* Wed Aug 14 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-64
- Removed XIE and PEX5 documentation from XFree86-doc subpackage because both
  of these extensions are obsolete and not included anymore.
- Temporarily disabled XFree86-4.2.0-ati-radeon-dda-removal.patch as it is
  untested, and I dont want to destabilize.  Will re-enable for testing soon.

* Tue Aug 13 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-63.1
- Added XFree86-4.2.0-ati-radeon-dda-removal.patch which removes the DDA
  code from the radeon driver which was leftovers from the r128 driver and
  apparently causes 1400x1050 and other modes to cause an FPE on some radeon
  boards in some refresh rates (#63593)
- Explicitly delete unshipped files from RPM_BUILD_ROOT at end of install
  section in order to pass RPMs new unpackaged_files_terminate_build option
- Moved around some file removals to the new DELETE section of specfile

* Mon Aug 12 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-63
- Added XFree86-4.2.0-ati-mach64-dsp-rounding-error.patch to fix a rounding
  error in Mach64 DSP calculation
- Added XFree86-4.2.0-ati-radeon-missing-commas.patch which fixes a missing
  comma issue in a struct in radeon_driver.c
- Bumped spec file release from 60.4 to 63 due to someone elses package
  release number conflicting.

* Thu Aug  8 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-60.4
- Fixed an xdm SEGV bug in verify.c which could be occasionally triggered,
  due to malloc() allocated memory not being zeroed out.  Also fixed a
  bad realloc() call that assumed the reallocated block of memory would be in
  the same location every time - fixes bug (#40729)

* Wed Aug  7 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-60.3
- Added XFree86-4.2.0-sane-deadacc.patch to fix dead diareisis problem reported
  by aoliva in bug (#71014)
* Tue Aug  6 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-60.2
- Disabled the ugly 1980 style ancient UNIX ugly ugly X server startup
  stipple pattern.

* Mon Aug  5 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-60.1
- Added XFree86-4.2.0-locale-alias-utf8-euro.patch to workaround bug in
  fi_FI.UTF-8@euro and pt_PT.UTF-8@euro locales (#67914)
- Added XFree86-4.2.0-i810-vtswitch-sync-fix.patch to fix i810 VTswitch
  lockup problem - BLOCKER bug (#66187,#53231)

* Mon Aug  5 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-60
- Removed /usr/share/fonts/default/TrueType from default xfs config file in
  order to fix BLOCKER bug (#68126,#70178)
- Made X resource extension off by default for official builds, due to
  irrational ABI compatibility concerns.  People wanting to use it can
  easily rebuild X from rpm after setting the define with_Xresource_extension
  to 1.

* Sat Aug  3 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-59.2
- Added restest dumb sample client to use the new Xres extension
- Conditionalized spec file inclusion of Xres and the sample client

* Sat Aug  3 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-59.1
- Bugfix to dixsym.c for the Xres extension from yesterday.

* Fri Aug  2 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-59
- Backported the new X-resource extension from XFree86 head CVS, which allows
  internal X server resource statistics, etc. to be queried by client
  applications.  This can aide in debugging client related pixmap leakage, and
  a variety of other various resource related problems/bugs in both client
  applications, as well as the X server itself.

* Wed Jul 31 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-58.1
- Disabled ParallelBuild on s390 upon request of pknirsch

* Tue Jul 30 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-58
- Added support to the Radeon driver CP engine to perform accelerated color
  expansion and image writes.  The CP engine is used when DRI is enabled.
  XFree86-4.2.0-ati-radeon-cp-colorexpansion-imagewrite-enhancement.patch

* Fri Jul 26 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-57.1
- Removed the following paths from the default xfs config file as we do not
  ship fonts in these directories by default or they dont belong in the default
  config: /usr/X11R6/lib/X11/fonts/CID, /usr/X11R6/lib/X11/fonts/local,
  /usr/X11R6/lib/X11/fonts/latin2/Type1, /usr/share/AbiSuite/fonts (#68126)

* Fri Jul 26 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-57
- Added XFree86-4.2.0-ati-r128-vtswitch-fix-busmaster-enable.patch to fix
  the exact same bug in the r128 driver as was just fixed in the radeon
  driver in 4.2.0-56. (#62442,#65136)

* Fri Jul 26 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-56
- Added XFree86-4.2.0-libICE-remove-stupid-delay.patch to remove stupid 5
  second delays from libICE (#66751)
- Added XFree86-4.2.0-ati-radeon-vtswitch-fix-busmaster-enable.patch to fix
  lockups reported in XFree86 4.2.0 for a long time now by users of ATI Radeon
  cards with certain hardware combinations. (#62171,#65330)

* Wed Jul 24 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-55.2
- Added -f flag to hostname command to attempt to fix Custom build
- Added fix for SysRq / Print Screen:  XFree86-4.2.0-sysreq.patch (#69743)

* Tue Jul 23 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-55.1
- Made all instances of "rm" in spec file "rm -f" in order to force removal
  of the file without prompting.  Reported by a few people that rebuilding X
  caused it to hang while compiling on an "rm" command.  (#69713)
- Added XFree86-4.2.0-manpage-document-nomtrr-option.patch to document
  Option "NoMTRR" in the XF86Config manpage.

* Mon Jul 22 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-55
- Added ati-rage-xl-pci-spec-cleanup patch to fix ATI Rage XL PCI spec
  violations (#69291)  Replaces previous patch for IBM/Dell/others from
  Feb 28, 2002 (#58188)

* Mon Jul 22 2002 Tim Powers <timp@redhat.com> 4.2.0-54
- rebuild using gcc-3.2-0.1

* Sat Jul 20 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-53.1
- Redirect stderr+stdout of hostname command in xon script to prevent stderr
  from being displayed ot user (#67323)
- Corrected incorrect filepath in XftConfig-README-OBSOLETE file (#68632,#69104)

* Thu Jul 18 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-53
- Previous ia64/alpha fix from Jul 08 removed the Xft1 patch,
  and made the ia64/alpha patch apply on all architectures.  Fixed.
- Added XFree86-4.2.0-overlay-crash.patch to fix bug (#68516)
- Added patch for module loader from Bill Nottingham for gcc 3.1 on ia64
- Add patch to enable/disable DMA for Xv on r128 (#64503,#68058,#68668)

* Mon Jul 08 2002 Elliot Lee <sopwith@redhat.com> 4.2.0-52.01
- Fix duplicate application of patch4201 on ia64/alpha
- Remove ExcludeArch: alpha ia64

* Tue Jun 25 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-52
- Reordered the spec install section so that Xft1 .so gets deleted after it
  the code which generates the .so devel symlinks
- Fixed libXft.so.1 to point to libXft.so.1.2 instead of 1.1, and made sure
  the files are explicitly listed in the files section.

* Sun Jun 23 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-51
- Added Obsoletes lines for remaining 3.3.6 servers that were not previously
  obsoleted from the olden days.
- Really made Xft headers excluded this time

* Sun Jun 23 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.24
- Assimilated mkxauth into the XFree86-xauth package, and added Obsoletes and
  Provides entries for it.
- Removed Xft headers when new Xft1 is used, as Xft2 now provides the Xft
  headers instead.

* Fri Jun 21 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.23
- Replaced libXft with the new Xft1 from XFree86 CVS which is completely
  compatible, however uses fontconfig instead of XftConfig.  This has been
  conditionalized so that it can be disabled for builds for RHL 7.3 et al.
  The new libXft is Xft 1.2 whereas the stock Xft is 1.1.  The new lib should
  be binary compatible and source compatible.
- xftcache conditionalized as well - replaced with fc-cache in fontconfig

* Thu Jun 20 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.22
- Backported the Trident driver from CVS, picking up many Trident fixes
  from Alan Hourihane

* Tue Jun 18 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.21
- Backported i810/i830 driver from CVS, adding 2D only i845 support
- Removed i830m workaround for Dell c400 laptop as it did not work
- Backported siliconmotion driver from CVS, picking up a few bugfixes
- Conditionalized spec file using backup prefixes on patches

* Mon Jun 17 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.20
- Backported i740 driver from CVS - i740-driver-update-cvs-20020617
- Renamed the radeon-mobility-LX patch to radeon-mobility-FireGL-7800 after
  determining the two are one and the same card.
- Added mkfontscale from XFree86 CVS so we can begin moving away from ttmkfdir
  and towards mkfontscale which is going to be better in the long run.
- Conditionalized inclusion of XftConfig file and Xft/Xrender libraries,
  so they can be disabled for builds using fontconfig (which replaces them).
- Added new /etc/X11/XftConfig-README-OBSOLETE file to explain wht it is no
  longer there.

* Mon Jun 17 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.19
- Reorganized patch section, moved all video driver patches into an
  alphabetically sorted driver patch section, and renumbered all patches
  to meet the new patch numbering scheme.
- Backported cirrus driver from XFree86 CVS (4.2.99.1)

* Fri Jun 14 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.18
- Created XFree86-4.2.0-xman-manconf.patch to fix the xman man config
  file path for once and for all.  Sent upstream so hopefully this will
  get merged into XFree86 4.3.0.
- Conditionalized building xf86cfg, and disabled it by default, as we are
  moving to our new redhat-config-xfree86 tool for X configuration.
- Backported apm driver from XFree86 CVS (4.2.99.1), DPMS support
  enhancements, and a few accel fixes.  apm-driver-update-cvs-20020617
- Backported ark driver from XFree86 CVS (4.2.99.1) ark-driver-update-cvs-20020617
- Backported chips driver from XFree86 CVS (4.2.99.1), with hardware mouse
  cursor and 2D accleration fixes.

* Wed Jun 12 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.17
- Added workaround for buggy laptop BIOSs (in particular the Dell
  Latitude C400) which use the Intel i830/i830m chipset, and limit the
  video memory to 1Mb of stolen system memory without making it
  configureable. This workaround addresses bugzilla bug (#65661)
  (Update: subsequently removed as it did not solve the problem.)
- Removed currently unused Glide3Libver macro.

* Tue Jun 11 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.16
- Fixed a bug in the VESA driver, where the X server would crash with
  an FPE due to a division by zero in miscreeninit() when the DisplaySize
  option was used in the config file.  Inside xf86SetDpi(), pScrn->virtualX
  and pScrn->virtualY are used only when DisplaySize is given in the config
  file, however these struct members were not initialized properly in the
  vesa driver prior to xf86SetDpi() being called.  Fixes bug (#66009)
- Removed specfile BuildXwrapper conditional as XFree86 4.x does not need or
  use Xwrapper - it only existed for XFree86 3.3.6 in the past.
- Removed specfile Build7x conditional as it was both poorly named, and the
  functionality it provided is no longer needed.

* Mon Jun 10 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.15
- Added alpha-ia64-_LP64-fix to workaround issue in xc/lib/X11/XlcDL.c
  preventing X from building on alpha/ia64 with gcc 3.1.
- Added 4 patches from Hewlett Packard for ia64 (XFree86-4.2.0-int10-hplso.diff,
  XFree86-4.2.0-pci-hplso.diff, XFree86-4.2.0-primpci-hplso.diff,
  XFree86-4.2.0-ps2-hplso.diff

* Wed Jun  5 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.14
- Added explicit Requires: _x11bindir/xauth to XFree86 main package now
  that xauth is split out.

* Mon Jun  3 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.13
- Update BuildPreReq: freetype-devel >= 2.0.6-3

* Thu May 30 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.12
- Disable debug mode in cirrus alpine driver - filling logfile (#65704)

* Wed May 29 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.11
- Split out xauth into a separate subpackage so things like ssh do not
  require the entire dependancy chain of XFree86 be installed merely
  to use ssh or similar (#38409,62426)
- Added neomagic-Xv-support (#63609)
- Added fix for deadkey-quotedbl in ISO8859-15 (#50282)

* Wed May 29 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.10
- Updated parallelmake-libfont Imake patch for more parallelism
- Fixed nasty problem in post script for libGLU, and added postun scripts
  that call ldconfig for the 2 Mesa subpackages
- Added remove-bitmap-scaler patch disabled by default pending testing,
  compatibility, etc.

* Tue May 28 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.9
- Added rpm post scripts for XFree86-Mesa-libGL, XFree86-Mesa-libGLU that
  call ldconfig properly
  
* Tue May 28 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.8
- Fixed defattr for new XFree86-Mesa-libGL* packages
- Removed Requires: XFree86 dep from Mesa-libGL subpackage

* Mon May 27 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.6
- Updated parallel make patch from H.J. Lu!!!
- Split out libGL.so.* and libGLU.so.* into new subpackages XFree86-Mesa-libGL
  and XFree86-Mesa-libGLU as suggested by H.J. Lu (#65152) and other vendors
- Moved _x11dir et al defines to top of spec file to ensure their definition
  precedes their usage.
- Completely removed XFree86.spec support for building using an external
  Mesa instead of the one included with XFree86.

* Fri May 24 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50.1
- Changed stripping policy and fixed a redundancy in the spec stripping

* Fri May 24 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-50
- Bumped release number to -50 and rebuilt in new build environment

* Fri May 17 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-9.13
- Changed Xnest, Xvfb to be in group "User Interface/X" (#62820)
- Added fix for glint driver for bug (#60895)

* Fri May 17 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-9.12
- Fix for i810 Xv maximum video size (#53329)
- Changed += to =+ on various entries in our default XftConfig as per (#64970)

* Wed May 15 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-9.11
- Changed all chkfontpath calls in specfile post scripts to use :unscaled
  for all bitmap fonts, otherwise scaled bitmap fonts get used, and that
  really really sucks.  Makes Windows users run fast back to Billy.
- Disabled Radeon PCI DRI code, as it has been reported as not working by
  a user despite claims before by others that it works.
- Fixed euro support for pl keymaps as per bug (#64559)
- Added Requires: /lib/cpp to XFree86 package as xrdb requires /lib/cpp at
  runtime and will fail with an error if it is not present.
- Added fix for Rage 128 DRI related bug ati-r128-indirectBuffer from Michal
  Daenzer.

* Tue May  7 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-9.10
- Removed s390 patch 3000, and fixed up file lists for s390/s390x

* Sat May  4 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-9.8
- Replaced /usr/lib throughout specfile with _libdir for compat with
  architectures which have /usr/lib and /usr/lib64.
- Replaced /usr/X11R6 throughout specfile with _x11dir - part of a
  gradual move to implement RPMified variable ProjectRoot support for
  developmental parallel installation.
- Added the following patches backported from XFree86 CVS for AMD x86_64
  AMD-x86_64-elfloader, AMD-x86_64-imake, AMD-x86_64-compiler_h,
  AMD-x86_64-int10, AMD-x86_64-misc-small-fixes, AMD-x86_64-os-support

* Sun Apr 27 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-9.0
- Added AMD x86-64 architecture (Hammer/Opteron) support to the Imake config
  files.
  
* Wed Apr 24 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-8.1.beta
- Changed BuildRequires to pam-devel instead of pam header file.
- Reworked BuildXF86DRI portion of host.def to exclude DRI on PPC for now
- Reworked Glide3 BuildRequires so that the CURRENT Glide3 packages are
  required instead of the mess of conditional code that was there.  People
  who rebuild now require the rawhide Glide3.  Hopefully they read my
  changelog messages.
- Changed xfs postinstall script to conditionalize the login shell at runtime
  instead of at build time to help ensure that packages _built_ on a newer
  release will work on an older release.  Also, /bin/nologin which was added
  in January - does not exist, it is /sbin/nologin.  Fixed, and tested.
- Added utempter to BuildRequires and Requires
- BuildXterm3d macro causes a buildrequires loop, and needs to be set to
  "0" if bootstrapping XFree86 on a new architecture.  Comment added.

* Thu Apr 18 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-8
- Fixed bug in XFree86 post install script, renaming XF86Config-4 config file
  to .rpmsave, and preserving permissions of the file. (#63822)
- Corrected perms on /dev/dri

* Sat Apr 13 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-7
- Updated mitshm patch

* Thu Apr 11 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.666
- Added code to XFree86 post install script to remove xie and pex5 module
  load lines from XF86Config-4 upon upgrade/install since XIE and PEX are
  no longer provided nor supported, and X will not start if those lines
  exist in the config file. (#63119)
- Added fix for sessreg being broken with high UIDs due to open() being used
  to open a file larger than 32bit offsets can handle. (#42850,#63116)
- Fixed startx ugliness issue with hostname command (#61278,63117)
- Removed double ghost flag in truetype-fonts package
- Removed config(noreplace) from Speedo fonts.dir (#63357,63735)
- I went outside today, and the snow is almost completely gone!

* Wed Apr 10 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.62
- Made specfile remove fonts.dir files generated by XFree86 build, and
  "touch" them instead so they satisfy the ghost flag.  Also for the fonts.alias
  for the TTF directory.
- Removed CID directory from list of dirs to run mkfontdir in and add to
  fontpath, because our XFree86 build is not including fonts in there anymore,
  so it should not add the dir to the fontpath, nor run mkfontdir in it.
- Fixed bug in truetype-fonts subpackage which was adding cyrillic to fontpath
  instead of the TTF directory due to cut and paste error.
- Audited all font subpackage file lists for accuracy, correcting various
  ghost/config/verify flags, adding missing ghosted fonts.alias, etc. files to
  the lists also, so the files are owned by the package if a user creates them.
- Added ISO8859-15 locale aliases to locale.alias for en_US and en_GB (#62844)

* Tue Apr  9 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.61
- Added patch to fix various ATI Radeon issues. Will fill in the
  details of what specifically is fixed after testing the fixes.
  VTswitch is one... <more later>

* Mon Apr  8 2002 Mike A. Harris <mharris@redhat.com>
- Changed xf86cfg dep on Xconfigurator to /usr/X11R6/lib/X11/Cards

* Fri Apr  5 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.60
- Added fix for Trident 9397 bug (#62119)

* Mon Apr  1 2002 Mike A. Harris <mharris@redhat.com>
- Updated ttmkfdir-freetype2-port-plus-cjk-chocolaty-goodness.patch to
  build properly with gcc 3.x (Bero,Yu Shao)

* Thu Mar 28 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.52
- Fixed Matrox G550 cursor on second head mga-g550-cursor patch
- Created new support for Euro currency symbol for gb, hu, hu_US, pl, pl2, tr,
  us_intl keymaps based on http://www.microsoft.com/typography/faq/faq12.htm,
  also closing bugs (#56818, and a few others I need to track down in bugzilla)
- Put fonts.alias back in misc fonts directory, it slipped out somehow.

* Thu Mar 28 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.51
 - Flagged encodings.dir, fonts.dir, fonts.scale files properly for the
  misc, Type1, and Speedo directories in base-fonts, and changed the file
  globs to match just the font files in order to fix bug (#59619)
- Fixed similar issues to above in bug (#61940)
- Added XFree86-4.2.0-sparc_pci_domains.patch for sparc support (#62037)
- Fixed duplicate Slovak entries - MF bug (#61709)
- Confirmed ulT1mo fonts work and closed - MF bug (#61694) and (#62036)

* Wed Mar 27 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.50
- Added ko, zh_CN, zh_TW entries to XftConfig for bug (#61282)
- Changed antialiasing on small fonts from "any size < 14" to "any size < 11"
- Added gb18030-enc patch from Yu Shao
- ttmkfdir ported to freetype2, plus misc enhancements for CJK

* Sun Mar 17 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.48
- Moved GL include files into /usr/include/GL for compliance with defacto
  and possibly official standards due to user complaints.
- Changed host.def to not symlink GL include dir into /usr/include

* Thu Mar 14 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.47
- Updated package descriptions to not suck quite so bad, and not be
  so meaninglessly verbose as they have been for a while.  We do not want
  to scare away Harry Homeowner.

* Tue Mar 12 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.46
- Cleaned up xfs initscript to use simpler syntax, and fix a few issues

* Sun Mar 10 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.45
- Added the /usr/X11R6/lib/X11/fonts/TTF dir to XftConfig (#60901)
- Updated bugfix for (#60906) from Keith Packard
- Built on all arches

* Sun Mar 10 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.44
- Fixed up tdfx DRI disable patch for hires on voodoo3/banshee
- Updated Glide3 dependancy, to pick up new Glide3 package with libs directly
  in /usr/lib, instead of in /usr/lib/glide3

* Thu Mar  7 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.42
- Added XFree86-4.2.0-mitshm.patch to fix security issue
- Added fix for time wraparound bug (#60906)

* Wed Mar  6 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.41
- Resolved some Brazillian and Icelandic keyboard issues (hopefully).

* Mon Mar  4 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.40
- Added XFree86-4.2.0-xkb-is.patch to fix bug (#60594)
- Moved all xkb symbol patches to section 800 - 819
- disabled tdfx font corruption patch

* Thu Feb 28 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.39
- Added XFree86-4.2.0-ati-mach64-rage-XL.patch to fix problems reported
  on many Dell, IBM servers (#58188)
- Fixed memleak in Xlib with XFree86-4.2.0-xlib-memleak.patch

* Wed Feb 27 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.38
- Reorganized various fonts.dir, fonts.alias, encodings.dir files to try and
  fix some of the reported problems that have come up after various
  installations.  All files are believed to be properly flaged with ghost,
  verify and config attributes now.

* Tue Feb 26 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.37
- Fixed xfs initscript to use "reload" instead of "restart" for the
  condrestart option.

* Sun Feb 24 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.36
- Fixed ghost/config flags on various fonts.dir, fonts.alias, encodings.dir
  files in file list section.
- Fixed bug in truetype-fonts scripts which contained %%_ttmkfdir instead
  of just plain old ttmkfdir

* Sat Feb 23 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.35
- Added specfile URL to http://www.xfree86.org
- Rebuilt with new built toolchain in new environment

* Mon Feb 11 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.34
- Enabled Radeon PCI pcigart support in radeon_dri.c and radeon_cp.c
- Disabled the ugly black and white pattern that X starts up with by default
  with XFree86-4.2.0-die-ugly-pattern-die-die-die.patch - blue or something
  else will replace it in the future likely.

* Mon Feb 11 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.33
- Ghosted encodings.dir files in 100dpi and 75dpi font subpackages
- Modified XftConfig with some suggested changes from Keith Packard for better
  AA font support, by moving stuff around (#59192)
- Added Luxi font aliases, etc. to XftConfig for bug (#59708)
  
* Sat Feb  9 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.32
- Created support for ATI Radeon Mobility M7 (LX) and also updated the
  pcitable, and Cards databases, in the hwdata package also.
- Removed the conditional BuildPrereq for pam-devel et al. and replaced it
  with /usr/include/security/pam_modules.h which will automatically do the
  right thing regardless of what distro release is being built for.

* Fri Feb  8 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.31
- Drop XFree86-4.0.2-neomagic_swcursor.patch previously included for sony
  laptops using Neomagic 256XL+ (NM2380), and set the option to default to
  on in the Cards database instead.
- Created sis-swcursor option patch
- Created xkb-us_intl-missing-commas to fix bug (#59529)
  
* Thu Feb  7 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.30
- Experimental patch to disable DRI on tdfx when an incompatible hires
  video mode is selected that is known to cause unstable behaviour.
- Removed -e arguments from calls to mkfontdir in spec file as they appear
  to be unnecessary now.
- Added XFree86-4.2.0-zh_TW-xcin.patch to fix xcin (Owen Taylor, Leon Ho)

* Wed Feb  6 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.24
- First merge with upstream stable branch xf-4_2-branch-patch-2002-02-06
- Misc fixes:  Fix startx script for ksh, temporary workaround for IA-64,
  fix SIGSEGV when printing modes that have no flags, fix an unresolved
  symbol in libGLU.so with gcc 3, revert the composite sync default to off
  in the ati driver.

* Tue Feb  5 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.23
- Updated XFree86-4.2.0-gb18030-20020207.patch from Yu Shao <yshao@redhat.com>
- Added i810-dont-force-XvMC-on-DRI-users patch to fix bug in where i810
  users must enable XvMC in addition to DRI in order for DRI to work. (#59318)
- Added patch XFree86-4.2.0-FIRSTINDEX-breaks-ttmkfdir to remove FIRSTINDEX
  entries from large font encoding files as it makes ttmkfdir deep six.

* Tue Feb  5 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.21
- Added XFree86-4.2.0-i810-dont-use-empty-for-loops-for-delays.patch which
  removes null for loops from the i810 driver and i810 and i830 kernel DRM
  drivers for Linux and BSD.  The for loops were used as a timing delay, and
  are now replaced with "usleep(1);" instead.
- Added ttmkfdir-CJK-bug-54087-fix and bugzilla-54087-fix-gbk-encoding
  patches to fix bug (#54087)
- Fixed libGLU symlink screwup by changing from absolute to relative symlinks

* Sun Feb  3 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.20
- NEW XFree86-truetype-fonts subpackage which includes the new Luxi
  fonts (formerly Lucidux) by Bigelow and Holmes.
- Added /usr/lib/libGLU.so.* and /usr/lib/libGLU.so symlinks to the libGLU
  libraries included in XFree86 in the /usr/X11R6 directories for OpenGL
  standards compliance, and disabled the non-working Imake patch I made
  earlier to do the same.  This is fairly CRITICAL as any OpenGL software
  which uses GLU, will fail to compile without the proper links.
- Removed a bunch of leftover Glide3 specfile mess.
- Removed ancient no longer necessary hardlink between xterm and nxterm

* Sun Feb  3 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.15
- Created support for interlaced video modes on 3dfx Voodoo 3/4/5, with
  the enable-interlaced-modes patch.
- Created tdfx-fix-vtswitch-font-corruption patch to try to fix the VGA
  font corruption that occurs on VT switch on Voodoo 3 and other 3dfx cards.
  
* Sun Feb  3 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6.14
- Added XFree86-4.2.0-tdfx-should-be-2048-not-2046.patch to fix a typo
  I found in the tdfx driver.
- Fixed bug in ttmkfdir Makefile.  In RHL 7.1 & 7.2 freetype 1 headers
  were in /usr/include/freetype however in RHL 7.2 for some god known
  reason they moved to /usr/include/freetype1/freetype.  No problem in
  RHL 7.2 as ttmkfdir used the freetype headers as part of the freetype
  build process rather than the system headers.
    
* Sun Feb  3 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-6
- Fixed base-fonts and font-utils conflicts lines
- Bumped release to 4.2.0-6, and rebuilt
- RHL 7.2 build release tag 4.2.0-0.6.13

* Sat Feb  2 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-5.2
- NEW XFree86-font-utils subpackage created for mkfontdir and ttmkfdir
  to reside in.  This will allow these utils to be available without
  requiring other XFree86 libs or packages being installed.
- Added patch to fix Matrox driver when VT switching to non-standard text
  modes (#59119)
- Created new Red Hat custom modelines patch, merged previous patches into
  it, and added new modelines from bug (#53364)
- RHL 7.2 build release tag 4.2.0-0.6.11
  
* Fri Feb  1 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-5.1
- Created XFree86-4.2.0-xfs-syslog.patch to make syslog log to LOG_DAEMON
  instead of LOG_LOCAL0 - which is supposed to be reserved for local
  system usage only.  Fixes bug (#24873)
- RHL 7.2 build release tag 4.2.0-0.6.10
  
* Thu Jan 31 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-5
- Enabled the now compiling gb18030 support patch
- RHL 7.2 build release tag 4.2.0-0.6.9

* Thu Jan 31 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-4.1
- Added gb18030 support patch to 4.2.0 <yshao@redhat.com>, but disabled it
  as it does not properly compile yet.
- enabled patch to force xfs to chdir to / before fork()
- RHL 7.2 build release tag 4.2.0-0.6.8

* Wed Jan 30 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-4.0
- Added XFree86-4.2.0-xkb-ar.patch for Arabic support (#56897)
- Also built 4.2.0-0.6.7 for RHL 7.2

* Tue Jan 29 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-3.6
- Added missing defattr to files list for XFree86-base-fonts (#59014,59020)
- Moved all /usr/X11R6/lib/modules files/dirs into same section of specfile
  and added dir flags for dirs that were not owned by the package.
- Enhanced the xfs initscript so "restart" shuts down xfs and starts it back
  up again, using the stop/start functions.  "reload" is now what reload and
  restart used to be - "kill -USR1" of xfs.
- Added zh_CN-i18n patch to fix an i18n problem with
  Chinese locales

* Mon Jan 28 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-3.4
- Added chmod kludge to bottom of install section to force locale/common
  *.so.* libraries to have execute perms.
- Also built 4.2.0-0.6.5 for RHL 7.2
- Removed the version from the Glide/Glide-devel build dependancies, so
  X will build if any version of Glide3 is present.
  
* Sun Jan 27 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-3.2
- Added link-glu-to-usrinclude patch for LSB conformance.
- Made xfs post script use /bin/false in 7.x builds and /bin/nologin in
  rawhide builds.  (#53088)
  
* Sat Jan 26 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-3.1
- NEW XFree86-base-fonts subpackage created to hold all of the base fonts
  that were previously contained in the main XFree86 package.  The new
  package contains Conflicts lines to minimize upgrading difficulties.
- Added Prereq: /sbin/chkconfig for XFree86-xfs
- Removed XFree86-4.1.0-ati-r128-PR-fix.patch as it was no longer needed,
  although not harmful in either case.
- Removed various other spurious patches that were no longer being applied,
  but were left in the specfile.
- Removed conditional support for building XIE and PEX as they have been
  deprecated by XFree86.org for quite some time now and are now obsolete

* Fri Jan 25 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-3.0
- Toggled BuildGlide3 flag so that Glide3 does not get built inside XFree86
  specfile by default.  Glide3 has been separated back out to a separate
  RPM package to simplify the XFree86 spec file, and ease maintenance.

* Thu Jan 24 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-2.5
- Fixed bug in xfs initscript fixing a problem with xfs having a CWD under
  /usr, which when located on an NFS mount, causes problems. (#57110)
- Enabled libGLw in build (#41791,#41974)
- Built also 4.2.0-0.6.1 for RHL 7.2
 
* Wed Jan 23 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-2.4
- Updated Wacom USB tablet driver Wacom-USB-driver-a25-update (#52947)
- Added xkb-french-canadian keyboard to xkb list (#52309)
- Fixed Xterm resource bugs (#48783,#49315,#58031,#58713)

* Sun Jan 20 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-2.2
- Disabled the old DisableModuleStringMerging hack in specfile as 4.2.0
  detects wether or not this option is required or not now via Imake tests.
- Conditionalized pam and automake buildprereqs

* Sun Jan 20 2002 Bernhard Rosenkraenzer <bero@redhat.com> 4.2.0-2.1
- Fix build in current tree (Glide is a mess)

* Sat Jan 19 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-2.0
- Bumped release number to -2.0 with no changes from -0.3 package, for
  building into rawhide.  All packages built for RHL 7.x should use release
  numbers less than -2, and preferably less than -1, ie: -0.x.y, so that
  upgrades stand a better chance of working in the future.

* Sat Jan 19 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-0.3
- Updated the "Requires: kernel-drm = 4.2.0" to ensure the user has the
  proper DRM version installed.  Newer rawhide kernels will now provide both
  kernel-drm = 4.2.0, as well as kernel-drm = 4.1.0 since the new DRM is
  supposed to be backward compatible.
  
* Sat Jan 19 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-0.2
- Added missing defattr(-,root,root) to xtrap-clients subpackage

* Sat Jan 19 2002 Mike A. Harris <mharris@redhat.com> 4.2.0-0.1
- XFree86 4.2.0 released - first build

* Fri Jan 18 2002 Mike A. Harris <mharris@redhat.com> 4.1.99.7-0.1
- CVS trunk update to 4.1.99.7
- dropped patches that have been merged upstream

* Sun Jan 06 2002 Mike A. Harris <mharris@redhat.com> 4.1.99.4-0.1
- CVS trunk update

* Wed Dec 26 2001 Mike A. Harris <mharris@redhat.com> 4.1.99.3-0.1
- CVS trunk update

* Thu Dec  6 2001 Mike A. Harris <mharris@redhat.com> 4.1.99.2-0.2.4
- Integrated PPC arch changes from streeter@redhat.com
- Integrated the Chinese gb18030 support patches received from yshao@redhat.com
- Added SiS DRM patch (doesnt affect build as our DRM is in kernel rpm)

* Tue Dec  4 2001 Mike A. Harris <mharris@redhat.com> 4.1.99.2-0.2.3
- Removed eurofonts-X11.tar.bz2, and ulT1mo-beta-1.0.tar.gz from XFree86
  package, moving them to their own separate packages that do not conflict
  with XFree86 namespaces.  (Removed the ISO8859-2-Type1-fonts package)
- Added new shared libs libXTrap, libXrandr.so to file lists
- Added new applications to filelist: xrandr, xedit, luit, and various
  others, and their documentation.
- Added new subpackage XFree86-xtrap-clients to hold the new xtrap client
  utilities
          
* Sun Dec  2 2001 Mike A. Harris <mharris@redhat.com> 4.1.99.2-0.1.7
- Made XFree86 server binary SUID root when not supporting Xwrapper (#56986)

* Wed Nov 28 2001 Mike A. Harris <mharris@redhat.com> 4.1.99.2-0.1.5
- Conditionalized out Xwrapper as its functionality is built directly into
  the X server now.  To build it set BuildXwrapper to 1 in specfile.
  
* Mon Nov 19 2001 Mike A. Harris <mharris@redhat.com> 4.1.99.2-0.1.3
- Fixed that annoying Radeon hardware mouse cursor bug, where any mouse
  pointer that has a hotspot *NOT* on the left side of the pointer, caused
  the mouse to freeze up and jump around on left side of screen.
  XFree86-4.1.0-radeon-hardware-cursor-fix.patch
      
* Mon Nov 12 2001 Mike A. Harris <mharris@redhat.com> 4.1.99.2-0.1.2
- Updated xman patch, to use FreeBSD style man.config (why? I dunno.)

* Tue Nov  6 2001 Mike A. Harris <mharris@redhat.com> 4.1.99.2-0.1.1
- Added new entries to XftConfig for "console" and "fixed" to not antialias,
  which solves problems reported in konsole and other Qt applications.
- Updated CVS source to current.
- Removed patches that are now integrated into new upstream source base:
  XFree86-4.1.0-ati-radeon-dri-buildfix.patch

* Fri Nov  2 2001 Mike A. Harris <mharris@redhat.com> 4.1.99.2-0.0.4
- Fixed problems with WithExternalMesa disabled, in the file lists, etc.
- Made new section for internationalizaton patches (30-39), and moved all
  locale.alias patches to that section.
- Created some new aliases for en_AU, and en_CA and sent patches upstream.
  
* Thu Nov  1 2001 Mike A. Harris <mharris@redhat.com> 4.1.99.2-0.0.2
- Initial fork from 4.1.0 codebase to separate branch for 4.1.99.2 CVS
- Set Build_7x to 0, which now means XIE, PEX and external Mesa are gone,
  and the doctor says I can stop taking my medication now.
- Added preliminary support for building CVS snapshots, which will
  eventually result in nightly builds from CVS or somesuch.
- Removed patches that are integrated into new upstream source base:
  ati-r128-SM, cirrus-foobaroo-fix, allow-module-flags, Xrender-required-libs,
  libXfont-put-eof, twm-coredumpfix, compose-iso8859-2, crash-message-fixup,
  xinerama-extmod-fix
- Updated locale-nn_NO locale-en_BG patch, and sent upstream _again_.
- Updated mkfontdir-perms
- Added patch to remove SuperProbe leftovers.

* Tue Oct 30 2001 Than Ngo <than@redhat.com>
- Added XFree86-4.1.0-cpp-s390x.patch which fixes a man-pages of size 0
  bug on s390 (#54927,#54932)

* Sat Oct 27 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-5
- Disabled VT switch patch from -4 release after feedback of regression
- Updated the Savage driver with Tim Roberts 1.1.20t driver, this should
  fix the reported bugs with Staroffice locking up X, and also video
  memory detection problems: (#31879)
- Added XFree86-4.1.0-keycodes-abnt2.patch to fix abnt2 support bug(#55128)

* Mon Oct  7 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-4
- Added patch to fix VT switch hangs that are hardware independent.  This
  should fix numerous reported VT switch bug reports.
- Fixed up host.def parallel make stuff.. HasParallelMake define is broken,
  and unneeded for now.

* Sat Oct  6 2001 Mike A. Harris <mharris@redhat.com>
- Removed __rmfontpath macro, and its usage, as well as the rpm 4.0.3 dep,
  because a lot of people were getting snagged on it, and it is questionable
  of the benefit of removing the fontpaths anyways, since it does not harm
  anything by leaving the font paths in config files really.
- Changed /lib/libpam reqs to pam-devel instead
- Commented the DisableModuleStringMerging specfile define, and moved to top
  of specfile where it is much more visible, as a lot of people have been
  getting snagged on this.

* Wed Oct  3 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-3.9
- Modified and unified the "make World" buildlines by removing all the
  buildflags, etc. from them, and moving them into proper Imake configuration
  variables.
- Added "-pipe" to default C compiler flags, as it should work on all
  architectures now.
- Various other specfile cleanups.
- Created support for ATI Rage 128 PP (1002:5050) XFree86-4.1.0-ati-r128-PP.patch
  
* Mon Sep 24 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-3.8
- Silenced some Glide3 compiler warnings with Glide3-redhat-cleanup-1.patch.

* Sun Sep 23 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-3.5
- Primary integration of changes in specfile to allow simple conditional
  build of fully debuggable modularized XFree86 packages.  This is done by
  enabling DebuggableBuild RPM macro at top of specfile, adding "dbg" to
  Release tag, and rebuilding.  The resulting RPM packages total in at 127Mb
  of data, as opposed to 55Mb or so regularly.  In order to debug this
  debuggable XFree86, a special patched version of gdb 5.0 is required, which
  is currently a work in progress based on a much older patch for gdb 4.18.

* Mon Sep 17 2001 Mike A. Harris <mharris@redhat.com>
- Changed xfs initscript to use find -cnewer instead of -newer to fix
  bug (#53737)

* Wed Sep  5 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-3 
- Reordered font paths in xfs catalogue to put 75dpi first, etc..
- fixed couple critical specfile bugs that have slipped through til now

* Tue Sep  4 2001 Mike A. Harris <mharris@redhat.com>
- Fixed fs/config bug (MF#53103) as well as doing the same for XftConfig

* Fri Aug 31 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-2
- Fixed a couple SHOULD-FIX bugs - fontpath order (SF#52413),
  metaSendsEscape bug (SF#49315)

* Wed Aug 29 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-1.1
- Added "Requires: kernel-drm = 4.1.0" so that a matching kernel RPM package
  is installed and DRI works properly.  (Brought up by mkj/arjan, and agreed
  upon by me)

* Tue Aug 28 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-1
- Added dont-build-pex-docs patch from Branden Robinson to disable building
  PEX documentation (deprecated and obsolete)
- Fix permissions on XftConfig, and other source files. (MF#52735)
- Bravely bumping version to 4.1.0-1
- Added xinerama-extmod patch for bug (#52842)

* Mon Aug 27 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.99.2
- Added Obsoletes: XFree86-ISO8859-2-Type1-fonts < 4.1.0, and provides
  ISO8859-2-Type1-fonts, to fix upgrade from 7.1, and prepare for future
  packaging.
- Removed (noreplace) from fs/config, I *want* it to replace.
  
* Sun Aug 26 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.99.1
- Completed font related fixups (hopefully)
- Added specfile buildroot install time removal of fonts.dir files as they
  should never ever be included in the RPM packaging, but generated at
  runtime instead.

* Fri Aug 24 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.20.5
- Added XFree86-4.1.0-ati-pciids-cleanup.patch, which includes misc
  cleanups to the PCI tables for ATI hardware.
- Added ati-radeon-dri-buildfix from notting@redhat.com which hopefully
  fixes bug (#51884)

* Tue Aug 21 2001 Mike A. Harris <mharris@redhat.com>
- Completed font screwup overhaul take1.

* Mon Aug 20 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.20.1
- Added XFree86-4.1.0-s3virge-mx.patch to fix some corruption issues on
  S3 Virge MX hardware.
- BuildPreReq: rpm >= 4.0.3  (parameterized macro fix)

* Sat Aug 18 2001 Mike A. Harris <mharris@redhat.com>
- Exclude XFree86 doc dir from, and add xdm pixmaps to s390 arch.

* Wed Aug 15 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.20.0
- Added xman-soelim-fix to fix bug (#51037).
- Modified cirrus-foobaroo patch to disable debug messages (#51179)
- Backed out an xfs change that breaks serving 3.3.6 servers.  Attempted
  workaround for (#)
- Disable ATI update patch to see if it fixes Radeon DRI bugs.

* Mon Aug 13 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.9.13
- Added XFree86-4.1.0-radeon-slowdownthere.patch to fix bug where ATI
  Radeon hangs on faster computers when VT switching.
- Created fix for mkfontdir to force permissions on newly created fonts.dir
  and encodings.dir files to be mode 644, fixes bug (#51636)
- Added fix for iso8859-2 compose file (affects Mozilla)
- Added patch to prevent X error messages from referencing log file if
  it has not yet been opened.
- Created support for ATI Rage 128 SM (Xpert2000), and added rage128-SM patch
  to fix (#34732,#51230,#50231) <mharris@redhat.com>
- Created XFree86-4.1.0-locale-alias-en_GB.patch to fix (#47247,51169)
- Moved video hardware documentation in /usr/X11R6/lib/X11/doc to main
  XFree86 package as that is where the drivers are (#50828)
- Updated XFree86 dependancy on Mesa to -> 3:3.4.2-5

* Thu Aug  9 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.9.12
- Synced with XFree86 stable branch to pick up upstream bugfixes
- Added support for Japanese 109 key USB keyboard

* Wed Aug  8 2001 Mike A. Harris <mharris@redhat.com>
- merged new changes into specfile
- added nn_NO, en_GB locale.alias support
- Added support to xfs.init for .ttc font files, and to use case
  insensitive regex when grepping for truetype fonts.  (#41169)

* Sun Aug  4 2001 Bill Nottingham <notting@redhat.com> 4.1.0-0.9.11
- port & apply necessary DRI fixes that fell out

* Thu Aug  2 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.9.10
- Added custom Red Hat XftConfig to fix AA font problems (#49937)
- Added RPM_BUILD_ROOT to ia64 libxrx removal.. ;o(

* Tue Jul 31 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.9.9
- Enabled "HasLinuxInput YES" to force wacom driver to get built with USB
  support with 2.4 kernel.  Fixes bug (#50453).
  
* Mon Jul 30 2001 Mike A. Harris <mharris@redhat.com>
- Attempted fix for (#50043) -frame option ignored when -id option used
  on xwd  (XFree86-4.1.0-xwd-frame-option.patch)
- Made XF86Config-4 outside ifnarch s390 as Bero claims s390 uses it.

* Thu Jul 26 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.9.8
- Added improved X startup messages for debugging purposes
- Updated patch148 from ATI plus 2 minor buildfixes

* Wed Jul 25 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.9.7
- Added XFree86-4.1.0-libXfont-put-eof.patch to fix bug (#48830) where
  the 100dpi/75dpi helvBO12.pcf.gz fonts were getting munged.
- Added XFree86-4.1.0-twm-coredumpfix.patch to fix (#49674)
- Added XFree86-4.1.0-cirrus-foobaroo-fix.patch from Egbert Eich to attempt
  to fix the Cirrus Logic problems.
- Fix libxrx problem on ia64 (#49990) by removing libxrx from non-x86/alpha

* Tue Jul 24 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.9.4
- Added XF86Config and XF86Config-4 as owned config files (latter ghosted)
- Fixed s390 Buildprereq on gcc by unnegating macro test
- Apply patch 3003 (64bit.patch) to all 64bit arch's.

* Tue Jul 24 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.9.3
- Worked around rpm parameterized macro processing bug that caused a problem
  with postun scripts - discovered by rpmlint.
- Reformatted all pre/post/postun/etc. scripts to be more readable and
  maintainable.
- Added patch8 to xterm resources to provide RFE (#48783)

* Mon Jul 23 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.9.2
- Added bison, zlib-devel as Buildprereqs - discovered on s390 by
  <Karsten.Hopp@redhat.de>
- Added ati-radeon-ve patch from ATI (patch148)
- Made Prereq's on /usr/sbin/chkfontpath instead of on chkfontpath

* Sun Jul 22 2001 Mike A. Harris <mharris@redhat.com>
- ifnarchd patch1013 for s390

* Wed Jul 18 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.9.1
- Created new macro __rmfontpath to be called from font package postun
  scripts to fix bug (#49243)

* Mon Jul 16 2001 Mike A. Harris <mharris@redhat.com>
- Added /usr/X11R6/man/man6, and other non existing manX dirs to XFree86-libs
  package so anything using them ends up having the dir owned by something.
- Removed unneeded shared lib stuff (Xv/Xxf86dga)

* Sun Jul 15 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.9.0
- Added BuildPrereq: gcc >= 2.96-93 to guarantee compiler used supports
  the -fno-merge-constants option
- Made External Mesa usage conditionalized via WithExternalMesa so that it is
  easy to rebuild XFree86 with/without using external Mesa, which will be the 
  default at some point in the future.

* Wed Jul 11 2001 Mike A. Harris <mharris@redhat.com>
- Explicitly state mkfontdir path in __mkfontdir macro (#48829)

* Tue Jul 10 2001 Mike A. Harris <mharris@redhat.com>
- Removed SharedLibXdmGreet from host.def, it is the same as default anyway
- Removed tcl and tk as buildprereq's, Bero says they're not needed anymore

* Tue Jul 10 2001 Tim Powers <timp@redhat.com> 4.1.0-0.8.6
- don't require XFree86-compat-libs in XFree86-libs

* Tue Jul 10 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.8.5
- Fixed missing requiredlibs on shared libXrender so that prelinking works.
- Built 4.1.0-0.8.4
- Woops, I left shared libXv and libXxf86dga on again by accident.
- Built 4.1.0-0.8.5
  
* Mon Jul  9 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.8.1
- Fixed up xdm pre script
- Fixed up missing Latin2 Type1 fonts, they are now in the fonts/Type1 dir
- Removed shared libXv.so and libXxf86dga.so at request of XFree86 team,
  and in conjunction with discussion with Debian X maintainer.

* Mon Jul  9 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.7.51
- Fixed ia64 Glide3 build failure.

* Sun Jul  8 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.7.50
- Merged with xf-4_1-branch to pick up stable bugfixes, and removed
  XFree86-4.1.0-redhat-glint-missing-symbols.patch, also Banshee
  ramtiming fix picked up from the update. 
  
* Fri Jul  6 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.7.12
- Really disabled string merging this time
- Added verify flag to /etc/X11/fs/config
- Disabled shared libraries Xv/xf86dga for standards compliance.  These
  libraries do not have a stable API and should not be shared.  It was
  a Bad Idea(tm) to ship these.

* Wed Jul  4 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.7.8
- Disabled string merging in modules using ModuleLdFlags in host.def
- Added WORLDOPTS= to make World to get rid of the "-k" passed to make so
  that failed X builds will fail immediately instead of continuing on.

* Mon Jul  2 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.7.6
- Phase 1 - Amalgamated all my local font related changes to get fonts
  working better in the new 4.1.0 release. Straightened out 75dpi/100dpi
  brokenness and split up packages.
- mkfontdir is now called in post(un)install scripts, and fonts.dir files are
  not installed as part of packages anymore because it was a bad broken idea
  to do so because these files should be generated, not provided.
- Added missing \ in main package post script

* Thu Jun 21 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.7.5
- Added customer requested custom 1152x864x85Hz modeline

* Sun Jun 17 2001 Mike A. Harris <mharris@redhat.com>
- Reworked all ISO8859-* font subpackages for 4.1.0.  fonts.dir is not
  included in the packages, rather it is generated at post install time.
- Refixed (#31618)

* Sat Jun 16 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.6.1
- More s390 cleanups

* Fri Jun 15 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.6.0
- Integrated s390 patches sent by Than from Oliver Paukstadt

* Sat Jun  9 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.5.6
- Cleaned up unneeded Freetype2 stuff in host.def

* Fri Jun  8 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.5.6
- Take-1 at cleaning up some of the font related 'issues' due to the different
  way fonts are generated in 4.1.0.  Still many issues remaining.

* Wed Jun  6 2001 Mike A. Harris <mharris@redhat.com>
- Folding the external Mesa into XFree86 created as many problems as it
  solved.  The DRI CVS trunk has a more permanent solution worth checking out.
- Since the V4L drivers have apparently been included in the main XFree86
  package all this time, I've removed the separate package.

* Mon Jun  4 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.1.5
- First stab at assimilating Mesa 3.4.2 package into XFree86 package
- Added missing symbols to glint driver (#42751)

* Mon Jun  4 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.0.2
- Rebuilt against Mesa 3.4.2 in new environment

* Sat Jun  2 2001 Mike A. Harris <mharris@redhat.com> 4.1.0-0.0.1
- XFree86 4.1.0 released - built 4.1.0-0.0.1

* Thu May 31 2001 Mike A. Harris <mharris@redhat.com> 4.0.99.901-0.0.6
- Remove GLw manpages since we don't ship libGLw (#41791)
- I finally got XIE and PEX disabled completely for sure this time absolutely
  no question.  No really...  It's gone.

* Wed May 30 2001 Mike A. Harris <mharris@redhat.com> 4.0.99.901-0.0.4
- Updated to 4.0.99.901, removed unneeded patches
- Removed Glide3 Provides/Obsoletes from devel package, and removed the
  Glide3 devel stuff from that package also - only X needs it during build
- Removed BuildGlide3 conditional - Glide3 will always be built from now on
- Added conditionals BuildPEX & BuildXIE.  These have officially been obsoleted
  by XFree86, and are no longer actively supported or used by anything.

* Mon May 28 2001 Mike A. Harris <mharris@redhat.com> 4.0.99.900-0.2.5
- Added "Options" database file, and also the following apps and their
  manpages:  dpsexec, dpsinfo, texteroids, xftcache
- Removed hardcopy doc creation code (groff) from specfile.  The XFree86
  makefiles have been fixed now to do this themselves properly.
- Removed Glide3 headers from XFree86-devel.  Only needed during build, no
  apps should be linking to Glide3.
- Simplified filelist for libs subpackage by using globs instead of hard
  coded library version numbers.
- Removed use-cpp patch, done with imake now.

* Sun May 27 2001 Mike A. Harris <mharris@redhat.com> 4.0.99.900-0.2.2
- Merged bero's changes to my local sources, and changed libXmuu inclusion
  from libXmuu.* to libXmuu.1.0, so that the *.so doesn't get picked up also,
  as it should be in the devel package.

* Mon May 21 2001 Bernhard Rosenkraenzer <bero@redhat.com> 4.0.99.900-0.2.1
- Add missing libXmuu.* files

* Sun May 20 2001 Mike A. Harris <mharris@redhat.com>
- Many fixes from H. J. Lu <hjl@gnu.org> including enhanced parallel make,
  xterm-xaw3d, pex patches, specfile updates, build enhancements and a
  partridge in a pear tree.  ;o)
- Fixed insane off-the-screen indenting levels in xfs.init

* Sat May 19 2001 Mike A. Harris <mharris@redhat.com>
- Updated to 4.0.99.900
- Updated with the latest parallelmake patch from H. J. Lu <hjl@gnu.org>
- Added new specfile option ParallelBuild, so that any parallel build
  stuff can be conditionally defined in the specfile in case the parallel
  make patch breaks in the future.

* Fri May 11 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Fix build

* Wed May  9 2001 Mike A. Harris <mharris@redhat.com> 4.0.99.3-0
- Updated 4.0.99.x package to 4.0.99.3 release, forward ported all
  relevant changes that have occured in 4.0.3 packaging since March 27th
  until now, and brought the 4.0.3 specfile changelogs into the 4.0.99.3
  spec changelog.  The two releases should be syncronized now.

* Mon May  7 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-14
- Syncronize XFree86 with Mesa 3.4.1-1
- Disable alpha-hack from May 3rd and add new patch from Compaq to replace it

* Fri May  4 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-13
- Updated patch0 to latest XFree86 stable branch for 4.0.3.  Fixes many
  3dfx bugs in tdfx driver.
- Moved locale data from /usr/X11R6/lib/X11/locale in main package to
  XFree86-libs package where it belongs. (#38408)
- Corrected dumb reversal in XFree86CustomVersion Imake define in specfile
    
* Thu May  3 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-12
- Reverted ia64-int10 patch from Alpha.
- Added XFree86-4.0.3-alpha-hack-bypass-int10bug.patch from
  Jay Estabrook for Alpha.

* Wed May  2 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-11
- Removed RPM_BUILD_ROOT from glide section (#38031)
- Enabled XFree86-4.0.2-ia64-int10.patch on alpha as well for testing.

* Wed Apr 25 2001 Mike A. Harris <mharris@redhat.com>
- Added XFree86-4.0.3-compose-kill-ctrl-shift-t.patch to fix (#23473)

* Mon Apr 23 2001 Mike A. Harris <mharris@redhat.com>
- Added rhl-startupmessages patch to aide debugging and troubleshooting
  bug reports.  This should increase the usefulness of user submitted
  XFree86 log files and decrease the turnaround time on requesting info
  and waiting for someone to provide that info.  Patch doesn't do much yet,
  but will be enhanced later.
- Added xset manpage enhancement

* Sat Apr 21 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-10
- ifarch'd XFree86-4.0.2-agpgart-load.patch to only apply on non-alpha

* Sat Apr 14 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-9
- Removed dependancy of main XFree86 package on xfs by moving the XFree86
  server modules "/usr/X11R6/lib/modules/{codeconv,fonts}/*" from the xfs
  subpackage to the main XFree86 package as they never belonged in the xfs
  package in the first place.  This is an ancient packaging error.
- Added patch from Tim Waugh to fix Xaw password entry in vnc.  (#19231)

* Thu Apr 12 2001 Mike A. Harris <mharris@redhat.com>
- Killed ancient non-FHS compliant symlink to /usr/man/X11
- Disabled XFree86-4.0.3-savage-glitch.patch to fix (#34376)

* Mon Apr  9 2001 Mike A. Harris <mharris@redhat.com>
- Made glidelink get called before ldconfig in %%post libs

* Mon Apr  9 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-8
- Simplified the main package %%pre script symlink munge code
- Fixed bug in %%post xfs section - inadvertently added in 4.0.3-6 release
- Disable patch #220 as it is unnecessary - taken care of via Imake ages ago.

* Sun Apr  8 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-7
- Fixed (#32574) by adding a preinstall script on xdm which moves the dir
  /etc/X11/xdm/authdir to /var/lib/xdm/authdir if it exists, and symlinking
  /etc/X11/xdm/authdir to it.  Corrected the filelist for xdm to include
  these changes.
- Fixed alpha build failure with tga driver patch, ifdef with no macro.

* Fri Apr  6 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-6
- Force enabled BuildXinerama and BuildXineramaLibrary in hosts.def
- FHS compliant manpage sections (4x/7x)

* Thu Apr  5 2001 Mike A. Harris <mharris@redhat.com>
- Added new patches submitted by Compaq for various drivers, etc.
  XFree86-4.0.3-compaq-alpha.patch, XFree86-4.0.3-compaq-glint.patch
  XFree86-4.0.3-compaq-radeon.patch, XFree86-4.0.3-compaq-r128.patch
  XFree86-4.0.3-compaq-mga.patch, XFree86-4.0.3-compaq-tga.patch
  (courtesy of Jay Estabrook)

* Thu Mar 29 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-5
- XFree86 4.0.3 defaults to building libfreetype if Xft is being built,
  so freetype is now disabled with Imake defines.
- Removed shared libsXxf86dga and libXv hack I added on Mar 9 and
  did it properly with Imake defines.  Also fixes (#31232)

* Wed Mar 28 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-4
- Added patch XFree86-4.0.3-glide3-libdir.patch so tdfx driver
  can find the Glide3 libs included with X package.
- Minor xfs.init fix
- Added XFree86-4.0.3-mga-hwcursor-fix.patch

* Tue Mar 27 2001 Mike A. Harris <mharris@redhat.com>
- Updated g450 port from 4.0.3 to XFree86-4.0.99.1-mga-g450-dualhead.patch
- Updated Savage driver dropin to version 1.15
- Added patches 405 - 408 from 4.0.3-4 build

* Sun Mar 25 2001 Mike A. Harris <mharris@redhat.com>
- Initial specfile fork of 4.0.99.1 from 4.0.3-3
- Removed unneeded patches:  XFree86-4.0.1-dri-sym.patch,
  XFree86-4.0.2-mga-busmstr.patch, XFree86-4.0.2-r128-busmstr2.patch,
  XFree86-4.0.2-r128-mobility.patch, XFree86-4.0.2-agpgart-load.patch,
  XFree86-4.0.2-r128-drm-do-wait-for-fifo.patch
- Updated patches: XFree86-4.0.99.1-parallelmake.patch,
  XFree86-4.0.99.1-locale-euro.patch, XFree86-4.0.99.1-winkey-alt-meta.patch  

* Fri Mar 23 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-3
- Drumroll...... Final (or is it?) working G450 dualhead update.  ;o)

* Thu Mar 22 2001 Mike A. Harris <mharris@redhat.com>
- Added pam patch for xdm from Nalin <nalin@redhat.com> Patch404

* Wed Mar 21 2001 Mike A. Harris <mharris@redhat.com>
- Fixed uninitialized memory reference in xlib (Patch401)  (#32222)
- Make libs subpackage depend on kudzu-devel, pciutils-devel for 
  Glide3 (#32534)
- Matrox G450 updates

* Mon Mar 19 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-2
- Fixed glitch in %%post xfs section of spec (#32281)
- Set "umask 133" in xfs initscript so that fonts.dir/fonts.alias files 
  created during script execution work also for non-root users that may
  have changed root's umask.
- Updated Mesa dependancy in specfile to 3.4-13

* Sun Mar 18 2001 Mike A. Harris <mharris@redhat.com>
- Removed XFree86-4.0.1-xterm-appdefaults.patch as it was redundant

* Sat Mar 17 2001 Mike A. Harris <mharris@redhat.com> 4.0.3-1
- New XFree86 4.0.3 released and integrated.
- Updated patches for 4.0.3, removed unneeded patches.
- Built 4.0.3-1

* Fri Mar 16 2001 Mike A. Harris <mharris@redhat.com>
- Reverted G450 driver back to dwmw2's driver.
- Built 4.0.2a-2

* Thu Mar 15 2001 Mike A. Harris <mharris@redhat.com> 4.0.2a-1
- Added XFree86-4.0.2-locale.patch from Phil Knirsch <pknirsch@redhat.com>
  which should fix all problems with euro locales, and other locale issues
  including bug id's (26300,21882,28447, others)
- xfs crash errors should all be fixed now by the XFree86 stable branch
  patch.  Bugzilla (#22538)

* Wed Mar 14 2001 Mike A. Harris <mharris@redhat.com> 4.0.2a-1
- New patch XFree86-4.0.2a-mga-g450-dual_6.patch - G450 driver update 
  from Luugi Marsan <lmarsan@matrox.com>
- Added new euro locale stuff from Phil Knirsch <pknirsch@redhat.com>
- Added XFree86-4.0.2-r128-drm-do-wait-for-fifo.patch from Gareth Hughes
  which should fix the r128 errors in (#26999)
  
* Tue Mar 13 2001 Mike A. Harris <mharris@redhat.com>
- Added provides entries for Glide3 in libs and devel subpackages
- Take 2 of XFree86-4.0.2a-im-being-included-and-i-cant-get-up2.patch
- Moved XftConfig file to /etc/X11 and made compatibility symlink.

* Fri Mar  9 2001 Mike A. Harris <mharris@redhat.com>
- Updated main tarball to 4.0.2a (even though it's the same code we had before
  with 4.0.2 + stable branch patch).
- Updated stable branch patch to bring 4.0.2a up to date with xf-4_0_2a-branch
- Nvidia nv driver updated with MANY fixes from XFree86 stable branch
- Added shared libraries: libXv.so, libXxf86dga.so
- Re-enabled Sparc build.  That machine is slow, someone
  needs to put a spark under it to get it going.  ;o)
- Fixed (#13882) with XFree86-4.0.2-winkey-alt-meta.patch
- Fixed (#19308) added X11R6-contrib obsolesence

* Fri Mar  9 2001 Bill Nottingham <notting@redhat.com> 4.0.2-12.1
- fix glide dependencies

* Thu Mar  8 2001 Mike A. Harris <mharris@redhat.com> 4.0.2-12
- Fixed alpha/ia64 build problems
- Built 4.0.2-12

* Tue Mar  6 2001 Mike A. Harris <mharris@redhat.com>
- Created XFree86-4.0.2-r128-mobility.patch to enable external display
  on Rage Mobility laptops, etc.
- Added XFree86-4.0.2-xft-match.patch (from Bero) (#30836)
  
* Mon Mar  5 2001 Mike A. Harris <mharris@redhat.com>
- Added XFree86-4.0.2-alpha-pci-resource.patch (#30417)

* Sat Mar  3 2001 Mike A. Harris <mharris@redhat.com>
- Glide3 is back (was previously removed on Feb 22)
- Removed loaderProcs.h hack, and replaced with a patch.
- Tidied up a tonne of XFree build warnings
- Added XFree86-4.0.2-im-being-included-and-i-cant-get-up.patch stop
  loaderProcs.h from being wrongly included in building Xnest due to
  a compiler bug.

* Fri Mar  2 2001 Mike A. Harris <mharris@redhat.com>
- Added mga and r128 busmaster patches that Todd Nix <todd@xymox.us.dell.com>
  sent me from Kevin E Martin <martin@valinux.com>.

* Wed Feb 28 2001 Mike A. Harris <mharris@redhat.com> 
- Updated xf-4_0_2-branch patch to todays latest stable code
- Removed unneeded patches after update: XFree86-4.0.2-time.patch,
  XFree86-4.0.2-sis-unresolved-memcpy.patch    
- Added XFree86-4.0.2-agpgart-load.patch from Bill Nottingham to force
  load AGPgart kernel module when a DRI module is loaded.
- Fixed "chmod" in xfs.init (#18573)
- Added BuildPreReq ncurses-devel
- Repaired ia64 int10 patch
- Tidied up specfile, particularly the host.def generation section, and 
  incorporated xfree86.def mess into host.def section where it belongs.

* Tue Feb 27 2001 Mike A. Harris <mharris@redhat.com> 4.0.2-11
- Added updated driver for Savage chipset.  Should fix all known issues
  with Savage cards that I'm aware of.
- Removed Prereq of chkfontpath on xfs subpackage and modified xfs initscript
  to only call chkfontpath if it is installed.
  
* Mon Feb 26 2001 Mike A. Harris <mharris@redhat.com> 4.0.2-10
- Added specfile %%pre fix for (#26857) - problem upgrading to
  Wolverine from Red Hat 5.2 due to directory/symlink fu glitch.
- Enabled Utempter for xterm with "UseUtempter" in specfile
- Added neomagic softcursor patch for (Helge Deller <hdeller@redhat.de>)
- Built 4.0.2-10
- Created patch XFree86-4.0.2-sis-unresolved-memcpy.patch to fix
  bugs (#19530,24670)

* Fri Feb 23 2001 Mike A. Harris <mharris@redhat.com>
- Added spec hack to fix bad include of loaderProcs.h in miinitext.c
  I believe this fixes some of the r128 DRI problems.  I can't get
  r128 DRI to crash anymore now anyways.  It isn't mind blowingly 
  fast though.  May have fixed other problems as well.  X seems much
  smoother now, and VT switching is much faster also.

* Thu Feb 22 2001 Mike A. Harris <mharris@redhat.com>
- Added ExcludeArch tag to quell failed sparc builds (unsupported)
- Re-enabled DRI for mga/r128, but they still do not work

* Sat Feb 17 2001 Mike A. Harris <mharris@redhat.com>
- Updated fix for xfs death bug with truetype fonts.
- Added chkfontpath require to xfs subpackage (#19603)
- Added XFree86-4.0.2-banshee-ramtiming.patch to fix (#26351,#18810)
- Added ia64-int10 patch. (Bill Nottingham)

* Thu Feb 15 2001 Mike A. Harris <mharris@redhat.com>
- Fixed xfs.config

* Tue Feb 13 2001 Mike A. Harris <mharris@redhat.com>
- Disabled DRI drivers r128 and mga because they are broken.
- Built XFree-4.0.2-8
- Fixed bad noarch thing
- Built XFree-4.0.2-9

* Mon Feb 12 2001 Mike A. Harris <mharris@redhat.com>
- Merged in separate XFree86-ISO8859-2 font package

* Sun Feb 11 2001 Mike A. Harris <mharris@redhat.com>
- Added 1400x1050 modeline patch for newer laptops
- Misc fixups
- Disabled DRM kernel module building as we don't use these modules
  anyway.
- Updated 4.0.2-branch patch
- Updated XFree86-4.0.2-xfree86.lst.patch

* Thu Feb 08 2001 Mike A. Harris <mharris@redhat.com>
- Internationalized xfs and xdm initscripts

* Wed Feb 07 2001 Mike A. Harris <mharris@redhat.com>
- New fix for Cirrus 5480 (H.J. Lu)
- Matrox g450 patch that _hopefully_ works this time (from dwmw2)

* Tue Feb 06 2001 Mike A. Harris <mharris@redhat.com>
- (#25890,#26131) tdfx dri driver not included.. specfile mixup, fixed.
- (#23896) Added option for building with Glide2 (default=off).  Dunno if
  it works or not as I'm not testing it.  If someone wants to further the
  enhancement at all, I'll accept specfile patches to add any missing bits. ;o)
- (#25131) Fixed xfs.config file glitch (Truetypex typos), and a similar
  bug in specfile hack.
- Updated to recent XFree86 stable bug fixes (Patch #1)
- Fix temp files vulnerabilites in xman on systems with mkstemp()
- Fix temp vulnerabilities in Xaw/MultiSrc.c
- Fix temp file vulnerability in gccmakedep based on report from Alan Cox.
- Fix temp file vulnerability in Imake.rules
- Fix temp file vulnerability in InstallManPageAliases
- Fix Neomagic 2200 screen corruption
- Add an imake control for determining when xload should be installed set-gid

* Thu Jan 25 2001 Mike A. Harris <mharris@redhat.com>
- Added g450 patch from Matrox.  Lets see some dualhead action baby!
- Filtered out M$ Windows CR's from the Matrox patch, hope I got them
  all.  Windows bad, Linux good.  ;o)
- Removed all prior g450 patches as the new one repaces them all
- Many spec file simplifications, and general tidy up job.

* Wed Jan 24 2001 Bill Nottingham <notting@redhat.com>
- fix perms on xload

* Wed Jan 24 2001 Matt Wilson <msw@redhat.com>
- chmod 644 XftConfig before piping to it

* Wed Jan 24 2001 Mike A. Harris <mharris@redhat.com>
- Disable Cirrus 5480 patch as it wont apply cleanly to 4.0.2.
- Removed v4l patch - its in 4.0.2 already
- (#23701) devel dependant on libs instead of main package.
- Added TrueType font dirs to config files for the ttfonts package
- Numerous other tweaks
- XFree86-4.0.2-4 built

* Tue Jan 23 2001 Mike A. Harris <mharris@redhat.com>
- Fixed xfs initscript to only start at boot time if X is installed.
- Put eurofonts package back and fixed it up with suggestions from
  H. J. Lu - as 2 font files are still needed.
- Changed xload %%install time chmod to %%attr instead
- Tidied up %%install section, removing redundancies.
- Added Cirrus Logic 5480 patch from from Egbert Eich (#24177)

* Mon Jan 22 2001 Mike A. Harris <mharris@redhat.com>
- Removed manpage "hack" section from specfile
- Removed eurofont tarball entirely.  It's included in X already under
  different names now.
- Removed mga, ATI, mesa patches from yesterday as they fail the
  build requiring many other missing items.
  
* Sun Jan 21 2001 Mike A. Harris <mharris@redhat.com>
- Added ATI driver patch from XFree CVS - lots of new fixes
- Added mga driver patch from XFree CVS (mainly for G450)
- Added mesa patch from XFree CVS
- Added BuildPrereq: pam-devel  (Bill Crawford <billc@netcomuk.co.uk>)
- Commented out BuildPrereq: pam-devel as it failed me
- Remove eurofont .bdf files after pcf's are created to quell duplicate
  font errors.

* Sat Jan 20 2001 Mike A. Harris <mharris@redhat.com>
- Added Xft update from XFree CVS
- Updated %%clean section
- Changed specfile bunzip references to bzcat
- Fixed all specfile references of "tar x" to "tar xf -"
- Added romanian-keyboard-fix from Cristian Gafton <gafton@redhat.com>

* Thu Jan 18 2001 Mike A. Harris <mharris@redhat.com>
- ATI r128 update from ATI.

* Wed Jan 17 2001 Mike A. Harris <mharris@redhat.com>
- Disabled tdfx builds as they die with missing glide3 libs
  (at least in RHL 7.0 it does)

* Tue Jan 16 2001 Mike A. Harris <mharris@redhat.com>
- Added BuildPrereq: flex >= 2.5.4a
- Added BuildPrereq: freetype-devel >= 2.0.1
- Added BuildPrereq: Glide3-devel >= 20001220 for tdfx

* Mon Jan 15 2001 Mike A. Harris <mharris@redhat.com>
- Updated fhs patch for 4.0.2
- Updated portuguese patch for 4.0.2

* Thu Jan 11 2001 Mike A. Harris <mharris@redhat.com>
- Integrated Matrox G450 driver for testing from Matrox

* Mon Jan 8 2001 Mike A. Harris <mharris@redhat.com>
- Added xfree86.lst patches from Brent Fox and also (#5977)
 
* Sat Jan 6 2001 Mike A. Harris <mharris@redhat.com>
- Misc spec file fixups

* Fri Jan 5 2001 Mike A. Harris <mharris@redhat.com>
- Integrated ATI driver from Michael Smith <msmith@ati.com>

* Wed Jan 3 2001 Mike A. Harris <mharris@redhat.com>
- Built 4.0.2 release 1

* Thu Dec 28 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Add a couple of missing man pages, noted by Thayne Harbaugh <thayne@plug.org>
- Use system freetype, now that we've updated
- Add missing XftConfig file

* Thu Dec 28 2000 Bill Nottingham <notting@redhat.com>
- don't list the driver modules explicitly; ship them all

* Thu Dec 21 2000 Bill Nottingham <notting@redhat.com>
- integrate tdfx_dri into main XFree86 package

* Tue Dec 19 2000 Bill Nottingham <notting@redhat.com>
- fix typos in xkb symlink/dir munging

* Tue Dec 19 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Add missing Xft (Xrender) includes in -devel
- Move xkb files back to their old locations, we can't replace directories
  with symlinks
- Add /etc/X11/xkb -> /usr/X11R6/lib/X11/xkb symlink for compatibility
- 4.0.2
- Get rid of twfix patch (it's in 4.0.2)
- Patch 302 must be applied with -p0, not -p1
- Add a %%clean section
- Get rid of /etc/X11/xdm/xdm-config in XFree86-xdm. Since kdm uses it, as well,
  it should be in xinitrc

* Thu Dec 14 2000 Mike A. Harris <mharris@redhat.com>
- Added XFree86-4.0.1-twfix.patch from bhuang@redhat.com to fix
  zh_TW locale.
- Added locale.alias patch from Jakub Jelinek.
- Removed unneeded patches, and tidied spec file a bit (yeah right). ;o)

* Wed Dec 13 2000 Bill Nottingham <notting@redhat.com>
- tweak the -pic patch so it works with the ELF loader (in theory)
- don't try and build the kernel modules

* Sun Dec 10 2000 Bill Nottingham <notting@redhat.com>
- reapply the parallelmake patch
- hm, libX11 and libXmu are now .6.2

* Sat Dec 9 2000 Mike A. Harris <mharris@redhat.com>
- Updated to CVS version xf-4.0.1Z

* Sat Dec  9 2000 Bill Nottingham <notting@redhat.com>
- add back in some patches (FHS, Xwrapper)
- make it build on ia64 (hopefully)

* Fri Dec 8 2000 Mike A. Harris <mharris@redhat.com>
- Added patch XFree86-4.0.1h-xf86Wacom.c-kernelheaderclash.patch to
  fix 4.0.1h build failure.

* Wed Dec 6 2000 Mike A. Harris <mharris@redhat.com>
- Fixed bug (#21303) changed 2 uses of arch "i386" to "%{ix86}"
- Remove dependancy on tar 1.13.18 by calling bunzip2 and piping to tar
- Removed I810Drm.tar.gz entirely as it smashes other dri code (mga,etc)
  and is ancient

* Wed Dec 6 2000 Mike A. Harris <mharris@redhat.com>
- Updated to CVS version xf-4.0.1h which includes many updates and
  integrates many Red Hat patches directly into XFree86 CVS.

* Sat Nov 10 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Update to current. This should fix, among other things, DRI/DRM stuff on
  Matrox cards and i18n.
- Fix build with tar 1.13.18
- Add XKB patch for Romanian keyboards from Christian Gafton <gafton@redhat.com>
- Fix up Euro sign support

* Wed Oct 25 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Don't apply the PIC patch on non-ia64 platforms, it breaks X startup on x86.

* Mon Sep 25 2000 Bill Nottingham <notting@redhat.com>
- minor tweaks for ia64/glibc-2.2 build

* Thu Aug 24 2000 Bill Nottingham <notting@redhat.com>
- never mind, it doesn't. Wheee.

* Wed Aug 23 2000 Bill Nottingham <notting@redhat.com>
- oops, the r128 mobility patch breaks regular r128 cards

* Tue Aug 22 2000 Bill Nottingham <notting@redhat.com>
- fix DGA for real
- add support for the r128 Mobility chips

* Tue Aug 15 2000 Bill Nottingham <notting@redhat.com>
- fix xterm app-defaults file (#13584)
- don't build a shared xdm greeter lib

* Mon Aug 14 2000 Bill Nottingham <notting@redhat.com>
- fixes for MGA dri (text corruption)
- spell Portuguese correctly in keymap list (#12343)
- fix some absolute symlinks (#16133)
- fix xman's man config path (#15974)
- fix broken xdm pam code (#15952)
- fix bug in ATI driver (#14344)

* Fri Aug 11 2000 Bill Nottingham <notting@redhat.com>
- revert some of the i810 code; it breaks VC switching

* Sun Aug  6 2000 Bill Nottingham <notting@redhat.com>
- fix DGA so that 4.x-compiled DGA1 apps can run against 3.3.x servers
- fix tempfile handling in makedepend
- use cpp, not gcc -E 

* Fri Aug  4 2000 Bill Nottingham <notting@redhat.com>
- more CVS updates (Neomagic fixes, some i810)
- fix sparc build

* Thu Aug  3 2000 Bill Nottingham <notting@redhat.com>
- do *not* do xfs stop/start in condrestat

* Wed Aug  2 2000 Bill Nottingham <notting@redhat.com>
- update CVS (i810 fixes, others)
- move some more files out of -xdm, into xinitrc package
- remove /usr/share/fonts/default/TrueType from default xfs config (#14683)
- fix weirdness in the i810 driver update

* Wed Aug  2 2000 Matt Wilson <msw@redhat.com>
- hack to work around gcc bug triggered by xwd (patch207)
- modified xfs post script to add in no-listen = tcp per Bill's request

* Tue Jul 25 2000 Elliot Lee <sopwith@redhat.com>
- Some i810/i815 stuff (new I810Drm.tar.gz, updated to xf4.0.1-I810copy.patch only to find out
that it is already included in this source tree).

* Mon Jul 24 2000 Bill Nottingham <notting@redhat.com>
- add patch for xf86 vidmode extension
- add icelandic keymap to list of keymaps

* Sat Jul 22 2000 Bill Nottingham <notting@redhat.com>
- hey, we recognize the geforce2 now. Wonder if it works. :)

* Thu Jul 19 2000 Bill Nottingham <notting@redhat.com>
- oops, I broke the sparc Mach64 patch on sparc

* Wed Jul 18 2000 Bill Nottingham <notting@redhat.com>
- move initscript back
- update CVS
- remove Mesa (use its own separate package for easier updating)
- kill the GL wrapper
- fix linking of dri modules so that symbol resolution with Mesa works right
- add sparc Mach64 patch from DaveM
- fix sparc Mach64 patch so it builds
- add ffb patch from Jakub
- fix xfs user creation

* Fri Jul 14 2000 Elliot Lee <sopwith@redhat.com>
- Fix Mesa library version info
- Set Mesa package version to reflect Mesa version (not the XFree86
  version), and set release to something that will facilitate upgrades
  from older Mesa pkgs while still being informative.
- Only pass -j to toplevel make, which takes care of passing it on down.

* Thu Jul 13 2000 Preston Brown <pbrown@redhat.com>
- fixed xfs condrestart to do a real stop/start.
- fonts.* files in font directories are config(noreplace)

* Thu Jul 13 2000 Elliot Lee <sopwith@redhat.com>
- Update Mesa to 3.2 release.
- Use mmx/sse/x86 stuff for Mesa on 386 and up, not just if building for 686 (since MMX is
available on 586 many times, and since the functionality is runtime-configured).
- Try to integrate newer i810/i815 driver (unfinished)

* Mon Jul 10 2000 Bill Nottingham <notting@redhat.com>
- update CVS while I'm here
- don't use ix86 PCI code on ia64
- fix some int/long bogosity in some of the drivers

* Sat Jul  8 2000 Bill Nottingham <notting@redhat.com>
- update CVS
- build with new compiler to fix Xserver problems on i386
- add parallel make patch from H. J. Lu

* Tue Jul  4 2000 Bill Nottingham <notting@redhat.com>
- oops, open the right software Mesa lib
- build DRI everywhere

* Mon Jul  3 2000 Bill Nottingham <notting@redhat.com>
- fix Mesa install
- add Romanian keymap so keymaps get installed

* Sun Jul  2 2000 Bill Nottingham <notting@redhat.com>
- add console.apps file for xserver (#13325)
- prereq chkfontpath for font packages
- update CVS
- bump version to 4.0.1
- add lemming patch

* Fri Jun 30 2000 Bill Nottingham <notting@redhat.com>
- update CVS, sparc patches now included
- ship pam files
- point X symlink to Xwrapper, not XFree86

* Thu Jun 29 2000 Bill Nottingham <notting@redhat.com>
- fix pamsession, xfsredhat patches
- turn off joystick, it relies on magic symbols defined *nowhere*

* Wed Jun 28 2000 Preston Brown <pbrown@redhat.com>
- merged in a bunch of patches from 3.3.6 that somehow got dropped including:
- xkb changes
- some xfs changes
- xterm app-defaults
- pam session fix for xdm
- define some paths in host.def instead of a wild mess of patches
- kill compat links from /etc/X11/<dirname> to /usr/X11R6/lib/X11/<dirname>

* Wed Jun 28 2000 Bill Nottingham <notting@redhat.com>
- add Mesa wrapper
- put Mesa libs in /usr/lib
- return of Xwrapper
- take setuid off XFree86

* Wed Jun 28 2000 Jakub Jelinek <jakub@redhat.com>
- remove 3 obsolete SPARC patches
- add 2 new ones

* Tue Jun 27 2000 Bill Nottingham <notting@redhat.com>
- put setuid on XFree86 (temporary)
- yank setuid off xload 
- put the xfs %%pre back in
- xfs initscript munging
- fix ia64 patches

* Tue Jun 27 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Update to current CVS

* Thu Jun 22 2000 Bill Nottingham <notting@redhat.com>
- return of the font %%post/%%postuns
- move some of the xdm stuff to xinitrc
- put libglut in with Mesa

* Sun Jun 18 2000 Matt Wilson <msw@redhat.com>
- build glint module on alpha

* Thu Jun 15 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Fix up Xaw (Bugs #11404 and #11426)
- more FHS fixes (fix bug #11358 and some related unreported bugs)

* Wed Jun 14 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- split off Mesa and Mesa-devel
- FHSify
- fix build on alpha and ia64

* Wed Jun  7 2000 Bill Nottingham <notting@redhat.com>
- merge in ia64 fixes

* Fri Jun  2 2000 Nalin Dahyabhai <nalin@redhat.com>
- change PAM configuration to use system-auth
- build fix for Sparc

* Tue May 23 2000 Jakub Jelinek <jakub@redhat.com>
- don't define GlxStubLib if DllModules is not defined -
  otherwise things don't compile on i386

* Mon May 22 2000 Jakub Jelinek <jakub@redhat.com>
- support ffb, leo and cg6 on sparc
- only switch to dlopen() loader on selected architectures

* Thu May 11 2000 Bill Nottingham <notting@redhat.com>
- switch to dlopen() loader

* Wed May 10 2000 Bill Nottingham <notting@redhat.com>
- add man pages to -devel

* Sun May  7 2000 Bill Nottingham <notting@redhat.com>
- more directory shuffles

* Fri May  5 2000 Bill Nottingham <notting@redhat.com>
- more random fixes

* Wed May  3 2000 Bill Nottingham <notting@redhat.com>
- various fixes
- fix specfile for ia64
- merge drivers back into XFree86 package

* Sun Apr 23 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- update xf86cfg
- fix up the xf86cfg patch
- various fixes

* Thu Apr 20 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Fix up x11perfcomp and move it to -tools
- Fix up xfs (missing init script...)
- chkconfig'ize xfs
- move pswrap to -devel

* Sat Apr  8 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Add xf86cfg (successor to XF86Setup, taken from the XFree86 4.0a tree
  with permission from the patch author)
- Move the directory fixup stuff from %pre to %triggerpostun -- XFree86 < 3.9
  We don't want to fix things twice...

* Wed Apr  5 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Fix post script breakage
- Disable build root strip policy (drivers can't be stripped)
- strip the stuff we can safely strip manually
- add /usr/include stuff
- add some stuff from Mesa - we don't really want to obsolete Mesa
  without providing GLU and glut.
- move some man pages from XFree86 to XFree86-tools, where they belong.
- move some files to subpackages:
  beforelight, xclipboard, xclock, xfd, xieperf, xmag, xwininfo are now
  in XFree86-tools (rather than XFree86)
  makeg is now in XFree86-devel (rather than XFree86)
- obsolete Mesa, glxMesa* and xpm in -libs
- hope it still compiles

* Tue Apr  4 2000 Jakub Jelinek <jakub@redhat.com>
- Even move sparc tweaks

* Sat Apr  1 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Make it compile on sparc (Patch from Jakub Jelinek <jakub@redhat.com>,
  some additional fixes from me)
- Autodetect the right version of Tcl/Tk
- remove xinitrc, we get it from the xinitrc package

* Sat Mar 18 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- More fixes
- Fix compilation on alpha
- TODO: Port our 3.3.6 patches

* Wed Mar 15 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Add the man pages ;)
- Merge some patches from the RPMs at seawood.org
- Various fixes

* Mon Mar 13 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Initial RPM

