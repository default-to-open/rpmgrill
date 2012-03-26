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
our $VERSION = "0.01";

use Carp;

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order { 30 }    # FIXME

# One-line description of this plugin
sub blurb { return "checks for rare problems in RPM manifests" }

# FIXME
sub doc {
    return <<"END_DOC" }
FIXME FIXME FIXME
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
                $non_fhs{$f->arch}{$f->subpackage}{"<b>$1</b>$2"} = 1;
            }


            if ($f->is_dir) {
                $path =~ s{/$}{};

                $is_owned{ $path } = 1;
            }

            # bz802557: check for non-systemd files
            if ($self->major_release =~ /^RHEL(\d+)/ && $1 >= 7) {
                if ( $path =~ m{^/etc/(xinetd\.d|init\.d)/}) {
                    $non_systemd{$f->arch}{$f->subpackage}{$path} = 1;
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

FIXME

=item   NonFHS

See L<http://docs.redhat.com/docs/en-US/Red_Hat_Enterprise_Linux/6/html/Storage_Administration_Guide/s1-filesystem-fhs.html>

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
