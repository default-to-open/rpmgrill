# -*- perl -*-
#
# RPM::Grill::Plugin::DanglingSymlinks - check for dangling symlinks
#
# $Id$
#
# Real-world packages that trigger errors in this module:
#    https://errata.devel.redhat.com/rpmdiff/show/46457?result_id=642496
#    seamonkey-1.0.9-66.el4_8 compared to seamonkey-1.0.9-65.el4_8
#    New file usr/src/debug/mozilla/dist/include/liveconnect/nsILiveconnect.h
#    is a dangling symlink (to ../../../js/src/liveconnect/nsILiveconnect.h)
#    on i386 x86_64 ia64 ppc s390 s390x
#
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::DanglingSymlinks;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order {81}

# One-line description of this plugin
sub blurb { return "checks for dangling symlinks" }

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

    return;    # FIXME 2010-12-17: this is too hard to do

    # FIXME: use what you need; delete what you don't

    #
    # Loop over each arch and subpackage
    #
    for my $arch ( $self->non_src_arches ) {
        $self->find_dangling_symlinks($arch);
    }
}

sub find_dangling_symlinks {
    my $self = shift;
    my $arch = shift;

    for my $subpkg ( $self->subpackages($arch) ) {
        for my $f ( grep { $_->is_symlink } $self->files( $arch, $subpkg ) ) {

            # Gather dangling symlinks
            # ...
            $self->check_link($f);
        }
    }
}

sub check_link {
    my $self = shift;
    my $f    = shift;

    #
    # The logic here is:
    #
    #   * start at the symlink's parent directory
    #   * traverse each component of the symlink, going up/down as needed
    #
    # Standard symlink stuff.  The trick is that the link dest may be in
    # a different subpackage, so we need to track a lot of LHSs at once.
    my $path    = $f->{path};     # FIXME
    my $linkval = $f->readlink;

    # Let the filesystem do the walking.  If dest exists, yippee!
    return if -e $path;

    # Dest does not exist, at least not trivially.
    my @lhs = split '/', $path;
    my @rhs = split '/', $linkval;

    # If symlink is absolute path, reset LHS
    if ( @rhs && !$rhs[0] ) {
        @lhs = shift @rhs;        # (empty component)
    }

    printf " check : %s  ->  %s\n", join( ' / ', @lhs ), join( ' / ', @rhs );

    while (@rhs) {
        my $item = shift @rhs;
        next if $item eq '.' || $item eq '';    # '/./' and '//' are NOPs

        if ( $item eq '..' ) {

            # Going up.  But never go beyond the top level.
            pop @lhs unless @lhs == 1;
        }

        # Gah.  This is tricky, because we need to readlink(). FIXME
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

none (yet)

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
