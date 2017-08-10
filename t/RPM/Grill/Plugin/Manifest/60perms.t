# -*- perl -*-
#
# tests for the permissions check in Manifest module
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Temp                  qw(tempdir);

use lib "t/lib";
use FakeTree;

# pass 1: read DATA
my @tests = FakeTree::read_tests( *DATA );

#use Data::Dumper;print Dumper(\@tests);exit 0;

plan tests => 3 + @tests;

# Pass 2: do the tests
my $tempdir = tempdir("t-SecurityPolicy.XXXXXX", CLEANUP => !$ENV{DEBUG});

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                          or exit;
use_ok 'RPM::Grill::RPM'                     or exit;
use_ok 'RPM::Grill::Plugin::Manifest'        or exit;

###############################################################################
# BEGIN override ->nvr()

package RPM::Grill::RPM;
use subs qw(nvr);
package RPM::Grill;
use subs qw(major_release);
package main;

# Set a fake NVR
{
    no warnings 'redefine';
    *RPM::Grill::RPM::nvr = sub {
        return "1.el7";
    };
    *RPM::Grill::major_release = sub {
        return "RHEL7";
    };
}

# END   override ->nvr()
###############################################################################

for my $i (0 .. $#tests) {
    my $t = $tests[$i];

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    my $g = FakeTree::make_fake_tree( $temp_subdir, $t->{setup} );

    my $expected_gripes;
    if ($t->{expect}) {
        $expected_gripes = eval "{ Manifest => [ $t->{expect} ] }";
        die "eval failed:\n\n $t->{gripe_string} \n\n  $@\n"     if $@;
    }

    bless $g, 'RPM::Grill::Plugin::Manifest';

    $g->analyze();

    eq_or_diff $g->{gripes}, $expected_gripes, $t->{name};
}


__DATA__

--------owned-by-root-------------------------------------------

>> -rw-r--r--  root root 0 /noarch/mypkg/usr/bin/foo

-------not-in-bin-dir-------------------------------------------

>> -rw-r--r--  badusr badgrp 0 /noarch/mypkg/usr/lib/foo
>> -rw-r--r--  badusr badgrp 0 /noarch/mypkg/usr/share/bin/foo

-------owned-by-foo---------------------------------------

>> -rw-r--r--  foo  root 0 /noarch/mypkg/usr/bin/foo

...expect:

 {
      arch => 'noarch',
      code => 'BinfileBadOwner',
      context => {
        path => '/usr/bin/foo'
      },
      diag => 'Owned by \'<tt>foo</tt>\'; files in /usr/bin must be owned by root',
      subpackage => 'mypkg'
 }

-------group-badgrp---------------------------------------

>> -rw-r--r--  root badgrp 0 /noarch/mypkg/usr/bin/foo

...expect:

 {
      arch => 'noarch',
      code => 'BinfileBadGroup',
      context => {
        path => '/usr/bin/foo'
      },
      diag => 'Owned by group \'<tt>badgrp</tt>\'; files in /usr/bin must be group \'root\'',
      subpackage => 'mypkg'
 }

-------both-bad---------------------------------------

>> -rw-r--r--  badusr badgrp 0 /noarch/mypkg/usr/sbin/foo

...expect:

 {
      arch => 'noarch',
      code => 'BinfileBadOwner',
      context => {
        path => '/usr/sbin/foo'
      },
      diag => 'Owned by \'<tt>badusr</tt>\'; files in /usr/sbin must be owned by root',
      subpackage => 'mypkg'
 },
 {
      arch => 'noarch',
      code => 'BinfileBadGroup',
      context => {
        path => '/usr/sbin/foo'
      },
      diag => 'Owned by group \'<tt>badgrp</tt>\'; files in /usr/sbin must be group \'root\'',
      subpackage => 'mypkg'
 }
