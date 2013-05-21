# -*- perl -*-
#
# Tests for numeric_mode() code in RPM::Grill::RPM::Files
#
use strict;
use warnings;

use Test::More;

our @tests;
BEGIN {
    # LHS = ls string, RHS = octal mode, comments are ignored
    my $tests = <<'END_TESTS';
-rw-r--r--      0100644         # regular file, not executable
-rwxr-xr-x      0100755         # regular file, executable
drwxr-xr-x      0040755         # directory
-rwsr-xr-x      0104755         # setuid file
-r-x--s--x      0102511         # setgid executable, go-r
END_TESTS
    for my $line (split "\n", $tests) {
        $line =~ s/\s*\#.*$//;                  # strip comments

        $line =~ /^(\S+)\s+([0-7]+)$/
            or die "Internal error: cannot grok test line '$line'";
        push @tests, { ls => $1, expect => $2 };
    }

    plan tests => 1 + @tests;
}

use_ok 'RPM::Grill::RPM::Files';

for my $t (@tests) {
    my $actual = sprintf("%09o", RPM::Grill::RPM::Files::_numeric_mode($t->{ls}));
    my $expect = sprintf("%09o", oct($t->{expect}));

    is $actual, $expect, "$t->{ls} = $t->{expect}"
}
