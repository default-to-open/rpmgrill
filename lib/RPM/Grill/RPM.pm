# -*- perl -*-
#
# FIXME  -  add package description here
#
# $Id$
#
package RPM::Grill::RPM;

use strict;
use warnings;

use version; our $VERSION = qv( '0.0.1' );

use Carp;
use File::Basename      qw(dirname);
use Moose;
use Moose::Util::TypeConstraints;

###############################################################################
# BEGIN user-configurable section

# Name, Version, Release (NVR), in that order
our @NVR_Fields = qw(name version release);

# END   user-configurable section
###############################################################################

# Program name of our caller
(our $ME = $0) =~ s|.*/||;

subtype 'RPMpath'
    => as Str
    => where { -e }
    => message { "path $_ does not exist" };

has 'path',       is => 'ro', isa => 'RPMpath', required => 1;
has 'dir',        is => 'ro', isa => 'Str', writer => '_set_dir';
has 'arch',       is => 'ro', isa => 'Str', writer => '_set_arch';
has 'subpackage', is => 'ro', isa => 'Str', writer => '_set_subpackage';

###########
#  BUILD  #  Invoked by Moose right after constructor. We set arch, subpackage
###########
sub BUILD {
    my $self = shift;

    my $path = $self->path;

    # Grumble. This should be done by subtype, but I can't figure out
    # how to give distinct error messages.
    $path =~ /\.rpm$/
        or croak "$ME: path '$path' does not end in .rpm";

    my ($arch, $subpackage) = $path =~ m{/ ([^/]+) / ([^/]+) / [^/]+\.rpm$}x
        or croak "$ME: path '$path' does not include /<arch>/<subpkg>/";

    $self->_set_arch($arch);
    $self->_set_subpackage($subpackage);

    $self->_set_dir( dirname($path) );

    use Data::Dumper; print Dumper($self);
}

#########
#  nvr  #  Returns n-v-r as string or list
#########
sub nvr {
    my $self = shift;

    # First time through
    if ( !exists $self->{nvr} ) {

        my $m = $self->metadata;

        for my $field (@NVR_Fields) {
            my $value = $m->get($field);
            defined $value
                or die "$ME: Internal error: No '$value' in RPM metadata";
            $self->{nvr}->{ lc $field } = $value;
        }
    }

    # Invoked with an arg?  Return just one of the fields.
    if (@_) {

        # This is the only arg we accept
        my $want = shift;
        croak "$ME: Invalid extra args (@_) in ->nvr()" if @_;

        my @match = grep {/^$want/i} @NVR_Fields
            or croak "$ME: ->nvr('$want'): Unknown N-V-R field";
        return $self->{nvr}->{ lc $match[0] };
    }

    # Return to caller, either as (n, v, r) or "n-v-r"
    my @nvr = map { $self->{nvr}->{$_} } @NVR_Fields;

    return wantarray
        ? @nvr
        : join( '-', @nvr );
}


##############
#  metadata  #  'rpm -qi' (info) for one specific rpm
##############
sub metadata {
    my $self       = shift;

    use    RPM::Grill::RPM::Metadata;
    return RPM::Grill::RPM::Metadata->new( $self->path );
}


################
#  capability  #  Returns the contents of one of the RPM.xxx files
################
sub capability {
    my $self = shift;
    my $cap  = shift;           # in: 'requires', 'provides', etc

    # eg ..../arch/subpackage/RPM.requires
    my $cap_file = $self->dir . '/RPM.' . $cap;
    -e $cap_file
        or croak "$ME: Capability file $cap_file does not exist";

    my @results;
    open my $cap_fh, '<', $cap_file
        or die "$ME: Internal error: Cannot read $cap_file: $!";
    while (<$cap_fh>) {
        chomp;
        push @results, $_;
    }
    close $cap_fh;

    return @results;
}

# Direct shortcut methods for the above capabilities files
sub requires  { push @_, 'requires';  goto &capability; }
sub provides  { push @_, 'provides';  goto &capability; }
sub obsoletes { push @_, 'obsoletes'; goto &capability; }
sub conflicts { push @_, 'conflicts'; goto &capability; }


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
