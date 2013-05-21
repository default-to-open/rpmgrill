# -*- perl -*-
#
# RPM::Grill::Plugin::Manifest - check for problems with list of shipped files
#
# This is intended to catch a case such as mailman-2.1.12-14.el6_0.2 ,
# in which mailman ships /usr/lib/mailman/Mailman but doesn't own it,
# i.e. this is in the specfile:
#
#        /usr/lib/mailman
#        /usr/lib/mailman/Mailman/Archiver
#                         ^^^^^^^---- not in specfile
#
package RPM::Grill::Plugin::Manifest;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;
use RPM::Grill::Util		qw(sanitize_text);

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order { 30 }

# One-line description of this plugin
sub blurb { return "checks for rare problems in RPM manifests" }

# Slightly more complete documentation on this test
sub doc {
    return <<"END_DOC" }
This module runs a variety of tests on the RPM manifest, i.e.
the list of files shipped in an RPM.
END_DOC

# List of mount points / directories which should be left to the end user.
our @Non_FHS = qw(
                     /home
                     /media
                     /mnt
                     /root
                     /usr/local
                     /(?:usr/|var/)?tmp
             );
our $Non_FHS = join('|', @Non_FHS);


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

    # FHS = Filesystem Hierarchy Standard, eg the spec that says we
    # shouldn't install into /usr/local : See http://www.pathname.com/fhs/
    my %non_fhs;

    # bz802557 : check for non-systemd files
    my %non_systemd;

    #
    # Pass 1: track all directory files in all RPM manifests
    #
    my %is_owned;
    for my $rpm ( $self->rpms ) {
        for my $f ( $rpm->files ) {
            my $path = $f->path;

            # Check for /usr/local
            if ($path =~ m{^($Non_FHS)(/.*|$)}o) {
                my ($parent, $rest) = ($1, $2);
                my $highlighted_name = "<b>" . sanitize_text($parent) . "</b>" . sanitize_text($rest);
                $non_fhs{$f->arch}{$f->subpackage}{$highlighted_name} = 1;
            }


            if ($f->is_dir) {
                $path =~ s{/$}{};

                $is_owned{ $path } = 1;
            }

            # bz802557: check for non-systemd files
            if ($self->_require_systemd) {
                if ( $path =~ m{^/etc/(xinetd\.d|init\.d)/}) {
                    $non_systemd{$f->arch}{$f->subpackage}{$path} = 1;
                }
            }

            # bz802554: check for files that should be in /usr
            if ($self->_require_usr_merge) {
                if ($path =~ m{^(/bin|/sbin|/lib|/lib64)/}) {
                    my $where = $1;
                    $self->gripe({
                        code       => 'MoveToUsr',
                        arch       => $f->arch,
                        subpackage => $f->subpackage,
                        diag       => "$where no longer exists; please move <tt>$path</tt> to <tt><b>/usr</b>$where</tt>",
                    });
                }
            }

            # bz853078: owner and group of (non-sxid) bin files must be root
            _check_bin_permissions($f);
        }
    }

    # Helper function for pass 2: returns true if any parent
    # directory of $d is owned by our package.
    my $should_be_owned = sub {
        my $d = shift;

        while ($d =~ s{/[^/]+$}{}) {
            return 1 if $is_owned{$d};
        }
        return;
    };

    #
    # Pass 2: for each owned directory, check if there's a gap
    # in its parents.
    #
    # FIXME: optimize. This is pretty inefficient.
    #
    my %griped;
    for my $d (sort keys %is_owned) {
        while ($d =~ s{/[^/]+$}{}) {
            if (! $is_owned{$d} && $should_be_owned->($d)) {
                unless ($griped{$d}++) {
                    $self->gripe({
                        code => 'UnownedDirectory',
                        arch => 'src',
                        diag => "Unowned mid-level directory <tt>$d</tt>",
                    });
                }
            }
        }
    }

    # Report non-FHS files
    for my $arch (sort keys %non_fhs) {
        for my $subpackage (sort keys %{$non_fhs{$arch}}) {
            my @files = sort keys %{ $non_fhs{$arch}{$subpackage} };

            my $gripe = {
                code       => 'NonFHS',
                arch       => $arch,
                subpackage => $subpackage,
                diag       => "FHS-protected director",
            };

            # Just 1? Report it in the diag. More? List files in excerpt.
            if (@files == 1) {
                $gripe->{diag} .= "y <tt>@files</tt>";
            }
            else {
                $gripe->{diag} .= "ies:";
                $gripe->{context} = { excerpt => \@files },
            }

            $self->gripe( $gripe );
        }
    }

    # Report non-systemd files
    for my $arch (sort keys %non_systemd) {
        for my $subpackage (sort keys %{$non_systemd{$arch}}) {
            my @files = sort keys %{ $non_systemd{$arch}{$subpackage} };

            my $gripe = {
                code       => 'NonSystemdFile',
                arch       => $arch,
                subpackage => $subpackage,
                diag       => "Non-systemd file",
            };

            if (@files == 1) {
                $gripe->{diag} .= ": <tt>@files</tt>";
            }
            else {
                $gripe->{diag} .= "s:";
                $gripe->{context} = { excerpt => \@files },
            }

            $self->gripe( $gripe );
        }
    }
}


