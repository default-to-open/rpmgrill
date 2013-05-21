# -*- perl -*-
#
# tests for methods in RPM::Grill::RPM.pm
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath rmtree);
use File::Temp                  qw(tempdir);

my $tempdir = tempdir("t-RPM-Grill-RPM.XXXXXX", CLEANUP => 1);

# Test 1 : load our module.
use_ok 'RPM::Grill::RPM'                       or exit;

# Test 2 : RPM.requires
my @expected = qw(aaa bbb ccc ThisIsInCaps ThisHas(version));
my $d = "$tempdir/myarch/mypkg";
mkpath $d, 0, 0755;
open OUT, '>', "$d/RPM.requires"
    or die "Cannot create $d/RPM.requires: $!";
print OUT "$_\n"                for @expected;
close OUT
    or die "Error writing $d/RPM.requires: $!";

# We happen to know that ->capabilities() only needs {dir}
my $b = bless { dir => $d }, 'RPM::Grill::RPM';
my @actual = $b->requires;

is_deeply \@actual, \@expected, 'RPM->requires';

done_testing();
