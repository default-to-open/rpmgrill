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
our $VERSION = '0.01';

use Carp;
use RPM::Grill::Util		qw(sanitize_text);
use File::Basename                      qw(basename);

###############################################################################
# BEGIN user-configurable section

# Sequence number for this plugin
sub order {15}

# One-line description of this plugin
sub blurb { return "checks specfile for unapplied patches" }

sub doc {
    return <<"END_DOC" }
This module checks for unapplied patches and for bad values of fuzz.
END_DOC

# END   user-configurable section
###############################################################################

# Program name of our caller
( our $ME = $0 ) =~ s|.*/||;

#############
#  analyze  #  Main entry point
#############
sub analyze {
    my $self = shift;

    # Keep track of patches defined in preamble section
    my %Patch_Defined;

    # Read all lines in the specfile. Check for common problems.
    for my $line ( $self->specfile->lines ) {
        my $s = $line->content;

        if ( $line->section eq '%preamble' ) {

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
                                excerpt => sanitize_text("$Patch_Defined{$n}\n$s"),
                                path    => basename( $self->specfile->path ),
                                lineno  => $line->lineno,
                            },
                            diag    => "Duplicate definition of Patch$n",

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
        if ( $line->section eq '%prep' ) {

            # FIXME: also check for commented-out %patch lines
        }

        # warn about invalid patch fuzz
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
                            excerpt => sanitize_text($s),
                            path    => basename( $self->specfile->path ),
                            lineno  => $line->lineno,
                        },
                        diag    => $msg,
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

=head1  DIAGNOSTICS

=over   4

=item   DuplicatePatch

Multiple definitions seen for C<PatchNN>.
This is often caused by a C<%if> in the specfile, but
it could also be an unintentional duplication.

=item   BadPatchFuzz

Overriding patch's fuzz factor is a bad idea. It means: "those
three lines of context that diff provides? Toss some of those
away, and try again". You can end up with code that compiles
but is silently corrupt. There really is no reason for this.
Why not take the time to regenerate your patches?

=back

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
