# -*- perl -*-
#
# Tests for RPM::Grill plugins : make sure they load & provide an order()
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
    # Load the plugin, make sure it provides ->order()
    use_ok($plugin)            or next PLUGIN;
    can_ok($plugin, 'order')   or next PLUGIN;

    # Get the order, make sure it has been reset from the default
    my $order = $plugin->order();
    if ($order eq '999') {
        diag "warning: $plugin->order() has not been initialized";
        next PLUGIN;
    }

    # The order() method in each package must be unique
    if (exists $order{$order}) {
        fail("$plugin : order=$order already used by $order{$order}");
    }
    else {
        pass("$plugin : order=$order is unique");
        $order{$order} = $plugin;
    }

    # While we're at it, make sure each module provides a ->analyze()
    can_ok($plugin, 'analyze');
}

# Signal to test harness
done_testing();
