# -*- perl -*-
#
# tests for RPM::Grill multilib stuff
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath rmtree);
use File::Temp                  qw(tempdir);

my $tempdir = tempdir("t-RPM-Grill.XXXXXX", CLEANUP => !$ENV{DEBUG});

# Test 1 : load our module.
use_ok 'RPM::Grill'                       or exit;


# Make a bunch of temp dirs
for my $arch qw( src i686 x86_64 ia64 ppc ppc64 s390 s390x ) {
    for my $subpkg qw(mypkg mysubpkg) {
        my $d = "$tempdir/$arch/$subpkg";
        mkpath $d,     0, 0755;
        open TMP, '>', "$d/rpm.rpm";
        close TMP;
    }
}

my $obj = RPM::Grill->new( $tempdir );

my @x86 = $obj->rpms( arch => 'i686', subpackage => 'mypkg' );
is scalar(@x86), 1, "one x86-mypkg rpm";

is $x86[0]->is_64bit, 0, "x86-mypkg rpm is not 64-bit";

my @peers = $x86[0]->multilib_peers;
is scalar(@peers), 2, "two 64-bit peers of x86-mypkg rpm";

my @peer_arches = sort map { $_->arch } @peers;
eq_or_diff \@peer_arches, [ qw(ia64 x86_64) ], "peer arches of x86";

my @s390x = $obj->rpms( arch => 's390x', subpackage => 'mysubpkg' );
is scalar(@s390x), 1, "one s390x-mysubpkg rpm";
is $s390x[0]->is_64bit, 1, "s390x-mysubpkg rpm is 64-bit";

@peers = $s390x[0]->multilib_peers;
is scalar(@peers), 1, "one 32-bit peer of s390x-mysubpkg rpm";

is $peers[0]->arch, 's390', 'peer arch of s390x';

done_testing;
