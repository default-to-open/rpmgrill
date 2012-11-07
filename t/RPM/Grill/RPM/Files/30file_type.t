#!/usr/bin/perl
#
# Test suite for RPM::Grill::RPM::File (file_type, i.e. File::LibMagic)
#

use strict;
use warnings;

use Test::More;
use Test::LongString;
use File::Slurp         qw(write_file);
use File::Temp          qw(tempdir);
use MIME::Base64;

# Because of the "last modified" timestamp in the gzip test, running this
# test in different time zones can result in failure. Override that.
$ENV{TZ} = 'EST5EDT';

my @tests;
while (my $line = <DATA>) {
    chomp $line;

    if ($line =~ /^(\S+):\s+(.*)/) {
        push @tests, { filename => $1, expected_type => $2, content => '' };

        # e.g. "foo.bar.gz*: ...." -- the '*' means 'the rest of this is base64'
        if ($tests[-1]{filename} =~ s/\*$//) {
            $tests[-1]{is_bin} = 1;
        }
    }
    elsif ($line =~ /^-{70,}$/) {
        # skip it
    }
    elsif ($line && @tests) {
        $tests[-1]->{content} .= ($tests[-1]{is_bin}
                                      ? decode_base64($line)
                                      : $line . "\n");
    }
}

plan tests => 1 + @tests;

use_ok 'RPM::Grill::RPM::Files'           or exit;

# Create a temporary directory. We will write files here.
my $tempdir = tempdir("t-file_type.XXXXXXX", CLEANUP => !$ENV{DEBUG});
chdir $tempdir || die "cannot cd $tempdir: $!";

for my $t (@tests) {
    my $filename = $t->{filename};

    write_file($filename, $t->{content});

    my $obj = bless {
        extracted_path => $filename,
    }, 'RPM::Grill::RPM::Files';

    my $actual_type = $obj->file_type;

    is_string $actual_type, $t->{expected_type}, $filename;
}

# Allow cleanup
chdir '..';
exit(0);

################################################################################
#
# Files to be tested. Syntax is:
#
#     ----------------------------------------------------------------------
#     <filename>: <expected type>
#     <file contents>
#     ...
#
# An asterisk (*) after filename indicates that <file contents> is base64
#
# The line of dashes is ignored; it's just there for readability.
#
__DATA__

--------------------------------------------------------------------------------
empty.c: empty

--------------------------------------------------------------------------------
foo.c: ASCII C program text
/*
** foo.c
*/
#include <stdio.h>

--------------------------------------------------------------------------------
foo.sh: POSIX shell script, ASCII text executable
#!/bin/sh
#
# hi there
echo hi

--------------------------------------------------------------------------------
foo.pl: a /usr/bin/perl script, ASCII text executable
#!/usr/bin/perl
#
# This one invokes perl directly

--------------------------------------------------------------------------------
foo2.pl: a perl script, ASCII text executable
#!/usr/bin/env perl
#
# This one invokes perl via env

--------------------------------------------------------------------------------
foo.pl.gz*: a /usr/bin/perl script, ASCII text executable (gzip compressed data, was "foo.pl", from Unix, last modified: Thu Jul 26 13:33:23 2012, max compression)
H4sICGN/EVACA2Zvby5wbABTVtQvLS7ST8rM0y9ILcrhUuZSVgjJyCxWyM9LVcjMK8vPTi1WAMko
pGQWpSaX5FRyAQBWpq1nMwAAAA==

--------------------------------------------------------------------------------
foo*: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, stripped
f0VMRgIBAQAAAAAAAAAAAAIAPgABAAAA4ANAAAAAAABAAAAAAAAAALgJAAAAAAAAAAAAAEAAOAAI
AEAAHAAbAAYAAAAFAAAAQAAAAAAAAABAAEAAAAAAAEAAQAAAAAAAwAEAAAAAAADAAQAAAAAAAAgA
