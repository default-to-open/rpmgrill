# -*- perl -*-
#
# RPM::Grill::Plugin::Manifest - FIXME
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::Manifest;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = "0.01";

use Carp;

###############################################################################
# BEGIN user-configurable section

# FIXME FIXME FIXME: this is intended to catch something like
#     https://errata.devel.redhat.com/rpmdiff/show/48150?result_id=695776
# ...in which mailman ships /usr/lib/mailman/Mailman but doesn't own it,
# i.e. this is in the specfile:
#        /usr/lib/mailman
#        /usr/lib/mailman/Mailman/Archiver
#                         ^^^^^^^---- not in specfile

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order {999}    # FIXME

# One-line description of this plugin
sub blurb { return "checks for FIXME FIXME" }

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

    #
    # Pass 1: track all directory files in all RPM manifests..
    #
    my %is_owned;
    for my $rpm ( $self->rpms ) {
        for my $f ( $rpm->files ) {
            if ($f->is_dir) {
                my $d = $f->path;
                $d =~ s{/$}{};

                $is_owned{ $d } = 1;
            }
        }
    }

    # Helper function for pass 2: returns true if any parent
    # directory of $d is owned by our package.
    my $should_be_owned = sub {
        my $d = shift;

        while ($d =~ s{/[^/]+$}{}) {
            return 1 if $is_owned{$d};
        }
        return;
    };

    #
    # Pass 2: for each owned directory, check if there's a gap
    # in its parents.
    #
    # FIXME: optimize. This is pretty inefficient.
    #
    my %griped;
    for my $d (sort keys %is_owned) {
        while ($d =~ s{/[^/]+$}{}) {
            if (! $is_owned{$d} && $should_be_owned->($d)) {
                unless ($griped{$d}++) {
                    $self->gripe({
                        code => 'UnownedDirectory',
                        arch => 'src',
                        diag => "Unowned mid-level directory <tt>$d</tt>",
                    });
                }
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
