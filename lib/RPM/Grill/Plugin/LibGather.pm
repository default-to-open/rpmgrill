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

our $Log = '/tmp/rpmgrill-libs.log';

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

    # FIXME: use what you need; delete what you don't

    for my $rpm ( $self->rpms ) {
        for my $f ( $rpm->files ) {
            $self->_gather_libs( $f )
        }
    }
}

sub _gather_libs {
    my $self = shift;
    my $f    = shift;                   # in: file obj

    my @libs;
    my $cmd = "eu-readelf -a " . $f->extracted_path . " 2>/dev/null";
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


    # Whether or not we found any libs, add a package ID to mysql to
    # indicate that we've analyzed this build.
    my @nvr = $self->nvr;
    if (my $dbh = DBI->connect("DBI:mysql:linkage:localhost", 'linkage')) {
        # Look for existing package id
        my $q_pkg = $dbh->prepare('SELECT package_id FROM packages
                           WHERE package_name=?
                             AND package_version=?
                             AND package_release=?');

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

        # Now insert individual libs.
        my $sth = $dbh->prepare('INSERT INTO linkage_xref
                        (package_id, subpackage, arch, libname, filepath)
                        VALUES ( ?,?,?,?,? )');

        for my $l (@libs) {
            $sth->execute($package_id, $f->{_subpackage},
                          $f->{_arch}, $l, $f->path);
        }
        $dbh->disconnect;
    }
    else {
        warn "$ME: Cannot connect to mysql; dumping just txt";
    }

    # Now dump to text file, but only if there's something to dump
    if (@libs) {
        # Log to txt file, because mysql is currently only in test mode
        open my $fh_log, '>>', $Log
            or die "$ME: Cannot append to $Log: $!\n";
        for my $l (@libs) {
            print { $fh_log } join("\t", @nvr, $f->{_arch}, $f->{_subpackage},
                                   $l, $f->path), "\n";
        }
        close $fh_log
            or die "$ME: Error writing to $Log: $!\n";
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
