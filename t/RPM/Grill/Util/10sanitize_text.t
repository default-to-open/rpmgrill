# -*- perl -*-
#
# Test suite for RPM::Grill::Util::sanitize_text()
#
use strict;
use warnings;

use utf8;
use open qw(:std :utf8);

use Test::More;
use Test::Differences;

my @tests = (
    [ 'aaa'                 => 'aaa'                 ],
    [ 'ccc&d'               => 'ccc&amp;d'           ], # HTML special char
    [ 'cccd'              => 'ccc[^V]d'            ], # ctrl character
    [ 'Muñoz'               => 'Muñoz'               ], # UTF-8 passthru
    [ "Mu\361oz"            => 'Mu&amp;#241;oz'      ], # GAH! non-utf8
    [ "Embedded\011tab"     => "Embedded\011tab"     ],
    [ "Embedded\012newline" => "Embedded\012newline" ],
);

plan tests => 1 + @tests;

use_ok 'RPM::Grill::Util', qw(sanitize_text)            or exit;

for my $t (@tests) {
    my ($text, $expect) = @$t;

    my $actual = sanitize_text($text);

    is $actual, $expect, "$text -> $expect";
}
