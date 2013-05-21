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
        'Algorithm::Diff'   => 0,
        'CGI'               => 0,
        'Clone'             => 0,
        'Encode'            => 0,
        'Errno'             => 0,
        'Fcntl'             => 0,
        'File::Basename'    => 0,
        'File::Copy'        => 0,
        'File::LibMagic'    => 0,
        'File::Path'        => 0,
        'File::Slurp'       => 0,
        'File::Temp'        => 0,
        'File::Which'       => 0,
        'HTML::Entities'    => 0,
        'IPC::Run'          => 0,
        'LWP::Simple'       => 0,
        'List::Util'        => 0,
        'Module::Pluggable' => 0,
        'Net::DNS'          => 0,
        'Sort::Versions'    => 0,
        'Test::Deep'        => 0,
        'Test::Differences' => 0,
        'Test::LongString'  => 0,
        'Text::ParseWords'  => 0,
        'Tie::File'         => 0,
        'Time::ParseDate'   => 0,
        'Time::Piece'       => 0,
        'XML::Simple'       => 0,
        'YAML'              => 0,
        'YAML::Syck'        => 0,
        'version'           => 0,
    },

    configure_requires => { 'Module::Build' => 0 },

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
