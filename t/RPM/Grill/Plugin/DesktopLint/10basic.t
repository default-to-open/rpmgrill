# -*- perl -*-
#
# tests for the .desktop file checks in DesktopLint plugin
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath rmtree);
use File::Temp                  qw(tempdir);
use File::Basename              qw(basename);

# pass 1: read DATA
my @tests;
while (my $line = <DATA>) {
    next if $line =~ /^\s*\#/;                  # Skip comment lines

    if ($line =~ /^-{5,}([^-].*[^-])-+$/) {
        push @tests, { name => $1 };
    }
    elsif (@tests) {
        if (exists $tests[-1]->{expect}) {
            $tests[-1]->{expect} .= $line;
        }
        elsif ($line =~ /^\.\.+expect:$/) {
            $tests[-1]->{expect} = '';
        }
        else {
            $tests[-1]->{setup} .= $line;
        }
    }
    elsif ($line =~ /\S/) {
        die "Cannot grok '$line'";
    }
}

#use Data::Dumper;print Dumper(\@tests);exit 0;

plan tests => 4 + @tests;

# Pass 2: do the tests
my $tempdir = tempdir("t-DesktopLint.XXXXXX", CLEANUP => 1);

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::RPM'                  or exit;
use_ok 'RPM::Grill::Plugin::DesktopLint'  or exit;

ok(require("t/lib/FakeTree.pm"), "loaded FakeTree.pm") or exit;

package RPM::Grill::RPM;
use subs qw(nvr);
package RPM::Grill;
use subs qw(major_release);
package main;

for my $i (0 .. $#tests) {
    my $t = $tests[$i];

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    my $g = FakeTree::make_fake_tree( $temp_subdir, $t->{setup} );

    my $expected_gripes;
    if ($t->{expect}) {
        $expected_gripes = eval "{ DesktopLint => [ $t->{expect} ] }";
        die "eval failed:\n\n $t->{gripe_string} \n\n  $@\n"     if $@;
    }

    # Set a fake NVR
    my $rhel = ($t->{name} =~ /rhel(\d+)/ ? $1 : 99);
    {
        no warnings 'redefine';
        *RPM::Grill::RPM::nvr = sub {
            return "1.el$rhel";
        };
        *RPM::Grill::major_release = sub {
            return "RHEL$rhel";
        };
    }

#    $obj->{nvr} = { name => 'fixme', version => '0.1', release => "1.el$rhel" };
    bless $g, 'RPM::Grill::Plugin::DesktopLint';

    RPM::Grill::Plugin::DesktopLint::analyze( $g );

    eq_or_diff $g->{gripes}, $expected_gripes, $t->{name};

}


__DATA__

---------exec-ok-(no-path)-----------------------------------------------------
# The executable exists.  No warnings.
>> -rw-r--r--  root root 0 /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root  0 /i386/mypkg/usr/bin/foo

>> -rwxr-xr-x  root  root  0 /i386/mypkg/usr/share/icons/myicons/no-icon.svg

---------exec-ok-(fullpath)----------------------------------------------------
# The executable exists.  No warnings.
>> -rw-r--r--  root root 0 /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root  0 /i386/mypkg/usr/bin/foo

>> -rwxr-xr-x  root  root  0 /i386/mypkg/usr/share/icons/myicons/no-icon.svg

-------exec-badmode----------------------------------------------------------
# Executable exists, but is not world-executable
>> -rw-r--r--  root  root 0 /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr--  root  root  0 /i386/mypkg/usr/bin/foo

>> -rwxr-xr-x  root  root  0 /i386/mypkg/usr/share/icons/myicons/no-icon.svg

...expect:

 { arch       => 'i386',
   subpackage => 'mypkg',
   code       => 'DesktopExecFileUnexecutable',
   diag       => 'Exec file <var>/usr/bin/foo</var> is not o+x (mode is <var>-rwxr-xr--</var>)',
   context    => { path => '/usr/share/applications/foo.desktop',
                   excerpt => ['Exec=foo'],
                   lineno=>'4' },
 }

-------exec-missing-(no-path)----------------------------------------------------
# Executable not found
>> -rw-r--r--  root  root 0 /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root  0 /i386/mypkg/usr/share/icons/myicons/no-icon.svg

...expect:

 { arch       => 'i386',
   subpackage => 'mypkg',
   code       => 'DesktopExecFileMissing',
   diag       => 'Exec file <var>/usr/bin/foo</var> not found',
   context    => { path => '/usr/share/applications/foo.desktop',
                   excerpt => ['Exec=foo'],
                   lineno=>'4' },
 }

