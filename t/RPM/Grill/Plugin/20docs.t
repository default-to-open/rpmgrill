# -*- perl -*-
#
# Tests for RPM::Grill plugins : make sure they provide blurb & doc methods
#
use strict;
use warnings;

# We don't know how many plugins there are, or if there are load/can
# problems, hence we can't know a priori how many tests we'll run.
use Test::More;

use_ok('RPM::Grill')  or exit;

my %order;
PLUGIN:
for my $plugin (RPM::Grill->plugins) {
    # Load the plugin
    use_ok($plugin)            or next PLUGIN;

    # Make sure it provides ->blurb(), and make sure ->blurb() is reasonable
    check_blurb( $plugin );

    # ditto for ->doc()
    check_doc( $plugin );
}

# Signal to test harness
done_testing();


#################
#  check_blurb  #  Sanity checks on blurbs
#################
sub check_blurb {
    my $plugin = shift;

    can_ok($plugin, 'blurb')            or return;

    my $blurb = $plugin->blurb();

    my $testname = "$plugin->blurb()";
    if ($plugin =~ /.*::(.*)/) {
        $testname = "$1->blurb()";
    }

    # Make sure it's nonempty
    if ($blurb !~ /\S/) {
        fail "$testname is empty";
        return;
    }
    # ...and has been initialized.
    if ($blurb =~ /FIXME/) {
        diag "Warning: $testname still contains FIXME";
        return;
    }

    # More sanity checks
    ok length($blurb) <= 55, "$testname must be <=55 chars";
    ok $blurb =~ /^[a-z]/,   "$testname should be lower-case";
    ok $blurb !~ /\n/,       "$testname shouldn't have newlines";
}


sub check_doc {
    my $plugin = shift;

    can_ok($plugin, 'doc')              or return;

    my $doc = $plugin->doc();

    my $testname = "$plugin->doc()";
    if ($plugin =~ /.*::(.*)/) {
        $testname = "$1->doc()";
    }

    # Make sure it's nonempty
    if ($doc !~ /\S/) {
        fail "$testname is empty";
        return;
    }
    # ...and has been initialized.
#    if ($doc =~ /FIXME/) {
#        fail "$testname still contains FIXME";
#        return;
#    }
}
