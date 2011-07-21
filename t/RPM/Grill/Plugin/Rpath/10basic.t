# -*- perl -*-

use strict;
use warnings;

use Test::More;
use Test::Differences;

# Tests 1-2 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                  or exit;
use_ok 'RPM::Grill::Plugin::Rpath'   or exit;

# BEGIN test list
my $tests = <<'END_TESTS';
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so  /lib65         /lib65 is not a known trusted path
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so  /foo           /foo is not a known trusted path
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so  /usr/share/foo /usr/share is not a known trusted path
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so  $ORIGIN        /usr/share is not a known trusted path
END_TESTS

for my $line (split "\n", $tests) {
    my ($path, $rpath, $expected_msg) = split ' ', $line, 3;

    my $actual_msg = RPM::Grill::Plugin::Rpath::_rpath_element_is_suspect( $path, $rpath );
    is $actual_msg, $expected_msg, "$path + $rpath";
}

done_testing();
