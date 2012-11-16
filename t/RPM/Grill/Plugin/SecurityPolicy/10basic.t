# -*- perl -*-
#
# tests for the SecurityPolicy module
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath rmtree);
use File::Temp                  qw(tempdir);

# pass 1: read DATA
my @tests;
while (my $line = <DATA>) {
    next if $line =~ /^\s*\#/;                  # Skip comment lines

    if ($line =~ /^-{5,}([^-].*[^-])-+$/) {
        push @tests, { name => $1 };
    }
    elsif (@tests) {
        if (exists $tests[-1]->{expect}) {
            $tests[-1]->{expect} .= $line;
        }
        elsif ($line =~ /^\.\.+expect:$/) {
            $tests[-1]->{expect} = '';
        }
        else {
            $tests[-1]->{setup} .= $line;
        }
    }
    elsif ($line =~ /\S/) {
        die "Cannot grok '$line'";
    }
}

#use Data::Dumper;print Dumper(\@tests);exit 0;

plan tests => 4 + @tests;

# Pass 2: do the tests
my $tempdir = tempdir("t-SecurityPolicy.XXXXXX", CLEANUP => !$ENV{DEBUG});

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                          or exit;
use_ok 'RPM::Grill::RPM'                     or exit;
use_ok 'RPM::Grill::Plugin::SecurityPolicy'  or exit;
ok(require("t/lib/FakeTree.pm"), "loaded FakeTree.pm") or exit;

for my $i (0 .. $#tests) {
    my $t = $tests[$i];

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    my $g = FakeTree::make_fake_tree( $temp_subdir, $t->{setup} );

    my $expected_gripes;
    if ($t->{expect}) {
        $expected_gripes = eval "{ SecurityPolicy => [ $t->{expect} ] }";
        die "eval failed:\n\n $t->{gripe_string} \n\n  $@\n"     if $@;
    }

    bless $g, 'RPM::Grill::Plugin::SecurityPolicy';

    $g->analyze();

    eq_or_diff $g->{gripes}, $expected_gripes, $t->{name};
}


__DATA__

---------no-warning---------------------------------------------------------

>> -rw-r--r--  root root 0 /noarch/mypkg/usr/share/polkit-1/actions/abrt_polkit.policy
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
 "-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
 "http://www.freedesktop.org/standards/PolicyKit/1.0/policyconfig.dtd">

<!--
PolicyKit policy definitions for ABRT

Copyright (c) 2012 ABRT Team <crash-catcher@fedorahosted.com>

-->

<policyconfig>
  <vendor>The ABRT Team</vendor>
  <vendor_url>https://fedorahosted.org/abrt/</vendor_url>

  <!-- by default only root can see other users problems -->
  <action id="org.freedesktop.problems.getall">
    <description>Get problems from all users</description>
    <message>Reading others problems requires authentication</message>
    <defaults>
      <allow_any>no</allow_any>
      <allow_active>auth_admin_keep</allow_active>
      <allow_inactive>no</allow_inactive>
    </defaults>
  </action>

</policyconfig>


---------actual-warning-----------------------------------------------------

>> -rw-r--r--  root root 0 /noarch/system-config-users/usr/share/polkit-1/actions/org.fedoraproject.config.users.policy
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE policyconfig PUBLIC
"-//freedesktop//DTD PolicyKit Policy Configuration 1.0//EN"
"http://www.freedesktop.org/standards/PolicyKit/1/policyconfig.dtd">
<policyconfig>

 <vendor>System Config Users</vendor>
 <vendor_url>http://fedorahosted.org/system-config-users</vendor_url>

 <action id="org.fedoraproject.config.users.pkexec.run">
    <description>Run System Config Users</description>
    <message>Authentication is required to run system-config-users</message>
    <icon_name>system-users</icon_name>
    <defaults>
     <allow_any>no</allow_any>
     <allow_inactive>no</allow_inactive>
     <allow_active>auth_self</allow_active>
    </defaults>
    <annotate key="org.freedesktop.policykit.exec.path">/usr/share/system-config-users/system-config-users.py</annotate>
    <annotate key="org.freedesktop.policykit.exec.allow_gui">true</annotate>
 </action>
</policyconfig>

...expect:

 { arch       => 'noarch',
   subpackage => 'system-config-users',
   code       => 'PolkitSelf',
   diag       => 'Suspicious polkit authorization result (any user accepted)',
   context    => { path => '/usr/share/polkit-1/actions/org.fedoraproject.config.users.policy',
                   excerpt => ['&lt;action id=&quot;org.fedoraproject.config.users.pkexec.run&quot;&gt;'],
               },
 }
