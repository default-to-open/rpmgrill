#
# tests for rpmgrill script
#
use v5.6.0;
use strict;
use warnings;

use Test::More;
use Test::Differences;
use Test::Exception;

use Cwd                         qw(abs_path getcwd);
use File::Temp                  qw(tempdir);
use File::Copy                  qw(copy);
use File::Copy::Recursive       qw(dircopy);
use File::Basename              qw(dirname);
use File::Spec;
use FindBin;

BEGIN {
    require_ok( "$FindBin::Bin/../bin/rpmgrill" );
    require_ok( "$FindBin::Bin/../bin/rpmgrill-unpack-rpms" );
}

subtest 'Sets exit code to 1 when failures detected' => sub {
    my $cwd = getcwd;
    my $tempdir = tempdir("t-RpmGrill.XXXXXX", CLEANUP => !$ENV{DEBUG});
    my $tempdir_path = Cwd::abs_path($tempdir);
    my $rpm_dir = 'rpm_with_errors';

    # Copy all files (rpms, build log, etc) into our tempdir
    my $copy_from = File::Spec->catfile(dirname(__FILE__), 'data', $rpm_dir);
    dircopy($copy_from, $tempdir_path);

    # unpack all rpms with rpmgrill-unpack
    RPM::Grill::UnpackRPMs::do_unpack($tempdir_path);
    my $unpack_dir_path = File::Spec->catfile($tempdir_path, 'unpacked');

    # run rpmgrill over the unpacked directory
    my $actual_exitcode = RPM::Grill::Checker::run_checks($unpack_dir_path);
    eq_or_diff($actual_exitcode, 1, 'Exited with error code 1');

    # set cwd back to it's initial state
    chdir $cwd;
};

subtest 'Sets exit code to 0 when all tests pass' => sub {
    my $cwd = getcwd;
    my $tempdir = tempdir("t-RpmGrill.XXXXXX", CLEANUP => !$ENV{DEBUG});
    my $tempdir_path = Cwd::abs_path($tempdir);
    my $rpm_dir = 'rpm_without_errors';

    # Copy all files (rpms, build log, etc) into our tempdir
    my $copy_from = File::Spec->catfile(dirname(__FILE__), 'data', $rpm_dir);
    dircopy($copy_from, $tempdir_path);

    # unpack all rpms with rpmgrill-unpack
    RPM::Grill::UnpackRPMs::do_unpack($tempdir_path);
    my $unpack_dir_path = File::Spec->catfile($tempdir_path, 'unpacked');

    # run rpmgrill over the unpacked directory
    my $actual_exitcode = RPM::Grill::Checker::run_checks($unpack_dir_path);
    eq_or_diff($actual_exitcode, 0, 'Exited without error');

    # set cwd back to it's initial state
    chdir $cwd;
};
done_testing();
