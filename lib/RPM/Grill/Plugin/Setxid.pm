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
use File::Spec::Functions   qw(catfile);
use RPM::Grill::Util        qw(sanitize_text);

###############################################################################
# BEGIN user-configurable section

# Sequence number for this plugin
sub order {91}

# One-line description of this plugin
sub blurb { return "warns about set[ug]id programs not on the whitelist" }

sub doc {
    return <<"END_DOC" }
This plugin warns about setxid (setuid, setgid) files not on the
authorized whitelist.
END_DOC

# Path to whitelist files. This is a directory containing one file
# per software release: FC17, FC18, FC19. See _read_whitelist() below
# for a description of the file contents.
#
# FIXME: there are better ways of doing this, e.g. using a config file
# to determine the path, or some RPC mechanism, or many other cleaner
# ways that don't require a hand-maintained flatfile. Fix when convenient.
our $Whitelist_Dir = $ENV{RPMGRILL_SETXID_WHITELIST_DIR}
                  ||  catfile($ENV{HOME}, qw(.rpmgrill plugins setxid));

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

    # Symlinks are listed in the manifest, but their permissions aren't
    # actually a security risk. Ignore them.
    return if $f->is_symlink;

    dprintf "%s (0%o) %s\n", $f->{mode}, $f->numeric_mode, $f->{path};


    # First time through: read the whitelist
    # FIXME: how do we get the right tags? cpe? anything?
    # FIXME: read in appropriate whitelist
    # FIXME: compare

    #
    # Find file in whitelist.  If found, compare attributes.
    #
    if (my $wl = _find_in_whitelist($f)) {
        for my $attribute (qw(mode user group)) {
            my $expected = $wl->{$attribute};
            my $actual   = $f->{$attribute} || "[no $attribute]";
            if ($actual ne $expected) {
                my $Attribute = ucfirst($attribute);
                $f->gripe({
                    code => "WrongFile$Attribute",
                    diag => "Incorrect $attribute on <var>$f->{path}</var>: expected $expected, got <var>$actual</var>",
                });
            }
        }

        return;
    }

    #
    # File not found in whitelist.
    #
    # Special case: setuid directories are always a bad idea
    if ( $f->is_dir && $f->is_suid ) {
        $f->gripe({
            code => 'SetuidDirectory',
            diag => "Directory <var>$f->{path}</var> is setuid $f->{user}. This is almost certainly a mistake.",
        });
        return;
    }

    # Generate a friendly diagnostic.  Distinguish between
    # files and dirs, setuid/setgid.
    my $diag = ( $f->is_dir ? 'Directory' : 'File' );
    $diag .= ' <var>' . sanitize_text($f->{path}) . '</var> is ';
    my @x;
    push @x, "setuid " . $f->{user}  if $f->is_suid;
    push @x, "setgid " . $f->{group} if $f->is_sgid;

    $diag .= join( ' and ', @x );
    $diag .= ' but is not on the setxid whitelist';

    # And if this file path is whitelisted under a different package,
    # say so. Maybe this is an accidental subpackage move; or maybe
    # a new package is providing the same binary intentionally; or
    # maybe someone is trying to pull a fast one.
    if (my @p = _any_packages_whitelisting($f)) {
        $diag .= sprintf(" for <tt>%s</tt>", sanitize_text($f->rpm->nvr('name')));
        $diag .= sprintf(" (it is whitelisted under <tt>%s</tt>)",
                         join('</tt> and <tt>', map { sanitize_text($_) } @p));
    }

    $f->gripe({
        code => 'UnauthorizedSetxid',
        diag => $diag . '.',
    });
    return;
}

