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
    chomp $line;

    # Line of dashes: new test
    if ($line =~ /^--/) {
        my $dashcount = ($line =~ tr/-/-/);
        $dashcount > 20
            or die "Internal error: Cannot grok test line '$line'";
        $line =~ /-([^-].*[^-])-/
            or die "Internal error: no test name in '$line'";
        push @tests, {
            name         => $1,
            files        => [],
            gripe_string => '',
        };

        # "this-is-a-test" => "this is a test"
        $tests[-1]->{name} =~ tr/-/ /;
    }

    # Leading '>>' : metadata indicating test setup
    #                       1   1    2   2   3   3     4     4 5     5 6  6 7     7
    elsif ($line =~ m{^>>\s+(-\S+)\s+(\w+)\s+(\w+)\s+/?([^/]+)/([^/]+)/(.*)/([^/]+)$}) {
        push @{ $tests[-1]->{files} }, {
            mode        => $1,
            user        => $2,
            group       => $3,

            arch        => $4,
            subpackage  => $5,
            dirname     => $6,
            basename    => $7,
            path        => "$4/$5/payload/$6/$7",
            fulldirname => "$4/$5/payload/$6",
            rootpath    => "/$6/$7",

            text        => '',
        };
    }

    # Leading '-|' : metadata indicating expected gripe results
    elsif ($line =~ /^-\|(.*)/) {
        $tests[-1]->{gripe_string} .= $1;
    }
    # Comments
    elsif ($line =~ /^\#/) {
        ;
    }
    # Text for a file
    elsif ($line) {
        $tests[-1]->{files}->[-1]->{text} .= $line . "\n";
    }
}

#use Data::Dumper;print Dumper(\@tests);exit 0;

plan tests => 3 + @tests;

# Pass 2: do the tests
my $tempdir = tempdir("t-DesktopLint.XXXXXX", CLEANUP => 1);

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::RPM'                  or exit;
use_ok 'RPM::Grill::Plugin::DesktopLint'  or exit;

package RPM::Grill::RPM;
use subs qw(nvr);
package RPM::Grill;
use subs qw(major_release);
package main;

for my $i (0 .. $#tests) {
    my $t = $tests[$i];

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    mkdir $temp_subdir, 02755
        or die "mkdir $temp_subdir: $!\n";

    my %arch;
    my %subpackage;

    # Create all the needed files (includes writing them to RPM.per_file_etc)
    for my $f (@{ $t->{files} }) {
        mkpath "$temp_subdir/$f->{fulldirname}", 0, 02755;
        open OUT, '>', "$temp_subdir/$f->{path}" or die;
        print OUT $f->{text};
        close OUT or die;
        chmod RPM::Grill::RPM::Files::_numeric_mode($f->{mode}),
            "$temp_subdir/$f->{path}";

        # Create rpm.rpm
        $f->{path} =~ m{^([^/]+/[^/]+)/} or die "foo: $f->{path}";
        open OUT, '>', "$temp_subdir/$1/rpm.rpm" or die "open $1: $!";
        close OUT;

        # Append to RPM.per_file_metadata
        my $per_file = join('/', $temp_subdir, $f->{arch},
                            $f->{subpackage}, 'RPM.per_file_metadata');
        open OUT, '>>', $per_file or die;
        print OUT join("\t",
                       "f"x32,
                       $f->{mode},
                       'root',
                       'root',
                        "0",
                       "(none)",
                       $f->{rootpath},
                    ), "\n";
        close OUT or die;

        $arch{ $f->{arch} }++;
        $subpackage{ $f->{subpackage} }++;
    }

    my $expected_gripes;
    if ($t->{gripe_string}) {
        $expected_gripes = eval "{ DesktopLint => [ $t->{gripe_string} ] }";
        die "eval failed:\n\n $t->{gripe_string} \n\n  $@\n"     if $@;
    }

    # invoke
    my $obj = RPM::Grill->new( $temp_subdir );

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
    bless $obj, 'RPM::Grill::Plugin::DesktopLint';

    RPM::Grill::Plugin::DesktopLint::analyze( $obj );

    eq_or_diff $obj->{gripes}, $expected_gripes, $t->{name};

}


__DATA__

---------exec-ok-(no-path)-----------------------------------------------------
# The executable exists.  No warnings.
>> -rw-r--r--  root root /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root  /i386/mypkg/usr/bin/foo

>> -rwxr-xr-x  root  root  /i386/mypkg/usr/share/icons/myicons/no-icon.svg

---------exec-ok-(fullpath)----------------------------------------------------
# The executable exists.  No warnings.
>> -rw-r--r--  root root /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root  /i386/mypkg/usr/bin/foo

>> -rwxr-xr-x  root  root  /i386/mypkg/usr/share/icons/myicons/no-icon.svg

-------exec-badmode----------------------------------------------------------
# Executable exists, but is not world-executable
>> -rw-r--r--  root  root /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr--  root  root  /i386/mypkg/usr/bin/foo

>> -rwxr-xr-x  root  root  /i386/mypkg/usr/share/icons/myicons/no-icon.svg

