# -*- perl -*-
#
# tests for the RPM Manifest checks
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath rmtree);
use File::Temp                  qw(tempdir);
use File::Basename              qw(basename);

my $tests = <<'END_TESTS';
------                            [the original mailman failure]
  /usr/lib/mailman
! /usr/lib/mailman/Mailman
  /usr/lib/mailman/Mailman/subdir

------                            [corrected situation. No gripe expected.]
  /usr/lib/mailman
  /usr/lib/mailman/Mailman
  /usr/lib/mailman/Mailman/subdir

------                            [simple case. No gripe expected.]
  /usr/lib/mailman

------                            [simple case, but deeper]
  /usr/lib/mailman/Mailman/subdir

------                            [made-up case with lots of missing dirs]
  /a/b/c/d/e/f/g
! /a/b/c/d/e/f/g/h
! /a/b/c/d/e/f/g/h/i
! /a/b/c/d/e/f/g/h/i/j
  /a/b/c/d/e/f/g/h/i/j/k
END_TESTS
my @tests;

for my $line (split "\n", $tests) {
    $line =~ s/\s*\#.*$//;              # Strip comments
    next unless $line;                  # skip empty and comment-only lines

    if ($line =~ /^-+\s+\[(.*)\]$/) {
        # Line of dashes. New test.
        push @tests, { name => $1, dirs => [], expect => [] };
    }
    elsif ($line =~ m{^\s+(/\S+)$}) {           # dir in manifest
        push @{ $tests[-1]->{dirs} }, $1;
    }
    elsif ($line =~ m{^\!\s+(/\S+)$}) {         # dir NOT in manifest
        # ...expect a warning about it.
        # Note that we unshift, not push. This is important, because
        # gripes are reported in depth-first order.
        unshift @{ $tests[-1]->{expect} }, $1;
    }
    else {
        die "Cannot grok test definition line '$line'";
    }
}

plan tests => 3 + @tests;

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::RPM'                  or exit;
use_ok 'RPM::Grill::Plugin::Manifest'     or exit;


# Run the tests
my $tempdir = tempdir("t-Manifest.XXXXXX", CLEANUP => !$ENV{DEBUG});

package RPM::Grill::RPM;
use subs qw(nvr);
package RPM::Grill;
use subs qw(major_release);
package main;

for my $i (0 .. $#tests) {
    my $t = $tests[$i];

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    mkdir $temp_subdir, 02755
        or die "mkdir $temp_subdir: $!\n";

    mkpath "$temp_subdir/src/mypkg", 0, 02755;

    # Create rpm.rpm
    open  OUT, '>', "$temp_subdir/src/mypkg/rpm.rpm" or die;
    close OUT;

    # Write RPM.per_file_metadata
    my $per_file = "$temp_subdir/src/mypkg/RPM.per_file_metadata";
    open OUT, '>>', $per_file or die;
    for my $d (@{ $t->{dirs} }) {
        # mkdir it, to avoid complaints
        mkpath "$temp_subdir/src/mypkg/payload$d", 0, 02755;

        # Add to manifest
        print OUT join("\t",
                       "f"x32,
                       'drwxr-xr-x',
                       'root',
                       'root',
                        "0",
                       "(none)",
                       $d,
                    ), "\n";
    }
    close OUT or die;

    # invoke
    my $obj = RPM::Grill->new( $temp_subdir );

    bless $obj, 'RPM::Grill::Plugin::Manifest';

    RPM::Grill::Plugin::Manifest::analyze( $obj );

    my $expected_gripes;
    if (my $d = $t->{expect}) {
        if (@$d) {
            $expected_gripes = {
                Manifest => [
                    map { +{
                        arch => 'src',
                        code => 'UnownedDirectory',
                        diag => "Unowned mid-level directory <tt>$_</tt>",
                    } } @$d
                ]
            };
        }
    }

    eq_or_diff $obj->{gripes}, $expected_gripes, $t->{name};

}
