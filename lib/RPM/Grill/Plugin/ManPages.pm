# -*- perl -*-
#
# RPM::Grill::Plugin::ManPages - test for missing or bad man pages
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::ManPages;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;
use RPM::Grill::Util		qw(sanitize_text);
use IPC::Run                    qw(run timeout);

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order { 45 }

# One-line description of this plugin
sub blurb { return "checks for missing or badly-formatted man pages" }

# FIXME
sub doc {
    return <<"END_DOC" }
This module checks man pages for validity, and checks that
man pages are present for all important executables.
END_DOC

# List of "important" directories. Used in _check_manpage_presence() to
# determine whether an executable needs a man page or not.
# FIXME: should this list be RHEL-dependent?
# FIXME: what about new RHEL7 init-script style?
our @Important_Bin_Directories = qw(/bin /sbin /usr/sbin /etc/init.d);
our $Important_Bin_Directories = join('|', @Important_Bin_Directories);

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

    # Step 1: go through all RPMs, collect manpages into an array
    $self->_gather_manpages();

    # Step 2: check each of those for correctness
    for my $manpage (@{ $self->{_manpages} }) {
        $self->_check_manpage_correctness($manpage);
    }

    # Step 3: warn about binaries without man pages
    for my $rpm ($self->rpms) {
        for my $f ($rpm->files) {
            $self->_check_manpage_presence($f);
        }
    }
}

######################
#  _gather_manpages  #  Initializes array of files that are (probably) man pages
######################
sub _gather_manpages {
    my $self = shift;                           # in: grill obj

    $self->{_manpages} = [];

    for my $rpm (grep { $_->arch ne 'src' } $self->rpms) {
        for my $f ($rpm->files) {
            if ($f->is_reg && $f->path =~ m|^/usr/share/man/|) {
                push @{ $self->{_manpages} }, $f;
            }
        }
    }
}

################################
#  _check_manpage_correctness  #  Look for man pages; run some checks on them
################################
sub _check_manpage_correctness {
    my $self    = shift;                        # in: grill obj
    my $manpage = shift;                        # in: Files obj

    # FIXME: can we assume that all manpages will be .gz ?
    $manpage->path =~ /\.[0-9n]\w*(\.gz)?$/ or do {
        $manpage->gripe({
            code => 'ManPageUnknownExtension',
            diag => "Man pages are expected to end in .[0-9n][a-z]*\.gz",
        });
        return;
    };

    my $content;

    if ($manpage->path =~ /\.gz$/) {
        my @cmd = ('gzip', '-dc', $manpage->extracted_path);
        my $stderr;
        run \@cmd, \undef, \$content, \$stderr, timeout(600);    # 10 min.
        my $exit_status = $?;

        if ($exit_status) {
            if ($stderr) {
                # gzip may include the file path in its error message.
                # Normalize it, so end users don't see /arch/payload/etc
                my $path_extracted = $manpage->extracted_path;
                my $path_plain     = $manpage->path;
                $stderr =~ s|\b$path_extracted\b|$path_plain|gs;

                # If the error is 'not in gzip format', invoke file(1)
                # and report what the file looks like
                if ($stderr =~ / not in gzip format\b/) {
                    $stderr .= " ('file' classifies this file as: " .
                        $manpage->file_type . ")";
                }

                $manpage->gripe({
                    code => 'ManPageBadGzip',
                    diag => "gunzip failed: " . sanitize_text($stderr),
                });
            }
            else {
                $manpage->gripe({
                    code => 'ManPageBadGzip',
                    diag => "Unknown error trying to gunzip file",
                });
            }
            return;
        }
        # No exit status.
    }
    else {
        # Not .gz; read directly. FIXME: can this happen?
        open my $fh, '<', $manpage->extracted_path or do {
            $manpage->gripe({
                code => 'ManPageReadError',
                diag => "Could not read file contents: $!",
            });
            return;
        };

        $content = do { local $/; <$fh>; };
        close $fh;
    }

    $content =~ /^\.(SH|Dd|so)/ms or do {
        $manpage->gripe({
            code => 'ManPageNoContent',
            diag => "No .SH, .Dd, or .so macros found; is this really a man page? ('file' classifies this file as: " . sanitize_text($manpage->file_type) . ")",
        });
    };
}


