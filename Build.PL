use strict;
use warnings;
use Module::Build;

my $builder = Module::Build->new(
    module_name       => 'rpmgrill',
    dist_version      => '0.0',
    dist_abstract     => 'Suite of sanity tests for RPM builds',
    license           => 'perl',
    dist_author       => 'Eduardo Santiago <santiago@redhat.com>',
    requires => {
        'CGI'              => 0,
        'Clone'             => 0,
        'Encode'           => 0,
        'File::Basename'   => 0,
        'File::LibMagic'   => 0,
        'File::Slurp'      => 0,
        'HTML::Entities'   => 0,
        'IPC::Run'         => 0,
        'LWP::UserAgent'   => 0,
        'List::Util'        => 0,
        'Module::Pluggable' => 0,
        'Net::DNS'         => 0,
        'Test::Deep'        => 0,
        'Text::ParseWords' => 0,
        'Tie::File'        => 0,
        'Time::Piece'       => 0,
        'XML::Simple'       => 0,
        'YAML'              => 0,
        'YAML::Syck'        => 0,
        'version'          => 0,
    },

    doc_files => {
        'doc/tooltips.txt' => 'usr/share/rpmgrill/tooltips.txt',
    },

    # Argh. Without this, tooltips.txt just goes into blib and stays there
    install_path        => { 'usr/share/rpmgrill' => '/usr/share/rpmgrill' },

    # Tests only
    build_requires => {
        'Test::More'        => 0,
        'Test::Differences' => 0,
        'Encode'            => 0,
    },
    add_to_cleanup      => [ 'RPM-Grill-*' ],
);

$builder->add_build_element('doc');
$builder->create_build_script();
