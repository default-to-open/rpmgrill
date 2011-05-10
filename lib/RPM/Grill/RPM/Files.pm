# -*- perl -*-
#
# RPM::Grill::RPM::Files - for iterating over files in an rpm
#
# $Id$
#
package RPM::Grill::RPM::Files;

use strict;
use warnings;
our $VERSION = "0.01";

use Carp;
use Fcntl qw(:mode);

( our $ME = $0 ) =~ s|^.*/||;

###############################################################################
# BEGIN user-configurable section

# FIXME: Must agree with values in rpm_unpack script
our @Per_File_Metadata = qw(md5sum mode user group flags color path);

# Table documenting the meaning of each char in an ls string mode.
# Each non-empty row describes all possible character values in a
# given position, and its corresponding octal value.  For example,
# in the string -rwsr-xr-x  there are three 'r's, and we see from
# the list below that they're 0400 0040 and 0004 respectively.
# The 's' sets two bits: 00100 (executable) and 0400 (setuid).
#
# This code copied from [1], with cleanup by Ed.
#   [1] http://perlmonks.org/?node=File%20Permission%20Converter
#
# See _numeric_mode() function below for parsing and use.
our $ls_String_Mode = <<'END_LS_STRING_MODE';
-:0100000  d:0040000  l:0120000  c:0020000  b:0060000  p:0010000  s:0140000

r:0400
w:0200
x:0100 s:04100 S:04000

r:0040
w:0020
x:0010 s:02010 l:02000

r:0004
w:0002
x:0001 t:01001 T:01000
END_LS_STRING_MODE

# END   user-configurable section
###############################################################################

sub gather {
    my $self       = shift;
    my $arch       = shift;
    my $subpackage = shift;
    my @out;

    my $path = $self->path( $arch, $subpackage );

    # FIXME: read payload, nested
    # FIXME: read RPM.per_file_metadata

    my $metadata = "$path/RPM.per_file_metadata";
    open my $metadata_fh, '<', $metadata
        or die "$ME: Cannot read $metadata: $!\naborting";
LINE:
    while ( my $line = <$metadata_fh> ) {
        chomp $line;
        my @values = split( "\t", $line );
        if ( @values != @Per_File_Metadata ) {
            warn "$ME: WARNING: $metadata:$.: Wrong # of fields in '$line'\n";
            next LINE;
        }

        my %x
            = map { $Per_File_Metadata[$_] => $values[$_] } ( 0 .. $#values );
        $x{_root}       = $path;
        $x{_arch}       = $arch;
        $x{_subpackage} = $subpackage;

        # FIXME: check that {path} isn't a dup?

        # Full path to the extracted file.
        # FIXME: handle iso/img/other nested-extracted files
        $x{extracted_path} = $x{_root} . '/payload' . $x{path};

        # FIXME: check that {path} exists?  stat()?
        push @out, bless \%x, __PACKAGE__;
    }
    close $metadata_fh;

    return wantarray ? @out : \@out;
}

sub is_symlink { substr( $_[0]->{mode}, 0, 1 ) eq 'l' }    # eg lrwxrwxrwx
sub is_dir     { substr( $_[0]->{mode}, 0, 1 ) eq 'd' }    # eg drwxr-xr-x
sub is_reg     { substr( $_[0]->{mode}, 0, 1 ) eq '-' }    # eg -rwxr-xr-x
sub is_suid { $_[0]->numeric_mode & S_ISUID }
sub is_sgid { $_[0]->numeric_mode & S_ISGID }

sub readlink {
    my $self = shift;

    my $path = $self->extracted_path;

    $self->{_readlink} ||= CORE::readlink($path)
        or warn "$ME: Cannot readlink $path : $!\n";
    return $self->{_readlink};
}

##############
#  AUTOLOAD  #  For accessing internal hash elements
##############
sub AUTOLOAD {
    my $self = shift;

    our $AUTOLOAD;
    ( my $field = lc($AUTOLOAD) ) =~ s/^.*:://;

    if ( exists $self->{$field} ) {
        my $val = $self->{$field};
        if ( ref($val) ) {
            if ( ref($val) eq 'ARRAY' ) {
                return @$val;
            }
        }

        return $val;
    }

    croak "$ME: Unknown field " . __PACKAGE__ . "->$field()";
}

###############################################################################
# BEGIN Code and helpers for converting string (ls) mode to octal

# Main table used for converting string to octal.  This is a LoH.  There
# will be 10 entries: 3 for each rwx, 1 for the prefix: - rwx rwx rwx .
# Each entry is a hash where key = character, value = octal mode.
# For instance, in position 1, 'r' = 0400.
our @Numeric_Mode;

###################
#  _numeric_mode  #  (note underscore) input=mode string, returns octal mode
###################
sub _numeric_mode {
    my $string_mode = shift;    # eg -rwxr-xr-x

    # First time through?  Parse the mode table at top.
    if ( !@Numeric_Mode ) {

        # position into ls string.  For -rwxr-xr-x, 0='-', 1='r', ..., 9='x'
        my $pos = 0;

        # Split the table at top into lines.  Each non-empty line is one
        # position in the ls mode string.
        for my $line ( split "\n", $ls_String_Mode ) {
            $line =~ s/\s*\#.*//;    # Trim comments
            $line or next;           # skip empty lines

            # Start by assuming that '-' is zero.  This will be overridden
            # on the first char, where '-' means regular file.
            $Numeric_Mode[$pos] = { '-' => 0 };

            # Each line will have one or more bit meanings.  Not 'r' and 'w',
            # those only have one, but 'x' can also be 's' (setuid).  And
            # the file type can have many different meanings.
            for my $field ( split " ", $line ) {

                # Each field is <letter>:<bits>
                $field =~ /^(.):([0-7]+)$/
                    or die "$ME: Internal error: Cannot grok mode '$field'";
                $Numeric_Mode[$pos]{$1} = $2;
            }

            # Done with this line.  Move to next char position.
            ++$pos;
        }
    }

    # Convert string to octal.  Starting with the leftmost char (position 0),
    # match each letter with its octal meaning.
    my $octal_mode = 0;
    for my $pos ( 0 .. 9 ) {
        my $c = substr( $string_mode, $pos, 1 );
        my $o = $Numeric_Mode[$pos]{$c};
        if ( defined $o ) {
            $octal_mode |= oct($o);
        }
        else {
            warn "$ME: WARNING: Unknown character '$c' at position $pos"
                . " in mode '$string_mode'\n";
        }
    }

    return $octal_mode;
}

##################
#  numeric_mode  #  (no underscore): file object method
##################
sub numeric_mode {
    my $self = shift;

    return _numeric_mode( $self->{mode} );
}

# END   Code and helpers for converting string (ls) mode to octal
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

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
