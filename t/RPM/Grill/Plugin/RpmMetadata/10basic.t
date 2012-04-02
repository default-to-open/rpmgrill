# -*- perl -*-
#
# tests for RPM metadata
#
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
            text         => '',
            gripe_string => '',
        };

        # "this-is-a-test" => "this is a test"
        $tests[-1]->{name} =~ tr/-/ /;
    }

    # Leading '-|' : metadata indicating expected gripe results
    elsif ($line =~ /^-\|(.*)/) {
        $tests[-1]->{gripe_string} .= $1;
    }
    # Comments
    elsif ($line =~ /^\#/) {
        ;
    }
    # Text for an RPM.metadata file
    elsif ($line) {
        $tests[-1]->{text} .= $line . "\n";
    }
}

#use Data::Dumper;print Dumper(\@tests);exit 0;

plan tests => 2 + @tests;

# Pass 2: do the tests
my $tempdir = tempdir("t-RpmMetadata.XXXXXX", CLEANUP => 1);

# Tests 1-2 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::Plugin::RpmMetadata'  or exit;

for my $i (0 .. $#tests) {
    my $t = $tests[$i];

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    mkdir $temp_subdir, 02755
        or die "mkdir $temp_subdir: $!\n";

    # Get package name
    $t->{text} =~ /^Name\s*:\s*(\S+)/m
        or die "No 'Name' (pkg name) in $t->{name}";
    my $pkg = $1;

    # Create metadata file
    mkpath "$temp_subdir/src/$pkg", 0, 02755;
    my $metadata = "$temp_subdir/src/$pkg/RPM.metadata";
    open  METADATA, '>', $metadata      or die "Cannot create $metadata: $!";
    print METADATA $t->{text};
    close METADATA                      or die "Error writing $metadata: $!";

    open  RPM, '>', "$temp_subdir/src/$pkg/rpm.rpm";
    close RPM;

    my $expected_gripes;
    if ($t->{gripe_string}) {
        $expected_gripes = eval "{ RpmMetadata => [ $t->{gripe_string} ] }";
        die "eval failed:\n\n $t->{gripe_string} \n\n  $@\n"     if $@;
    }

    # invoke
    my $obj = RPM::Grill->new( $temp_subdir );
    bless $obj, 'RPM::Grill::Plugin::RpmMetadata';

    $obj->analyze();

    eq_or_diff $obj->{gripes}, $expected_gripes, $t->{name};

}


__DATA__

---------metadata-ok-----------------------------------------------------------

Name        : git-daemon           Relocations: (not relocatable)
Version     : 1.7.1                     Vendor: Red Hat, Inc.
Release     : 2.el6_0.1             Build Date: Thu 16 Dec 2010 07:25:20 AM MST
Install Date: (not installed)       Build Host: x86-010.build.bos.redhat.com
Group       : Development/Tools     Source RPM: git-1.7.1-2.el6_0.1.src.rpm
Size        : 499329                   License: GPLv2
Signature   : (none)
Packager    : Red Hat, Inc. <http://bugzilla.redhat.com/bugzilla>
URL         : http://git-scm.com/
Summary     : Git protocol dæmon
Description :
The git dæmon for supporting git:// access to git repositories

---------internal-host----------------------------------------------------------

Name        : vdsm22               Relocations: (not relocatable)
Version     : 4.5                       Vendor: Red Hat, Inc.
Release     : 63.10.el5_6           Build Date: Wed 12 Jan 2011 05:44:46 AM MST
Install Date: (not installed)       Build Host: x86-005.build.bos.redhat.com
Group       : Applications/System   Source RPM: (none)
Size        : 1454223                  License: GPLv2+
Signature   : (none)
Packager    : Red Hat, Inc. <http://bugzilla.redhat.com/bugzilla>
URL         : http://git.engineering.redhat.com/?p=users/bazulay/vdsm.git
Summary     : Virtual Desktop Server Manager
Description :
The VDSM service is required by a RHEV Manager to manage RHEV Hypervisors
and Red Hat Enterprise Linux hosts. VDSM manages and monitors the host's
storage, memory and networks as well as virtual machine creation, other host
administration tasks, statistics gathering, and log collection.

-|  { arch       => 'src',
-|    subpackage => 'vdsm22',
-|    code       => 'HostnameLeak',
-|    diag       => 'Host <var>git.engineering.redhat.com</var> appears to be internal-only.',
-|    context    => { path => '[RPM metadata]',
-|                    excerpt => ['URL: http://git.engineering.redhat.com/?p=users/bazulay/vdsm.git'] },
-|  }


---------nonexistent-host------------------------------------------------------

