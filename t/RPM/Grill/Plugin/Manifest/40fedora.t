#!/usr/bin/perl

use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath rmtree);
use File::Temp                  qw(tempdir);

# pass 1: read tests. Anything with an exclamation point in front is
# expected to fail the Fedora test
my @tests;
my $tests = <<'END_TESTS';
  i686 /usr/share/doc/README         /usr/share/doc/README.redhat
! i686 /usr/share/doc/README.fedora
! i686 /usr/share/doc/README.Fedora  /etc/init.fedora
  src  /README.fedora
END_TESTS

for my $line (split "\n", $tests) {
    next if !$line;                             # Skip blank lines

    my @atoms = split ' ', $line;
    my $not;
    if ($atoms[0] eq '!') {
        $not = 1;
        shift @atoms;
    }

    my $test_name = $line;

    push @tests, {
        name  => $test_name,
        arch  => shift(@atoms),
        paths => \@atoms,
        fail  => $not,
    };
}

#use Data::Dumper;print Dumper(\@tests);exit 0;

plan tests => 3 + @tests;

# Pass 2: do the tests
my $tempdir = tempdir("t-Manifest.XXXXXX", CLEANUP => !$ENV{DEBUG});

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::RPM'                  or exit;
use_ok 'RPM::Grill::Plugin::Manifest'     or exit;


package RPM::Grill::RPM;
use subs qw(nvr);
package RPM::Grill;
use subs qw(major_release);
package main;

# Set a fake NVR
{
    no warnings 'redefine';
    *RPM::Grill::RPM::nvr = sub {
        return "1.el7";
    };
    *RPM::Grill::major_release = sub {
        return "RHEL7";
    };
}


for my $t (@tests) {
    my $expected_gripes;
    if ($t->{fail}) {
        my @paths = @{$t->{paths}};

        my @g = map { +{
            arch       => $t->{arch},
            subpackage => 'mypkg',
            code       => 'FedoraInFilename',
            diag       => "Filenames should not include \'Fedora\'",
            context    => { path => $_ },
        } } @paths;

        $expected_gripes = { Manifest => [ @g ] };
    }

    # invoke
    my $temp_subdir = make_tempdir( $t->{arch}, @{$t->{paths}} );
    my $obj = RPM::Grill->new( $temp_subdir );

    bless $obj, 'RPM::Grill::Plugin::Manifest';

    $obj->analyze;

    eq_or_diff $obj->{gripes}, $expected_gripes, $t->{name};
}

###############################################################################
# BEGIN helper

sub make_tempdir {
    my $arch = shift;

    use feature 'state';
    state $i = 0;

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i++);
    mkdir $temp_subdir, 02755
        or die "mkdir $temp_subdir: $!\n";

    for my $f (@_) {
        # Make the path
        mkpath "$temp_subdir/$arch/mypkg/payload$f", 0, 02755;

        # Create rpm.rpm
        open OUT, '>', "$temp_subdir/$arch/mypkg/rpm.rpm"
            or die "open rpm.rpm: $!";
        close OUT;

        # Append to RPM.per_file_metadata. Note that the fields in the
        # here-document are separated by ONE TAB
        my $per_file = "$temp_subdir/$arch/mypkg/RPM.per_file_metadata";
        open OUT, '>>', $per_file or die;
        print OUT <<"END_METADATA";
0000000000000	-rwxr-xr-x	root	root	0	(none)	$f
END_METADATA
        close OUT or die;
    }

    return $temp_subdir;
}
