#!/usr/bin/perl

use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath rmtree);
use File::Temp                  qw(tempdir);
use File::Basename              qw(dirname);

# pass 1: read DATA
my @tests;
my $tests = <<'END_TESTS';
  /usr/lib/mylib.a
  /usr/bin/mybin
! /usr/local/lib/mylib.a
! /usr/local/lib/mylib.a
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

plan tests => 3 + @tests;

# Pass 2: do the tests
my $tempdir = tempdir("t-Multilib.XXXXXX", CLEANUP => !$ENV{DEBUG});

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::RPM'                  or exit;
use_ok 'RPM::Grill::Plugin::Manifest'     or exit;


for my $i (0 .. $#tests) {
    my $t = $tests[$i];

    my ($path, $not) = @$t;

    my $test_name = $path . ($not ? " [not acceptable]" : " [acceptable]");

    my $dirname = dirname($path);

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    mkdir $temp_subdir, 02755
        or die "mkdir $temp_subdir: $!\n";

    # Make the path to the file, then touch the file
    mkpath "$temp_subdir/i386/mypkg/payload/$dirname", 0, 02755;
    open OUT, '>', "$temp_subdir/i386/mypkg/payload/$path" or die "Cannot mk $path: $!";
    close OUT or die;

    # Create rpm.rpm
    open OUT, '>', "$temp_subdir/i386/mypkg/rpm.rpm" or die "open rpm.rpm: $!";
    close OUT;

    # Create RPM.per_file_metadata. Note that the fields in the here-doc
    # are separated by ONE TAB
    my $per_file = "$temp_subdir/i386/mypkg/RPM.per_file_metadata";
    open OUT, '>', $per_file or die;
    print OUT <<"END_METADATA";
0000000000000	-rw-r--r--	root	root	0	(none)	$path
END_METADATA
    close OUT or die;

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
    my $obj = RPM::Grill->new( $temp_subdir );

    bless $obj, 'RPM::Grill::Plugin::Manifest';

    $obj->analyze;

    eq_or_diff $obj->{gripes}, $expected_gripes, $test_name;
}
