# -*- perl -*-
#
# RPM::Grill::Plugin::Manifest - check for problems with list of shipped files
#
# This is intended to catch something like:
#
#     https://errata.devel.redhat.com/rpmdiff/show/48150?result_id=695776
#
# ...in which mailman ships /usr/lib/mailman/Mailman but doesn't own it,
# i.e. this is in the specfile:
#
#        /usr/lib/mailman
#        /usr/lib/mailman/Mailman/Archiver
#                         ^^^^^^^---- not in specfile
#
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#    mailman-2.1.12-14.el6_0.2
#
package RPM::Grill::Plugin::Manifest;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;
use CGI                         qw(escapeHTML);

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order { 30 }    # FIXME

# One-line description of this plugin
sub blurb { return "checks for rare problems in RPM manifests" }

# FIXME
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
    #
    # 2012-01-13 pathname.com is unreachable. Here's another FHS document:
    # http://docs.redhat.com/docs/en-US/Red_Hat_Enterprise_Linux/6/html/Storage_Administration_Guide/s1-filesystem-fhs.html
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
                my $highlighted_name = "<b>" . escapeHTML($parent) . "</b>" . escapeHTML($rest);
                $non_fhs{$f->arch}{$f->subpackage}{$highlighted_name} = 1;
            }


            if ($f->is_dir) {
                $path =~ s{/$}{};

                $is_owned{ $path } = 1;
            }

            # bz802557: check for non-systemd files
            # bz802554: check for files that should be in /usr
            if ($self->major_release =~ /^RHEL(\d+)/ && $1 >= 7) {
                if ( $path =~ m{^/etc/(xinetd\.d|init\.d)/}) {
                    $non_systemd{$f->arch}{$f->subpackage}{$path} = 1;
                }

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

            # bz802555: check for "Fedora" in filenames (but not in srpms)
            unless ($f->arch eq 'src') {
                if ($path =~ /fedora/i) {
                    $f->gripe({
                        code       => 'FedoraInFilename',
                        diag       => "Filenames should not include 'Fedora'",
                    });
                }
            }
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

I'm not sure this is a real problem. Basically: your package claims
ownership of the parent directory, and at least one subdirectory inside
the complained-about directory, but not the complained-about directory
itself. This may have to do with the rpm C<%dir> directive. I need to
learn more about packaging, and may remove this test if it's useless.
If you're rpm-savvy, help would be appreciated.

=item   NonFHS

See L<http://docs.redhat.com/docs/en-US/Red_Hat_Enterprise_Linux/6/html/Storage_Administration_Guide/s1-filesystem-fhs.html>

=item   NonSystemdFile

See L<bz802557|https://bugzilla.redhat.com/show_bug.cgi?id=802557>

=item   MoveToUsr

RHEL7 is doing away with C</usr>. Your package has one or more
files that are still living there.
See L<bz802554|https://bugzilla.redhat.com/show_bug.cgi?id=802554>

=item   FedoraInFilename

Files containing C<fedora> as part of the name might be inappropriate
for RHEL. See L<bz802555|https://bugzilla.redhat.com/show_bug.cgi?id=802555>

(Note: As of April 2012 there are some known false positives here
that should be whitelisted. Ed is trying to figure out a way to
whitelist these).


=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
