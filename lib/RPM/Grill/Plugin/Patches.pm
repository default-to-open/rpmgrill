# -*- perl -*-
#
# Patches - check spec file for unapplied patches
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::Patches;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = "0.01";

use Carp;
use File::Basename qw(basename);

###############################################################################
# BEGIN user-configurable section

# Sequence number for this plugin
sub order {15}

# One-line description of this plugin
sub blurb { return "checks specfile for unapplied patches" }

sub doc {
    return <<"END_DOC" }
FIXME: check for unapplied patches
FIXME: check for fuzz
END_DOC

# END   user-configurable section
###############################################################################

# Program name of our caller
( our $ME = $0 ) =~ s|.*/||;

#
# FIXME
#
sub analyze {
    my $self = shift;    # in: FIXME

    # Keep track of patches defined in preamble section
    my %Patch_Defined;

    # Read all lines in the specfile. Check for common problems.
    for my $line ( $self->specfile->lines ) {
        my $s = $line->content;

        if ( $line->section eq 'preamble' ) {

            # Track all 'patch<n>: foo.patch' lines.
            if ( $s =~ /^\s*patch(\d*):\s+\S+\s*$/i ) {
                my $n = $1;
                $n = '' if ! defined $n; # (empty, eg 'Patch: foo.patch')

                # Gripe if <n> has already been used
                if ( exists $Patch_Defined{$n} ) {
                    $self->gripe(
                        {   code    => 'DuplicatePatch',
                            arch    => 'src',
                            context => {
                                path   => basename( $self->specfile->path ),
                                lineno => $line->lineno,
                            },
                            diag    => "Duplicate definition of Patch$n",
                            excerpt => "$Patch_Defined{$n}\n$s",

                        # FIXME: explain that this is OK if ifdef'ed
                        # FIXME: if there's a commented-out patch, offer hint?
                        }
                    );
                }
                $Patch_Defined{$n} = $s;
            }

            # FIXME: also check for commented-out Patch: lines
        }

        # In %prep section: check for applied patches
        if ( $line->section eq 'prep' ) {

            # FIXME: also check for commented-out %patch lines
        }

        # rpmdiff bz692142: warn about invalid patch fuzz
        #
        # Warn if we see this anywhere in the specfile
        if ( $s =~ /^\s*%\s*(define|global)\s+_default_patch_fuzz\s+(\d+)/ ) {
            my $fuzz = $2;

            # FIXME: don't warn if setting to 0, even though it's NOP on RHEL6?
            if ($fuzz > 0) {
                my $msg  = "Do not override _default_patch_fuzz";
                if ( $fuzz > 2 ) {
                    $msg .= "; *ESPECIALLY* not with anything >2";
                }
                $msg .= ". Please redo your patches instead.";

                $self->gripe(
                    {   code    => 'BadPatchFuzz',
                        arch    => 'src',
                        context => {
                            path   => basename( $self->specfile->path ),
                            lineno => $line->lineno,
                        },
                        diag    => $msg,
                        excerpt => $s,
                    }
                );
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

L<Fixme::Xxxx>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
