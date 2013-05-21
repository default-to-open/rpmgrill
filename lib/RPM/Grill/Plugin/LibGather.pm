# -*- perl -*-
#
# RPM::Grill::Plugin::LibGather - example of using rpmgrill for data collection
#
# This plugin does not gripe; it just has side effects. It just creates
# a log file containing a list of files and the shared libraries they
# link against. This could be saved into a DB by our caller, and another
# tool can then search something like "what packages rely on libfoo.so?"
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
sub order { 12 }

# One-line description of this plugin
sub blurb { return "gathers info about libs used by this pkg" }

sub doc { return <<"END_DOC" };
This module does not report any tests. It is an internal data-collection
module used to gather information which can later be used by other tools.
END_DOC

our $Log = 'rpmgrill.lib-linkage.txt';

# END   user-configurable section
###############################################################################

# Program name of our caller
(our $ME = $0) =~ s|.*/||;

#############
#  analyze  #  Main entry point for this plugin
#############
sub analyze {
    my $self = shift;

    # Create a text log. Always create it, even if we end up not writing
    # anything to it, because that's a signal that we've run.
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
