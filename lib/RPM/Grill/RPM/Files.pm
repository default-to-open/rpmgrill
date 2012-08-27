# -*- perl -*-
#
# RPM::Grill::RPM::Files - for iterating over files in an rpm
#
# $Id$
#
package RPM::Grill::RPM::Files;

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;
use Fcntl                       qw(:mode);
use File::LibMagic              qw(:complete);

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

# FIXME
#
# This table defines the way we invoke eu-readelf, and what we get out of it.
# Format is:
#
#  [flag] [section]  >  [regex] : [action]
#
# where:
#
#  [flag]    is the command-line option to eu-readelf. These may appear more
#            than once (like -d).
#  [section] is the label that eu-readelf emits for the given flag
#  [regex]   is a regular expression to search for inside this section
#  [action]  is what to do if we find the regex. Action can be of three forms:
#                     a) @something    - preserve $1, keeping a list of all seen
#                     b) something     - preserve $1, and hope we see just one
#                     c) something = 1 - just mark that we've seen this.
#
our $ReadElf_Parse_Table = <<'END_READELF';
-h ELF Header        > /^\s+Type:\s+(.*)/                         : elf_type

-d Dynamic segment   > /^\s*NEEDED\s+Shared library:\s+\[(\S+)\]/ : @libs
-d Dynamic segment   > /^\s*RPATH\s.*\s\[(.*)\]/                  : rpath
-d Dynamic segment   > /^\s+BIND_NOW\b/                           : bind_now = 1
-d Dynamic segment   > /^\s+DEBUG\b/                              : debug    = 1

-l Program Headers   > /^\s*GNU_RELRO\s.*\s(R\S*)\s+0x/           : gnu_relro

-S Section Headers   > /^\[\s*\d+\]\s+\.stab(str)?\s/             : stabs = 1
END_READELF

our %ReadElf_Parse_Table;
our %ReadElf_Flags;
for my $line (split "\n", $ReadElf_Parse_Table) {
    next unless $line;                  # skip blank lines

    $line =~ m{^(-\S+) \s+ (\S.*?\S) \s+ > \s+ /(.*?)/ \s+ : \s+ (.*)}xo
        or die "$ME: Internal error: cannot grok readelf parse table definition '$line'";
    my ($flag, $section, $re, $action) = ($1, $2, $3, $4);

    $ReadElf_Flags{$flag}++;
    $ReadElf_Parse_Table{$section}{$re} = $action;
}

our $ReadElf_Sections = join('|', sort keys %ReadElf_Parse_Table);
our $ReadElf_Section_RE = qr/^($ReadElf_Sections).*:\s*$/;

our @ReadElf_Flags = sort keys %ReadElf_Flags;

#
# Constant values obtained from <rpm/rpmfi.h>. We use only a subset.
#
use constant RPMFILE_CONFIG     => (1 << 0);
use constant RPMFILE_DOC        => (1 << 1);
use constant RPMFILE_ICON       => (1 << 2);
use constant RPMFILE_GHOST      => (1 << 6);

# File::LibMagic object, initialized once, used often
our $File_Lib_Magic;

# END   user-configurable section
###############################################################################

