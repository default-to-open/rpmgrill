#!/usr/bin/perl

use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath rmtree);
use File::Temp                  qw(tempdir);

# pass 1: read tests. Anything with an exclamation point in front is
# expected to fail the systemd test.
my @tests;
my $tests = <<'END_TESTS';
  el4 /bin/foo
  el5 /bin/foo
  el6 /bin/foo
! el7 /bin/foo

  el4 /sbin/foo
  el5 /sbin/foo
  el6 /sbin/foo
! el7 /sbin/foo

! el7 /lib/libfoo.so.1
! el7 /lib/foo/libbar.so.1

! el7 /lib64/libfoo.so.1
END_TESTS

for my $line (split "\n", $tests) {
    next if !$line;                             # Skip blank lines

    $line =~ m{^(!)? \s+ el(\d+) \s+ (/\S+(\s+/\S+)*)$}x
        or die "Internal error: cannot grok test line '$line'";
    my ($not, $rhel, @paths) = ($1, $2, split(' ',$3));

    my $test_name = "RHEL$rhel : @paths" . ($not ? " (should fail)" : "");

    push @tests, {
        name  => $test_name,
        rhel  => $rhel,
        paths => \@paths,
        fail  => $not,
    };
}

#use Data::Dumper;print Dumper(\@tests);exit 0;

plan tests => 3 + @tests;

# Pass 2: do the tests
my $tempdir = tempdir("t-Manifest.XXXXXX", CLEANUP => !$ENV{DEBUG});

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::RPM'                  or exit;
use_ok 'RPM::Grill::Plugin::Manifest'     or exit;


package RPM::Grill::RPM;
use subs qw(nvr);
package RPM::Grill;
use subs qw(major_release);
package main;


for my $t (@tests) {
    my $expected_gripes;
    if ($t->{fail}) {
        my @paths = @{$t->{paths}};

        my $g = {
            arch       => 'i386',
            subpackage => 'mypkg',
            code       => 'MoveToUsr',
        };

        if (@paths == 1) {
            $paths[0] =~ m{^(/[^/]+)};
            $g->{diag} = "$1 no longer exists; please move <tt>$paths[0]</tt> to <b>/usr</b>";
        }
        else {
            die;
            $g->{diag}    = "Non-systemd files:";
            $g->{context} = { excerpt => [ sort @paths ] };
        }

        $expected_gripes = { Manifest => [ $g ] };
    }

    # invoke
    my $temp_subdir = make_tempdir( @{$t->{paths}} );
    my $obj = RPM::Grill->new( $temp_subdir );

    bless $obj, 'RPM::Grill::Plugin::Manifest';

    # Set a fake NVR
    {
        no warnings 'redefine';
        *RPM::Grill::RPM::nvr = sub {
            return "1.el$t->{rhel}";
        };
        *RPM::Grill::major_release = sub {
            return "RHEL$t->{rhel}";
        };
    }

    $obj->analyze;

    eq_or_diff $obj->{gripes}, $expected_gripes, $t->{name};
}

###############################################################################
# BEGIN helper

sub make_tempdir {
    use feature 'state';
    state $i = 0;

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i++);
    mkdir $temp_subdir, 02755
        or die "mkdir $temp_subdir: $!\n";

    for my $f (@_) {
        # Make the path
        mkpath "$temp_subdir/i386/mypkg/payload$f", 0, 02755;

        # Create rpm.rpm
        open OUT, '>', "$temp_subdir/i386/mypkg/rpm.rpm"
            or die "open rpm.rpm: $!";
        close OUT;

        # Append to RPM.per_file_metadata. Note that the fields in the
        # here-document are separated by ONE TAB
        my $per_file = "$temp_subdir/i386/mypkg/RPM.per_file_metadata";
        open OUT, '>>', $per_file or die;
        print OUT <<"END_METADATA";
0000000000000	-rwxr-xr-x	root	root	0	(none)	$f
END_METADATA
        close OUT or die;
    }

    return $temp_subdir;
}
