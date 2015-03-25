# -*- perl -*-
#
# tests for the SecurityPolicy module
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Temp                  qw(tempdir);

require 't/lib/FakeTree.pm' or die "Could not require FakeTree.pm: $!";

# pass 1: read DATA
my @tests = FakeTree::read_tests(*DATA);

plan tests => 3 + @tests;

# Pass 2: do the tests
my $tempdir = tempdir("t-SecurityPolicy.XXXXXX", CLEANUP => !$ENV{DEBUG});

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                          or exit;
use_ok 'RPM::Grill::RPM'                     or exit;
use_ok 'RPM::Grill::Plugin::SecurityPolicy'  or exit;

# Override nvr(); otherwise, the Ruby Gem CVE check barfs
package RPM::Grill::RPM;
use subs qw(nvr);
package main;
{
    no warnings 'redefine';
    *RPM::Grill::RPM::nvr = sub { return ('nnn', 'vvv', 'rrr') };
}

for my $i (0 .. $#tests) {
    my $t = $tests[$i];

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    my $g = FakeTree::make_fake_tree( $temp_subdir, $t->{setup} );

    my $expected_gripes;
    if ($t->{expect}) {
        $expected_gripes = eval "{ SecurityPolicy => [ $t->{expect} ] }";
        die "eval failed:\n\n $t->{gripe_string} \n\n  $@\n"     if $@;
    }

    bless $g, 'RPM::Grill::Plugin::SecurityPolicy';

    $g->analyze();

    eq_or_diff $g->{gripes}, $expected_gripes, $t->{name};
}


__DATA__

---------ok-path---------------------------------------------------------

>> -rw-r--r--  root root 0 /noarch/mypkg/usr/share/test_file0
PATH=/usr/bin

---------home-path---------------------------------------------------------

>> -rw-r--r--  root root 0 /noarch/mypkg/usr/share/test_file1
PATH=/home/test_dir

...expect:

{
    arch => 'noarch',
    code => 'SuspiciousPath',
    context => {
        excerpt => [ 'PATH=/home/test_dir' ],
        path => '/usr/share/test_file1'
    },
    diag => 'Potentially insecure PATH element <tt>/home</tt>',
    subpackage => 'mypkg'
}

---------tmp-path---------------------------------------------------------

>> -rw-r--r--  root root 0 /noarch/mypkg/usr/share/test_file2
PATH=/tmp/another/test_dir

...expect:

{
    arch => 'noarch',
    code => 'SuspiciousPath',
    context => {
        excerpt => [ 'PATH=/tmp/another/test_dir' ],
        path => '/usr/share/test_file2'
    },
    diag => 'Potentially insecure PATH element <tt>/tmp</tt>',
    subpackage => 'mypkg'
}

---------local-path---------------------------------------------------------

>> -rw-r--r--  root root 0 /noarch/mypkg/usr/share/test_file3
PATH=/usr/local/test_dir/bin

...expect:

{
    arch => 'noarch',
    code => 'SuspiciousPath',
    context => {
        excerpt => [ 'PATH=/usr/local/test_dir/bin' ],
        path => '/usr/share/test_file3'
    },
    diag => 'Potentially insecure PATH element <tt>/local</tt>',
    subpackage => 'mypkg'
}
