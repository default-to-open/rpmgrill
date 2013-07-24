# -*- perl -*-
#
# RPM::Grill::Util - standard non-OO helper functions for RPM::Grill
#
# $Id$
#
package RPM::Grill::Util;

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;
use CGI                         qw(escapeHTML);
use Encode                      qw(decode_utf8);
use utf8;

###############################################################################
# BEGIN user-configurable section

# END   user-configurable section
###############################################################################

# Program name of our caller
(our $ME = $0) =~ s|.*/||;

# For non-OO exporting of code, symbols
our @ISA         = qw(Exporter);
our @EXPORT      = qw(sanitize_text);
our @EXPORT_OK   = qw();
our %EXPORT_TAGS =   (all => \@EXPORT_OK);

###################
#  sanitize_text  #  Used in preparing gripes. Returns html-suitable text
###################
sub sanitize_text {
    my $text = shift;                           # in: text string

    # Although we assume that our input is UTF8, it might not be. This
    # converts non-UTF8 characters into '&nnn;'
    my $decoded = decode_utf8($text, Encode::FB_HTMLCREF);

    # Control characters except tab and newline: show as ^x
    $decoded =~ s{([[:cntrl:]])}{
        if ($1 eq "\t" || $1 eq "\n") {
            $1
        }
        else {
            sprintf("[^%c]",ord($1) ^ 0x40);      # eg 0x01 -> 0x41, "^A"
        }
    }ge;

    # Finally, since our string will be interpreted as html, fix
    # any < or > or &
    return escapeHTML($decoded);
}

1;


###############################################################################
#
# Documentation
#

=head1	NAME

RPM::Grill::Util - helper functions for RPM::Grill

=head1	SYNOPSIS

    use RPM::Grill::Util;

    ...

=head1	DESCRIPTION

Helper functions intended for use by RPM::Grill and its plugins

=head1	EXPORTED FUNCTIONS

=over   4

=item   B<sanitize_text>( STRING )

Converts an input string into something that can safely be shoved
into a DB and/or sent to a browser. This is used by plugins preparing
to gripe(), in order to make a string (such as an excerpt from a file)
safe for rendering.

It would be nice if gripe() did this itself, but Ed has deliberately
chosen to let plugins use HTML tags to highlight parts of messages.

=back

=head1	EXPORTED CONSTANTS

=head1	EXPORTABLE FUNCTIONS

=head1	FILES

=head1	SEE ALSO

L<Some::OtherModule>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
