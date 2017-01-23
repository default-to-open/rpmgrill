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

use Cwd                         qw(abs_path);
use File::Temp                  qw(tempdir);
use File::Copy                  qw(copy);
use File::Basename              qw(dirname);
use File::Path                  qw(mkpath);
use File::Spec;
use FindBin;

BEGIN {
    require_ok( "$FindBin::Bin/../bin/rpmgrill-fetch-build" );
}

throws_ok (
    sub { Koji::Build->new({'id' => 123}) },
    qr/missing in build info/,
    'Do not construct object if not enough information is available.'
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
        { 'arch' => 'src', },
        { 'arch' => 'i386', },
    ];
    my @got = $build->arches($rpms);
    eq_or_diff (\@got, [qw( i386 src )], 'returns correct arches');
};


subtest 'Koji Client created successfully' => sub {
    my $koji = Koji::Client->new('foo', 'fake xmlrpc client', 'ignored');
    ok (defined $koji, 'Successfully created Koji Client instance');
    ok (defined $koji->get_xmlrpc_client(), 'XMLRPC client correctly assigned');
};


subtest 'Koji Client returns instance of Koji Build holding build info' => sub {
    my $mock_rpc_result = Test::MockObject->new();
    my $mock_client = Test::MockObject->new();
    my $expected = {'id' => '123', 'nvr' => 'libfoo-1-2', 'package_name' => 'libfoo'};

    $mock_rpc_result->mock('result',
        sub { return $expected });
    $mock_client->mock('getBuild',
        sub { return $mock_rpc_result} );

    my $koji = Koji::Client->new($mock_client, 'ignored');
    my $build = $koji->get_build_info('dummy.nvr');
    ok (defined $build, 'buildinfo is defined');
    eq_or_diff($build->{'build_info'}, $expected, 'buildinfo can be retrieved');
};


subtest 'Koji Client downloads successfully' => sub {
    my $tempdir = tempdir("t-FetchBuild.XXXXXX", CLEANUP => !$ENV{DEBUG});
    my $rpm_nvr = 'testbuild-0.1-1.fc20';
    my $rpm_name = "$rpm_nvr.noarch.rpm";

    #
    # Create the directory structure from brew in our temporary
    # directory. We copy our RPM file into that directory in order to
    # simulate a download.
    #
    my $tempdir_path = Cwd::abs_path($tempdir);
    my @created = mkpath(File::Spec->catfile($tempdir_path, 'packages/testbuild/0.1/1.fc20/noarch/'));
    my $rpm_testfile = File::Spec->catfile(pop @created, $rpm_name);
    my $copy_from = File::Spec->catfile(dirname(__FILE__), 'data', $rpm_name);
    copy($copy_from, $rpm_testfile);

    #
    # Create a build info hash which would usually be obtained by the
    # Koji::Client.
    #
    my $build_info = {
        id => '123',
        nvr => $rpm_nvr,
        package_name => 'testbuild'
    };
    my $build = Koji::Build->new($build_info);

    #
    # Now create list of rpms to retrieved.
    # The client will iterate over all rpms found by the build id given
    # by the former instantiated Koji::Build and it's information.
    #
    # We use the mocks to mock the call to retrieve all rpm information.
    #
    my $rpms = [
        {
            version => '0.1',
            nvr => $rpm_nvr,
            release => '1.fc20',
            arch => 'noarch',
            id => '3740308',
            name => 'testbuild',
        },
        {
            #
            # This version can not be retrieved from our temporary
            # directory. We only have one test build copied.
            #
            version => '0.1',
            nvr => $rpm_nvr,
            release => '1.fc20',
            arch => 'i386',
            id => '3740309',
            name => 'testbuild',
        }
    ];
    my $mock_rpc_result = Test::MockObject->new();
    my $mock_client = Test::MockObject->new();
    $mock_rpc_result->mock('result',
        sub { return $rpms });
    $mock_client->mock('listRPMs',
        sub { return $mock_rpc_result} );

    #
    # Now we do the actual work.
    #
    my $koji = Koji::Client->new($mock_client, "file://$tempdir_path");
    $koji->_download_rpms_from_koji($build, $tempdir);

    #
    # Verify the result.
    #
    opendir my($dh), $tempdir_path or die "Couldn't open temporary directory: $!";
    my @files = readdir $dh;
    closedir $dh;
    my @actual = grep {$_ eq $rpm_name} @files;
    eq_or_diff (\@actual, [ ($rpm_name) ], 'successfully downloaded RPM');

    #
    # Should be empty. Our "fake" server root will not find this
    # build in the test directory.
    #
    @actual = grep {$_ eq "$rpm_nvr.i386.rpm"} @files;
    eq_or_diff (\@actual, [], 'not downloaded i386 RPM') ;
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