Name        : mypkg                Relocations: (not relocatable)
Version     : 4.5                       Vendor: Red Hat, Inc.
Release     : 63.10.el5_6           Build Date: Wed 12 Jan 2011 05:44:46 AM MST
Install Date: (not installed)       Build Host: x86-005.build.bos.redhat.com
Group       : Applications/System   Source RPM: (none)
Size        : 1454223                  License: GPLv2+
Signature   : (none)
Packager    : Red Hat, Inc. <http://bugzilla.redhat.com/bugzilla>
URL         : http://sdfsdf.sdfsdf.sdfsdf.sdfsdf/sdfsdf
Summary     : Virtual Desktop Server Manager
Description :
Blah blah

-|  { arch       => 'src',
-|    subpackage => 'mypkg',
-|    code       => 'NoSuchHost',
-|    diag       => 'Host <var>sdfsdf.sdfsdf.sdfsdf.sdfsdf</var> does not resolve.',
-|    context    => { path => '[RPM metadata]',
-|                    excerpt => ['URL: http://sdfsdf.sdfsdf.sdfsdf.sdfsdf/sdfsdf'] },
-|  }


---------WrongVendor-1----------------------------------------------------

Name        : mypkg                Relocations: (not relocatable)
Version     : 4.5                       Vendor: Not Red Hat, Inc.
Release     : 63.10.el5_6           Build Date: Wed 12 Jan 2011 05:44:46 AM MST
Install Date: (not installed)       Build Host: x86-005.build.bos.redhat.com
Group       : Applications/System   Source RPM: (none)
Size        : 1454223                  License: GPLv2+
Signature   : (none)
Packager    : Red Hat, Inc. <http://bugzilla.redhat.com/bugzilla>
Summary     : Virtual Desktop Server Manager
Description :
Blah blah

-|  { arch       => 'src',
-|    subpackage => 'mypkg',
-|    code       => 'WrongVendor',
-|    diag       => 'Vendor field must be "Red Hat, Inc."',
-|    context    => { path => '[RPM metadata]',
-|                    excerpt => ['Vendor: Not Red Hat, Inc.'] },
-|  }

---------WrongVendor-2-----------------------------------------------------

Name        : mypkg                Relocations: (not relocatable)
Version     : 4.5                       Vendor: Red Hat, Inc
Release     : 63.10.el5_6           Build Date: Wed 12 Jan 2011 05:44:46 AM MST
Install Date: (not installed)       Build Host: x86-005.build.bos.redhat.com
Group       : Applications/System   Source RPM: (none)
Size        : 1454223                  License: GPLv2+
Signature   : (none)
Packager    : Red Hat, Inc. <http://bugzilla.redhat.com/bugzilla>
Summary     : Virtual Desktop Server Manager
Description :
Blah blah

-|  { arch       => 'src',
-|    subpackage => 'mypkg',
-|    code       => 'WrongVendor',
-|    diag       => 'Vendor field must be "Red Hat, Inc." (the dot matters)',
-|    context    => { path => '[RPM metadata]',
-|                    excerpt => ['Vendor: Red Hat, Inc'] },
-|  }

---------WrongVendor-3-----------------------------------------------------

Name        : mypkg                Relocations: (not relocatable)
Version     : 4.5                       Vendor: Red Hat
Release     : 63.10.el5_6           Build Date: Wed 12 Jan 2011 05:44:46 AM MST
Install Date: (not installed)       Build Host: x86-005.build.bos.redhat.com
Group       : Applications/System   Source RPM: (none)
Size        : 1454223                  License: GPLv2+
Signature   : (none)
Packager    : Red Hat, Inc. <http://bugzilla.redhat.com/bugzilla>
Summary     : Virtual Desktop Server Manager
Description :
Blah blah

-|  { arch       => 'src',
-|    subpackage => 'mypkg',
-|    code       => 'WrongVendor',
-|    diag       => 'Vendor field must be "Red Hat, Inc." (missing "Inc.")',
-|    context    => { path => '[RPM metadata]',
-|                    excerpt => ['Vendor: Red Hat'] },
-|  }

---------VendorMissingDot---------------------------------------------------

Name        : mypkg                Relocations: (not relocatable)
Version     : 4.5                       Vendor: Red Hat, Inc
Release     : 63.10.el5_6           Build Date: Wed 12 Jan 2011 05:44:46 AM MST
Install Date: (not installed)       Build Host: x86-005.build.bos.redhat.com
Group       : Applications/System   Source RPM: (none)
Size        : 1454223                  License: GPLv2+
Signature   : (none)
Packager    : Red Hat, Inc. <http://bugzilla.redhat.com/bugzilla>
Summary     : Virtual Desktop Server Manager
Description :
Blah blah

