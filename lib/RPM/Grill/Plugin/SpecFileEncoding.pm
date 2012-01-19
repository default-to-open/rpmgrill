# -*- perl -*-
#
# SpecFileEncoding -- check for non-UTF-8 characters in the specfile
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::SpecFileEncoding;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = "0.01";

use Carp;
use CGI qw(escapeHTML);
use Encode qw(decode_utf8);
use File::Basename qw(basename);
use HTML::Entities;

###############################################################################
# BEGIN user-configurable section

# Sequence number for this plugin
sub order {10}

# One-line description of this plugin
sub blurb { return "warns about non-UTF-8 characters in a specfile" }

# FIXME
sub doc {
    return <<"END_DOC" }
FIXME FIXME FIXME
END_DOC

# END   user-configurable section
###############################################################################

# Program name of our caller
( our $ME = $0 ) =~ s|.*/||;

sub analyze {
    my $self = shift;    # in: FIXME

    #
    # find the specfile
    #
    for my $line ( $self->specfile->lines ) {
        my $s = escapeHTML( $line->content );

        # decode_utf8() calls our helper function when it sees non-utf8
        # characters.  Our helper marks this, and returns a formatted
        # version of the char.  We assume an input encoding ISO-8859-1
        # for converting to HTML entities.  This may be a bad idea.
        my @barfed;
        my $s2 = decode_utf8(
            $s,
            sub {
                my $c = shift;
                push @barfed, $c;
                if ( my $ent = encode_entities( chr($c) ) ) {
                    return "<u>$ent</u>";
                }
                else {
                    return sprintf( "<u>[%02X]</u>", $c );
                }
            }
        );

        # Helper function adds each invalid char to @barfed
        if (@barfed) {
            my $path   = basename( $self->specfile->path );
            my $lineno = $line->lineno;

            # One gripe per line.
            $self->gripe(
                {   code    => 'NonUtf8',
                    arch    => 'src',
                    diag    => 'non-UTF8 content',
                    context => {
                        excerpt => $s2,
                        path    => $path,
                        lineno  => $lineno,
                    },

                    # FIXME: try hint => "something appropriate to this char"?
                }
            );
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

=item   NonUtf8

Packaging guidelines require that the rpm specfile be encoded in UTF-8.
This message code indicates that your specfile includes characters
that are not valid in UTF-8.

FIXME: link to packaging guidelines

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
