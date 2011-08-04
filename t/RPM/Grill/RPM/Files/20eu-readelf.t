#!/usr/bin/perl
#
# Test suite for RPM::Grill::RPM::File (eu-readelf tests)
#

use strict;
use warnings;

use Test::More;
use Test::Differences;
use File::Slurp         qw(read_dir read_file);

our $test_subdir;
our @tests;

# Tests live in a subdirectory with our same test name,
# but with .d instead of .t.  Under this subdirectory are
# one or more subdirectories named NN-nnn, each containing
# two files: 'eu-readelf' and 'expect':
#
#   ../20eu-readelf.d/
#   ├── 10-aaa/
#   │   ├── eu-readelf
#   │   └── expect
#   ├── 20-no-diff.pic/
#   │   ├── eu-readelf
#   │   └── expect
#   ...
#
# Read those, to plan for our testing.
BEGIN {
    ($test_subdir = $0) =~ s|\.t$|.d|
        or die "Internal error: test name $0 doesn't end in .t";

    for my $d (sort grep { /^\d+\D+/ } read_dir($test_subdir)) {
        -d "$test_subdir/$d"
            or die "Internal error: $test_subdir/$d is not a directory";

        my $t = { name => $d };

        #
        $t->{expect} = do "$test_subdir/$d/expect";
        die "Internal error: eval $test_subdir/$d/expect: $@" if $@;

        push @tests, $t;
    }
}

plan tests => 3 + 3 * @tests;



#
# override open(), so we can feed fake eu-readelf data to the script
#
package RPM::Grill::RPM::Files;
use subs qw(open);
package main;

# When called to eu-readelf ddd/libxxx.a, read the file
# test-work-dir/ddd/eu-readelf.xxx instead.
*RPM::Grill::RPM::Files::open = sub {
    # e.g (undef, '-|', 'eu-readelf -a -b -c ...')
    my $pipe = $_[1];           # must be '-|'
    my $prog = $_[2];           # eu-readelf ...

    $pipe eq '-|'
        or die "Internal error: wrong 'open' (@_)";

    $prog =~ s/^eu-readelf\s+//
        or die "invoked with wrong program (expected eu-readelf): $prog";
    $prog =~ s/^-d -h -l //
        or die "eu-readelf invoked with wrong flags (expected '-d -h -l'): $prog";

    # Strip off '2>/dev/null'
    $prog =~ s{\s*\d*>\s*.*$}{};

    # e.g. 20gripes.d/10-basic/eu-readelf
    return CORE::open($_[0], '<', "$test_subdir/$prog/eu-readelf" );
};


use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::RPM'                  or exit;
use_ok 'RPM::Grill::RPM::Files'           or exit;

for my $t (@tests) {
    my $obj = bless {
        _file_type     => 'ELF blah blah blah',
        extracted_path => $t->{name},
    }, 'RPM::Grill::RPM::Files';

    $obj->_run_eu_readelf;

#    use Data::Dumper; print STDERR Dumper($obj->{_eu_readelf});
    eq_or_diff $obj->{_eu_readelf}, $t->{expect}, $t->{name};

    # Test name tells is whether the output should be PIE
    if ($t->{name} =~ /-pie/) {
        ok $obj->elf_is_pie, "$t->{name} is PIE";
    }
    else {
        ok !$obj->elf_is_pie, "$t->{name} is not PIE";
    }

    # Likewise for relro
    if ($t->{name} =~ /-([^-]+)relro/) {
        my $expected_relro = $1;
        is $obj->elf_relro||'no', $expected_relro, "$t->{name} RELRO = $expected_relro";
    }
    else {
        is $obj->elf_relro, '', "$t->{name} is not RELRO";
    }

    # KLUDGE: if the expect file consists solely of the string 'FIXME',
    # dump our actual results. This makes it easy for me to cut&paste
    # into the expect file.
    if (defined $t->{expect}) {
        if ($t->{expect} eq 'FIXME') {
            use Data::Dumper; print STDERR Dumper($obj->{_eu_readelf});
        }
    }
}
