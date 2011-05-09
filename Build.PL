use strict;
use warnings;
use Module::Build;

my $builder = Module::Build->new(
    module_name         => 'RPM::Grill',
    license             => 'perl',
    dist_author         => 'Eduardo Santiago <santiago@redhat.com>',
    dist_version_from   => 'lib/RPM/Grill.pm',
    requires => {
        'Test::More' => 0,
        'version'    => 0,
    },
    add_to_cleanup      => [ 'RPM-Grill-*' ],
);

$builder->create_build_script();
