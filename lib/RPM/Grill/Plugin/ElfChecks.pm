# -*- perl -*-
#
# RPM::Grill::Plugin::ElfChecks - check ELF binaries (RPATH, RELRO, ...)
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::ElfChecks;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;
use RPM::Grill::Util		qw(sanitize_text);
use File::Basename      qw(dirname);

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order { 14 }

# One-line description of this plugin
sub blurb { return "checks for problems in ELF files" }

# Slightly more complete documentation on this test
sub doc {
    return <<"END_DOC" }
This plugin examines ELF attributes of binary files.
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

    # Pass 1: analyze every file. Some of these helpers may store gripes
    # in an internal staging area, instead of calling ->gripe() directly.
    for my $rpm ( $self->rpms ) {
        for my $f ( grep { $_->is_elf } $rpm->files ) {
            $self->_check_rpath( $f );
            $self->_check_relro( $f );

            # 2013-01-17 new check for supplemental groups
            $self->_check_supplemental_groups( $f );

            # bz809907: complain if compiled with gstabs
            if ($f->elf_has_stabs) {
                $self->gripe({
                    arch => $f->arch,
                    subpackage => $f->subpackage,
                    code => 'ElfHasStabs',
                    diag => "File compiled with -gstabs: <tt>".$f->path."</tt>",
                });
            }
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
            my $excerpt = sanitize_text($rpath);
            if (@rpath > 1) {
                $excerpt = join(':',
                                (map { sanitize_text($_) } @rpath[0..$i-1]),
                                "<u>$rpath[$i]</u>",
                                (map { sanitize_text($_) } @rpath[$i+1..$#rpath]));
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

    # bz797428 (attempt #1): SCL awareness.
    #
    # If a binary lives in /opt/rh/foo/root/bin, allow /opt/rh/foo/root/ as
    # the root of RPATH. This is a simpleminded first stab, and will not
    # handle cases such as /opt/rh/foo-extra linking against /opt/rh/foo-base.
    # But we'll deal with that as the need arises.
    my $SCL_Prefix = '';
    if ($file_path =~ m{^(/opt/rh/.*?/root)/}) {
        $SCL_Prefix = "(?:$1)?";
    }

    # check for crap like '/usr/lib/foo/../../../tmp'. I can't imagine
    # any realistic scenario in which this could happen ... but it
    # doesn't cost to check.
    if ($rpath =~ m{/\.\./}) {
        return "'..' in rpath element";
    }

    # Check if OK path element
    my $re = join('|', @Acceptable_Paths);
    return if $rpath =~ m{^$SCL_Prefix($re)(/|$)};

    # Not in desired path. Try to generate a helpful msg

    # Special case for bz797428 (SCL)
    if ($rpath =~ m{^/opt/rh/([^/]+)/root/}) {
        return "RPATH is in a different SCL package ($1); I can't deal with this yet.";
    }

    # Not SCL.
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
        shift;                          # remove unused 'code' keyword
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
            $gripe->( code => 'PiePartialRelro',
                      'File<|s> <is|are> PIE but only partially RELRO' );
        }
        else {
            $gripe->( code => 'PieNotRelro',
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
                code => 'LibMissingRELRO',
                'Library file<|s> not compiled with RELRO or PIE',
            );
        }
        return;         # Nothing more to check for libraries
    }

    # "we want all setuid/segid/setcap/daemons to be compiled with full
    # relro and PIE."
    #
    # Here we identify if our file is one of those types. If it is,
    # we check RELRO. Note that the order below is important: we
    # want Setuid to be more important than Setgid, and both more
    # important than Daemon.
    my $label;
    $label = 'Daemon'   if $f->is_daemon;
    $label = 'Setgid'   if $f->is_sgid;
    $label = 'Setuid'   if $f->is_suid;
    # FIXME: how to check "cap"?

    if ($label) {
        if (!$relro) {
            $gripe->(
                code => "${label}MissingRELRO",
                "$label file<|s> not compiled with RELRO or PIE",
            );
        }
        elsif ($relro ne 'full') {
            $gripe->(
                code => "${label}PartialRELRO",
                "${label} file<|s> compiled with only partial RELRO (should be full)",
            );
        }

        return;
    }
}

# END   relro code
###############################################################################
# BEGIN supplemental groups
#
# See http://cwe.mitre.org/data/definitions/271.html
#

sub _check_supplemental_groups {
    my $self = shift;
    my $f    = shift;

    # FIXME: This should be abstracted into RPM::Grill::Files
    my $path = $f->extracted_path;
    open my $readelf_fh, '-|', 'eu-readelf', '-s', $path
        or do {
            warn "$ME: WARNING: Cannot fork eu-readelf $path: $!";
            return;
        };

    my %have_glibc_sym;
    while (my $line = <$readelf_fh>) {
        # eg:
        #    6: 0000... ..... _exit@GLIBC_2.2.5 (2)
        if ($line =~ /^\s*\d+:\s+[0-9a-fA-F]+\s.*\s(\S+)\@GLIBC/) {
            $have_glibc_sym{$1}++;
        }
    }
    close $readelf_fh
        or do {
            warn "$ME: WARNING: Error reading from eu-readelf -s $path: $!\n";
            return;
        };

    # setgroups/initgroups indicates that the binary is OK
    return if grep { $have_glibc_sym{$_} } qw(setgroups initgroups);

    # Nope. But if there's no set*gid, we have nothing to worry about
    return unless grep { $have_glibc_sym{$_} } qw(setgid setegid setresgid);

    # There's set*gid. But if there's no set*uid, nothing to worry about.
    return unless grep { $have_glibc_sym{$_} } qw(setuid seteuid setresuid);

    # Binary has both set*gid and set*uid. Not good.
    $f->gripe({
        code => 'SupplementalGroups',
        diag => 'Use of supplemental groups',
    });
}

# END   supplemental groups
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

Setuid executable not compiled with RELRO.

=item   SetgidMissingRELRO

Setgid executable not compiled with RELRO.

=item   DaemonMissingRELRO

Daemon executable not compiled with RELRO.
Note that we use heuristics to identify daemons, and these may result in
false positives (we identify "foo" as a daemon but it really isn't) and
false negatives (we fail to identify "bar" as a daemon, and don't check
it for RELRO).

=item   SetuidPartialRELRO

Setuid executable compiled with only I<partial> RELRO (RHEL6 requires I<full>).

=item   SetgidPartialRELRO

Setgid executable compiled with only I<partial> RELRO (RHEL6 requires I<full>).

=item   DaemonPartialRELRO

Daemon executable compiled with only I<partial> RELRO (RHEL6 requires I<full>).
Note that we use heuristics to identify daemons, and these may result in
false positives (we identify "foo" as a daemon but it really isn't) and
false negatives (we fail to identify "bar" as a daemon, and don't check it for RELRO).

=item   ElfHasStabs

Executable has been compiled with C<-gstabs>. This can cause strange
problems.

=item   SupplementalGroups

ELF binary or library is setuid/setgid but does not take steps to protect
group leakage. Solution involves using C<setgroups()> or C<initgroups()>.

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
