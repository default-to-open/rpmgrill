#!/usr/bin/perl
#
# Test suite for SpecFileSanity plugin
#

use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Slurp         qw(read_dir read_file write_file);

our @tests;

# Tests live in a subdirectory with our same test name, but with .d
# instead of .t.  Under this subdirectory are one or more files
# named N-V-R.spec, each containing an actual spec file.  For each
# of those there's a corresponding N-V-R.expect containing the
# expected gripe messages.
#
# Read those, to plan for our testing.
BEGIN {
    (my $test_subdir = $0) =~ s|\.t$|.d|
        or die "Internal error: test name $0 doesn't end in .t";

    for my $spec (sort grep { /\.spec$/ } read_dir($test_subdir)) {
        my $t = { name => $spec, path => "$test_subdir/$spec" };

        # Read the .expect file
        (my $expect = $spec) =~ s/\.spec/.expect/;

        $t->{expect} = eval read_file("$test_subdir/$expect");
        die "FIXME: Error reading $test_subdir/$expect: $@"     if $@;

        $t->{expect_path} = "$test_subdir/$expect";

        # Useful when adding new tests: this will be true if the .expect file
        # is nonzero size. When false (empty file), special-case code below
        # will trigger and will fill in the file.
        $t->{have_expect} = -s $t->{expect_path};

        push @tests, $t;
    }

    plan tests => 3 + @tests;
}

# Load our modules
use_ok 'RPM::Grill'                           or exit;
use_ok 'RPM::Grill::RPM::SpecFile'            or exit;
use_ok 'RPM::Grill::Plugin::SpecFileSanity'   or exit;

# FIXME: override ->nvr()
package RPM::Grill;
use subs qw(nvr);
package main;

# Run the tests
for my $t (@tests) {
    my $name = $t->{name};

    my ($n, $v, $r) = $name =~ /^(.*)-(.*)-(.*)$/
        or die "Cannot determine N-V-R from $name";
    # Hack: Redefine the nvr() method. Otherwise we need to create
    # a fake srpm.
    {
        no warnings 'redefine';
        *RPM::Grill::nvr = sub {
            return ($n, $v, $r)
        };
    }

    my $spec_obj = RPM::Grill::RPM::SpecFile->new( $t->{path} );
    my $grill    = bless { specfile => $spec_obj },
        'RPM::Grill::Plugin::SpecFileSanity';

    # FIXME: make a temp dir, copy spec file into expected place?
    eval { $grill->analyze };
    if ($@) {
        fail "$name : $@";
    }
    else {
        if ($t->{have_expect}) {
            # The usual case. We have something to expect (even if it's undef).
            # Run the test.
            eq_or_diff $grill->{gripes}, $t->{expect}, $name;
        }
        else {
            # Only triggers once, when adding a new test and the .expect file
            # is empty. In this case, we just fill the file in with our
            # obtained results. This makes it easy to add new tests or,
            # occasionally, to reset the expected output of a test.
            diag "FIRST TIME: writing $t->{expect_path}";

            use Time::Piece;
            my $timestamp = localtime->datetime;
            use Data::Dumper;
            $Data::Dumper::Terse  = 1;  # Omit the '$VAR1 = ...' prefix
            $Data::Dumper::Indent = 1;  # Compact but readable

          SKIP: {
                write_file(
                    $t->{expect_path},
                    "# Created: $timestamp\n",
                    Dumper($grill->{gripes})
                );
                skip $name, 1;
            }
        }
    }
}