-|  { arch       => 'i386',
-|    subpackage => 'mypkg',
-|    code       => 'DesktopExecFileUnexecutable',
-|    diag       => 'Exec file <var>/usr/bin/foo</var> is not o+x (mode is <var>-rwxr-xr--</var>)',
-|    context    => { path => '/usr/share/applications/foo.desktop',
-|                    excerpt => ['Exec=foo'],
-|                    lineno=>'4' },
-|  }

-------exec-missing-(no-path)----------------------------------------------------
# Executable not found
>> -rw-r--r--  root  root /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root  /i386/mypkg/usr/share/icons/myicons/no-icon.svg

-|  { arch       => 'i386',
-|    subpackage => 'mypkg',
-|    code       => 'DesktopExecFileMissing',
-|    diag       => 'Exec file <var>/usr/bin/foo</var> not found',
-|    context    => { path => '/usr/share/applications/foo.desktop',
-|                    excerpt => ['Exec=foo'],
-|                    lineno=>'4' },
-|  }

-------exec-missing-(full-path)----------------------------------------------------
# Same as above, but with explicit /usr/bin path
>> -rw-r--r--  root  root /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root  /i386/mypkg/usr/share/icons/myicons/no-icon.xpm

-|  { arch       => 'i386',
-|    subpackage => 'mypkg',
-|    code       => 'DesktopExecFileMissing',
-|    diag       => 'Exec file <var>/usr/bin/foo</var> not found',
-|    context    => { path => '/usr/share/applications/foo.desktop',
-|                    excerpt => ['Exec=/usr/bin/foo'],
-|                    lineno=>'4' },
-|  }


-------exec-missing-(noarch)--------------------------------------------------
# Same as above, but desktop file is in noarch
>> -rw-r--r--  root  root /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root  /noarch/mypkg/usr/share/icons/myicons/no-icon.png

-|  { arch       => 'noarch',
-|    subpackage => 'mypkg',
-|    code       => 'DesktopExecFileMissing',
-|    diag       => 'Exec file <var>/usr/bin/foo</var> not found',
-|    context    => { path => '/usr/share/applications/foo.desktop',
-|                    excerpt => ['Exec=/usr/bin/foo'],
-|                    lineno=>'4' },
-|  }

-------exec-missing-(including-noarch)------------------------------------------
# .desktop file is in i386, and we _have_ a noarch package but no exec in it
>> -rw-r--r--  root  root /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=no-icon
Terminal=false
Type=Application

>> -rw-r--r--  root  root /noarch/mypkg/usr/bin/notfoo

>> -rwxr-xr-x  root  root  /i386/mypkg/usr/share/icons/myicons/no-icon.svg

-|  { arch       => 'i386',
-|    subpackage => 'mypkg',
-|    code       => 'DesktopExecFileMissing',
-|    diag       => 'Exec file <var>/usr/bin/foo</var> not found, even in noarch',
-|    context    => { path => '/usr/share/applications/foo.desktop',
-|                    excerpt => ['Exec=foo'],
-|                    lineno=>'4' },
-|  }

-------exec-is-in-another-arch-------------------------------------------------
# desktop file is in noarch, executable is in i386
>> -rw-r--r--  root  root /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root  /i386/mypkg/usr/bin/foo

>> -rwxr-xr-x  root  root  /noarch/mypkg/usr/share/icons/myicons/no-icon.svg

-------exec-is-in-one-other-arch-but-not-all----------------------------------
# desktop file is in noarch, executable is in i386, but missing from other arches
>> -rw-r--r--  root  root /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/foo
Icon=no-icon
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root    /i386/mypkg/usr/bin/foo
>> -rwxr-xr-x  root  root  /x86_64/mypkg/usr/bin/notfoo
>> -rwxr-xr-x  root  root     /ppc/mypkg/usr/bin/notfoo

>> -rwxr-xr-x  root  root  /noarch/mypkg/usr/share/icons/myicons/no-icon.svg

-|  { arch       => 'x86_64',
-|    subpackage => 'mypkg',
-|    code       => 'DesktopExecFileMissing',
-|    diag       => 'Exec file <var>/usr/bin/foo</var> not found',
-|    context    => { path => '/usr/share/applications/foo.desktop',
-|                    excerpt => ['Exec=/usr/bin/foo'],
-|                    lineno=>'4' },
-|  },
-|  { arch       => 'ppc',
-|    subpackage => 'mypkg',
-|    code       => 'DesktopExecFileMissing',
-|    diag       => 'Exec file <var>/usr/bin/foo</var> not found',
-|    context    => { path => '/usr/share/applications/foo.desktop',
-|                    excerpt => ['Exec=/usr/bin/foo'],
-|                    lineno=>'4' },
-|  }


-------exec-is-htmlview-rhel5----------------------------------------------
# for rhel5
>> -rw-r--r--  root  root /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/htmlview
Icon=no-icon
Terminal=false
Type=Application
Encoding=UTF-8

>> -rwxr-xr-x  root  root  /noarch/mypkg/usr/share/icons/myicons/no-icon.svg

