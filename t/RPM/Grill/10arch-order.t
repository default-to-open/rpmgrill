# -*- perl -*-
#
# tests for ensuring that RPM::Grill->arches() returns a consistent order
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath rmtree);
use File::Temp                  qw(tempdir);

my @tests = (
    [ qw( src i386 x86_64                      ) ],
    [ qw( src i386 x86_64           s390 s390x ) ],
    [ qw( src i686 x86_64 ppc ppc64            ) ],     # Note i386 -> i686
    [ qw( src i686 x86_64 ppc ppc64 s390 s390x ) ],
    [ qw( src             ppc ppc64 s390 s390x ) ],
    [ qw(                 ppc ppc64 s390 s390x ) ],
);
plan tests => 1 + 2 * @tests;

my $tempdir = tempdir("t-RPM-Grill.XXXXXX", CLEANUP => 1);

# Test 1 : load our module.
use_ok 'RPM::Grill'                       or exit;

# For each of the arch lists above, create a series of subdirs for RPM::Grill
my $i = 0;
for my $t (@tests) {
    # The "reverse" is pointless; the goal is to catch it if somehow
    # the code were to start readdir()ing in mtime order.
    for my $arch (reverse @$t) {
        my $d = "$tempdir/$i/$arch/mypkg";
        mkpath $d, 0, 0755;
        open TMP, '>', "$d/rpm.rpm";
        close TMP;
    }

    # Poor Man's constructor
    my $obj = RPM::Grill->new( "$tempdir/$i" );

    # Now see what we get for ->arches, and compare to the list above
    my @got = $obj->arches;
    eq_or_diff \@got, $t, join(" ", @$t);

    shift @$t           if $t->[0] eq 'src';

    @got = $obj->non_src_arches;
    eq_or_diff \@got, $t, " \\_ non_src_arches()";

    ++$i;
}
