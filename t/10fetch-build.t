#
# tests for fetch-build script
#
use v5.6.0;
use strict;
use warnings;

use Test::More;
use Test::Differences;
use Test::MockObject;
use Test::Exception;

use File::Temp                  qw(tempdir);
use File::Copy                  qw(copy);
use File::Basename              qw(dirname);
use File::Spec;

BEGIN {
    require_ok( 'bin/rpmgrill-fetch-build' );
}

throws_ok (
    sub { Koji::Build->new({'id' => 123}) },
    qr/Unable to find/,
    'Dont construct object if not enough information is available.'
);
subtest 'Koji Build' => sub {
    my $build_info = {'id' => '123', 'nvr' => 'rpmdiff-1.8.11-1.el5', 'package_name' => 'rpmdiff'};
    my $build = Koji::Build->new($build_info);
    my @nvr = $build->nvr();

    ok ($build->nvr(), 'calling nvr does not die');
    eq_or_diff ($build->id(), $$build_info{'id'}, 'calling id returns expected id');
    eq_or_diff (\@nvr, [qw( rpmdiff 1.8.11 1.el5 )], 'calling nvr returns expected nvr');

    my $rpms = [
        { 'arch' => 'src', },
        { 'arch' => 'i386', },
    ];
    my @got = $build->arches($rpms);
    eq_or_diff (\@got, [qw( i386 src )], 'returns correct arches');
};


my $client = Koji::Client->new('foo', 'fake xmlrpc client');
ok (defined $client, 'Successfully created Koji Client instance');
ok (defined $client->get_xmlrpc_client(), 'XMLRPC client correctly assigned');


subtest 'Koji Client returns instance of Koji Build holding build info' => sub {
    my $mock_rpc_result = Test::MockObject->new();
    my $mock_client = Test::MockObject->new();
    my $expected = {'id' => '123', 'nvr' => 'libfoo-1-2', 'package_name' => 'libfoo'};

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
    my $tempdir = tempdir("t-FetchBuild.XXXXXX", CLEANUP => !$ENV{DEBUG});
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
