# -*- perl -*-
#
# RPM::Grill::Plugin::Rpath - check RPATH in binaries
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::Rpath;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = "0.01";

use Carp;
use File::Basename      qw(dirname);

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order { 14 }

# One-line description of this plugin
sub blurb { return "checks for problems in RPATH" }

# FIXME
sub doc {
    return <<"END_DOC" }
FIXME FIXME FIXME
END_DOC

# Paths that are OK
my $acceptable_paths = <<'END_ACCEPTABLE_PATHS';
/lib
/lib64
/usr/lib
/usr/lib64
/usr/libexec
/usr/src/kernels             # bz447625
END_ACCEPTABLE_PATHS

our @Acceptable_Paths;
for my $line (split "\n", $acceptable_paths) {
    $line =~ s/\s+\#.*$//;              # Trim comments
    push @Acceptable_Paths, $line;
}

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

    for my $rpm ( $self->rpms ) {
        for my $f ( $rpm->files ) {
            if (my $rpath = $f->elf_rpath) {
                $self->_check_rpath( $f, $rpath );
            }
        }
    }
}


sub _check_rpath {
    my $self  = shift;
    my $f     = shift;                 # in: file obj
    my $rpath = shift;

    my $file_path = $f->path;

    for my $element (split ':', $rpath) {
        if (my $why = rpath_element_is_suspect( $file_path, $element )) {
            # FIXME: gripe
            print $file_path, "  ", $element, " ", $why, "\n";
        }
    }
}


##############################
#  rpath_element_is_suspect  #  Returns a reason string, or undef if all's OK
##############################
sub rpath_element_is_suspect {
    my $file_path = shift;              # in: root-level path, eg /usr/bin/foo
    my $element   = shift;              # in: one RPATH element

    if ($element =~ m{^\$ORIGIN(/.*)?}) {
        my $rest = $1 || '';
        $element = dirname($file_path) . $rest;

        # FIXME: handle .. traversal. How?
        while ($element =~ s{/[^/]+/\.\./}{/}g) {
            # ...
        }
    }

    # check for crap like '/usr/lib/foo/../../../tmp'. I can't imagine
    # any realistic scenario in which this could happen ... but it
    # doesn't cost to check.
    if ($element =~ m{/\.\./}) {
        return "'..' in path element";
    }

    # Check if OK path element
    my $re = join('|', @Acceptable_Paths);
    return if $element =~ m{^($re)/};

    return "FIXME";     # unknown path element
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
