# -*- perl -*-
#
# RPM::Grill::Plugin::Systemd - RHEL7 uses systemd (bz802557)
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::Systemd;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = "0.01";

use Carp;

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order { 80 }

# One-line description of this plugin
sub blurb { return "checks for sysv/xinetd init scripts" }

# FIXME
sub doc {
    return <<"END_DOC" }
FIXME FIXME FIXME
END_DOC

# END   user-configurable section
###############################################################################

# Program name of our caller
( our $ME = $0 ) =~ s|.*/||;

#
# input: a RPM::Grill object, blessed into this package.
# return value: not checked.
#
# Calls $self->gripe() with problems.  Return value is meaningless,
# but code can die/croak if necessary -- it will be trapped in an eval.
#
sub analyze {
    my $self = shift;

    # This is only applicable to RHEL7 (and above?)
    return unless $self->major_release =~ /^RHEL(\d+)/ && $1 >= 7;

    # Loop over all rpms, and all files in all rpms
    for my $rpm ( $self->rpms ) {
        for my $f ( $rpm->files ) {
            if ( $f->is_reg && $f->{path} =~ m{^/etc/(xinetd\.d|init\.d)/}) {
                $self->gripe({
                    code    => 'NonSystemdFile',
                    diag    => "Non-systemd file",
                    context => { path => $f->{path} },
                });
            }
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
