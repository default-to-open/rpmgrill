# -*- perl -*-

use strict;
use warnings;

use Test::More;
use Test::Differences;

my %map_to = ( '-' => ['ante'], '+' => ['post'], '=' => ['ante','post']);

my @tests;
while (my $line = <DATA>) {
    next if $line =~ /^\s*$/;           # Skip blank ...
    next if $line =~ /^\s*#/;           # ...or comment-only lines

    if ($line =~ /^-{10,}(.*[^-])-{10,}$/) {
        push @tests, { name => $1, ante => [], post => [] };
    }
    elsif ($line =~ s/^(-|\+|=)\s+//) {
        my $token = $1;

        my ($arch, $subpackage, $code, $rest) = split ' ', $line, 4;
        defined $rest
            or die "Internal error: incomplete test case '$line'";
        $rest =~ s/^("|')(.*?)\1//
            or die "Internal error: no diag string in '$rest'";
        my $diag = $2;
        # FIXME: context?

        for my $which (@{ $map_to{$token} }) {
            push @{ $tests[-1]{$which} }, {
                arch       => $arch,
                subpackage => $subpackage,
                code       => $code,
                diag       => $diag,
            };
        }
    }
}

plan tests => 1 + @tests;

use_ok 'RPM::Grill'                       or exit;

###############################################################################
# BEGIN sidetrack
#
# RPM::Grill::gripe() invokes caller() to find out the name of the module.
# This function definition inside ::Foo namespace makes gripes go into
# the right place.
#
package RPM::Grill::Plugin::Foo;

sub gripe {
    RPM::Grill::gripe(@_);
}

package main;

# END   sidetrack
###############################################################################

for my $t (@tests) {
    my $module = "Foo";
    my $obj = bless {}, "RPM::Grill::Plugin::$module";

    # Invoke gripe() for each one.
    for my $g (@{ $t->{ante} }) {
        $obj->gripe($g);
    }

    # FIXME
    eq_or_diff $obj->{gripes}{$module}, $t->{post}, $t->{name};
#    use Data::Dumper; print STDERR Dumper($obj);
}


__DATA__

#
# Format is:
#
#   <arch> <subpackage> <code> "<diag>" ...
#

--------------Simple aggregation (different arches)----------------

- i386        pkg Code "My Diag"
- x86_64      pkg Code "My Diag"
+ i386,x86_64 pkg Code "My Diag"

--------------Simple aggregation (different subpkgs)--------------

- i386 pkg1      Code "My Diag"
- i386 pkg2      Code "My Diag"
+ i386 pkg1,pkg2 Code "My Diag"

--------------No aggregation (different codes)--------------

= i386   pkg Code1 "My Diag"
= x86_64 pkg Code2 "My Diag"

--------------No aggregation (different diags)--------------

= i386   pkg Code "My Diag 1"
= x86_64 pkg Code "My Diag 2"

--------------Partial aggregation---------------------------

- i386             pkg Code "My Diag"
- x86_64           pkg Code "My Diag"
- s390             pkg Code "My Diag"
+ i386,x86_64,s390 pkg Code "My Diag"

= s390             pkg Code "Another diag"

--------------Partial aggregation, with out-of-order msgs-----------

- i386             pkg Code "My Diag"
- x86_64           pkg Code "My Diag"
+ i386,x86_64,s390 pkg Code "My Diag"

= s390             pkg Code "Another diag"

- s390             pkg Code "My Diag"
