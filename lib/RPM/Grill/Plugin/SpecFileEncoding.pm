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
our $VERSION = '0.01';

use Carp;
use RPM::Grill::Util		qw(sanitize_text);
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
This module warns about non-UTF8 characters in the specfile.
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
        my $s = $line->content;

        # GAH. This is way more complicated than it needs to be,
        # because RHEL6 ships with a buggy Encode.pm:
        #    https://rt.cpan.org/Ticket/Display.html?id=51204
        # As soon as we can run this tool on RHEL7, or RHEL6 gets a
        # fixed Encode.pm, feel free to revert this file back to
        # a (much cleaner) pre-2013-04-19 version.

        # decode_utf8() replaces non-utf8 characters with &#nnn; but we may
        # already have such sequences in our string. Escape them before
        # running decode_utf8.
        $s =~ s{&}{&amp;}g;
        my $s2 = decode_utf8($s, Encode::FB_HTMLCREF);

        # We look for &#nnn; sequences. If we see any, gripe. For
        # readability, take a gamble on the assumption that the
        # input is ISO-8859-1. We can then show chr(241) as &ntilde;
        # If our assumption is false, this may end up causing more
        # confusion than it's worth. Let's assess over time, and
        # perhaps just show all characters as [XX].
        if ($s2 =~ s{&#(\d+);}{
            my $c = $1;
            my $replacement = sprintf("<u>[%02X]</u>", $c);

            if (my $ent = encode_entities( chr($c) )) {
                if ($ent !~ /^&#\d+;$/) {
                    # eg byte 241 becomes "&ntilde;"
                    $replacement = "<u>$ent</u>";
                }
            }
            $replacement;
        }ge) {
            my $path   = basename( $self->specfile->path );
            my $lineno = $line->lineno;

            # Gaaaah. Those ampersands we escaped a few lines ago? Unescape
            # them. Then escape HTML, then (sigh) unescape any underlines
            # we may have added.
            $s2 =~ s{&amp;}{&}g;
            my $excerpt = sanitize_text($s2);
            $excerpt =~ s{&lt;u&gt;&amp;(.*?)&lt;/u&gt;}{<u>&$1</u>}g;
            $excerpt =~ s{&lt;u&gt;(\[..\])&lt;/u&gt;}{<u>$1</u>}g;

            # One gripe per line.
            $self->gripe(
                {   code    => 'NonUtf8',
                    arch    => 'src',
                    diag    => 'non-UTF8 content',
                    context => {
                        excerpt => $excerpt,
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
