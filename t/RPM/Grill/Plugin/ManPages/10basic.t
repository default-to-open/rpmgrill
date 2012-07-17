# -*- perl -*-
#
# Tests for the ManPages plugin
#
use strict;
use warnings;

use Test::More;
use Test::Differences;
use File::Temp                  qw(tempdir);

# Slurp in the DATA section, which defines the tests we'll run
my @tests;
while (my $line = <DATA>) {
    if ($line =~ /^-{10,}([^-].*[^-])-+$/) {
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
}

plan tests => 3 + @tests;

# Load required libraries
use_ok 'RPM::Grill'                     or exit;
use_ok 'RPM::Grill::Plugin::ManPages'   or exit;

ok(require("t/lib/FakeTree.pm"), "loaded FakeTree.pm") or exit;

# Make a temp dir
my $tempdir = tempdir("t-ManPages.XXXXXX", CLEANUP => !$ENV{DEBUG});

my $i = 0;
for my $t (@tests) {
    my $temp_subdir = sprintf("%s/%02d", $tempdir, ++$i);

    my $g = FakeTree::make_fake_tree( $temp_subdir, $t->{setup} );

#    use Data::Dumper; print STDERR Dumper($g);

    # FIXME
    bless $g, 'RPM::Grill::Plugin::ManPages';
    eval { $g->analyze() };
    if ($@) {
        fail "$t->{name} : ERROR: $@";
    }
    else {
        my $expected_gripes = eval $t->{expect};
        die "eval failed:\n\n $t->{expect} \n\n $@" if $@;

        if ($expected_gripes) {
            # FIXME
        }

        eq_or_diff $g->{gripes}, $expected_gripes, $t->{name};
    }
}

__DATA__

------------sdfsdfsdf------------

>> -rwxr-xr-x  root root /i386/mypkg/usr/sbin/foo

...expect:

{
  ManPages => [
    {
      arch => 'i386',
      code => 'ManPageMissing',
      context => {
        path => '/usr/sbin/foo'
      },
      diag => 'No man page for /usr/sbin/foo',
      subpackage => 'mypkg'
    }
  ]
}