#############################
#  _check_manpage_presence  #  "Important" executables must have a man page
#############################
sub _check_manpage_presence {
    my $self = shift;                           # in: Grill obj
    my $bin  = shift;                           # in: RPM::Grill::RPM::Files obj

    return unless _file_needs_manpage( $bin );

    # Got here. File is an executable in an important directory. Let's
    # make sure it has a corresponding man page.
    my $basename = $bin->basename;
    my %arch_seen;
    for my $manpage (@{ $self->{_manpages} }) {
        if ($manpage->path =~ m{/$basename\.[^/]+$}) {
            # The usual case: man page is in same arch or in noarch
            return if $manpage->rpm->arch eq $bin->arch
                   || $manpage->rpm->arch eq 'noarch';

            # Not one of the usual cases. We could have a file in noarch
            # that's documented in <arch>. See below.
            $arch_seen{ $manpage->rpm->arch }++;
        }
    }

    # Man page might be missing. Prepare a gripe message.
    my $diag = "No man page for <tt>" . sanitize_text($bin->path) . "</tt>";

    # Corner case: a config file (eg /etc/gitweb.conf in git-1.8.2.1-4.el7)
    # ships in noarch, but its man page is packaged in arch (i686, etc).
    # If *every* arch includes the man page, we're probably OK. (Not 100%
    # certain, because we're not cross-checking subpackages, but we can't
    # check everything).
    if ($bin->rpm->arch eq 'noarch' && keys %arch_seen) {
        my @arch_missing;
        for my $arch ($bin->rpm->grill->non_src_arches) {
            if ($arch ne 'noarch' && !$arch_seen{$arch}) {
                push @arch_missing, $arch;
            }
        }

        return if ! @arch_missing;

        # We have a man page on one arch, but it's missing on others.
        # This seems *really* unlikely ever to trigger...
        $diag = sprintf("Man page for <tt>%s</tt> shipped on %s but missing on %s",
                        sanitize_text($bin->path),
                        join(',', sort keys %arch_seen),
                        join(',', @arch_missing));
    }

    # No man page anywhere.
    $bin->gripe({
        code       => 'ManPageMissing',
        diag       => $diag,
        context    => undef,
    });

    return;
}

#########################
#  _file_needs_manpage  #  Helper. Does this file need a man page?
#########################
sub _file_needs_manpage {
    my $bin  = shift;                           # in: RPM::Grill::RPM::Files obj

    # We get invoked for all files, but we're only interested in:
    #   * regular files (i.e. not symlinks or directories) that are:
    return 0 if ! $bin->is_reg;

    #      * executable and in an important directory
    return 1 if $bin->numeric_mode & 0x100
             && $bin->path =~ m{^($Important_Bin_Directories)/};

    # Not one of the above. File does not need a man page.
    return;
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

=item   ManPageUnknownExtension

The file extension of a man page should be .C<section>.gz, where
C<section> is a digit or the letter "n" perhaps followed by more
letters: .1.gz, .0pm.gz, .8.gz

=item   ManPageBadGzip

Although the man page ends in C<.gz>, gzip encountered an error
trying to decompress it. See diagnostic message for more info.
This probably means that the file isn't gzip'ed even though it
ends in .gz.

=item   ManPageReadError

Encountered an error reading the man page file. This error is not
likely to happen; if it does, the maintainer of this tool needs to know
about it.

=item   ManPageNoContent

We look for certain key roff macros in the file content; these
macros are expected in all man pages. This diagnostic means that none
of those macros appear in the man page file.

=item   ManPageMissing

Certain files are expected to have corresponding man pages; as
of 2012-11-28 the rule is that: (a) any executable regular
file C<foo> in C</bin> C</sbin> C</usr/sbin> or C</etc/init.d>;
or (b) any file marked as C<%config> in the specfile; should have a
corresponding man page in C</usr/share/man>.

Hint: if you see this warning on a file in /etc, reassess whether
you should be marking the file as C<%config>: if it's not meant to
be touched by a sysadmin, it probably shouldn't be C<%config>.

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
