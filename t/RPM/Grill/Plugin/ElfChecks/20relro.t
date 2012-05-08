# -*- perl -*-
#
# tests for the ElfChecks plugin
#
use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(mkpath rmtree);
use File::Temp                  qw(tempdir);
use File::Basename              qw(dirname);

(my $test_subdir = $0) =~ s|\.t$|.d|
    or die "Internal error: test name $0 doesn't end in .t";

our @tests;
while (my $line = <DATA>) {
    chomp $line;
    $line =~ s/\s*\#.*$//;              # Strip comments
    next unless $line;                  # skip empty and comment-only lines

    if ($line =~ /^-+\s+\[(.*)\]$/) {
        # Line of dashes. New test.
        push @tests, { name => $1, files => [], expected_gripes => [] };
    }
    elsif ($line =~ m{^(\S+)\s+(\S+)\s+(\S+)\s+(/\S+)(\s+\[(.*)\])?$}) {
        my ($arch, $subpkg, $mode, $path, $flags) = ($1, $2, $3, $4, $6);

        push @{ $tests[-1]->{files} }, [ $arch, $subpkg, $mode, $path, $flags ];
    }
    elsif ($line =~ m{^\*\*+\s+(\S+)$}) {
        push @{ $tests[-1]->{expected_gripes} }, split ',', $1;
    }
    else {
        die "Cannot grok test definition line '$line'";
    }
}

plan tests => 3 + @tests;

#use Data::Dumper; print Dumper(\@tests);

# Tests 1-3 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                       or exit;
use_ok 'RPM::Grill::RPM'                  or exit;
use_ok 'RPM::Grill::Plugin::ElfChecks'    or exit;


# Run the tests
my $tempdir = tempdir("t-ElfChecks.XXXXXX", CLEANUP => !$ENV{DEBUG});

for my $i (0 .. $#tests) {
    my $t = $tests[$i];

    # Create new tempdir for this individual test
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    mkdir $temp_subdir, 02755
        or die "mkdir $temp_subdir: $!\n";

    my %foo;
    my %flags;

    # Write RPM.per_file_metadata
    for my $f (@{ $t->{files} }) {
        my ($arch, $subpkg, $mode, $path, $flags) = @$f;

        $flags{$arch}{$subpkg}{$path} = $flags;

        my $basedir = "$temp_subdir/$arch/$subpkg";
        mkpath $basedir, 0, 02755;

        my $per_file = "$basedir/RPM.per_file_metadata";
        open OUT, '>>', $per_file or die;

        $foo{$arch}{$subpkg} = 1;

        # mkdir it, to avoid complaints
        my $d = dirname($path);
        mkpath "$temp_subdir/$arch/$subpkg/payload$d", 0, 02755;
        open TMP, '>', "$temp_subdir/$arch/$subpkg/payload$path" or die;
        close TMP;

        # Add to manifest
        print OUT join("\t",
                       "f"x32,
                       $mode,
                       'root',
                       'root',
                        "0",
                       "(none)",
                       $path,
                    ), "\n";
    }
    close OUT or die;

    for my $arch (sort keys %foo) {
        for my $subpkg (sort keys %{ $foo{$arch} }) {
            mkpath "$temp_subdir/$arch/$subpkg", 0, 02755;

            # Create rpm.rpm
            open  OUT, '>', "$temp_subdir/$arch/$subpkg/rpm.rpm" or die;
            close OUT;
        }
    }

    # Parse the extracted files
    my $obj = RPM::Grill->new( $temp_subdir );

    for my $rpm ( $obj->rpms ) {
        for my $f ( $rpm->files ) {
            my $arch   = $f->arch;
            my $subpkg = $f->subpackage;
            my $path   = $f->path;

            $f->{_file_type} = "ELF blah blah";
            $f->{_eu_readelf} = { elf_type => "UNKNOWN" };

            if (my $flags = $flags{$arch}{$subpkg}{$path}) {
                if ($flags =~ s/relro=(full|partial|no)//) {
                    if ($1 eq 'full') {
                        $f->{_eu_readelf}{gnu_relro} = 1;
                        $f->{_eu_readelf}{bind_now}  = 1;
                    }
                    elsif ($1 eq 'partial') {
                        $f->{_eu_readelf}{gnu_relro} = 1;
                    }
                }

                if ($flags =~ s/pie=(yes|no)//) {
                    $f->{_eu_readelf}{elf_type} = "DYN blah blah";
                    if ($1 eq 'yes') {
                        $f->{_eu_readelf}{debug} = 1;
                    }
                }

                if ($flags =~ /[^,]/) {
                    die "FIXME: unknown flag remnant '$flags'";
                }
            }

        }
    }

    # invoke
    bless $obj, 'RPM::Grill::Plugin::ElfChecks';

    $obj->analyze();

    my @actual_gripes;
    if (my $g = $obj->{gripes}) {
        my %codes = map { $_->{code} => 1 } @{ $g->{ElfChecks} };

        @actual_gripes = sort keys %codes;
    }

    eq_or_diff \@actual_gripes, $t->{expected_gripes}, $t->{name};

}

__DATA__

---------------------- [basic]

i386 mypkg -rwxr-xr-x /usr/bin/foo [relro=partial,pie=no]

---------------------- [PIE binary with partial relro]

i386 mypkg -rwxr-xr-x /usr/bin/foo [relro=partial,pie=yes]

*** PiePartialRelro

---------------------- [PIE binary with no relro]

i386 mypkg -rwxr-xr-x /usr/bin/foo [relro=no,pie=yes]

*** PieNotRelro

---------------------- [library without relro]

i386 mypkg -rwxr-xr-x /usr/lib/libfoo.so [relro=no,pie=no]

*** LibMissingRELRO

---------------------- [setuid missing relro]

i386 mypkg -rwsr-xr-x /usr/bin/foo [relro=no,pie=no]

*** SetuidMissingRELRO

---------------------- [setuid partial relro]

i386 mypkg -rwsr-xr-x /usr/bin/foo [relro=partial,pie=no]

*** SetuidPartialRELRO

---------------------- [setgid missing relro]

i386 mypkg -rwxr-sr-x /usr/bin/foo [relro=no,pie=no]

*** SetgidMissingRELRO

---------------------- [setgid partial relro]

i386 mypkg -rwxr-sr-x /usr/bin/foo [relro=partial,pie=no]

*** SetgidPartialRELRO

---------------------- [daemon partial relro]

i386 mypkg -rwxr-xr-x /usr/bin/foo    [relro=partial,pie=no]
i386 mypkg -rwxr-xr-x /etc/init.d/foo []

*** DaemonPartialRELRO

---------------------- [daemon missing relro]

i386 mypkg -rwxr-xr-x /usr/bin/foo    [relro=no,pie=no]
i386 mypkg -rwxr-xr-x /etc/init.d/foo []

*** DaemonMissingRELRO
