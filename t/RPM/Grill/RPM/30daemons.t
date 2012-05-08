# -*- perl -*-
#
# Tests for RPM::Grill::RPM::_find_daemon_files()
#
use strict;
use warnings;
use v5.10;

use Test::More;
use File::Path                  qw(mkpath);
use File::Temp                  qw(tempdir);

my @packages;
my $n_tests = 3;

while (my $line = <DATA>) {
    chomp $line;

    given ($line) {
        when (/^-{10,}\s+(.*)$/) {
            push @packages, bless {
                name  => $1,
                files => [],
                tests => [],
            }, 'RPM::Grill::RPM';
        }
        when (/^\s*$/) {
            # ignore blank lines
        }
        when (m{^(/\S+)(\s+\((.*)\))?$}) {
            # FIXME: flag for is_daemon
            push @{ $packages[-1]{files} }, bless {
                path    => $1,
                rpm     => $packages[-1],
                content => '',
                name    => $3 || 'no',
                _expected_is_daemon => defined($2) ? 1 : undef,
            }, 'RPM::Grill::RPM::Files';

            ++$n_tests;
        }

        when (m{^\s{2,}\|\s(.*)$}) {
            $packages[-1]{files}[-1]{content} .= $1 . "\n";
        }

        default {
            die "Cannot grok: '$line'";
        }
    }
}

plan tests => $n_tests;

use_ok 'RPM::Grill'                     or exit;
use_ok 'RPM::Grill::RPM'                or exit;
use_ok 'RPM::Grill::RPM::Files'         or exit;

my $tempdir = tempdir("t-RPM-Grill-RPM.XXXXXX", CLEANUP => !$ENV{DEBUG});

for my $i (0 .. $#packages) {
    # Make the test directory
    my $d = sprintf("%s/%02d", $tempdir, $i);
    mkpath $d, 0, 0700;

    my $p = $packages[$i];

    # Pass 1: create all the files
    for my $f (@{ $p->{files} }) {
        my $f_path = $f->{path};

        $f_path =~ m{^/(\S+)/([^/]+)$}
            or die "CANNOT HAPPEN! $f_path";
        mkpath "$d/$1", 0, 0700;
        open my $fh, '>', "$d$f_path"
            or die "Cannot create $d$f_path: $!";
        print { $fh } $f->{content};
        close $fh
            or die "Error writing $d$f_path: $!";

        $f->{extracted_path} = "$d$f_path";
    }

    # Pass 2: invoke the daemon finder
    $p->_find_daemon_files;

    # Pass 3: Make sure it marked all expected daemon files
    my $p_name = $p->{name};
    for my $f (@{ $p->{files} }) {
        my $name = sprintf("%02d[%-35s] %-20s (%s)", $i, $p_name, $f->{path}, $f->{name});
        $p_name = ' ' x length($p_name);

        is $f->{_is_daemon}, $f->{_expected_is_daemon}, $name;
    }
}

__END__

--------------- No daemons

/bin/foo

--------------- Same as init file

/bin/foo (yes)
/etc/init.d/foo

--------------- Init file + d

/bin/food (yes)
/etc/init.d/foo

--------------- Init file has "d", bin file doesn't

/bin/foo
/etc/init.d/food

--------------- testing init file under rc.d

/bin/foo (yes)
/etc/rc.d/init.d/foo

--------------- init file contents

/bin/foo   (yes)
/etc/rc.d/init.d/bar
  | hi there
  |  [ -x /bin/foo ] || exit 5

--------------- init file is in comments

/bin/foo
/etc/rc.d/init.d/bar
  | hi there
  | # [ -x /bin/foo ] || exit 5

--------------- systemd-style

/bin/foo (yes)
/sbin/foo
/usr/sbin/foo
/usr/bin/food
/lib/systemd/foo/bar
  | ExecStart=-/bin/foo
