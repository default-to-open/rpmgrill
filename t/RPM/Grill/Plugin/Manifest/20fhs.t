#!/usr/bin/perl

use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath rmtree);
use File::Temp                  qw(tempdir);

# pass 1: read DATA
my @tests;
my $tests = <<'END_TESTS';
  /usr/lib
  /usr/lib64
  /usr/lib64/mysubdir
  /usr/bin
! /usr/local/lib
! /usr/local/lib64
! /media
! /media/foo
! /home/sdfsdf
! /var/tmp
! /usr/tmp
END_TESTS

for my $line (split "\n", $tests) {
    $line =~ m{^(!)?\s+(/\S+)$} or die "Cannot grok: '$line'";
    my ($not, $path) = ($1, $2);

    push @tests, [ $path, $not ];
}

#use Data::Dumper;print Dumper(\@tests);exit 0;

plan tests => 3 + @tests + 1;

# Pass 2: do the tests
my $tempdir = tempdir("t-Manifest.XXXXXX", CLEANUP => !$ENV{DEBUG});

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::RPM'                  or exit;
use_ok 'RPM::Grill::Plugin::Manifest'     or exit;


for my $t (@tests) {
    my ($path, $not) = @$t;

    my $test_name = $path . ($not ? " [not acceptable]" : "");

    my $expected_gripes;
    if ($not) {
        $expected_gripes = { Manifest => [ {
            arch       => 'i386',
            subpackage => 'mypkg',
            code       => 'NonFHS',
            diag       => "FHS-protected directory <tt>$path</tt>",
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
my @bad = sort map { $_->[0] } grep { $_->[1] } @tests;
my $temp_subdir = make_tempdir( @bad );
my $expected_gripes = { Manifest => [ {
    arch       => 'i386',
    subpackage => 'mypkg',
    code       => 'NonFHS',
    diag       => 'FHS-protected directories:',
    context    => { excerpt    => [ @bad ] },
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
