# -*- perl -*-
#
# Tests for the Setxid plug in
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(rmtree);
use File::Temp                  qw(tempdir);
use File::Basename              qw(basename);

# We're not testing anything having to do with arch / subpackage,
# so these are always the same
our $Arch;
our $Pkg;

our @wl;
our @tests;
BEGIN {
    $Arch = 'noarch';
    $Pkg  = 'mypkg';

    # Whitelist file.  This is written to a dummy (test) WL file
    my $wl = <<'END_WL';
-rwsr-xr-x root root /usr/bin/setuid-root-4755
-r-s--x--x root root /usr/bin/setuid-root-4511
---s--x--x root root /usr/bin/setuid-root-4111
-rwxr-sr-x root root /usr/bin/setgid-root-2755
-rwxr-sr-x root foo  /usr/bin/setgid-foo-2755
drwxr-sr-x root ggg  /var/lib/setgid-dir
END_WL

    # Actual tests.
    my $tests = <<'END_TESTS';
# No gripes expected
-rwsr-xr-x root root /usr/bin/setuid-root-4755
-rwxr-sr-x root foo  /usr/bin/setgid-foo-2755
drwxr-sr-x root ggg  /var/lib/setgid-dir

# 1 gripe
-r-sr-xr-x root root /usr/bin/setuid-root-4755
    WrongFileMode  Incorrect mode on <var>/usr/bin/setuid-root-4755</var>: expected -rwsr-xr-x, got <var>-r-sr-xr-x</var>

# multiple gripes
-r-sr-xr-x foo root /usr/bin/setuid-root-4755
    WrongFileMode  Incorrect mode on <var>/usr/bin/setuid-root-4755</var>: expected -rwsr-xr-x, got <var>-r-sr-xr-x</var>
    WrongFileUser  Incorrect user on <var>/usr/bin/setuid-root-4755</var>: expected root, got <var>foo</var>

# Not on whitelist
-r-sr-xr-x root root /usr/bin/non-wl-suid
    UnauthorizedSetxid File <var>/usr/bin/non-wl-suid</var> is setuid root but is not on the setxid whitelist.

-r-sr-sr-x root root /usr/bin/non-wl-sugid
    UnauthorizedSetxid File <var>/usr/bin/non-wl-sugid</var> is setuid root and setgid root but is not on the setxid whitelist.

-r-xr-sr-x root ggg /usr/bin/non-wl-sgid
    UnauthorizedSetxid File <var>/usr/bin/non-wl-sgid</var> is setgid ggg but is not on the setxid whitelist.

drwxr-sr-x  root ggg /var/lib/non-wl-sgid-dir
    UnauthorizedSetxid Directory <var>/var/lib/non-wl-sgid-dir</var> is setgid ggg but is not on the setxid whitelist.

# Setuid (U) directory
drwsr-xr-x  root ggg /var/lib/suid-dir
    SetuidDirectory Directory <var>/var/lib/suid-dir</var> is setuid root.  This is almost certainly a mistake.
END_TESTS

    # Parse the whitelist file
    for my $line (split "\n", $wl) {
        # Start with '*' = new whitelist entry
        if ($line =~ /^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)/) {
            push @wl, [ $1, $2, $3, $4 ];
        }
        else {
            die "Cannot grok whitelist line '$line'";
        }
    }

    # Parse the tests
    for my $line (split "\n", $tests) {
        $line =~ s/\s*\#.*$//;                  # Trim comments

        # <mode><user><group><path> indicates a new test
        if ($line =~ m!^[d-]\S+\s+\S+\s+\S+\s+/\S+$!) {
            my @x = split ' ', $line;
            @x == 4
                or die "Wrong number of fields in '$line' (expected 4)";
            push @tests, { mode   => $x[0],
                           user   => $x[1],
                           group  => $x[2],
                           path   => $x[3],
                           gripes => [],
                       };
        }
        # <space><code><diag> is what we expect from this test
        elsif ($line =~ /^\s+(\S+)\s+(.*)$/) {
            push @{ $tests[-1]->{gripes} }, {
                code => $1,
                diag => $2,
                arch => $Arch,
                subpackage => $Pkg,
                context => { path => $tests[-1]->{path} },
            };
        }
        elsif ($line) {
            die "Internal error: Cannot grok test line '$line'";
        }
    }

    plan tests => 2 + @tests;
}


# Tests 1-2 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                     or exit;
use_ok 'RPM::Grill::Plugin::Setxid'     or exit;


# Create a temporary directory in which to test
my $tempdir = tempdir("t-Setxid.XXXXXX", CLEANUP => 1);

# Create the setxid whitelist file
mkdir "$tempdir/wl", 02755
    or die "mkdir $tempdir/wl: $!";
open WL, '>', "$tempdir/wl/RHEL5"
    or die "cannot create $tempdir/wl/RHEL5: $!\n";
for my $aref (@wl) {
    # Note that the file format is horrible: path first,
    # which prevents us from having properly-aligned columns
    # because path is variable length.  A better format is
    # mode-user-group-path, but it'll take some effort to
    # make that change.
    my ($mode, $user, $group, $path) = @$aref;
    print WL join("\t", $path, $user, $group, $mode), "\n";
}
close WL
    or die "error writing $tempdir/wl/RHEL5: $!";

# Point the plugin at this whitelist
no warnings 'once';
$RPM::Grill::Plugin::Setxid::Whitelist_Dir = "$tempdir/wl";
use warnings;

# FIXME: override
package RPM::Grill;
use subs qw(nvr);
package main;

# Run the tests.
for my $i (0 .. $#tests) {
    my $t = $tests[$i];

    # Create new tmpdir
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    mkdir $temp_subdir, 02755
        or die "mkdir $temp_subdir: $!\n";

    mkdir "$temp_subdir/$Arch"
        or die "mkdir $temp_subdir/$Arch: $!\n";
    mkdir "$temp_subdir/$Arch/$Pkg"
        or die "mkdir $temp_subdir/$Arch/$Pkg: $!\n";
    open TMP, '>', "$temp_subdir/$Arch/$Pkg/rpm.rpm";
    close TMP;

    # Write to arch/pkg/filelist.  This will be read by ::Files
    my $filelist = "$temp_subdir/$Arch/$Pkg/RPM.per_file_metadata";
    open FILELIST, '>', $filelist
        or die "cannot create $filelist: $!";
    print FILELIST join("\t",
                        "f"x32,
                        $t->{mode},
                        $t->{user},
                        $t->{group},
                        "0",
                        "(none)",
                        $t->{path},
                    ), "\n";
    close FILELIST
        or die "error writing $filelist: $!";

    # prepare the expected set of gripes
    my $gripes;
    $gripes = { Setxid => $t->{gripes} } if @{$t->{gripes}};

    # Hack: Redefine the nvr() method. Otherwise we need to create
    # a fake srpm.
    {
        no warnings 'redefine';
        *RPM::Grill::nvr = sub {
            return ($Pkg, '1', "$i.el5");
        };
    }

    my $obj = RPM::Grill->new( $temp_subdir );
    bless $obj, 'RPM::Grill::Plugin::Setxid';

    $obj->analyze;

    my $name = basename($t->{path});
    eq_or_diff $obj->{gripes}, $gripes, "$i : $name";
##    use Data::Dumper; print Dumper($spec_obj);
}