-------exec-missing-(full-path)----------------------------------------------------
# Same as above, but with explicit /usr/bin path
>> -rw-r--r--  root  root 0 /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root  0 /i386/mypkg/usr/share/icons/myicons/no-icon.xpm

...expect:

 { arch       => 'i386',
   subpackage => 'mypkg',
   code       => 'DesktopExecFileMissing',
   diag       => 'Exec file <var>/usr/bin/foo</var> not found',
   context    => { path => '/usr/share/applications/foo.desktop',
                   excerpt => ['Exec=/usr/bin/foo'],
                   lineno=>'4' },
 }


-------exec-missing-(noarch)--------------------------------------------------
# Same as above, but desktop file is in noarch
>> -rw-r--r--  root  root 0 /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root  0 /noarch/mypkg/usr/share/icons/myicons/no-icon.png

...expect:

 { arch       => 'noarch',
   subpackage => 'mypkg',
   code       => 'DesktopExecFileMissing',
   diag       => 'Exec file <var>/usr/bin/foo</var> not found',
   context    => { path => '/usr/share/applications/foo.desktop',
                   excerpt => ['Exec=/usr/bin/foo'],
                   lineno=>'4' },
 }

-------exec-missing-(including-noarch)------------------------------------------
# .desktop file is in i386, and we _have_ a noarch package but no exec in it
>> -rw-r--r--  root  root 0 /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=no-icon
Terminal=false
Type=Application

>> -rw-r--r--  root  root 0 /noarch/mypkg/usr/bin/notfoo

>> -rwxr-xr-x  root  root 0 /i386/mypkg/usr/share/icons/myicons/no-icon.svg

...expect:

 { arch       => 'i386',
   subpackage => 'mypkg',
   code       => 'DesktopExecFileMissing',
   diag       => 'Exec file <var>/usr/bin/foo</var> not found, even in noarch',
   context    => { path => '/usr/share/applications/foo.desktop',
                   excerpt => ['Exec=foo'],
                   lineno=>'4' },
 }

-------exec-missing-(src)------------------------------------------------------
# See e.g. http://brewtap.app.eng.bos.redhat.com/nvr/git/1.7.12/2.el7
# in which we complain about a .desktop file in the srpm

>> -rw-r--r--  root  root 0 /src/mypkg/subdir/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=no-icon
Terminal=false
Type=Application

-------exec-is-in-another-arch-------------------------------------------------
# desktop file is in noarch, executable is in i386
>> -rw-r--r--  root  root 0 /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root 0 /i386/mypkg/usr/bin/foo

>> -rwxr-xr-x  root  root 0 /noarch/mypkg/usr/share/icons/myicons/no-icon.svg

-------exec-is-in-one-other-arch-but-not-all----------------------------------
# desktop file is in noarch, executable is in i386, but missing from other arches
>> -rw-r--r--  root  root 0 /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root 0    /i386/mypkg/usr/bin/foo
>> -rwxr-xr-x  root  root 0  /x86_64/mypkg/usr/bin/notfoo
>> -rwxr-xr-x  root  root 0     /ppc/mypkg/usr/bin/notfoo

>> -rwxr-xr-x  root  root 0  /noarch/mypkg/usr/share/icons/myicons/no-icon.svg

...expect:

 { arch       => 'x86_64',
   subpackage => 'mypkg',
   code       => 'DesktopExecFileMissing',
   diag       => 'Exec file <var>/usr/bin/foo</var> not found',
   context    => { path => '/usr/share/applications/foo.desktop',
                   excerpt => ['Exec=/usr/bin/foo'],
                   lineno=>'4' },
 },
 { arch       => 'ppc',
   subpackage => 'mypkg',
   code       => 'DesktopExecFileMissing',
   diag       => 'Exec file <var>/usr/bin/foo</var> not found',
   context    => { path => '/usr/share/applications/foo.desktop',
                   excerpt => ['Exec=/usr/bin/foo'],
                   lineno=>'4' },
 }


-------exec-is-htmlview-rhel5----------------------------------------------
# for rhel5
>> -rw-r--r--  root  root 0 /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/htmlview
Icon=no-icon
Terminal=false
Type=Application
Encoding=UTF-8

>> -rwxr-xr-x  root  root 0 /noarch/mypkg/usr/share/icons/myicons/no-icon.svg

>> -r--r--r--  root  root 0 /noarch/mypkg/../RPM.requires
sdfsdfd
htmlview
sdfdf

