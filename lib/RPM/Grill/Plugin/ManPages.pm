# -*- perl -*-
#
# RPM::Grill::Plugin::ManPages - test for missing or bad man pages
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::ManPages;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order { 45 }

# One-line description of this plugin
sub blurb { return "checks for missing or badly-formatted man pages" }

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

    # FIXME: use what you need; delete what you don't

    #
    # Loop over each arch and subpackage
    #
    for my $rpm ($self->rpms) {
        for my $f ($rpm->files) {
            _check_manpage_correctness($f);
            _check_manpage_presence($f);
        }
    }
}


sub _check_manpage_correctness {
    my $f = shift;

    # FIXME: return if ! /usr/share/man
    return unless $f->path =~ m|^/usr/share/man/|;

    # FIXME: return if ! S_ISREG
    return unless $f->is_reg;

    # FIXME: check extension? .[num].gz/bz2/xz ? '*.[0-9n]*.gz'

    # FIXME: run manchecker
}


sub _check_manpage_presence {
    my $bin = shift;

    # FIXME: return if ! S_ISREG
    # FIXME: return if ! S_IXUSR (not executable by owner)
    # FIXME: return if ! important_directory (/bin, /sbin, /usr/sbin, /etc/init.d, FIXME: what about new init style?)
    return unless $bin->is_reg;
    return unless $bin->numeric_mode & 0x100;
    return unless $bin->path =~ m{^(/bin|/sbin|/usr/sbin|/etc/init\.d)/};

    # If we get here, it's a bin


    # FIXME: return if has_manpage()
    #          FIXME: need to check all other arches

    # FIXME: has_manpage() checks all subpackages in this arch

    for my $
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
