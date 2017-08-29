#
# tests for fetch-build script
#
use v5.6.0;
use strict;
use warnings;

use Test::More;
use Test::Differences;

use Cwd                         qw(getcwd);
use File::Temp                  qw(tempdir);
use File::Spec;
use FindBin;


sub touch {
    my $filename = shift;

    open HANDLE, ">>$filename" || die "can't touch $filename: $!\n";
    close HANDLE;
}

sub with_get_build_log_for_rpm {
    my $buildlog_name = shift;
    my $rpm_name = shift;

    my $cwd = getcwd;
    my $tempdir_path = tempdir("t-rpmgrill-unpack.XXXXXX", CLEANUP => !$ENV{DEBUG});

    my $buildlog_path = File::Spec->catfile($tempdir_path, $buildlog_name);
    touch $buildlog_path;

    chdir($tempdir_path);

    my $actual = RPM::Grill::UnpackRPMs::get_build_log_for_rpm($rpm_name);
    chdir($cwd);

    return $actual;
}

BEGIN {
    require_ok( "$FindBin::Bin/../bin/rpmgrill-unpack-rpms" );
}

subtest 'get_build_log_for_rpm default' => sub {
    my $actual = with_get_build_log_for_rpm('build.log', 'foo-1.3.1-1.fc28.noarch.rpm');
    eq_or_diff ($actual, 'build.log', 'default build.log for noarch');
};

subtest 'get_build_log_for_rpm 1:1 mapping between arches' => sub {
    my $actual = with_get_build_log_for_rpm('build.i386.log', 'foo-1.3.1-1.fc28.i386.rpm');
    eq_or_diff ($actual, 'build.i386.log', 'arch build.log for arch rpm');
};

subtest 'get_build_log_for_rpm different arch' => sub {
    my $actual = with_get_build_log_for_rpm('build.i386.log', 'foo-1.3.1-1.fc28.i686.rpm');
    eq_or_diff ($actual, 'build.i386.log', 'arch build.log for arch rpm');

    my $actual = with_get_build_log_for_rpm('build.armhfp.log', 'foo-1.3.1-1.fc28.armv7hl.rpm');
    eq_or_diff ($actual, 'build.armhfp.log', 'arch build.log for arch rpm');
};
done_testing();
