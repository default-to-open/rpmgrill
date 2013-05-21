#!/usr/bin/perl

use strict;
use warnings;

use Test::More;
use Test::Differences;

use Digest::SHA1                qw(sha1_hex);
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
            gripe_string => '',
        };

        # "this-is-a-test" => "this is a test"
        $tests[-1]->{name} =~ tr/-/ /;
    }

    # Leading '>>' : metadata indicating test setup
    #                       1   1    2   2   3   3     4     4 5     5 6  6 7     7
    elsif ($line =~ m{^>>\s+(-\S+)\s+(\w+)\s+(\w+)\s+/?([^/]+)/([^/]+)/(.*)/([^/\s]+)\s+(.*)$}) {
        push @{ $tests[-1]->{files} }, {
            mode        => $1,
            user        => $2,
            group       => $3,

            arch        => $4,
            subpackage  => $5,
            dirname     => $6,
            basename    => $7,
            path        => "$4/$5/payload/$6/$7",
            fulldirname => "$4/$5/payload/$6",
            rootpath    => "/$6/$7",
            color       => $8,

            text        => '',
        };
    }

    # Leading '-|' : metadata indicating expected gripe results
    elsif ($line =~ /^-\|(.*)/) {
        $tests[-1]->{gripe_string} .= $1;
    }
    # Comments
    elsif ($line =~ /^\#/) {
        ;
    }
    # Text for a file
    elsif ($line) {
        $tests[-1]->{files}->[-1]->{text} .= $line . "\n";

        if ($line =~ /^ELF/) {
            $tests[-1]->{files}->[-1]->{_file_type} = 'ELF';
        }
    }
}

#use Data::Dumper;print Dumper(\@tests);exit 0;

plan tests => 3 + @tests;

# Pass 2: do the tests
my $tempdir = tempdir("t-Multilib.XXXXXX", CLEANUP => !$ENV{DEBUG});

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::RPM'                  or exit;
use_ok 'RPM::Grill::Plugin::Multilib'     or exit;


for my $i (0 .. $#tests) {
    my $t = $tests[$i];

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    mkdir $temp_subdir, 02755
        or die "mkdir $temp_subdir: $!\n";

    my %arch;
    my %subpackage;

    # Create all the needed files (includes writing them to RPM.per_file_etc)
    for my $f (@{ $t->{files} }) {
        mkpath "$temp_subdir/$f->{fulldirname}", 0, 02755;
        open OUT, '>', "$temp_subdir/$f->{path}" or die;
        print OUT $f->{text};
        close OUT or die;
        chmod RPM::Grill::RPM::Files::_numeric_mode($f->{mode}),
            "$temp_subdir/$f->{path}";

        # Create rpm.rpm
        $f->{path} =~ m{^([^/]+/[^/]+)/} or die "foo: $f->{path}";
        open OUT, '>', "$temp_subdir/$1/rpm.rpm" or die "open $1: $!";
        close OUT;

        # Append to RPM.per_file_metadata
        my $per_file = join('/', $temp_subdir, $f->{arch},
                            $f->{subpackage}, 'RPM.per_file_metadata');
        open OUT, '>>', $per_file or die;
        print OUT join("\t",
                       sha1_hex($f->{text}),
                       $f->{mode},
                       'root',
                       'root',
                        "0",
                       $f->{color},
                       $f->{rootpath},
                    ), "\n";
        close OUT or die;

        $arch{ $f->{arch} }++;
        $subpackage{ $f->{subpackage} }++;
    }

    my $expected_gripes;
    if ($t->{gripe_string}) {
        $expected_gripes = eval "{ Multilib => [ $t->{gripe_string} ] }";
        die "eval failed:\n\n $t->{gripe_string} \n\n  $@\n"     if $@;
    }

    # invoke
    my $obj = RPM::Grill->new( $temp_subdir );

    bless $obj, 'RPM::Grill::Plugin::Multilib';

    $obj->analyze;

    eq_or_diff $obj->{gripes}, $expected_gripes, $t->{name};
}

__END__

-------------no-difference--------------------------------


>> -rwxr-xr-x  root  root  /i386/mypkg/usr/bin/foo      (none)
aaaa

>> -rwxr-xr-x  root  root  /x86_64/mypkg/usr/bin/foo    (none)
aaaa

>> -rwxr-xr-x  root  root  /s390/mypkg/usr/bin/foo      (none)
aaaa

>> -rwxr-xr-x  root  root  /s390x/mypkg/usr/bin/foo     (none)
aaaa

>> -rwxr-xr-x  root  root  /ppc/mypkg/usr/bin/foo       (none)
aaaa

>> -rwxr-xr-x  root  root  /ppc64/mypkg/usr/bin/foo     (none)
aaaa


-------------diff-one-arch--------------------------------


>> -rwxr-xr-x  root  root  /i386/mypkg/usr/bin/myscript      (none)
aaaa

>> -rwxr-xr-x  root  root  /x86_64/mypkg/usr/bin/myscript    (none)
bbbb

>> -rwxr-xr-x  root  root  /s390/mypkg/usr/bin/myscript      (none)
aaaa

>> -rwxr-xr-x  root  root  /s390x/mypkg/usr/bin/myscript     (none)
aaaa

>> -r--r--r--  root  root  /src/mypkg/./foo.spec (none)

-|  { arch       => 'x86_64',
-|    code       => 'MultilibMismatch',
-|    diag       => 'Files differ: {i386,x86_64}/usr/bin/myscript',
-|  }

-------------using-filter-setup--------------------------------

>> -rwxr-xr-x  root  root  /i386/mypkg/usr/bin/myscript      (none)
aaaa

>> -rwxr-xr-x  root  root  /x86_64/mypkg/usr/bin/myscript    (none)
bbbb

>> -rwxr-xr-x  root  root  /s390/mypkg/usr/bin/myscript      (none)
aaaa

>> -rwxr-xr-x  root  root  /s390x/mypkg/usr/bin/myscript     (none)
aaaa

>> -r--r--r--  root  root  /src/mypkg/./mypkg.spec (none)
hi there
%filter_setup

-|  { arch       => 'x86_64',
-|    code       => 'MultilibMismatch',
-|    diag       => 'Files differ: {i386,x86_64}/usr/bin/myscript',
-|  },
-|  {
-|    code       => 'DepGenDisabled',
-|    diag       => "Multilib errors may be due to the dependency generator being disabled",
-|    context    => {
-|                  path   => "mypkg.spec",
-|                  lineno => '2',
-|                  excerpt => [ '%filter_setup' ],
-|    }
-|  }





-------------binary-diff-ok------------------------------


>> -rwxr-xr-x  root  root  /i386/mypkg/usr/bin/mybin      1
aaaa

>> -rwxr-xr-x  root  root  /x86_64/mypkg/usr/bin/mybin    2
bbbb

>> -rwxr-xr-x  root  root  /s390/mypkg/usr/bin/mybin      1
aaaa

>> -rwxr-xr-x  root  root  /s390x/mypkg/usr/bin/mybin     2
aaaa
