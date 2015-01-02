# -*- perl -*-

use strict;
use warnings;

use Test::More;
use Test::Differences;

use Encode              qw(from_to);
use File::Slurp         qw(read_dir read_file);

#
# Pass 1: find tests
#
our @tests;
BEGIN {
    (my $test_subdir = $0) =~ s|\.t$|.d|
        or die "Internal error: test name $0 doesn't end in .t";

    for my $spec (sort grep { /\.spec$/ } read_dir($test_subdir)) {
        my $t = { name => $spec, path => "$test_subdir/$spec" };

        # Read the .expect file
        (my $expect = $spec) =~ s/\.spec$/.expect/;

        if (-e "$test_subdir/$expect") {
            $t->{expect} = eval read_file("$test_subdir/$expect");
            die "FIXME: Error reading $test_subdir/$expect: $@"     if $@;
        }

        push @tests, $t;
    }

    plan tests => 3 + @tests;
}


# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                     or exit;
use_ok 'RPM::Grill::RPM::SpecFile'      or exit;
use_ok 'RPM::Grill::Plugin::RpmScripts' or exit;

#
# Run tests
#
for my $t (@tests) {
    my $spec_obj = RPM::Grill::RPM::SpecFile->new( $t->{path} );

    my $grill = bless { specfile => $spec_obj },
        'RPM::Grill::Plugin::RpmScripts';
    $spec_obj->{grill} = $grill;

    $grill->analyze;

    my $actual_gripes = $grill->{gripes};

    # Host system may have different version of 'setup' package
    if ($actual_gripes) {
        for my $href ($actual_gripes, $t->{expect}) {
            for my $gripe (@{ $href->{RpmScripts} }) {
                $gripe->{diag} =~ s{/setup(-[\d.]+)?/}{/setup-[v]/}g;
            }
        }
    }

    # For debugging
    if ($actual_gripes && !$t->{expect}) {
        use Data::Dumper;$Data::Dumper::Indent = 1; print Dumper($actual_gripes); exit;
    }

    unified_diff;
    eq_or_diff $actual_gripes, $t->{expect}, $t->{name};
}

done_testing;