>> -r--r--r--  root  root /noarch/mypkg/../RPM.requires
sdfsdfd
htmlview
sdfdf

-------exec-is-htmlview-but-not-req-rhel5-----------------------------------
# for rhel5
>> -rw-r--r--  root  root /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=/usr/bin/htmlview
Icon=no-icon
Terminal=false
Type=Application
Encoding=UTF-8

>> -rwxr-xr-x  root  root  /noarch/mypkg/usr/share/icons/myicons/no-icon.svg

>> -r--r--r--  root  root /noarch/mypkg/../RPM.requires
sdfsdfd
sdfdf

-|  { arch       => 'noarch',
-|    subpackage => 'mypkg',
-|    code       => 'DesktopExecMissingReq',
-|    diag       => 'Package should Require: htmlview',
-|    context    => { path => '/usr/share/applications/foo.desktop',
-|                    excerpt => ['Exec=/usr/bin/htmlview'],
-|                    lineno=>'4' },
-|  }


#
# Icon checks
#
-------icon-ok-------------------------------------------------------
>> -rw-r--r--  root  root /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root    /i386/mypkg/usr/bin/foo
>> -rwxr-xr-x  root  root    /i386/mypkg/usr/share/icons/myicon.png

-------icon-ok-(noarch)---------------------------------------------------
# Same as above, but noarch instead of i386
>> -rw-r--r--  root  root /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root    /noarch/mypkg/usr/bin/foo
>> -rwxr-xr-x  root  root    /noarch/mypkg/usr/share/icons/myicon.png

-------icon-ok-(cross-pkg)-------------------------------------------------
# Same as above, but icon is in a different subpackage (same arch)
>> -rw-r--r--  root  root /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root    /noarch/mypkg/usr/bin/foo
>> -rwxr-xr-x  root  root    /noarch/mypkg-icons/usr/share/icons/myicon.png

-------icon-badmode-------------------------------------------------
# icon is not world-readable
>> -rw-r--r--  root  root /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root    /noarch/mypkg/usr/bin/foo
>> -rwxr-x---  root  root    /noarch/mypkg/usr/share/icons/myicon.png

-|  { arch       => 'noarch',
-|    subpackage => 'mypkg',
-|    code       => 'DesktopIconFileUnreadable',
-|    diag       => 'Icon file <var>/usr/share/icons/myicon.png</var> is not world-readable (mode is <var>-rwxr-x---</var>)',
-|    context    => { path => '/usr/share/applications/foo.desktop',
-|                    excerpt => ['Icon=/usr/share/icons/myicon.png'],
-|                    lineno=>'5' },
-|  }

-------icon-missing-(arch)--------------------------------------------
# icon is not present (real arch)
>> -rw-r--r--  root  root /i386/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root    /i386/mypkg/usr/bin/foo
>> -rwxr-x---  root  root    /i386/mypkg/usr/share/icons/myicon.jpg

-|  { arch       => 'i386',
-|    subpackage => 'mypkg',
-|    code       => 'DesktopIconFileMissing',
-|    diag       => 'Icon file <var>/usr/share/icons/myicon.png</var> not found',
-|    context    => { path => '/usr/share/applications/foo.desktop',
-|                    excerpt => ['Icon=/usr/share/icons/myicon.png'],
-|                    lineno=>'5' },
-|  }

-------icon-missing-(noarch)--------------------------------------------
# same as above, but noarch
>> -rw-r--r--  root  root /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=false
Type=Application

>> -rwxr-xr-x  root  root    /noarch/mypkg/usr/bin/foo
>> -rwxr-x---  root  root    /noarch/mypkg/usr/share/icons/myicon.jpg

-|  { arch       => 'noarch',
-|    subpackage => 'mypkg',
-|    code       => 'DesktopIconFileMissing',
-|    diag       => 'Icon file <var>/usr/share/icons/myicon.png</var> not found',
-|    context    => { path => '/usr/share/applications/foo.desktop',
-|                    excerpt => ['Icon=/usr/share/icons/myicon.png'],
-|                    lineno=>'5' },
-|  }


#
# Some simple tests for the external validator
#
-------external-validator--------------------------------------------
# Nothing fancy.  Just check that the desktop-file-validate command runs.
>> -rw-r--r--  root  root /noarch/mypkg/usr/share/applications/foo.desktop
[Desktop Entry]
Name=Foo
Comment=Bar
Exec=foo
Icon=/usr/share/icons/myicon.png
Terminal=0
Type=Application

>> -rwxr-xr-x  root  root    /noarch/mypkg/usr/bin/foo
>> -rwxr-xr-x  root  root    /noarch/mypkg/usr/share/icons/myicon.png

-|  { arch       => 'noarch',
-|    subpackage => 'mypkg',
-|    code       => 'DesktopFileValidation',
-|    diag       => 'warning: boolean key "Terminal" in group "Desktop Entry" has value "0", which is deprecated: boolean values should be "false" or "true"',
-|    context    => { path => '/usr/share/applications/foo.desktop' },
-|  }
