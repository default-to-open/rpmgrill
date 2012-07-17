# -*- perl -*-
#
# FakeTree.pm - create a fake Rpm::Grill object
#
# $Id$
#
package FakeTree;

use strict;
use warnings;

use Carp;
use RPM::Grill;
use File::Path                  qw(mkpath);

###############################################################################
# BEGIN user-configurable section

# END   user-configurable section
###############################################################################

# Program name of our caller
(our $ME = $0) =~ s|.*/||;

# RCS id, accessible to our caller via "$<this_package>::VERSION"
(our $VERSION = '$Revision: 0.0 $ ') =~ tr/[0-9].//cd;

#########
#  new  #  Constructor.
#########
sub make_fake_tree {
    my $dir = shift;                    # in: directory in which to unpack
    my $foo = shift;                    # in: string

    # FIXME: make sure dir exists and is empty

    my $fh;                     # FIXME: filehandle to latest file

    for my $line (split "\n", $foo) {
        if ($line =~ m{^>>\s+(-\S+)\s+(\w+)\s+(\w+)\s+/?([^/]+)/([^/]+)/(.*)/([^/]+)$}) {
            my ($mode, $user, $group, $arch, $subpackage, $f_dir, $f_base)
                = ($1, $2, $3, $4, $5, $6, $7);

            my $subdir = "$dir/$arch/$subpackage/payload/$f_dir";
            mkpath $subdir, 0, 02755;

            if (defined $fh) {
                close $fh;
            }

            open $fh, '>', "$subdir/$f_base"
                or die "FIXME";

            # FIXME: write to per_file_metadata
            my $meta = "$dir/$arch/$subpackage/RPM.per_file_metadata";
            open my $fh_meta, '>>', $meta
                or die "Cannot append to $meta: $!";
            print { $fh_meta } join("\t",
                                    "f" x 32,
                                    $mode,
                                    $user,
                                    $group,
                                    "0",               # ?
                                    "(none)",          # color
                                    "/$f_dir/$f_base",
                                ), "\n";
            close $fh_meta
                or die "Error writing to $meta: $!";

            # FIXME: create/touch rpm.rpm
            my $rpm = "$dir/$arch/$subpackage/rpm.rpm";
            open my $fh_rpm, '>>', $rpm;
            close $fh_rpm;

        }
    }

    return RPM::Grill->new($dir);
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

L<Some::OtherModule>

=head1	AUTHOR

Ed Santiago <ed@edsantiago.com>

=cut
