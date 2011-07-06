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

plan tests => 2 + 4;

# Pass 2: do the tests
my $tempdir = tempdir("t-RpmMetadata.XXXXXX", CLEANUP => !$ENV{DEBUG});

# Tests 1-2 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::Plugin::RpmMetadata'  or exit;

my %nvr = (
    name    => 'mypkg',
    version => '1.2',
    release => '3.el4',
);

check_metadata( qw( mypkg      1.2     3.el4           ));
check_metadata( qw( wrongpkg   1.2     3.el4  Name     ));
check_metadata( qw( mypkg      1.2.3   3.el4  Version  ));
check_metadata( qw( mypkg      1.2     3.el5  Release  ));

sub check_metadata {
    use feature "state";
    state $i = 0;

    my ($n, $v, $r, @gripe_codes) = @_;

    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i++);

    # Create metadata file
    mkpath "$temp_subdir/src/mypkg", 0, 02755;
    my $metadata_file = "$temp_subdir/src/$nvr{name}/RPM.metadata";
    open  METADATA, '>', $metadata_file
        or die "Cannot create $metadata_file: $!";
    print METADATA <<"END_METADATA";
Name         : $n
Version      : $v
Release      : $r
Vendor       : Red Hat, Inc.
Build Host   : foo.redhat.com
END_METADATA
    close METADATA
        or die "Error writing $metadata_file: $!";

    open  RPM, '>', "$temp_subdir/src/$nvr{name}/rpm.rpm";
    close RPM;

    my $obj = RPM::Grill->new( $temp_subdir );
    bless $obj, 'RPM::Grill::Plugin::RpmMetadata';
    $obj->srpm->{nvr} = { %nvr };

    $obj->analyze();

    my $expected_gripes;
    if (@gripe_codes) {
        my %actual_nvr = (name => $n, version => $v, release => $r);

        $expected_gripes = { RpmMetadata => [ map { +{
            arch       => 'src',
            subpackage => $nvr{name},
            context    => { path => '[RPM metadata]' },
            code       => "Wrong$_",
            diag       => "$_: expected $nvr{lc $_}, got $actual_nvr{lc $_}",
        } } @gripe_codes ] };
    }

    my $test_name = join(",", map { "Wrong$_" } @gripe_codes) || '[no gripes]';

    eq_or_diff $obj->{gripes}, $expected_gripes, $test_name;
}
