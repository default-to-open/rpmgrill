# -*- perl -*-
#
# RPM::Grill::Plugin::ElfChecks - check ELF binaries (RPATH, RELRO, ...)
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
# This module created in response to
#   https://errata.devel.redhat.com/rpmdiff/show/52153?result_id=821293
package RPM::Grill::Plugin::ElfChecks;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;
use CGI                 qw(escapeHTML);
use File::Basename      qw(dirname);

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order { 14 }

# One-line description of this plugin
sub blurb { return "checks for problems in ELF files" }

# FIXME
sub doc {
    return <<"END_DOC" }
This plugin contains two tests:

  RPATH - looks for suspicious directories in ELF RPATH

  RELRO - require security-enhanced compile options on certain executables
END_DOC

# Path components that are OK in RPATH.
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

    $self->{_plugin_state} = {};

    # Pass 1: analyze every file. Some of these helpers may store gripes
    # in an internal staging area, instead of calling ->gripe() directly.
    for my $rpm ( $self->rpms ) {
        for my $f ( grep { $_->is_elf } $rpm->files ) {
            $self->_check_rpath( $f );

            # FIXME
            $self->_check_relro( $f );
        }
    }

    # Collect gripes. This is helpful for avoiding lots of the same message.
    #
    # The organization here looks something like:
    #
    #   |- diag
    #   |  |- LibMissingRELRO = Library file<|s> not compiled with RELRO or PIE
    #   |  `- SetxidMissingRELRO = Setxid file<|s> not compiled with RELRO or PIE
    #   `- gripes
    #      |- LibMissingRELRO  <--- code
    #      |  |- i686          <--- arch
    #      |  |  |- perl       <--- subpackage
    #      |  |  |  |- 0 = /usr/lib/perl5/auto/B/B.so
    #      |  |  |  |- 1 = /usr/lib/perl5/auto/Cwd/Cwd.so
    #      :  :  :  :
    #
    for my $code (sort keys %{ $self->{_plugin_state}{gripes} }) {
        my $code_gripes = $self->{_plugin_state}{gripes}{$code};

        for my $arch (sort keys %$code_gripes) {
            for my $subpackage (sort keys %{ $code_gripes->{$arch} }) {
                # Here we are. Get list of files for this tuple.
                my @files = @{ $code_gripes->{$arch}{$subpackage} };

                my $gripe = {
                    code => $code,
                    arch => $arch,
                    subpackage => $subpackage,
                };

                # Get the corresponding diag message for this code.
                # It will look like "File<|s>", where <lhs|rhs> indicates
                # what to show for singular (lhs) or plural (rhs).
                my $diag = $self->{_plugin_state}{diag}{$code};

                # Filter it as singular or plural.
                # If singular, include filename as part of diagnostic.
                # If plural, include filenames in our separate context.
                if (@files == 1) {
                    $diag =~ s{<(.*?)\|.*?>}{$1}g;
                    $gripe->{diag} = "$diag: <tt>$files[0]</tt>";
                }
                else {                                  # plural
                    $diag =~ s{<\|(.*?)>}{$1}g;
                    $gripe->{diag} = $diag . ":";
                    $gripe->{context} = {
                        excerpt => \@files,
                    };
                }

                $self->gripe($gripe);
            }
        }
    }
}


###############################################################################
# BEGIN rpath code

