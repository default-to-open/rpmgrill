# -*- perl -*-
#
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

use_ok 'RPM::Grill'                       or exit;

package RPM::Grill::SubClassForTesting;

sub nvr { return ("nnn", "vvv", "rrr") }

sub plugins {
    my $self = shift;

    my $plugins = <<'END_PLUGINS';
1    a     completed
2    bbb   failed
10   aa    notrun
END_PLUGINS
    my @plugins;

    my %gripes = (
        a   => [ { code => 'MyCode', diag => 'this is a diag' } ],
        bbb => [ { code => 'MyCode2', diag => 'mydiag2',
                   context => { excerpt => 'This is a UTF-8 øéxçerpt' } } ],
    );


    for my $line (split "\n", $plugins) {
        my ($order, $name, $status) = split ' ', $line;

        eval "push \@RPM::Grill::Plugin::${name}::ISA, 'RPM::Grill::Plugin'";
        die "FOO: $@" if $@;

        push @plugins, bless {
            name => $name,
            order => $order,
            status => $status,
        }, "RPM::Grill::Plugin::$name";

        $self->{results}{$name} = { status => $status, run_time => 10 };
        if (my $g = $gripes{$name}) {
            $self->{gripes}{$name} = $g;
        }
    }

    return @plugins;
}

package RPM::Grill::Plugin;

sub order { return $_[0]->{order} };

use overload '""' => sub { return ref($_[0]) };

package main;

my $x = bless {}, 'RPM::Grill::SubClassForTesting';

my $actual_xml = RPM::Grill::results_as_xml($x);

$actual_xml =~ s{\b(timestamp|version)=".*?"}{$1="n/a"}g;

my $expected_xml = do { local $/ = undef; <DATA>; };

eq_or_diff $actual_xml, $expected_xml, "sdfdsf";

done_testing();

__DATA__
<?xml version="n/a" encoding="UTF-8" ?>
<results timestamp="n/a" tool="50as_xml.t" version="n/a">
  <package name="nnn" version="n/a" release="rrr"/>
  <test name="a"   order="01" status="completed" run_time="10">
    <gripe code="MyCode" diag="this is a diag" />
  </test>
  <test name="bbb" order="02" status="failed" run_time="10">
    <gripe code="MyCode2" diag="mydiag2">
      <context excerpt="This is a UTF-8 øéxçerpt" />
    </gripe>
  </test>
  <test name="aa"  order="10" status="notrun" run_time="10"/>
</results>
