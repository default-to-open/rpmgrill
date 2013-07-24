# -*- perl -*-
#
# Tests for the VirusCheck plugin
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath);
use File::Temp                  qw(tempdir);

#
# Read in tests from the DATA section below.
#
my @tests;
my $current_file;
my $delimiter;
while (my $line = <DATA>) {
    chomp $line;

    next if $line =~ /^\s*#/;           # Skip comment lines

    # Line of dashes: new test
    if ($line =~ /^-{10,}$/) {
        push @tests, {
            name         => sprintf("[unnamed test %d]", scalar(@tests)),
            arch         => 'noarch',
            build_log    => '',
            gripe_string => '',
        };
    }
    # Leading '>>' : metadata indicating test results
    elsif ($line =~ /^>>\s*(\S+)\s*=\s*(.*)/) {
        $tests[-1]->{$1} = $2;
    }

    # /usr/bin/myfile = <<END
    elsif ($line =~ m{^(/\S+)\s*=\s*<<(\S+)$}) {
        ($current_file, $delimiter) = ($1, $2);
        $tests[-1]->{files}{$current_file} = '';
    }
    elsif ($delimiter) {
        if ($line eq $delimiter) {
            undef $delimiter;
        }
        else {
            $tests[-1]->{files}{$current_file} .= $line . "\n";
        }
    }

    # -| blah blah : what we expect to see from the gripe
    elsif ($line =~ /^-\|(.*)/) {
        $tests[-1]->{gripe_string} .= $1;
    }
    elsif ($line =~ /\S/) {
        # FIXME
        warn "FIXME: $line";
    }
}

# Tests 1-2 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::Plugin::VirusCheck'   or exit;

# Create a temporary directory based on our name.
(my $ME = $0) =~ s|^.*/||;
my $tempdir = tempdir( "$ME.XXXXXX", CLEANUP => !$ENV{DEBUG} );

for my $t (@tests) {
    # Create a hierarchy
    my $name = $t->{name};

    my $d = "$tempdir/$name/noarch/mypkg/payload";
    mkpath $d, 0, 02755;

    open OUT, '>', "$tempdir/$name/noarch/mypkg/rpm.rpm";
    close OUT;

    # Create each file
    if (my $files = $t->{files}) {
        for my $f (sort keys %$files) {
            $f =~ m{^/(.*)/(.*)$}
                or die;
            my ($dirname, $basename) = ($1, $2);
            mkpath "$d/$dirname", 0, 02755;
            open OUT, '>', "$d/$dirname/$basename" or die;
            print OUT $files->{$f};
            close OUT or die;
        }
    }

    my $obj = RPM::Grill->new( "$tempdir/$name" );
    bless $obj, 'RPM::Grill::Plugin::VirusCheck';
    eval { $obj->analyze() };
    if ($@) {
        fail "$t->{name} : ERROR: $@";
    }
    else {
        # FIXME: check the gripes
        my $expected_gripes = eval $t->{gripe_string};
        die "eval failed:\n\n $t->{gripe_string} \n\n  $@\n"     if $@;

        # Any gripes?  Set arch and subpkg, to minimize clutter below
        if ($expected_gripes) {
            for my $g (@{$expected_gripes->{VirusCheck}}) {
                $g->{arch}       = 'noarch';
                $g->{subpackage} = 'mypkg';
            }
        }

        # Check for clamscan --version. Remove it from the results (because
        # we can't possibly hardcode a match for it in our expectations)
        # but at least perform some sanity checks on it.
        if ($obj->{gripes}) {
            if (my $gripes = $obj->{gripes}{VirusCheck}) {
                for my $g (@$gripes) {
                    if ($g->{diag} =~ s/\s+\(\ClamAV\s+(.*)\)$//) {
                        my $v = $1;

                        # e.g. '0.97.3/15064/Wed Jun 20 13:03:45 2012'
                        $v =~ m|^\d+(\.\d+)+/\d+/[\w\s:]+\s\d+$|
                            or fail "Suspicious ClamAV version string '$v'";
                    }
                    else {
                        fail "Diag message '$g->{diag}' does not include ClamAV version string";
                    }
                }
            }
        }

        eq_or_diff $obj->{gripes}, $expected_gripes, $t->{name};
    }
}


done_testing();


# FIXME: embedding virus strings below will cause clamscan to complain
# about this file.

__DATA__

-------------------------------------------------------------------------------
>> name = nogripes

-------------------------------------------------------------------------------
>> name = clamav-testdata

/usr/bin/myfile = <<END
From test@example.com  Thu Jul 31 13:51:21 2008
From: test@example.com
MIME-Version: 1.0
Content-Type: Application/Octet-Stream; name="clam.exe"
Content-Transfer-Encoding: x-uuencode

begin 644 clam.exe
M35I0``(````$``\`__\``+@````A````0``:````````````````````````
M``````````````````````$``+MQ$$``,\!04(OS4U-0L"E`,`1FK'GYNC$`
M>`VM4/]F<`X?OC$`Z>7_M`G-(;1,S2%B#`H!`G!V%P(>3@P$+]K,$```````
M````````````P!```(`0``````````````````#:$```]!``````````````
M````````````````2T523D5,,S(N1$Q,``!%>&ET4')O8V5S<P!54T52,S(N
M1$Q,`$-,04UE<W-A9V5";WA!`.80````````/S\_/U!%``!,`0$`84-A0@``
M````````X`".@0L!`AD`!`````8```````!`$````!```$```````$```!``
M```"```!``````````,`"@```````"`````$`````````@``````$```(```
M```0```0````````$```````````````A!```(``````````````````````
M````````````````````````````````````````````````````````````
M````````````````````````````````````````````````````````````
M````````````6T-,04U!5ET`$````!`````"```!````````````````````
$````P```
`
e
END

-| { VirusCheck => [
-|  { code    => 'ClamAV',
-|    diag    => 'ClamAV <b>ClamAV-Test-File</b> subtest triggered',
-|    context => { path => '/usr/bin/myfile' },
-|  } ] }


-------------------------------------------------------------------------------
>> name = eicar

/usr/bin/myfile = <<END
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
END

-| { VirusCheck => [
-|  { code    => 'ClamAV',
-|    diag    => 'ClamAV <b>Eicar-Test-Signature</b> subtest triggered',
-|    context => { path => '/usr/bin/myfile' },
-|  } ] }

-------------------------------------------------------------------------------
>> name = eicar-multiple

/usr/bin/myfile1 = <<END
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
END

/usr/bin/myfile2 = <<END
X5O!P%@AP[4\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*
END

# FIXME FIXME FIXME: how does clamav do ordering? file2 comes before file1,
# but can we rely on that?

-| { VirusCheck => [
-|  { code    => 'ClamAV',
-|    diag    => 'ClamAV <b>Eicar-Test-Signature</b> subtest triggered',
-|    context => { path => '/usr/bin/myfile1' },
-|  },
-|  { code    => 'ClamAV',
-|    diag    => 'ClamAV <b>Eicar-Test-Signature</b> subtest triggered',
-|    context => { path => '/usr/bin/myfile2' },
-|  } ] }