##################
#  _check_rpath  #  Check a complete rpath (i.e. multiple:elements)
##################
sub _check_rpath {
    my $self  = shift;
    my $f     = shift;                 # in: file obj

    # We are called indiscriminately. Return if we have no RPATH to check.
    my $rpath = $f->elf_rpath
        or return;

    my $file_path = $f->path;

    # Test components individually. We delegate that to a helper function.
    my @rpath = split ':', $rpath;

    # For readability in diagnostic messages
    my $element = (@rpath == 1 ? '' : ' element');

    # Invoke helper on each rpath element. Report problems, if any.
    for my $i (0 .. $#rpath) {
        if (my $why = _rpath_element_is_suspect( $file_path, $rpath[$i] )) {
            # Problem found; report it.
            # For readability, on multi-element RPATHs, highlight
            # the offending one.
            my $excerpt = escapeHTML($rpath);
            if (@rpath > 1) {
                $excerpt = join(':',
                                (map { escapeHTML($_) } @rpath[0..$i-1]),
                                "<u>$rpath[$i]</u>",
                                (map { escapeHTML($_) } @rpath[$i+1..$#rpath]));
            }

            # FIXME: gripe
            $f->gripe({
                code => 'BadRpath',
                diag => "Suspicious-looking RPATH$element: $why",
                context => { path    => $file_path,
                             excerpt => $excerpt },
            });
        }
    }

    # FIXME: low pri: check for writable directories?

    return;
}


##############################
#  rpath_element_is_suspect  #  Returns a reason string, or undef if all's OK
##############################
sub _rpath_element_is_suspect {
    my $file_path = shift;              # in: root-level path, eg /usr/bin/foo
    my $rpath     = shift;              # in: one RPATH element

    if ($rpath =~ m{^\$ORIGIN(/.*)?}) {
        my $rest = $1 || '';
        $rpath = dirname($file_path) . $rest;

        # FIXME: handle .. traversal. How?
        while ($rpath =~ s{/[^/]+/\.\./}{/}g) {
            # ...
        }
    }

    # check for crap like '/usr/lib/foo/../../../tmp'. I can't imagine
    # any realistic scenario in which this could happen ... but it
    # doesn't cost to check.
    if ($rpath =~ m{/\.\./}) {
        return "'..' in rpath element";
    }

    # Check if OK path element
    my $re = join('|', @Acceptable_Paths);
    return if $rpath =~ m{^($re)(/|$)};

    # Not in desired path. Try to generate a helpful msg
    my @ok;
    for my $rpath_element (split '/', $rpath) {
        push @ok, $rpath_element;
        my $ok = join('/', @ok);
        if (! grep { m{^$ok} } @Acceptable_Paths) {
            return "$ok is not a known trusted path";
        }
    }

    return "not a known trusted path";     # unknown path element
}

# END   rpath code
###############################################################################
# BEGIN relro code

##################
#  _check_relro  #
##################
#
# The policy used here is defined by Steve Grubb:
#
#    we want all setuid/segid/setcap/daemons to be compiled with
#    full relro and PIE. We want all libraries to have partial relro.
#    ...
#    when you have an application with PIE, you want full relro so that
#    these sections become readonly and not part of an attacker's target areas.
#
#  http://post-office.corp.redhat.com/archives/os-devel-list/2011-July/msg00149.html
#
# See also discussion at https://fedorahosted.org/fesco/ticket/563
#
sub _check_relro {
    my $self  = shift;
    my $f     = shift;                 # in: file obj

    my $file_path = $f->path;

    # Files we are never interested in
    return if $file_path =~ m{/lib.*/debug};            # eg /usr/lib/debug/...
    return if $file_path =~ m{\.debug$};                # foo.debug

    my $is_pie = $f->elf_is_pie;
    my $relro  = $f->elf_relro;

    # Gripe shortcut. This lets us abbreviate our gripe calls to just
    # a code and a message string.
    my $gripe = sub {
        my $code = shift;
        my $msg  = shift;

        my $arch = $f->arch;
        my $subp = $f->subpackage;
        push @{ $self->{_plugin_state}{gripes}{$code}{$arch}{$subp} }, $file_path;
        $self->{_plugin_state}{diag}{$code} = $msg;
    };

    # First, check PIE. If we have PIE and RELRO, all is good.
    if ($is_pie) {
        if ($relro eq 'full') {
            return;             # PIE + RELRO = always good (at least from
                                # our perspective. Not necessarily from that
                                # of the end user who has to wait longer
                                # at program startup time).
        }

        # PIE but not RELRO. Bad. (see above)
        # FIXME
        if ($relro eq 'partial') {
            $gripe->( 'PiePartialRelro',
                      'File<|s> <is|are> PIE but only partially RELRO' );
        }
        else {
            $gripe->( 'PieNotRelro',
                      'File<|s> <is|are> PIE but not RELRO' );
        }
        # FIXME: is this enough diagnostic?
        return;
    }

    # Not PIE. Should it be? What about RELRO?
    #
    # "we want all libraries to have partial relro"
    if ($file_path =~ m{/lib.*\.so$}) {
        if (! $relro) {
            $gripe->(
                'LibMissingRELRO',
                'Library file<|s> not compiled with RELRO or PIE',
            );
        }
        return;         # Nothing more to check for libraries
    }

    # "setuid/setgid" ... "full RELRO and PIE"
    # FIXME: how to check "cap"?
    if ($f->is_suid || $f->is_sgid) {
        my $ug = ($f->is_suid ? 'u' : 'g');

        if (!$relro) {
            $gripe->(
                "Set${ug}idMissingRELRO",
                "Set${ug}id file<|s> not compiled with RELRO or PIE",
            );
        }
        elsif ($relro ne 'full') {
            $gripe->(
                "Set${ug}idPartialRELRO",
                "Set${ug}id file<|s> compiled with only partial RELRO (should be full)",
            );
        }

        return;
    }

    # FIXME: how to check daemon??
}

# END   relro code
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

=item   BadRpath

=item   PiePartialRelro

FIXME

=item   PieNotRelro

File compiled with PIE but not RELRO.

FIXME: I don't remember why this is important.

=item   LibMissingRELRO

Library file not compiled with RELRO or PIE.

FIXME: I don't remember why this is important.

=item   SetuidMissingRELRO

Setuid executable not compiled with RELRO. This is probably bad.

=item   SetgidMissingRELRO

Setgid executable not compiled with RELRO. This is probably bad.

=item   SetuidPartialRELRO

Setuid executable compiled with I<partial> RELRO. I don't know
what this means or why (if) it's bad.

=item   SetgidPartialRELRO

Setuid executable compiled with I<partial> RELRO. I don't know
what this means or why (if) it's bad.

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
