# -*- perl -*-
#
# RPM::Grill::Plugin::LibGather - temporary(?) hack for Ed Rousseau
#
# This plugin does not gripe; it just has side effects. It appends
# to the file $FIXME
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::LibGather;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = "0.01";

use Carp;
use DBI;
use File::LibMagic              qw(:easy);

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order { 12 }      # FIXME

# One-line description of this plugin
sub blurb { return "gathers info about libs used by this pkg" }

# FIXME
sub doc { return <<"END_DOC" };
FIXME FIXME FIXME
END_DOC

our $Log = 'rpmgrill.pw-linkage.txt';

# END   user-configurable section
###############################################################################

# Program name of our caller
(our $ME = $0) =~ s|.*/||;

#
# input: a RPM::Grill object, blessed into this package.
# return value: not checked.
#
# Calls $self->gripe() with problems.  Return value is meaningless,
# but code can die/croak if necessary -- it will be trapped in an eval.
#
sub analyze {
    my $self = shift;

    # Add a package ID to mysql to indicate that we've analyzed this build.
    my $dbh;
    my $sth;

    if ($dbh = DBI->connect("DBI:mysql:linkage:localhost", 'linkage')) {
        # Look for existing package id
        # FIXME: what about brew scratch builds?
        my $q_pkg = $dbh->prepare('SELECT package_id FROM packages
                           WHERE package_name=?
                             AND package_version=?
                             AND package_release=?');

        my @nvr = $self->nvr;
        $q_pkg->execute(@nvr);
        my $package_id;
        while (my $x = $q_pkg->fetchrow_arrayref) {
            if (defined $package_id) {
                warn "Duplicate entry for @nvr: $package_id, $x->[0]\n";
            }
            $package_id = $x->[0];
        }

        # Not found. Insert.
        if (! defined $package_id) {
            my $i_pkg = $dbh->prepare('INSERT INTO packages
                     (package_name, package_version, package_release, analyzed_by)
                     VALUES (?,?,?,?)');
            $i_pkg->execute(@nvr,  __PACKAGE__ . " " . $VERSION);
            $package_id = $dbh->{mysql_insertid};
        }

        # Prepare an STH for our analyze code
        $sth = $dbh->prepare("INSERT INTO linkage_xref
                        (package_id, subpackage, arch, libname, filepath)
                        VALUES ( $package_id,?,?,?,? )");
    }
    else {
        warn "$ME: Cannot connect to mysql; will dump just txt";
    }

    # Create a text log too. Always create it, as a signal that we've run.
    open my $fh_log, '>>', $Log
        or die "$ME: Cannot append to $Log: $!\n";

    for my $rpm ( $self->rpms ) {
        for my $f ( $rpm->files ) {
            $self->_gather_libs( $f, $sth, $fh_log )
        }
    }

    # If we're doing mysql, disconnect now
    $dbh->disconnect                    if $dbh;

    # We always have a log file
    close $fh_log
        or die "$ME: Error writing to $Log: $!\n";
}

sub _gather_libs {
    my $self   = shift;
    my $f      = shift;                 # in: file obj
    my $sth    = shift;                 # in: MySQL insert thingy
    my $fh_log = shift;                 # in: filehandle to log file

    # eu-readelf hangs, apparently forever, on certain clamav files:
    #   payload/usr/share/doc/clamav-0.97/test/.split/split.clam.exe.bz2aa
    my $file_path = $f->extracted_path;
    my $file_type = MagicFile( $file_path )
        or do {
            warn "$ME: Cannot determine file type (Magic) of $file_path\n";
            return;
        };
    return unless $file_type =~ /\bELF\b/;

    my @libs;
    my $cmd = "eu-readelf -d $file_path 2>/dev/null";
    open my $fh_readelf, "-|", $cmd
        or die "$ME: Cannot fork: $!\n";
    while (my $line = <$fh_readelf>) {
        # FIXME: check to make sure we're in the right section
        # FIXME: what about .gnu.liblist in -A?
        if ($line =~ /^\s*NEEDED\s+Shared library:\s+\[(\S+)\]/) {
            push @libs, $1;
        }
    }
    close $fh_readelf;  # No status check: file could be non-elf


    if (defined $sth) {
        $sth->execute($f->subpackage, $f->arch, $_, $f->path)       for @libs;
    }

    # Now dump to text file.
    if (@libs) {
        my @nvr = $self->nvr;

        for my $l (@libs) {
            print { $fh_log } join("\t", @nvr, $f->arch, $f->subpackage,
                                   $l, $f->path), "\n";
        }
    }
}

1;


###############################################################################
#
# Documentation
#

=head1	NAME

FIXME - FIXME

=head1	SYNOPSIS

    use Fixme::FIXME;

    ....

=head1	DESCRIPTION

FIXME fixme fixme fixme

=head1	CONSTRUCTOR

FIXME-only if OO

=over 4

=item B<new>( FIXME-args )

FIXME FIXME describe constructor

=back

=head1	METHODS

FIXME document methods

=over 4

=item	B<method1>

...

=item	B<method2>

...

=back


=head1	EXPORTED FUNCTIONS

=head1	EXPORTED CONSTANTS

=head1	EXPORTABLE FUNCTIONS

=head1	FILES

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
