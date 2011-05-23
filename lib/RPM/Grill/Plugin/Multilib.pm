# -*- perl -*-
#
# RPM::Grill::Plugin::Multilib - check for multilib conflicts
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::Multilib;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = "0.01";

use Carp;

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order {20}    # FIXME

# One-line description of this plugin
sub blurb { return "reports multilib conflicts" }

sub doc {
    return <<"END_DOC" }
Blah blah blah
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

    for my $rpm64 (grep { $_->is_64bit } $self->rpms ) {
        my @files64 = $rpm64->files;

        for my $rpm32 ($rpm64->multilib_peers) {
            my @files32 = $rpm32->files;

            # FIXME: compare files
            # FIXME: in which directories?
            for my $file64 (@files64) {
                if (my @match = grep { $_->path eq $file64->path } @files32) {
                    $self->_compare( $file64, $_ )          for @match;
                }
            }
        }
    }
}


sub _compare {
    my $self   = shift;
    my $file64 = shift;
    my $file32 = shift;

    return if $file32->md5sum eq $file64->md5sum;

    # md5sums differ. This means the files are different.
    # If both files have a different "rpm color", that's OK.
    my $color64 = $file64->color;
    my $color32 = $file32->color;

    if ($color64 =~ /^\d+$/) {
        if ($color32 =~ /^\d+$/) {
            if (($color64 & $color32) == 0) {
                return;
            }
        }
    }

    # Files have the same (or no) rpm color. Gripe.
    my $path = $file64->path;

    my $arch64 = $file64->arch;
    my $arch32 = $file32->arch;

    $self->gripe({
        code => 'MultilibMismatch',
        diag => "Files differ: {$arch32,$arch64}$path",
        arch => $arch64,
    });
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
