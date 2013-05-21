# -*- perl -*-
#
# RPM::Grill::dprintf -- debugging printf
#
# $Id$
#
package RPM::Grill::dprintf;

use strict;
use warnings;

use Carp;

use RPM::Grill;

###############################################################################
# BEGIN user-configurable section

#
# USAGE: to debug, set $RPMGRILL_DEBUG in your environment.  Settings:
#
#     RPMGRILL_DEBUG=all              -- everything
#                   =setxid           -- just the Setxid plugin
#                   =setxid,buildlog  -- Setxid and BuildLog plugins
#
# Note that case does not matter.
#
our %debug;

# END   user-configurable section
###############################################################################

# Program name of our caller
( our $ME = $0 ) =~ s|.*/||;

our $VERSION = '0.01';

# For non-OO exporting of code, symbols
our @ISA    = qw(Exporter);
our @EXPORT = qw(dprintf);

sub dprintf {

    # First time through: initialize %debug based on $RPMGRILL_DEBUG
    if ( !keys %debug ) {
        if ( my $tmp = $ENV{RPMGRILL_DEBUG} ) {

            # FIXME: need a way to specify debugging for RPM::Grill itself
            #        and for the rpmgrill script
            if ( $tmp eq 'all' ) {
                $debug{all} = 1;
            }
            else {
                my @debug = RPM::Grill->matching_plugins( split( /\b/, $tmp ) );
                %debug = map { $_ => 1 } @debug;
            }
        }
        else {
            $debug{none} = 1;
        }
    }

    # FIXME: instead of this, replace this sub with a null stub?
    return if $debug{none};

    # Something to debug.  If it's 'all', proceed.  If it isn't, check
    # that our calling module is one that wants debugging.
    if ( !$debug{all} ) {
        my ( $package, undef, undef ) = caller();
        $package =~ s/^.*:://;    # RPM::Grill::Plugin::Foo -> Foo

        return unless $debug{$package};
    }

    CORE::printf("[%02d:%02d:%02d] ",(CORE::localtime)[2,1,0]); # timestamp
    CORE::printf(@_);
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

L<Some::OtherModule>

=head1	AUTHOR

Ed Santiago <ed@edsantiago.com>

=cut