-------exec-is-htmlview-but-not-req-rhel5-----------------------------------
# for rhel5
>> -rw-r--r--  root  root 0 /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/htmlview
Icon=no-icon
Terminal=false
Type=Application
Encoding=UTF-8

>> -rwxr-xr-x  root  root 0 /noarch/mypkg/usr/share/icons/myicons/no-icon.svg

>> -r--r--r--  root  root 0 /noarch/mypkg/../RPM.requires
sdfsdfd
sdfdf

...expect:

 { arch       => 'noarch',
   subpackage => 'mypkg',
   code       => 'DesktopExecMissingReq',
   diag       => 'Package should Require: htmlview',
   context    => { path => '/usr/share/applications/foo.desktop',
                   excerpt => ['Exec=/usr/bin/htmlview'],
                   lineno=>'4' },
 }


#
# Icon checks
#
-------icon-ok-------------------------------------------------------
>> -rw-r--r--  root  root 0 /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root 0   /i386/mypkg/usr/bin/foo
>> -rwxr-xr-x  root  root 0   /i386/mypkg/usr/share/icons/myicon.png

-------icon-ok-(noarch)---------------------------------------------------
# Same as above, but noarch instead of i386
>> -rw-r--r--  root  root 0 /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root 0   /noarch/mypkg/usr/bin/foo
>> -rwxr-xr-x  root  root 0   /noarch/mypkg/usr/share/icons/myicon.png

-------icon-ok-(cross-pkg)-------------------------------------------------
# Same as above, but icon is in a different subpackage (same arch)
>> -rw-r--r--  root  root 0 /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root 0   /noarch/mypkg/usr/bin/foo
>> -rwxr-xr-x  root  root 0   /noarch/mypkg-icons/usr/share/icons/myicon.png

-------icon-badmode-------------------------------------------------
# icon is not world-readable
>> -rw-r--r--  root  root 0 /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root 0   /noarch/mypkg/usr/bin/foo
>> -rwxr-x---  root  root 0   /noarch/mypkg/usr/share/icons/myicon.png

...expect:

 { arch       => 'noarch',
   subpackage => 'mypkg',
   code       => 'DesktopIconFileUnreadable',
   diag       => 'Icon file <var>/usr/share/icons/myicon.png</var> is not world-readable (mode is <var>-rwxr-x---</var>)',
   context    => { path => '/usr/share/applications/foo.desktop',
                   excerpt => ['Icon=/usr/share/icons/myicon.png'],
                   lineno=>'5' },
 }

-------icon-missing-(arch)--------------------------------------------
# icon is not present (real arch)
>> -rw-r--r--  root  root 0 /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root 0   /i386/mypkg/usr/bin/foo
>> -rwxr-x---  root  root 0   /i386/mypkg/usr/share/icons/myicon.jpg

...expect:

 { arch       => 'i386',
   subpackage => 'mypkg',
   code       => 'DesktopIconFileMissing',
   diag       => 'Icon file <var>/usr/share/icons/myicon.png</var> not found',
   context    => { path => '/usr/share/applications/foo.desktop',
                   excerpt => ['Icon=/usr/share/icons/myicon.png'],
                   lineno=>'5' },
 }

-------icon-missing-(noarch)--------------------------------------------
# same as above, but noarch
>> -rw-r--r--  root  root 0 /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root 0   /noarch/mypkg/usr/bin/foo
>> -rwxr-x---  root  root 0   /noarch/mypkg/usr/share/icons/myicon.jpg

...expect:

 { arch       => 'noarch',
   subpackage => 'mypkg',
   code       => 'DesktopIconFileMissing',
   diag       => 'Icon file <var>/usr/share/icons/myicon.png</var> not found',
   context    => { path => '/usr/share/applications/foo.desktop',
                   excerpt => ['Icon=/usr/share/icons/myicon.png'],
                   lineno=>'5' },
 }


#
# Some simple tests for the external validator
#
-------external-validator--------------------------------------------
# Nothing fancy.  Just check that the desktop-file-validate command runs.
>> -rw-r--r--  root  root 0 /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=0
Type=Application

>> -rwxr-xr-x  root  root 0   /noarch/mypkg/usr/bin/foo
>> -rwxr-xr-x  root  root 0   /noarch/mypkg/usr/share/icons/myicon.png

...expect:

  { arch       => 'noarch',
    subpackage => 'mypkg',
    code       => 'DesktopFileValidation',
    diag       => 'warning: boolean key "Terminal" in group "Desktop Entry" has value "0", which is deprecated: boolean values should be "false" or "true"',
    context    => { path => '/usr/share/applications/foo.desktop' },
  }
