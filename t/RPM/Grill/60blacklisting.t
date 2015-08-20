# -*- perl -*-

use strict;
use warnings;

use Test::More;
use Test::Differences;
use File::Temp qw(tempdir);

my $bfile = "blacklist.test";
my $tempdir = tempdir("t-RPM-Grill-RPM.XXXXXX", CLEANUP => 1);

use_ok 'RPM::Grill' or exit;

###############################################################################
package RPM::Grill::Plugin::Foo;

sub load_blacklist {
    RPM::Grill::load_blacklist(@_);
}

sub is_blacklisted {
    return RPM::Grill::is_blacklisted(@_);
}

sub gripe_signature {
    return RPM::Grill::gripe_signature(@_);
}

sub nvr { return ("name", "ver", "rel") }

sub plugins {
    my $self = shift;

    my $plugins = <<END_PLUGINS;
1    BuildLog      completed
2    DesktopLint   completed
5    ElfChecks     completed
10   Multilib      completed
END_PLUGINS
    my @plugins;

    my %gripes = (
        BuildLog    => {code => 'MacroExpansion', diag => 'diag1'},
        DesktopLint => {code => 'DesktopFileValidation', diag => 'diag2'},
        ElfChecks   => {code => 'DaemonPartialRELRO', diag => 'diag3'},
        Multilib    => {code => 'MultilibMismatch', diag => 'diag4'},
    );

    load_blacklist("$tempdir/$bfile");

    for my $line (split "\n", $plugins) {
        my ($order, $name, $status) = split ' ', $line;

        eval "push \@RPM::Grill::Plugin::${name}::ISA, 'RPM::Grill::Plugin'";
        die "Foo: $@" if $@;

        push @plugins, bless {
            name => $name,
            order => $order,
            status => $status,
        }, "RPM::Grill::Plugin::$name";

        $self->{results}{$name} = { status => $status, run_time => 10 };
        if (my $g = $gripes{$name}) {
            my $sig = gripe_signature(\%$g);
            if (! is_blacklisted($name, $sig)) {
                $self->{gripes}{$name} = $g;
            }
        }
    }

    return @plugins;
}

package RPM::Grill::Plugin;
sub order { return $_[0]->{order} };
use overload '""' => sub { return ref($_[0]) };

package main;
###############################################################################

open my $fileh, '>', "$tempdir/$bfile" or die "Unable to create new file: $!";
print $fileh <<EOF;
---
blacklist:
  BuildLog: MacroExpansion, MiscBuildError
  Multilib: MultilibMismatch, DepGenDisabled
EOF
close("$tempdir/$bfile");


my $m = bless {}, 'RPM::Grill::Plugin::Foo';
my $actual_yaml = RPM::Grill::results_as_yaml($m);

# remove timestamp and rpmgrill version from final output
$actual_yaml =~ s/^.*timestamp.*\n//gm;
$actual_yaml =~ s/^.*version.*\n//m;

my $expected_yaml = do { local $/ = undef; <DATA>; };

eq_or_diff $actual_yaml, $expected_yaml, "blacklist-config option";

unlink "$tempdir/$bfile";
done_testing;


__DATA__
---
results:
  tool: 60blacklisting.t
package:
  name: name
  version: ver
  release: rel
tests:
  - '001 BuildLog    : completed (10s)'
  - '002 DesktopLint : completed (10s)':
      code: DesktopFileValidation
      diag: diag2
  - '005 ElfChecks   : completed (10s)':
      code: DaemonPartialRELRO
      diag: diag3
  - '010 Multilib    : completed (10s)'
