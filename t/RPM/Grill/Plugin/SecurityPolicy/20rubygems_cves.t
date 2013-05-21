# -*- perl -*-
#
# tests for the Ruby Gem CVE check in the SecurityPolicy module
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

###############################################################################
# BEGIN test definitions

# Note that 2012-3465 and -3463 are listed below in non-sorted order!
# That's because those are defined in files named OSVDB-84513 and -84515
# respectively (we read filenames in sorted order).
my $basic_tests = <<'END_TESTS';
actionpack 2.3.1  2012-1099 2012-3424 2012-3465 2012-3463 2013-0156 2013-1855
actionpack 2.3.15 2012-1099 2012-3424 2012-3465 2012-3463           2013-1855
actionpack 2.3.18 2012-1099 2012-3424 2012-3465 2012-3463
actionpack 2.3.19 2012-1099 2012-3424 2012-3465 2012-3463

actionpack 3.0.11 2012-1099 2012-3424 2012-3465 2012-3463 2013-0156 2013-1855
actionpack 3.0.12           2012-3424 2012-3465 2012-3463 2013-0156 2013-1855
actionpack 3.0.16                     2012-3465 2012-3463 2013-0156 2013-1855
actionpack 3.0.17                                         2013-0156 2013-1855
actionpack 3.0.19                                                   2013-1855

actionpack 3.1.3  2012-1099 2012-3424 2012-3465 2012-3463 2013-0156 2013-1855
actionpack 3.1.4            2012-3424 2012-3465 2012-3463 2013-0156 2013-1855
actionpack 3.1.7                      2012-3465 2012-3463 2013-0156 2013-1855
actionpack 3.1.8                                          2013-0156 2013-1855
actionpack 3.1.10                                                   2013-1855
actionpack 3.1.12

actionpack 3.2.0  2012-1099 2012-3424 2012-3465 2012-3463 2013-0156 2013-1855
actionpack 3.2.2            2012-3424 2012-3465 2012-3463 2013-0156 2013-1855
actionpack 3.2.7                      2012-3465 2012-3463 2013-0156 2013-1855
actionpack 3.2.8                                          2013-0156 2013-1855
actionpack 3.2.11                                                   2013-1855
actionpack 3.2.13
END_TESTS

my @basic_tests;
for my $line (split "\n", $basic_tests) {
    next if !$line;
    my ($n, $v, @cves) = split ' ', $line;
    push @basic_tests, {
        name   => "$n-$v -> " . ("@cves" || "(ok)"),,
        nvr    => { name =>  "rubygem-$n", version => $v, release => "1.el6" },
        changelog => '',
    };

    if (@cves) {
        $basic_tests[-1]{expected_gripes} = {
            SecurityPolicy => [
                map { +{
                    code => 'RubyAdvisoryDB',
                    diag => "<tt>$n</tt> gem may be affected by <var>CVE-$_</var>",
                } } @cves
            ]
        };
    }
}

# One extra: check that SCL packages ("ruby193-rubygem-etc") are recognized
push @basic_tests, $basic_tests[0];
$basic_tests[-1]{name}      .= " (SCL)";
$basic_tests[-1]{nvr}{name} =~ s/^/ruby193-/;

# This tests our ability to detect "Fix CVE-x" in the specfile %changelog.
# Each stanza beginning with '*' indicates one test; the changelog is all
# lines from there to the next '*'. The test uses actionpack-2.3.1 as the
# gem under test; we expect no gripes.
#
# Some of the tests below should probably not
my $changelog_tests = <<'END_TESTS';
* Each "Fix" on its own line
- Fix CVE-2012-1099
- Fix CVE-2012-3424
- Fix CVE-2012-3465
- Fix CVE-2012-3463
- Fix CVE-2013-0156
- Fix CVE-2013-1855

* Multiple "Fix"es on one line
- Fix CVE-2012-1099; Fix CVE-2012-3424; Fix CVE-2012-3465; Fix CVE-2012-3463
- Fix CVE-2013-0156; Fix CVE-2013-1855

* Comma-separated list
- Fixed CVE-2012-1099, 2012-3424, 2012-3465, 2012-3463
- Fixes CVE-2013-0156; 2013-1855

* Plural ("CVEs")
- Fix CVEs 2012-1099, 2012-3424, 2012-3465, 2012-3463, 2013-0156, 2013-1855
END_TESTS

# Split the above into a list of tests.
my @changelog_tests;
for my $line (split "\n", $changelog_tests) {
    next unless $line;
    if ($line =~ /^\*\s+(.*)/) {
        push @changelog_tests, {
            name      => $1,
            nvr       => { name => "rubygem-actionpack",
                           version => "2.3.1" },
            changelog => "$line\n",
        };
    }
    else {
        $changelog_tests[-1]{changelog} .= $line . "\n";
    }
}

# END   test definitions
###############################################################################

plan tests => 1 + @basic_tests + @changelog_tests;

# Pass 2: do the tests

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill::Plugin::SecurityPolicy'  or exit;

# Override the advisory directory; use our static (non-updated) copy.
{
    # i.e. "t/RPM/.../20rubygems_cves.d" (.d for dir, replaces .t)
    (my $testdir = $0) =~ s|\.t$|.d|
        or die "Internal error: Test name does not end in '.t': $0";
    -d $testdir
        or die "Internal error: test subdir does not exist: $testdir";

    no warnings 'once';
    $RPM::Grill::Plugin::SecurityPolicy::Ruby_Advisory_DB = $testdir;
}

###############################################################################
# BEGIN method overrides for testing

package RPM::Grill::Plugin::SecurityPolicy;

# For our purposes, we only need to return 'name' or 'version'.
sub nvr {
    return $_[0]->{nvr}{$_[1]}
        || die "Internal error: bad NVR field '$_[1]'";
}

# Stubs for presenting a changelog
sub specfile {
    return $_[0];
}

# Convert a string into a list of blessed objects providing ->content
sub lines {
    return map {
            bless +{ content => $_}, 'RPM::Grill::Plugin::SecurityPolicy'
        } split "\n", $_[0]->{changelog};
}

# One changelog line
sub content {
    return $_[0]{content};
}

package main;

# END   method overrides for testing
###############################################################################
# BEGIN tests

for my $t (@basic_tests) {
    bless $t, 'RPM::Grill::Plugin::SecurityPolicy';

    $t->_check_rubygem_cves($t);

    # gripe context includes CVE title and a URL. Those are too
    # complicated to check.
    if ($t->{gripes}) {
        delete $_->{context} for @{ $t->{gripes}{SecurityPolicy} };
    }

    eq_or_diff $t->{gripes}, $t->{expected_gripes}, $t->{name};
}

for my $t (@changelog_tests) {
    bless $t, 'RPM::Grill::Plugin::SecurityPolicy';

    $t->_check_rubygem_cves($t);

    eq_or_diff $t->{gripes}, undef, $t->{name};
}
