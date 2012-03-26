#!/usr/bin/perl

use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath rmtree);
use File::Temp                  qw(tempdir);

# pass 1: read tests. Anything with an exclamation point in front is
# expected to fail.
#
# Note that some directories are separated by spaces. That indicates
# that the left-hand side is the actual FHS-protected directory, and
# the right-hand side is a subdirectory. This is needed because the
# test highlights the FHS part in <b>bold</b>, to make it clear
# that (e.g.) /home is the problem, not /home/fribbedygibbet.
my @tests;
my $tests = <<'END_TESTS';
  /usr/lib
  /usr/lib64
  /usr/lib64 /mysubdir
  /usr/bin
! /usr/local  /lib
! /usr/local  /lib64
! /media
! /media    /subdir
! /home
! /home     /subdir
! /var/tmp
! /var/tmp  /subdir
! /usr/tmp
! /usr/tmp  /subdir
! /tmp
! /tmp      /subdir
  /var/spool/foo/tmp
END_TESTS

for my $line (split "\n", $tests) {
    $line =~ m{^(!)?\s+(/\S+)(\s+(/\S+))?$} or die "Cannot grok: '$line'";
    my ($not, $path, $subpath) = ($1, $2, $4||'');

    # [ Path, 0=pass 1=fail, path-with-highlights ]
    push @tests, [ "$path$subpath", $not, "<b>$path</b>$subpath" ];
}

#use Data::Dumper;print Dumper(\@tests);exit 0;

plan tests => 3 + @tests + 1;

# Pass 2: do the tests
my $tempdir = tempdir("t-Manifest.XXXXXX", CLEANUP => !$ENV{DEBUG});

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::RPM'                  or exit;
use_ok 'RPM::Grill::Plugin::Manifest'     or exit;

# Kludge alert
package RPM::Grill::RPM;
use subs qw(nvr);
package RPM::Grill;
use subs qw(major_release);
package main;

# Set a fake NVR
{
    no warnings 'redefine';
    *RPM::Grill::RPM::nvr = sub {
        return "1.el6";
    };
    *RPM::Grill::major_release = sub {
        return "RHEL6";
    };
}

for my $t (@tests) {
    my ($path, $not, $highlighted_path) = @$t;

    my $test_name = $path . ($not ? " [not acceptable]" : "");

    my $expected_gripes;
    if ($not) {
        $expected_gripes = { Manifest => [ {
            arch       => 'i386',
            subpackage => 'mypkg',
            code       => 'NonFHS',
            diag       => "FHS-protected directory <tt>$highlighted_path</tt>",
        } ] };
    }

    # invoke
    my $temp_subdir = make_tempdir( $path );
    my $obj = RPM::Grill->new( $temp_subdir );

    bless $obj, 'RPM::Grill::Plugin::Manifest';

    $obj->analyze;

    eq_or_diff $obj->{gripes}, $expected_gripes, $test_name;
}

#
# One more; testing multi-bad-dir results
#
my @failing_tests = grep { $_->[1] } @tests;
my @bad_dirs      = sort map { $_->[0] } @failing_tests;
my @bad_excerpt   = sort map { $_->[2] } @failing_tests;

my $temp_subdir = make_tempdir( @bad_dirs );
my $expected_gripes = { Manifest => [ {
    arch       => 'i386',
    subpackage => 'mypkg',
    code       => 'NonFHS',
    diag       => 'FHS-protected directories:',
    context    => { excerpt    => [ @bad_excerpt ] },
} ] };


my $obj = RPM::Grill->new( $temp_subdir );

bless $obj, 'RPM::Grill::Plugin::Manifest';
$obj->analyze;

eq_or_diff $obj->{gripes}, $expected_gripes, 'aggregate results';






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
0000000000000	drwxr-xr-x	root	root	0	(none)	$f
END_METADATA
        close OUT or die;
    }

    return $temp_subdir;
}
