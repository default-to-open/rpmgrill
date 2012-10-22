#!/usr/bin/perl
#
# Test suite for RPM::Grill::RPM::File::dw_at_producer()
#

use strict;
use warnings;

use Test::More;
use Test::Differences;

# Tests live at end of file
our @tests;
while (my $line = <DATA>) {
    chomp $line;

    if ($line =~ /^>\s*(\S+)\s*:(\s+(.*))?/) {
        my ($k, $v) = ($1, $3||'');
        if ($k eq 'test') {
            push @tests, { filename => $v };
        }
        $tests[-1]->{$k} = $v;
    }
    elsif ($line =~ /^-{70,}$/) {
        # skip it
    }
    elsif ($line && @tests) {
        $tests[-1]->{eu_readelf} .= $line . "\n";
    }
}

plan tests => 1 + @tests;

use_ok 'RPM::Grill::RPM::Files'           or exit;

# override open(), so we can feed fake eu-readelf data to the script
#
package RPM::Grill::RPM::Files;
use subs qw(open);
package main;

our $EU_READELF_FAKE = '';

# When called to eu-readelf ddd/libxxx.a, read the file
# test-work-dir/ddd/eu-readelf.xxx instead.
*RPM::Grill::RPM::Files::open = sub {
    # e.g (undef, '-|', 'eu-readelf -a -b -c ...')
    my $pipe = $_[1];           # must be '-|'
    my $prog = $_[2];           # eu-readelf ...

    $pipe eq '-|'
        or die "Internal error: wrong 'open' (@_)";

    $prog eq 'eu-readelf'
        or die "invoked with wrong program (expected eu-readelf): '$prog'";

    # e.g. 20gripes.d/10-basic/eu-readelf
    return CORE::open($_[0], '<', \$EU_READELF_FAKE);
};


for my $t (@tests) {
    my $obj = bless {
        _file_type     => $t->{_file_type},
        extracted_path => $t->{filename},
        path           => $t->{filename},
    }, 'RPM::Grill::RPM::Files';

    $EU_READELF_FAKE = $t->{eu_readelf};

    is $obj->dw_at_producer, $t->{expected_producer}, $t->{filename};
}


__END__

> test: anaconda/auditd.debug
> _file_type: ELF blah blah blah
> expected_producer: GNU C 4.7.2 20121001 (Red Hat 4.7.2-3) -m64 -march=z9-109 -mtune=z10 -mzarch -g -O2 -fexceptions -fstack-protector --param ssp-buffer-size=4

DWARF section [27] '.debug_info' at offset 0x2ec:
 [Offset]
 Compilation unit at offset 0:
 Version: 4, Abbreviation section offset: 0, Address size: 8, Offset size: 4
 [     b]  compile_unit
           producer             (strp) "GNU C 4.7.2 20121001 (Red Hat 4.7.2-3) -m64 -march=z9-109 -mtune=z10 -mzarch -g -O2 -fexceptions -fstack-protector --param ssp-buffer-size=4"
           language             (data1) ISO C89 (1)
           name                 (form: 0x1f21) ???
eu-readelf: cannot get next DIE: invalid DWARF

-----------------------------------------------------------------------------

> test: foo.wrong-extension
> _file_type: ELF blah blah blah

sdfsdf

-----------------------------------------------------------------------------

> test: foo.wrong-type.debug
> _file_type: not ELF
> expected_producer:

sdfsdf
