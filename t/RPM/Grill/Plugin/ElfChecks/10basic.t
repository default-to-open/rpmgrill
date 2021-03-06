# -*- perl -*-

use strict;
use warnings;

use Test::More;
use Test::Differences;

# Tests 1-2 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                     or exit;
use_ok 'RPM::Grill::Plugin::ElfChecks'  or exit;

#
# Test list. Format is:
#
#      <path>   <RPATH>   <expected message>
#
# Each RPATH is one single element (other scripts will test '/foo:/bar').
# If the combination is OK, use '-' for 'no error'.
#
# You'll need a pretty wide window. Sorry. Tradeoff.
my $tests = <<'END_TESTS';
# These should be OK
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     /lib                -
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     /lib64              -
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     /usr/lib            -
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     /usr/lib64          -

# Subpaths of the above. Also OK.
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     /lib/foo            -
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     /lib64/bar          -
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     /usr/lib/subdir     -
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     /usr/lib64/subdir   -

# These are not
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     /usr                not a known trusted path
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     /lib65              /lib65 is not a known trusted path
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     /foo                /foo is not a known trusted path
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     /usr/share/foo      /usr/share is not a known trusted path
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     $ORIGIN             /usr/share is not a known trusted path
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     $ORIGIN/../../lib   /usr/share is not a known trusted path
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     $ORIGIN             /usr/share is not a known trusted path

# Weird case should never happen
/usr/share/java-1.6.0-ibm/demo/jvmti/gctest/lib/libgctest.so     /usr/lib/../lib     '..' in rpath element

# Back to OK
/usr/lib/libfoo.so                                               $ORIGIN             -
/usr/lib/libfoo.so                                               $ORIGIN/subdir      -

/usr/lib/subdir/libfoo.so                                        $ORIGIN             -
/usr/lib/subdir/libfoo.so                                        $ORIGIN/..          -
/usr/lib/subdir/libfoo.so                                        $ORIGIN/../otherdir -

# bz797428 (SCL awareness)
/opt/rh/devtoolset-1.0/root/usr/bin/ar                           /opt/rh/devtoolset-1.0/root/usr/lib -

# bz797428 duh! SCL should still allow /lib, etc
#  e.g. ruby193-ruby-1.9.3.327-27.el5
/opt/rh/devtoolset-1.0/root/usr/bin/ar                           /lib       -
/opt/rh/devtoolset-1.0/root/usr/bin/ar                           /usr/lib64 -

# placeholder for some future day
/opt/rh/devtoolset-1.0-addon/root/usr/bin/ar                     /opt/rh/devtoolset-1.0/root/usr/lib RPATH is in a different SCL package (devtoolset-1.0); I can't deal with this yet.
END_TESTS

for my $line (split "\n", $tests) {
    $line =~ s/^\s*\#.*//;                      # Trim comments
    next unless $line;                          # skip empty lines

    my ($path, $rpath, $expected_msg) = split ' ', $line, 3;
    $expected_msg = undef if $expected_msg eq '-';

    my $actual_msg = RPM::Grill::Plugin::ElfChecks::_rpath_element_is_suspect( $path, $rpath );
    is $actual_msg, $expected_msg, "$path + $rpath";
}

done_testing();
