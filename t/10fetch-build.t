# -*- perl -*-
#
# tests for fetch-build script
#
use strict;
use warnings;

use Test::More;
use Test::Differences;
use Test::MockObject;
use Carp;
use Data::Dumper;

use File::Temp                  qw(tempdir);
use File::Copy                  qw(copy);
use File::Basename              qw(dirname);
use File::Spec;

BEGIN {
    require_ok( 'bin/rpmgrill-fetch-build' );
}

my $client = Koji::Client->new('foo', 'fake xmlrpc client');
ok (defined $client, 'Successfully created Koji Client instance');
ok (defined $client->get_xmlrpc_client(), 'XMLRPC client correctly assigned');


subtest 'Koji Client returns instance of Koji Build holding build info' => sub {
    my $mock_rpc_result = Test::MockObject->new();
    my $mock_client = Test::MockObject->new();
    my $expected = {'epoch' => undef };

    $mock_rpc_result->mock('result',
        sub { return $expected });
    $mock_client->mock('getBuild',
        sub { return $mock_rpc_result} );

    my $client= Koji::Client->new($mock_client);
    my $build = $client->get_build_info('dummy.nvr');
    ok (defined $build, 'buildinfo is defined');
    eq_or_diff($build->{'build_info'}, $expected, 'buildinfo can be retrieved');
};

eq_or_diff (
    RPM::Grill::FetchBuild::get_full_rpm_name({'nvr' => 'foo', 'arch' => 'i64'}),
    'foo.i64.rpm',
    'RPM name is formatted correctly.'
);

subtest 'extracts downloaded RPM successfully' => sub {
    #
    # prepare the RPM file and move it to our temporary directory. That
    # corresponds to the state that the package has just been
    # downloaded.
    #
    my $tempdir = tempdir("t-FetchBuild.XXXXXX", CLEANUP => 1);
    my $rpm_name = 'testbuild-0.1-1.fc20.noarch.rpm';
    my $rpm_testfile = File::Spec->catfile($tempdir, $rpm_name);
    copy( File::Spec->catfile(dirname(__FILE__), 'data', $rpm_name), $rpm_testfile );

    #
    # Redirect the print statements. The function was successful, if it
    # created test directories and written dependencies to RPM files.
    #
    my $fetch_stdout;
    close STDOUT;
    open(STDOUT, '>', \$fetch_stdout)
        or die "Can't open STDOUT: $!";

    RPM::Grill::FetchBuild::extract_rpm (
        {'nvr' => 'testbuild-0.1-1.fc20', 'arch' => 'noarch'},
        $tempdir,
        1
    );

    like ($fetch_stdout, qr/mkdir -p/, 'successfully created payload directory' );
    like ($fetch_stdout, qr/rpm2cpio/, 'successfully wrote RPM payload' );
};
done_testing();