#####################
#  _read_whitelist  #  Reads the setxid whitelist for this NVR
#####################
sub _read_whitelist {
    my $self = shift;

    return if exists $self->{_whitelist};

    #printf "got here: %s -- %s -- %s\n", $self->nvr;

    # Whitelist is based on major, eg RHEL6, F15
    # FIXME: should we be more specific, eg RHEL6.1?
    # FIXME: should we use cpe?  How the heck do we get cpe?
    # FIXME: get build tags?
    my $whitelist = catfile $Whitelist_Dir, $self->major_release;
    open my $whitelist_fh, '<', $whitelist or do {
        warn "$ME: WARNING: Unable to read whilelist file: '$whitelist' - $!\n",
             "To suppress this warning: \n",
             "     mkdir -p $Whitelist_Dir \n",
             "     touch $whitelist \n ";

        $self->{_whitelist} = undef;
        return;
    };

    #
    # Until August 2012, the format of the whitelist file was:
    #
    #         <path>         <owner> <group> <mode>   [separated by 1 tab]
    #  e.g.   /usr/bin/sudo  root    root    ---s--x--x
    #
    # Through May 2013, the format of the whitelist is:
    #
    #         # <comments prefixed by octothorpe>
    #         <mode>       <owner> <group>  <path> [separated by whitespace]
    #  e.g.   ---s--x--x   root    root     /usr/bin/sudo
    #
    # As of May 2013 we're experimenting with a new format in which
    # the first field is the package name:
    #
    #        sudo            ---s--x--x   root    root     /usr/bin/sudo
    #
    # To ease the transition, this code can handle either format.
    #
  LINE:
    while ( my $line = <$whitelist_fh> ) {
        chomp $line;

        next LINE       if $line =~ /^\s*$/;    # Skip blank lines
        next LINE       if $line =~ /^\s*#/;    # Skip comment-only lines

        my @values = split /\s+/, $line;

        # Assume the new format...
        my @fields = qw(package mode user group path);
        # ...but if there are only four elements, use a nil package
        unshift @values, ''             if @values < 5;

        my %value = map { $fields[$_] => $values[$_] } ( 0 .. $#fields );
        $value{_lineno} = $.;

        # Look for dups.
        # FIXME: this might actually be legit: multiple packages might
        # provide /usr/bin/crontab or /usr/lib/sendmail
        my $path = $value{path};
        if (my @dup = grep { $self->{_whitelist}{$_}{$path} } sort keys %{$self->{_whitelist}}) {
            warn "$ME: $whitelist:$.: WARNING: Duplicate entry for $path (present in packages @dup, $value{package})\n";
        }

        $self->{_whitelist}{$value{package}}{$path} = \%value;
    }
    close $whitelist_fh;
}

########################
#  _find_in_whitelist  #  Given a file, return its whitelist entry (if any)
########################
sub _find_in_whitelist {
    my $f    = shift;

    $f->rpm->grill->_read_whitelist();

    my $whitelist = $f->rpm->grill->{_whitelist};
    my $f_package = $f->rpm->nvr('name');
    my $f_path    = $f->{path};

    # The best case: there's a whitelist, and this file is on it, under
    # the appropriate package.
    if (my $pkg_whitelist = $whitelist->{$f_package}) {
        if (my $entry = $pkg_whitelist->{$f_path}) {
            return $entry;
        }
    }

    return;
}

################################
#  _any_packages_whitelisting  #  Does _any_ package whitelist this setxid file?
################################
sub _any_packages_whitelisting {
    my $f = shift;

    $f->rpm->grill->_read_whitelist();
    my $whitelist = $f->rpm->grill->{_whitelist};
    my $f_path    = $f->{path};

    my @p = grep { exists $whitelist->{$_}{$f_path} } sort keys %$whitelist;

    return @p;
}

1;

###############################################################################
#
# Documentation
#

=head1  NAME

FIXME - FIXME

=head1  SYNOPSIS

    use Fixme::FIXME;

    ....

=head1  DESCRIPTION

FIXME fixme fixme fixme

=head1  CONSTRUCTOR

FIXME-only if OO

=over 4

=item B<new>( FIXME-args )

FIXME FIXME describe constructor

=back

=head1  METHODS

FIXME document methods

=over 4

=item   B<method1>

...

=item   B<method2>

...

=back


=head1  EXPORTED FUNCTIONS

=head1  EXPORTED CONSTANTS

=head1  EXPORTABLE FUNCTIONS

=head1  FILES

=head1  DIAGNOSTICS

=over   4

=item   SetuidDirectory

There is no reason to have a Setuid directory. Perhaps you meant to
make it setB<g>id (group)?

=item   UnauthorizedSetxid

rpmgrill found a setuid/setgid file which is B<not on the whitelist>.

All setgid directories and setuid/setgid files must be enumerated in
a trusted whitelist. This whitelist is maintained by FIXME.

The whitelist lists both file path and package. It is possible for this
test to trigger if your RPM provides a setxid file that another package
also provides, eg C</usr/bin/crontab>. If this is intentional and desired,
the whitelist maintainer can add your RPM+file as well.

=item   WrongFileMode

rpmgrill found a setuid/setgid file which is whitelisted, but
the file B<permissions don't match> what's specified in the whitelist.

All setgid directories and setuid/setgid files must be enumerated in
a trusted whitelist. This whitelist is maintained by FIXME.

=item   WrongFileUser

rpmgrill found a setuid/setgid file which is whitelisted, but
the file B<owner doesn't match> the one specified in the whitelist.

All setgid directories and setuid/setgid files must be enumerated in
a trusted whitelist. This whitelist is maintained by FIXME.

=item   WrongFileGroup

rpmgrill found a setuid/setgid file which is whitelisted, but
the file B<group doesn't match> the one specified in the whitelist.

All setgid directories and setuid/setgid files must be enumerated in
a trusted whitelist. This whitelist is maintained by FIXME.

=back

=head1  SEE ALSO

L<>

=head1  AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
