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

####################
#  make_fake_tree  #  Convert a string into an unpacked set of directories
####################
#
# Given a directory and a string description of some files, returns
# an RPM::Grill object corresponding to an unpacked set of directories.
#
# Inputs:
#
#    $dir    - is a path to a temporary directory. It should be empty.
#    $layout - is a multiline string describing the layout of files.
#
# $layout needs to be described in detail. Here's an example:
#
#     >> -rwxr-xr-x  root root 0 /i386/mypkg/usr/sbin/foo
#     >> -rw-r--r--  root root 0 /x86_64/mypkg-docs/usr/share/man/man1/foo.1
#     blah blah blah
#     blah blah blah line 2
#
# (please ignore leading whitespace). This describes two files, the
# first of which is empty and the second has two lines.
#
# Leading '>> ' (the space is important) denotes a new file. The fields
# are, in order: mode, owner, group, flags, path. Note that path includes
# arch and subpackage name but MUST NOT include the "payload" string which
# is typically part of an extracted file. We add that ourself.
#
# FIXME: should we also interpret the $expected_gripes string?
#
sub make_fake_tree {
    my $dir    = shift;                 # in: directory in which to unpack
    my $layout = shift;                 # in: string describing file layout

    # FIXME: make sure dir exists and is empty

    my $fh;                     # FIXME: filehandle to latest file

    for my $line (split "\n", $layout) {
        if ($line =~ m{^>>\s+(-\S+)\s+(\w+)\s+(\w+)\s+(\d+)\s+/?([^/]+)/([^/]+)/(.*)/([^/]+)$}) {
            my ($mode, $user, $group, $flags, $arch, $subpackage, $f_dir, $f_base)
                = ($1, $2, $3, $4, $5, $6, $7, $8);

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
                                    $flags,
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
        elsif (defined $fh) {
            print { $fh } $line, "\n";
        }
        elsif ($line) {
            warn "$ME: WARNING: Cannot grok '$line'";
        }
    }

    close $fh                   if defined $fh;

    return RPM::Grill->new($dir);
}

################
#  read_tests  #  reads test setup and expectations from __END__ of script
################
sub read_tests {
    my $fh = shift;                             # in: input filehandle (*DATA)

    my @tests;

    while (my $line = <$fh>) {
        next if $line =~ /^\s*\#/;                  # Skip comment lines

        # eg '----------my-test-name-------------------'
        if ($line =~ /^-{5,}([^-].*[^-])-+$/) {
            push @tests, { name => $1 };
        }

        elsif (@tests) {
            # If we're in the 'expect' section
            if (exists $tests[-1]->{expect}) {
                $tests[-1]->{expect} .= $line;
            }

            # This begins the 'expect' section
            elsif ($line =~ /^\.\.+expect:$/) {
                $tests[-1]->{expect} = '';
            }

            else {
                $tests[-1]->{setup} .= $line;
            }
        }
        elsif ($line =~ /\S/) {
            die "Cannot grok '$line'";
        }
    }

    # FIXME: for {expect}, figure out plugin name & run eval?
    #     if ($t->{expect}) {
    #        $expected_gripes = eval "{ SecurityPolicy => [ $t->{expect} ] }";
    #        die "eval failed:\n\n $t->{gripe_string} \n\n  $@\n"     if $@;
    #

    return @tests;
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
