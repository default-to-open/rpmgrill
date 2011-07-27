#!/usr/bin/perl

use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath rmtree);
use File::Temp                  qw(tempdir);
use File::Basename              qw(basename);

# pass 1: read DATA
my @tests;
while (my $line = <DATA>) {
    chomp $line;

    # Line of dashes: new test
    if ($line =~ /^--/) {
        my $dashcount = ($line =~ tr/-/-/);
        $dashcount > 20
            or die "Internal error: Cannot grok test line '$line'";
        $line =~ /-([^-].*[^-])-/
            or die "Internal error: no test name in '$line'";
        push @tests, {
            name         => $1,
            files        => [],
            gripes       => undef,
        };

        # "this-is-a-test" => "this is a test"
        $tests[-1]->{name} =~ tr/-/ /;
    }

    # Leading slash : new file
    #                     1     1  2     2 3     3 4  4 5       5
    elsif ($line =~ m{^\s*(\!\s+)?/([^/]+)/([^/]+)/(.*)/([^/\s]+)\s*}) {
        push @{ $tests[-1]->{files} }, {
            arch        => $2,
            subpackage  => $3,
            dirname     => $4,
            basename    => $5,
            path        => "$2/$3/payload/$4/$5",
            fulldirname => "$2/$3/payload/$4",
            rootpath    => "/$4/$5",
        };

        if ($1) {
            $tests[-1]->{gripes} ||= { Manifest => [] };
            push @{ $tests[-1]->{gripes}->{Manifest} }, {
                arch => $2,
                subpackage => $3,
                code       => 'NonFHS',
                diag       => "FHS-protected directory <tt>/$4/$5</tt>",
            };
        }
    }

    # Comments
    elsif ($line =~ /^\#/) {
        ;
    }
    # Text for a file
    elsif ($line) {
        die "Cannot grok: '$line'\n";
        $tests[-1]->{files}->[-1]->{text} .= $line . "\n";
    }
}

#use Data::Dumper;print Dumper(\@tests);exit 0;

plan tests => 3 + @tests;

# Pass 2: do the tests
my $tempdir = tempdir("t-Multilib.XXXXXX", CLEANUP => !$ENV{DEBUG});

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::RPM'                  or exit;
use_ok 'RPM::Grill::Plugin::Manifest'     or exit;


for my $i (0 .. $#tests) {
    my $t = $tests[$i];

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    mkdir $temp_subdir, 02755
        or die "mkdir $temp_subdir: $!\n";

    # Create all the needed files (includes writing them to RPM.per_file_etc)
    for my $f (@{ $t->{files} }) {
        # Make the path to each file, then touch the file
        mkpath "$temp_subdir/$f->{fulldirname}", 0, 02755;
        open OUT, '>', "$temp_subdir/$f->{path}" or die;
        close OUT or die;

        # Create rpm.rpm
        $f->{path} =~ m{^([^/]+/[^/]+)/} or die "foo: $f->{path}";
        open OUT, '>', "$temp_subdir/$1/rpm.rpm" or die "open $1: $!";
        close OUT;

        # Append to RPM.per_file_metadata
        my $per_file = join('/', $temp_subdir, $f->{arch},
                            $f->{subpackage}, 'RPM.per_file_metadata');
        open OUT, '>>', $per_file or die;
        print OUT join("\t",
                       '0000000000000000000000000000',
                       '-rw-r--r--',
                       'root',
                       'root',
                        "0",
                       '(none)',
                       $f->{rootpath},
                    ), "\n";
        close OUT or die;
    }

    # invoke
    my $obj = RPM::Grill->new( $temp_subdir );

    bless $obj, 'RPM::Grill::Plugin::Manifest';

    $obj->analyze;

    eq_or_diff $obj->{gripes}, $t->{gripes}, $t->{name};
}

__END__

------no-problem-------------------

/i386/mypkg/usr/lib/mylib.a
/x86_64/mypkg/usr/lib/mylib.a

-----/usr/local-(2-arches)--------------------

! /i386/mypkg/usr/local/lib/mylib.a
! /x86_64/mypkg/usr/local/lib/mylib.a

-----------other---dirs-------------------

! /i386/mypkg/media/foo
! /i386/mypkg/home/sdfsdf
! /i386/mypkg/var/tmp
! /i386/mypkg/usr/tmp
