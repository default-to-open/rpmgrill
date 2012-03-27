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
our $VERSION = '0.01';

use Carp;

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

    # Create a text log. Always create it, as a signal that we've run.
    open my $fh_log, '>>', $Log
        or die "$ME: Cannot append to $Log: $!\n";

    for my $rpm ( $self->rpms ) {
        for my $f ( $rpm->files ) {
            $self->_gather_libs( $f, $fh_log )
        }
    }

    # Done with the log file.
    close $fh_log
        or die "$ME: Error writing to $Log: $!\n";
}

sub _gather_libs {
    my $self   = shift;
    my $f      = shift;                 # in: file obj
    my $fh_log = shift;                 # in: filehandle to log file

    my @libs = $f->elf_shared_libs
        or return;

    # Dump results to text file.
    for my $l (@libs) {
        print { $fh_log } join("\t",$f->arch,$f->subpackage,$l,$f->path),"\n";
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

=head1  DIAGNOSTICS

none

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