############
#  gather  #  Returns LoH
############
sub gather {
    my $rpm = shift;                    # in: RPM::Gather::RPM obj
    my @out;                            # out: list of ::File objects

    # Reusable fields
    my $dir        = $rpm->dir;
    my $arch       = $rpm->arch;
    my $subpackage = $rpm->subpackage;

    # FIXME: read payload, nested

    #
    # RPM.per_file_metadata contains a list of files and their attributes
    #
    my $metadata_file = "$dir/RPM.per_file_metadata";
    open my $metadata_fh, '<', $metadata_file
        or die "$ME: Cannot read $metadata_file: $!\naborting";
LINE:
    while ( my $line = <$metadata_fh> ) {
        chomp $line;
        my @values = split( "\t", $line );
        if ( @values != @Per_File_Metadata ) {
            warn "$ME: WARNING: $metadata_file:$.: Wrong # of fields in '$line'\n";
            next LINE;
        }

        my %x
            = map { $Per_File_Metadata[$_] => $values[$_] } ( 0 .. $#values );
        $x{_root}      = $dir;
        $x{arch}       = $arch;
        $x{subpackage} = $subpackage;
        $x{rpm}        = $rpm;
        $x{grill}      = $rpm->grill;

        # Directory and basename
        if ($x{path} =~ m{^(.*)/(.*)}) {
            $x{dirname}  = $1;
            $x{basename} = $2;
        }
        elsif ($arch eq 'src') {
            # e.g. 'foo.patch' in SRPM
            $x{dirname}  = '.';
            $x{basename} = $x{path};
        }
        else {
            # FIXME: can this happen?
            warn "$ME: WARNING: Unexpected path '$x{path}' (no slashes)";
            $x{dirname}  = '/';
            $x{basename} = $x{path};
        }

        # FIXME: check that {path} isn't a dup?

        # Full path to the extracted file.
        # FIXME: handle iso/img/other nested-extracted files
        $x{extracted_path} = $x{_root}
                                . '/payload'
                                . ($x{path} =~ m{^/} ? '' : '/')
                                . $x{path};

        # Check that extracted file is present. We don't like to see
        # files listed in the specfile but not actually shipped.
        unless (-e $x{extracted_path} || -l $x{extracted_path}) {
            # (unless it's flagged as %ghost. Then it's OK. "Ghost"
            # indicates that a file may be listed in the specfile but
            # not actually shipped in the rpm.)
            if ($x{flags} & RPMFILE_GHOST) {
                next LINE;              # it's OK
            }
            warn "$ME: File listed in spec, but not actually shipped: $x{extracted_path}\n";
            # FIXME: continue anyway? Or should we next?
        }

        push @out, bless \%x, __PACKAGE__;
    }
    close $metadata_fh;

    return wantarray ? @out : \@out;
}

sub is_symlink { substr( $_[0]->{mode}, 0, 1 ) eq 'l' }    # eg lrwxrwxrwx
sub is_dir     { substr( $_[0]->{mode}, 0, 1 ) eq 'd' }    # eg drwxr-xr-x
sub is_reg     { substr( $_[0]->{mode}, 0, 1 ) eq '-' }    # eg -rwxr-xr-x
sub is_suid    { $_[0]->numeric_mode & S_ISUID }
sub is_sgid    { $_[0]->numeric_mode & S_ISGID }

# RPM flags
sub is_config  { $_[0]->{flags} & RPMFILE_CONFIG }
sub is_doc     { $_[0]->{flags} & RPMFILE_DOC    }
sub is_icon    { $_[0]->{flags} & RPMFILE_ICON   }
sub is_ghost   { $_[0]->{flags} & RPMFILE_GHOST  }

############
#  is_elf  #  Determines file type; returns true if /ELF/
############
sub is_elf {
    my $self = shift;

    return $self->file_type =~ /\bELF\b/;
}

###############
#  is_daemon  #  FIXME
###############
sub is_daemon {
    my $self = shift;

    $self->rpm->_find_daemon_files;

    return $self->{_is_daemon};
}

###############
#  file_type  # ...as determined by libmagic
###############
sub file_type {
    my $self = shift;

    # First time through? Initialize File::LibMagic. The COMPRESS flag
    # tells libmagic to peek inside compressed data, e.g. to say
    # "man page, compressed" instead of just "compressed data"
    if (! defined $File_Lib_Magic) {
        $File_Lib_Magic = magic_open(MAGIC_COMPRESS);
        magic_load($File_Lib_Magic, "");                # Use default magic file
    }

    # FIXME: what if extracted_path doesn't exist??

    $self->{_file_type} ||= do {
        my $file_path = $self->extracted_path;
        my $file_type = eval { magic_file( $File_Lib_Magic, $file_path ) };
        my $err;
        if ($@) {
            $err = $@;
        }
        elsif (! $file_type) {
            $err = "(unknown error)";
        }

        warn "$ME: Cannot determine file type (Magic) of $file_path: $err\n"
            if $err;

        $file_type || '[unknown]';
    };

    return $self->{_file_type};
}

sub readlink {
    my $self = shift;

    my $path = $self->extracted_path;

    $self->{_readlink} ||= CORE::readlink($path)
        or warn "$ME: Cannot readlink $path : $!\n";
    return $self->{_readlink};
}

###########
#  gripe  #
###########
sub gripe {
    my $self  = shift;                  # in: RPM::Grill::RPM::Files obj
    my $gripe = shift;                  # in: hashref with gripe info

    croak "$ME: ->gripe() called without args"        if ! $gripe;
    croak "$ME: ->gripe() called with too many args"  if @_;
    croak "$ME: ->gripe() called with a non-hashref"  if ref($gripe) ne 'HASH';

    my %gripe = (
        # Defaults ...
        arch       => $self->arch,
        subpackage => $self->subpackage,
        context    => $self->context,

        # ... overridden by our caller.
        %$gripe,
    );

    # If our caller said 'context => undef', delete context entirely.
    # This is useful when doing $file->gripe() to *mention* the file,
    # but the problem isn't *in* the file. It will prevent brewtap from
    # adding a download link for the file.
    delete $gripe{context}              if ! defined $gripe{context};

    $self->rpm->grill->gripe( \%gripe );
}

#############
#  context  #  helper for gripe
#############
sub context {
    my $self = shift;

    if (@_) {
        return $self->{gripe_context} = shift;
    }
    else {
        my %context;

        if (my $context = $self->{gripe_context}) {
            %context = %$context;
        }
        $context{path} = $self->path;

        return \%context;
    }
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

sub DESTROY { }

###############################################################################
# BEGIN code and helpers for running eu-readelf

#####################
#  _run_eu_readelf  #  (private): run eu-readelf -d, extract useful info
#####################
sub _run_eu_readelf {
    my $self = shift;

    # Only need to run once
    return if exists $self->{_eu_readelf};

    $self->{_eu_readelf} = { };

    # eu-readelf hangs, apparently forever, on certain clamav files:
    #   payload/usr/share/doc/clamav-0.97/test/.split/split.clam.exe.bz2aa
    return unless $self->is_elf;

    my $file_path = $self->extracted_path;
    my $cmd = "eu-readelf @ReadElf_Flags $file_path 2>/dev/null";
    open my $fh_readelf, "-|", $cmd
        or die "$ME: Cannot fork: $!\n";

    my $current_section;

    while (my $line = <$fh_readelf>) {
        chomp $line;

        if ($line =~ /^[A-Z].*\s((section|segment|contains)\s.*|Headers?):\s*$/) {
            if ($line =~ /$ReadElf_Section_RE/) {
                $current_section = $1;
            }
            else {
                undef $current_section;
            }
        }

        elsif ($current_section) {
            for my $re (sort keys %{ $ReadElf_Parse_Table{$current_section} }) {
                if ($line =~ /$re/) {
                    my $value = $1;
                    my $action = $ReadElf_Parse_Table{$current_section}{$re};

                    if ($action =~ /^\@(\S+)$/) {
                        my $var = $1;
                        push @{ $self->{_eu_readelf}{$var} }, $value;
                    }
                    elsif ($action =~ /^(\S+)\s*=\s*(\S+)$/) {
                        # FIXME: what if already defined?
                        $self->{_eu_readelf}{$1} = $2;
                    }
                    elsif ($action =~ /^(\S+)$/) {
                        # FIXME: what if already defined?
                        $self->{_eu_readelf}{$1} = $value;
                    }
                    else {
                        die "$ME: Internal error: unknown action '$action' for RE '$re'";
                    }
                }
            }
        }

        # FIXME: what about .gnu.liblist in -A?
    }
    close $fh_readelf
        or die "$ME: Command failed: $cmd\n";

    return;
}

#####################
#  elf_shared_libs  #  Returns a list of shared libs; see above
#####################
sub elf_shared_libs {
    my $self = shift;

    $self->_run_eu_readelf();

    if (my $libs = $self->{_eu_readelf}{libs}) {
        return @$libs;
    }

    return;
}

###############
#  elf_rpath  #  Returns a simple RPATH string, eg '/opt/foo:$ORIGIN'
###############
sub elf_rpath {
    my $self = shift;

    $self->_run_eu_readelf();

    return $self->{_eu_readelf}{rpath};
}

################
#  elf_is_pie  #  Returns true if ELF file is PIE
################
sub elf_is_pie {
    my $self = shift;

    $self->_run_eu_readelf();

    return unless $self->{_eu_readelf}{elf_type} =~ /^DYN/;
    return unless $self->{_eu_readelf}{debug};

    return 1;           # FIXME: "DSO" vs "yes" ?
}

###############
#  elf_relro  #  Returns empty string (false), 'partial', or 'full'
###############
sub elf_relro {
    my $self = shift;

    $self->_run_eu_readelf();

    # Here are a couple of good writeups:
    #
    #    http://www.gentoo.org/proj/en/hardened/hardened-toolchain.xml
    #    https://wiki.ubuntu.com/Security/Features
    #
    # Basically:
    #    * GNU_RELRO makes _part_ of the relocation table read-only ('partial')
    #    * BIND_NOW makes _all_ of it RO ('full')
    if ($self->{_eu_readelf}{gnu_relro}) {
        if ($self->{_eu_readelf}{bind_now}) {
            return 'full';
        }
        return 'partial';
    }
    elsif ($self->{_eu_readelf}{bind_now}) {
        # Should not happen
        warn "$ME: WEIRD: have BIND_NOW but no RELRO in " . $self->extracted_path;
    }

    return '';
}

###################
#  elf_has_stabs  #  For bz809907; returns true if object is built with -gstabs
###################
sub elf_has_stabs {
    my $self = shift;

    $self->_run_eu_readelf();

    return $self->{_eu_readelf}{stabs};
}

# END   code and helpers for running eu-readelf
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
