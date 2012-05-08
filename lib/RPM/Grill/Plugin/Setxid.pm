# -*- perl -*-
#
# RPM::Grill::Plugin::Setxid - check set[ug]id files and dirs
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::Setxid;

use base qw(RPM::Grill);
use RPM::Grill::dprintf;

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;

###############################################################################
# BEGIN user-configurable section

# Sequence number for this plugin
sub order {91}

# One-line description of this plugin
sub blurb { return "warns about set[ug]id programs not on the whitelist" }

# FIXME
sub doc {
    return <<"END_DOC" }
This plugin warns about setxid (setuid, setgid) files not on the
authorized whitelist. The whitelist is currently (2012-05-08)
maintained by Josh Bressers.
END_DOC

# Path to whitelist files
our $Whitelist_Dir = '/mnt/redhat/scripts/rel-eng/rpmdiff_data/suid';

# END   user-configurable section
###############################################################################

# Program name of our caller
( our $ME = $0 ) =~ s|.*/||;

#
# Calls $self->gripe() with problems
#
sub analyze {
    my $self = shift;    # in: FIXME

    for my $rpm ( $self->rpms ) {
        for my $f ( $rpm->files ) {
            # Only want setuid or setgid files (or directories)
            _check_setxid($f)   if $f->is_suid || $f->is_sgid;
        }
    }
}

###################
#  _check_setxid  #  Gripes if file not on list, or if anything is different
###################
sub _check_setxid {
    my $f    = shift;    # in: file obj

    dprintf "%s (0%o) %s\n", $f->{mode}, $f->numeric_mode, $f->{path};

    # First time through: read the whitelist
    # FIXME: how do we get the right tags? cpe? anything?
    # FIXME: read in appropriate whitelist
    # FIXME: compare

    #
    # Find file in whitelist.  If not found, gripe and return.
    #
    my $wl = _find_in_whitelist($f)
        or do {

        # Special case: setuid directories are always a bad idea
        if ( $f->is_dir && $f->is_suid ) {
            $f->gripe(
                {   code => 'SetuidDirectory',
                    diag =>
                        "Directory <var>$f->{path}</var> is setuid $f->{user}.  This is almost certainly a mistake.",
                }
            );
            return;
        }

        # Generate a friendly diagnostic.  Distinguish between
        # files and dirs, setuid/setgid.
        my $diag = ( $f->is_dir ? 'Directory' : 'File' );
        $diag .= ' <var>' . $f->{path} . '</var> is ';
        my @x;
        push @x, "setuid " . $f->{user}  if $f->is_suid;
        push @x, "setgid " . $f->{group} if $f->is_sgid;

        $diag .= join( ' and ', @x );
        $diag .= ' but is not on the setxid whitelist.';

        $f->gripe(
            {   code => 'UnauthorizedSetxid',
                diag => $diag,
            }
        );
        return;
    };

    #
    # File is on whitelist, but double-check permissions, owner, and group
    #
    for my $field (qw(mode user group)) {
        my $expected = $wl->{$field};
        my $actual = $f->{$field} || "[no $field]";
        if ( $actual ne $expected ) {
            $f->gripe(
                {   code => 'WrongFile' . ucfirst($field),
                    diag =>
                        "Incorrect $field on <var>$f->{path}</var>: expected $expected, got <var>$actual</var>",
                }
            );
        }
    }
}

#####################
#  _read_whitelist  #  Reads the setxid whitelist for this NVR
#####################
sub _read_whitelist {
    my $self = shift;

    return if exists $self->{_whitelist};

    # FIXME: get brew tags?
    # FIXME: get cpe?  How the heck do we get cpe?

    #printf "got here: %s -- %s -- %s\n", $self->nvr;

    # Whitelist is based on major, eg RHEL6, F15
    # FIXME: should we be more specific, eg RHEL6.1?
    # FIXME: should we use cpe? brew tags?
    my $whitelist = $Whitelist_Dir . '/' . $self->major_release;
    open my $whitelist_fh, '<', $whitelist
        or do {
        warn "$ME: WARNING: Cannot read $whitelist: $!";
        $self->{_whitelist} = undef;
        return;
        };

    # FIXME: read
    while ( my $line = <$whitelist_fh> ) {
        chomp $line;
        my @x = split "\t", $line;
        my @f = qw(path user group mode);
        my %x = map { $f[$_] => $x[$_] } ( 0 .. $#f );
        $x{_lineno} = $.;

        my $path = $x{path};
        if ( my $first = $self->{_whitelist}->{$path} ) {
            warn
                "$ME: $whitelist:$.: WARNING: Duplicate entry for $path (overrides previous entry on line $first->{_lineno})\n";
        }
        $self->{_whitelist}->{$path} = \%x;
    }
    close $whitelist_fh;
}

########################
#  _find_in_whitelist  #  Given a file, return its whitelist entry (if any)
########################
sub _find_in_whitelist {
    my $f    = shift;

    $f->rpm->grill->_read_whitelist();
    return $f->rpm->grill->{_whitelist}->{ $f->{path} };
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

=item   SetuidDirectory

There is no reason to have a Setuid directory. Perhaps you meant to
make it setB<g>id (group)?

=item   UnauthorizedSetxid

All setgid directories and setuid/setgid files must be enumerated in
a L<whitelist|https://FIXME.redhat.com/FIXME>. sdfdsf

=item   WrongFileMode

rpmgrill found a setuid/setgid file which is whitelisted, but
the file B<permissions don't match> what's specified in the whitelist.

=item   WrongFileUser

rpmgrill found a setuid/setgid file which is whitelisted, but
the file B<owner doesn't match> the one specified in the whitelist.

=item   WrongFileGroup

rpmgrill found a setuid/setgid file which is whitelisted, but
the file B<group doesn't match> the one specified in the whitelist.

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
