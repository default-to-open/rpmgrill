# -*- perl -*-

use strict;
use warnings;

use Test::More;
use Test::Differences;

use Encode              qw(from_to);
use File::Slurp         qw(read_dir read_file);

#
# Pass 1: find tests
#
our @tests;
BEGIN {
    (my $test_subdir = $0) =~ s|\.t$|.d|
        or die "Internal error: test name $0 doesn't end in .t";

    for my $spec (sort grep { /\.spec$/ } read_dir($test_subdir)) {
        my $t = { name => $spec, path => "$test_subdir/$spec" };

        # Read the .expect file
        (my $expect = $spec) =~ s/\.spec$/.expect/;

        if (-e "$test_subdir/$expect") {
            $t->{expect} = eval read_file("$test_subdir/$expect");
            die "FIXME: Error reading $test_subdir/$expect: $@"     if $@;
        }

        push @tests, $t;
    }

    plan tests => 3 + @tests;
}


# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                     or exit;
use_ok 'RPM::Grill::RPM::SpecFile'      or exit;
use_ok 'RPM::Grill::Plugin::RpmScripts' or exit;

#
# Run tests
#
for my $t (@tests) {
    my $spec_obj = RPM::Grill::RPM::SpecFile->new( $t->{path} );

    my $grill = bless { specfile => $spec_obj },
        'RPM::Grill::Plugin::RpmScripts';
    $spec_obj->{grill} = $grill;

    $grill->analyze;

    my $actual_gripes = $grill->{gripes};

    # Host system may have different version of 'setup' package
    if ($actual_gripes) {
        for my $href ($actual_gripes, $t->{expect}) {
            for my $gripe (@{ $href->{RpmScripts} }) {
                $gripe->{diag} =~ s{/setup-[\d.]+/}{/setup-[v]/}g;
            }
        }
    }

    # For debugging
    if ($actual_gripes && !$t->{expect}) {
        use Data::Dumper;$Data::Dumper::Indent = 1; print Dumper($actual_gripes); exit;
    }

    unified_diff;
    eq_or_diff $actual_gripes, $t->{expect}, $t->{name};
}

done_testing;

__DATA__

Examples from recent rpmdiff runs

  https://errata.devel.redhat.com/rpmdiff/show/50029?result_id=754412
    jbossas-web-5.1.1-6.ep5.el4
    Invocation of <tt>useradd</tt> without specifying a UID on noarch:
    Invocation of useradd with a shell other than /sbin/nologin on noarch

  https://errata.devel.redhat.com/rpmdiff/show/50024?result_id=754257
    abrt-1.1.16-3.el6
    Invocation of useradd with a UID greater than 100 on all architectures

  https://errata.devel.redhat.com/rpmdiff/show/50008?result_id=753741
    kvm-83-230.el5
    Invocation of useradd without specifying a UID on x86_64:

  https://errata.devel.redhat.com/rpmdiff/show/50125?result_id=757324
    sesame-0.10-1.el6
    Invocation of useradd without specifying a UID on i686 x86_64:

  https://errata.devel.redhat.com/rpmdiff/show/50126?result_id=757352
    wallaby-0.10.5-3.el6
    Invocation of useradd without specifying a UID on noarch

  https://errata.devel.redhat.com/rpmdiff/show/50095?result_id=756482
    luci-0.22.2-14.el6_0.2
    Invocation of useradd with a UID greater than 100 on i686 x86_64:

  https://errata.devel.redhat.com/rpmdiff/show/50094?result_id=756311
    xorg-x11-6.8.2-1.EL.68
    Invocation of useradd with a shell other than /sbin/nologin

#-------------------------------------------------------------------------------
# expect: xx
/usr/sbin/useradd -c "Privilege-separated SSH" -u 74   \
	-s /sbin/nologin -r -d /var/empty/sshd sshd 2> /dev/null ||


#-------------------------------------------------------------------------------
# expect: xx
#
# this is: x86_64/qpid-cpp-server
preinstall scriptlet (using /bin/sh):
getent group qpidd >/dev/null || groupadd -r qpidd
getent passwd qpidd >/dev/null || \
  useradd -r -M -g qpidd -d /var/lib/qpidd -s /sbin/nologin \
    -c "Owner of Qpidd Daemons" qpidd
exit 0
postinstall scriptlet (using /bin/sh):
# This adds the proper /etc/rc*.d links for the script
/sbin/chkconfig --add qpidd
/sbin/ldconfig
preuninstall scriptlet (using /bin/sh):
# Check that this is actual deinstallation, not just removing for upgrade.
if [ $1 = 0 ]; then
        /sbin/service qpidd stop >/dev/null 2>&1 || :
        /sbin/chkconfig --del qpidd
fi
postuninstall scriptlet (using /bin/sh):
if [ "$1" -ge "1" ]; then
        /sbin/service qpidd condrestart >/dev/null 2>&1 || :
fi
/sbin/ldconfig
/usr/sbin/semodule -r qpidd


# === Package: qpid-cpp-server-devel ===
