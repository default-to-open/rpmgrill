# -*- perl -*-
#
# tests for RPM::Grill::major_release_ge()
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

# Test table:
#
#   * Left-hand column is the release we *want*, i.e. the argument
#     to ->major_release_ge().
#   * Top row is the *current* major release, i.e. the package's version
#   * dot indicates true, bang indicates false
#
# e.g. package version is RHEL5 (top row), we want RHEL6 (LHS), expect=false.
#
my $tests = <<'END_TESTS';
       | RHEL5 RHEL6 RHEL7 RHEL8 RHEL9 RHEL10 RHEL11 FC9 FC10 FC18 FC19 FC22
RHEL6  |     !     .     .     .     .      .      .   !    !    !    !    !
RHEL7  |     !     !     .     .     .      .      .   !    !    !    !    !
RHEL8  |     !     !     !     .     .      .      .   !    !    !    !    !
RHEL10 |     !     !     !     !     !      .      .   !    !    !    !    !
RHEL12 |     !     !     !     !     !      !      !   !    !    !    !    !
FC4    |     !     !     !     !     !      !      !   .    .    .    .    .
FC8    |     !     !     !     !     !      !      !   .    .    .    .    .
FC9    |     !     !     !     !     !      !      !   .    .    .    .    .
FC10   |     !     !     !     !     !      !      !   !    .    .    .    .
FC18   |     !     !     !     !     !      !      !   !    !    .    .    .
FC99   |     !     !     !     !     !      !      !   !    !    !    !    !
END_TESTS

my @major_releases;
my @tests;
for my $line (split "\n", $tests) {
    my ($desired_release, $statuses) = ($line =~ /^(.*?)\s+\|\s+(.*)/)
        or die "Internal error: cannot grok test definition line '$line'";
    my @statuses = split(' ', $statuses);

    # First line defines the FIXME
    if (! @major_releases) {
        @major_releases = @statuses;
    }
    else {
        @statuses == @major_releases
            or die "Internal error: mismatch in statuses, line '$line'";

        for my $i (0 .. $#statuses) {
            # Convert '.' and '!' to '1' and undef (expected return code)
            my $status = $statuses[$i];
            my $expect = ($status eq '.' ? 1 : undef);

            # Test name, including ' (false)' if that's what we expect
            my $name   = "$major_releases[$i] >= $desired_release";
            $name .= " (false)"  if !$expect;

            push @tests, bless {
                major_release   => $major_releases[$i],
                desired_release => $desired_release,
                expect          => $expect,
                name            => $name,
            }, 'RPM::Grill';
        }
    }
}
plan tests => 1 + @tests;

# Test 1 : load our module.
use_ok 'RPM::Grill'                       or exit;

# Override the ->major_release() method so it provides what we hardcode above
package RPM::Grill;
use subs qw(major_release);
no warnings 'redefine';
*RPM::Grill::major_release = sub {
    return $_[0]->{major_release};
};
package main;

# Tests themselves
for my $t (@tests) {
    is $t->major_release_ge($t->{desired_release}), $t->{expect}, $t->{name};
}
