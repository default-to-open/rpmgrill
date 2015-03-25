#
# Unit tests for the SecurityPolicy module
#
use strict;
use warnings;

use Test::More;
use Test::Differences;
use Test::MockModule;

use File::Temp                  qw(tempdir);

use FindBin;
use lib ("$FindBin::Bin/../../../../lib/", "$FindBin::Bin/../../../../../lib/");

use_ok 'FakeTree'
    or exit;

# Read DATA
my @tests = FakeTree::read_tests(*DATA);

# Do the tests
my $tempdir = tempdir("t-SecurityPolicy.XXXXXX", CLEANUP => !$ENV{DEBUG});

# Load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                          or exit;
use_ok 'RPM::Grill::RPM'                     or exit;
use_ok 'RPM::Grill::Plugin::SecurityPolicy'  or exit;

# Override nvr(); otherwise, the Ruby Gem CVE check barfs
my $rpm_module = new Test::MockModule('RPM::Grill::RPM');
$rpm_module->mock( nvr => sub { return ('nnn', 'vvv', 'rrr') } );

for my $i (0 .. $#tests) {
    my $test = $tests[$i];

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    my $security_plugin = create_fake_tree($test, $temp_subdir);

    $security_plugin->analyze();

    eq_or_diff $security_plugin->{gripes}, get_expected_gripes($test), $test->{name};
}

done_testing;

sub create_fake_tree {
    my ($test, $temp_subdir) = @_;

    my $plugin = FakeTree::make_fake_tree( $temp_subdir, $test->{setup} );
    bless $plugin, 'RPM::Grill::Plugin::SecurityPolicy';

    return $plugin;
}

sub get_expected_gripes {
    my ($test) = @_;

    my $expected_gripes;
    if ($test->{expect}) {
        $expected_gripes = eval "{ SecurityPolicy => [ $test->{expect} ] }";
        die "eval failed:\n\n $test->{gripe_string} \n\n  $@\n"
            if $@;
    }

    return $expected_gripes;
}

__DATA__

---------ok-path---------------------------------------------------------

>> -rw-r--r--  root root 0 /noarch/mypkg/usr/share/test_file0
PATH=/usr/bin

---------home-path---------------------------------------------------------

>> -rw-r--r--  root root 0 /noarch/mypkg/usr/share/test_file1
PATH=/home/test_dir

...expect:

{
    arch => 'noarch',
    code => 'SuspiciousPath',
    context => {
        excerpt => [ 'PATH=/home/test_dir' ],
        path => '/usr/share/test_file1'
    },
    diag => 'Potentially insecure PATH element <tt>/home</tt>',
    subpackage => 'mypkg'
}

---------tmp-path---------------------------------------------------------

>> -rw-r--r--  root root 0 /noarch/mypkg/usr/share/test_file2
PATH=/tmp/another/test_dir

...expect:

{
    arch => 'noarch',
    code => 'SuspiciousPath',
    context => {
        excerpt => [ 'PATH=/tmp/another/test_dir' ],
        path => '/usr/share/test_file2'
    },
    diag => 'Potentially insecure PATH element <tt>/tmp</tt>',
    subpackage => 'mypkg'
}

---------local-path---------------------------------------------------------

>> -rw-r--r--  root root 0 /noarch/mypkg/usr/share/test_file3
PATH=/usr/local/test_dir/bin

...expect:

{
    arch => 'noarch',
    code => 'SuspiciousPath',
    context => {
        excerpt => [ 'PATH=/usr/local/test_dir/bin' ],
        path => '/usr/share/test_file3'
    },
    diag => 'Potentially insecure PATH element <tt>/local</tt>',
    subpackage => 'mypkg'
}
