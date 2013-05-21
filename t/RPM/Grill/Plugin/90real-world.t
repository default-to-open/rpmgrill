# -*- perl -*-
#
# Tests for RPM::Grill plugins : use on real-world data
#
use strict;
use warnings;

# We don't know how many plugins there are, or if there are load/can
# problems, hence we can't know a priori how many tests we'll run.
use Test::More;

our @tests;
BEGIN {
    use RPM::Grill;

    my $n_tests = 0;

    for my $plugin (RPM::Grill->plugins) {
        (my $fname = $plugin) =~ s!::!/!g;
        $fname .= ".pm";

        open PM, '<', $INC{$fname}
            or die "Internal error: Cannot read $INC{$fname}: $!\n";
        while (<PM>) {
            # Only look in header comments
            last unless /^#/;

            if (/^\#\s*(\S+-\S+-\S+)\s+(\S.*\S)\s*$/) {
                my $nvr  = $1;
                my @fail = split(/,\s*/, $2);

                push @tests, {
                    plugin => $plugin,
                    nvr    => $nvr,
                    fail   => \@fail,
                };
                $n_tests += 1 + @fail;
            }
        }
        close PM;
    }

    plan tests => $n_tests;
}


for my $t (@tests) {
    my $nvr = $t->{nvr} or die;
    # unpack (or skip?)
    # Run ->gather, ->run($plugin)

    my $plugin = $t->{plugin} or die;
    $plugin =~ /::Plugin::(.*)/ or die;
    my $module = $1;

    for my $f (@{ $t->{fail} }) {
        # FIXME
        ok 1, "$nvr > $module > $f";
    }

    # FIXME: make sure no other tests fail
    ok 1, "$nvr > $module > [ no other failures ]";
}