############################
#  _check_bin_permissions  #
############################
sub _check_bin_permissions {
    my $f = shift;                              # in: file obj

    # Not interested in SRPM files
    return if $f->arch eq 'src';

    # Only interested in files installed under certain bin directories,
    # and in ELF .so libraries
    my $what;
    if ($f->path =~ m{^(/bin|/usr/bin|/sbin|/usr/sbin)/}) {
        $what = "files in $1";
    }
    elsif ($f->is_elf && $f->basename =~ /\.so/) {
        $what = "ELF libraries";
    }
    return if !$what;

    # Check User
    unless ($f->is_suid) {
        if ((my $u = $f->user) ne 'root') {
            $f->gripe({
                code => 'BinfileBadOwner',
                diag => "Owned by '<tt>$u</tt>'; $what must be owned by root",
            });
        }
    }

    # Check Group
    unless ($f->is_sgid) {
        if ((my $g = $f->group) ne 'root') {
            $f->gripe({
                code => 'BinfileBadGroup',
                diag => "Owned by group '<tt>$g</tt>'; $what must be group 'root'",
            });
        }
    }
}

###############################################################################
# BEGIN helpers

######################
#  _require_systemd  #  Does this OS release require systemd?
######################
sub _require_systemd {
    my $self = shift;

    $self->{_plugin_state}{require_systemd}
        //= $self->major_release_ge('RHEL7')
         || $self->major_release_ge('F17');
}

########################
#  _require_usr_merge  #  Does this OS release do away with /bin, /sbin, /lib*
########################
sub _require_usr_merge {
    my $self = shift;

    $self->{_plugin_state}{require_usr_merge}
        //= $self->major_release_ge('RHEL7')
         || $self->major_release_ge('F17');
}

# END   helpers
###############################################################################

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

=item   UnownedDirectory

Your package claims ownership of the parent directory, and at least
one subdirectory inside the complained-about directory, but not the
complained-about directory itself. You probably need to fix this
using the rpm C<%dir> directive in your specfile.

See L<https://fedoraproject.org/wiki/Packaging:UnownedDirectories>

=item   NonFHS

Your package ships a file or directory underneath a protected
part of the Filesystem Hierarchy Standard (e.g. C</usr/local>).
See L<http://www.pathname.com/fhs/>.

=item   NonSystemdFile

As of Fedora 17, C</etc/init.d> is obsolete. All packages should be
using B<systemd>.
See L<https://fedoraproject.org/wiki/Packaging:Systemd>

=item   MoveToUsr

Fedora 17 and RHEL7 are doing away with C</bin>, C</sbin>, and C</lib*>.
Your package has one or more files that are still living there. These
should be moved to the corresponding place under C</usr>.
See L<freedesktop.org|http://www.freedesktop.org/wiki/Software/systemd/TheCaseForTheUsrMerge>.

=item   BinfileBadOwner

Non-setuid files under C</bin>, C</usr/bin>, C</sbin>, or C</usr/sbin>;
and ELF DSOs; must be owned by user root.

=item   BinfileBadGroup

Non-setgid files under C</bin>, C</usr/bin>, C</sbin>, or C</usr/sbin>;
and ELF DSOs; must be owned by group root.

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