-|  { arch       => 'src',
-|    subpackage => 'mypkg',
-|    code       => 'WrongVendor',
-|    diag       => 'Vendor field must be "Red Hat, Inc." (the dot matters)',
-|    context    => { path => '[RPM metadata]',
-|                    excerpt => ['Vendor: Red Hat, Inc'] },
-|  }

---------BadBuildHost------------------------------------------------------

Name        : mypkg                Relocations: (not relocatable)
Version     : 4.5                       Vendor: Red Hat, Inc.
Release     : 63.10.el5_6           Build Date: Wed 12 Jan 2011 05:44:46 AM MST
Install Date: (not installed)       Build Host: gandalf.fedora.org
Group       : Applications/System   Source RPM: (none)
Size        : 1454223                  License: GPLv2+
Signature   : (none)
Packager    : Red Hat, Inc. <http://bugzilla.redhat.com/bugzilla>
Summary     : Virtual Desktop Server Manager
Description :
Blah blah

-|  { arch       => 'src',
-|    subpackage => 'mypkg',
-|    code       => 'BadBuildHost',
-|    diag       => 'Build Host is not within .redhat.com',
-|    context    => { path => '[RPM metadata]',
-|                    excerpt => ['Build Host: gandalf.fedora.org'] },
-|  }


---------BadURL-404------------------------------------------------------

Name        : git-daemon           Relocations: (not relocatable)
Version     : 1.7.1                     Vendor: Red Hat, Inc.
Release     : 2.el6_0.1             Build Date: Thu 16 Dec 2010 07:25:20 AM MST
Install Date: (not installed)       Build Host: x86-010.build.bos.redhat.com
Group       : Development/Tools     Source RPM: git-1.7.1-2.el6_0.1.src.rpm
Size        : 499329                   License: GPLv2
Signature   : (none)
Packager    : Red Hat, Inc. <http://bugzilla.redhat.com/bugzilla>
URL         : http://www.redhat.com/thisURLDoEsNOTexist
Summary     : Git protocol dæmon
Description :
The git dæmon for supporting git:// access to git repositories

-|  { arch       => 'src',
-|    subpackage => 'git-daemon',
-|    code       => 'BadURL',
-|    diag       => 'HTTP GET failed for URL (404 Not Found)',
-|    context    => { path => '[RPM metadata]',
-|                    excerpt => ['URL: http://www.redhat.com/thisURLDoEsNOTexist'] },
-|  }


---------InvalidURL------------------------------------------------------

Name        : git-daemon           Relocations: (not relocatable)
Version     : 1.7.1                     Vendor: Red Hat, Inc.
Release     : 2.el6_0.1             Build Date: Thu 16 Dec 2010 07:25:20 AM MST
Install Date: (not installed)       Build Host: x86-010.build.bos.redhat.com
Group       : Development/Tools     Source RPM: git-1.7.1-2.el6_0.1.src.rpm
Size        : 499329                   License: GPLv2
Signature   : (none)
Packager    : Red Hat, Inc. <http://bugzilla.redhat.com/bugzilla>
URL         : www.redhat.com
Summary     : Git protocol dæmon
Description :
The git dæmon for supporting git:// access to git repositories

-|  { arch       => 'src',
-|    subpackage => 'git-daemon',
-|    code       => 'InvalidURL',
-|    diag       => 'URL must be of the form &lt;protocol&gt;://&lt;host&gt;',
-|    context    => { path => '[RPM metadata]',
-|                    excerpt => ['URL: www.redhat.com'] },
-|  }


---------BadProtocol------------------------------------------------------

Name        : git-daemon           Relocations: (not relocatable)
Version     : 1.7.1                     Vendor: Red Hat, Inc.
Release     : 2.el6_0.1             Build Date: Thu 16 Dec 2010 07:25:20 AM MST
Install Date: (not installed)       Build Host: x86-010.build.bos.redhat.com
Group       : Development/Tools     Source RPM: git-1.7.1-2.el6_0.1.src.rpm
Size        : 499329                   License: GPLv2
Signature   : (none)
Packager    : Red Hat, Inc. <http://bugzilla.redhat.com/bugzilla>
URL         : xtp://ftp.redhat.com/blahblah
Summary     : Git protocol dæmon
Description :
The git dæmon for supporting git:// access to git repositories

-|  { arch       => 'src',
-|    subpackage => 'git-daemon',
-|    code       => 'UnknownProtocol',
-|    diag       => "Unknown protocol 'xtp' in URL; expected http/https/ftp/git",
-|    context    => { path => '[RPM metadata]',
-|                    excerpt => ['URL: xtp://ftp.redhat.com/blahblah'] },
-|  }
