# -*- perl -*-
#
# RPM::Grill::Plugin::DesktopLint - check desktop files (icons)
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::DesktopLint;

use strict;
use warnings;
our $VERSION = '0.01';

use base qw(RPM::Grill);
use RPM::Grill::dprintf;


use Carp;
use RPM::Grill::Util		qw(sanitize_text);
use File::Which         qw(which);
use IPC::Run            qw(run timeout);

###############################################################################
# BEGIN user-configurable section

# Sequence number for this plugin
sub order {93}

# One-line description of this plugin
sub blurb { return "checks for common problems in .desktop files" }

sub doc {
    return <<"END_DOC" }
This module checks for common problems in .desktop files. We run
the RHEL 'desktop-file-validate' program, and also run consistency
checks of our own on the Exec and Icon lines.
END_DOC

# END   user-configurable section
###############################################################################

# Program name of our caller
( our $ME = $0 ) =~ s|.*/||;

#
# See
# http://standards.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html
#
sub analyze {
    my $self = shift;

    #
    # Main loop.  Finds .desktop and .directory files in all arches & pkgs
    # (except for src). For each one, we invoke TWO checking functions:
    #
    #   _desktop_file_validate()  - invokes external checker
    #   _check_desktop_file()     - internal checks
    #
    for my $rpm ( grep { $_->arch ne 'src' } $self->rpms ) {
        for my $f ( $rpm->files ) {
            if ( $f->is_reg && $f->{path} =~ m{[^/]\.(desktop|directory)$} ) {
                # Note that $f has _arch and _subpackage already
                _desktop_file_validate($f);
                _check_desktop_file($f);
            }
        }
    }
}

############################
#  _desktop_file_validate  #  External checker
############################
#
# This invokes the /usr/bin/desktop-file-validate command, part of
# desktop-file-utils.
#
sub _desktop_file_validate {
    my $f    = shift;    # in: file obj

    # FIXME: desktop-file-validate is an awesome tool, but frustrating too.
    # In particular, the desktop file specification is a moving target,
    # which leads to confusion: eg the 'Encoding' field was required
    # in RHEL5, then deprecated in RHEL6. When analyzing a RHEL5 package
    # on a RHEL6 worker, desktop-file-validate gripes inappropriately.
    #
    # "Solution" (kludge): the human owner of the rpmgrill worker host
    # can copy over the desktop-file-validate binary from other releases
    # into /usr/bin/desktop-file-validate-$RELEASE (eg -fc16). Or, you
    # can set up a farm so all .fc16 jobs are run on a FC16 host, etc.
    # Other suggestions welcome.
    my $tool = 'desktop-file-validate';
    if ( $f->rpm->nvr('release') =~ /\.((el|fc)\d+)/ ) {
        if (my $custom_tool = which("$tool-$1")) {
            $tool = $custom_tool;
        }
    }

    my $fullpath = $f->extracted_path;
    my @cmd = ( $tool => $fullpath );
    my ( $stdout, $stderr );

    my $ok = run( \@cmd, \undef, \$stdout, \$stderr, timeout(30) );

    # I've only seen warnings sent to stdout, but let's check stderr too.
    #
    # Example warning message (newlines added for readability):
    #
    #   <full-path>/mozilla.desktop: warning:
    #        boolean key "Terminal" in group "Desktop Entry" has value "0",
    #        which is deprecated: boolean values should be "false" or "true"
    #
    for my $stream ( $stdout, $stderr ) {
        for my $line ( split "\n", $stream ) {

            # Strip off the desktop file path; that's already part of gripe()
            $line =~ s|^$fullpath:\s*||;

            $f->gripe(
                {   code    => 'DesktopFileValidation',
                    diag    => $line,
                    context => { path => $f->{path} },
                }
            );
        }
    }

    # If tool exited error status, but didn't give us any output, warn
    if ( !$ok && !$stdout ) {
        warn
            "$ME: WARNING: command exited with nonzero status, but emitted no output: @cmd\n";
    }
}

#########################
#  _check_desktop_file  #  Internal checks on a .desktop or .directory file
#########################
sub _check_desktop_file {
    my $f    = shift;    # in: file obj

    dprintf "Checking: %s\n", $f->{path};

    # Full path to the file, eg i386/mypkg/payload/path/to/file.desktop
    my $fullpath = $f->extracted_path;
    open my $fh_desktop, '<', $fullpath
        or die "$ME: Internal error: Cannot read $fullpath: $!";

    # FIXME: warn instead?

    # Read the .desktop file, looking for Exec= and Icon= lines
    while (<$fh_desktop>) {
        chomp;    # Trim newline & trailing blanks
        s/\s+$//;

        $f->context( { lineno => $., excerpt => sanitize_text($_) } );

        # Exec can be 'Exec=foo' or 'Exec=/some/path/foo arg1 arg2 ...'
        # We only care about the foo, not about args.
        if (/^Exec=\s*(\S+)/) {
            _check_exec( $f, $1 );
        }

        elsif (/^Icon=\s*(.*)/) {
            _check_icon( $f, $1 );
        }
    }
    close $fh_desktop;
}

#################
#  _check_exec  #  Look for an executable
#################
sub _check_exec {
    my $f       = shift;
    my $exec    = shift;

    # FIXME! If .desktop file is in noarch, we need to check for Exec
    #        in all real arches

    # Make sure $exec is an absolute path.  If it isn't one to begin with,
    # assume /usr/bin .
    if ( substr( $exec, 0, 1 ) ne '/' ) {
        $exec = "/usr/bin/$exec";
    }

    # Always return if we find the exec in our same arch.
    return if _find_exec( $f, $f->arch, $exec );

    # Special case for RHEL5: lots of packages rely on 'htmlview' package
    if ($exec eq '/usr/bin/htmlview') {
        if ($f->grill->major_release =~ /^RHEL(\d+)/ && $1 < 6) {
            if (! grep { $_ eq 'htmlview' } $f->rpm->requires) {
                $f->gripe(
                    { code => 'DesktopExecMissingReq',
                      diag => "Package should Require: htmlview",
                  });
            }

            return;
        }
    }

    # Special case for RHEL6 and xdg-open
    if ($exec eq '/usr/bin/xdg-open') {
        if ($f->grill->major_release =~ /^RHEL(\d+)/ && $1 >= 6) {
            if (! grep { $_ eq 'xdg-utils' } $f->rpm->requires) {
                $f->gripe(
                    { code => 'DesktopExecMissingReq',
                      diag => "Package should Require: xdg-utils",
                  });
            }

            return;
        }
    }

    # Special case for SCL packages
    if ($exec eq '/usr/bin/scl') {
        # FIXME: check for dependencies
    }

    # Exec is not in our same arch.
    #
    # As of RHEL6:
    #    * If .desktop file is in noarch, exec file must be in all arches
    #    * Otherwise (.desktop file in real arch) look in noarch
    #
    if ( $f->arch eq 'noarch' ) {
        my @other_arches = grep { $_ !~ /^(noarch|src)$/ } $f->grill->arches;
        if (@other_arches) {
            my @missing
                = grep { !_find_exec( $f, $_, $exec ) } @other_arches;
            return if !@missing;

            $f->gripe(
                {   code    => 'DesktopExecFileMissing',
                    diag    => "Exec file <var>$exec</var> not found",
                    arch    => $_,
                }
            ) for @missing;
            return;
        }

    }

    # Fall through: this is a noarch package, but there are no other
    # arches in the build.  This counts as "not found"
    elsif ( $f->grill->have_arch('noarch') ) {

        # We are in <real arch>, but there's a noarch pkg available; check it
        return if _find_exec( $f, 'noarch', $exec );

        # Nope.  Note the slightly different wording of diag.
        $f->gripe(
            {   code    => 'DesktopExecFileMissing',
                diag    => "Exec file <var>$exec</var> not found, even in noarch",
            }
        );
        return;
    }

    # Exec not found
    $f->gripe(
        {   code    => 'DesktopExecFileMissing',
            diag    => "Exec file <var>$exec</var> not found",
        }
    );
}

################
#  _find_exec  #  Look for $exec in all subpackages of $arch
################
sub _find_exec {
    my $f     = shift;
    my $arch  = shift;
    my $exec  = shift;

    dprintf "_find_exec: Looking for $exec in $arch\n";

    for my $rpm ( $f->grill->rpms( arch => $arch ) ) {
        dprintf "got here: $rpm\n";
        for my $rpm_file ( $rpm->files ) {
            if ( $rpm_file->path eq $exec ) {

                # Found it.
                dprintf "_find_exec: Found $exec in $rpm\n";

                # Before we return, check permissions. Must be world-executable
                my $mode = $rpm_file->mode;
                if ( $mode !~ /x$/ ) {

                    # Not world-executable
                    # FIXME: include rpm name?
                    $f->gripe(
                        {   code => 'DesktopExecFileUnexecutable',
                            diag =>
                                "Exec file <var>$exec</var> is not o+x (mode is <var>$mode</var>)",
                        }
                    );
                }

                # Executable or not, we've found it.  We're OK.
                return 1;
            }
        }
    }

    # Not found.
    return 0;
}

#################
#  _check_icon  #
#################
#
# See Icon Theme Specification:
#  http://standards.freedesktop.org/icon-theme-spec/icon-theme-spec-latest.html
#
sub _check_icon {
    my $f       = shift;
    my $icon    = shift;

    my $icon_re;                # Regex to use for searching for icon

    # If icon has an extension (png, xpm, svg; per ref above), search
    # for it explicitly
    if ($icon =~ /\.(png|xpm|svg)$/) {
        if ($icon =~ m{^/}) {
            $icon_re = qr{^\Q$icon\E$};         # Explicit full path
        }
        else {
            $icon_re = qr{\Q/$icon\E$};         # Look in any directory
        }
    }
    elsif ($icon =~ m{^/}) {    # Already an explicit path?
        $icon_re = qr{^\Q$icon\E$};
    }
    else {
        $icon_re = qr{^/usr/share/(icons|pixmaps)/.*\Q/$icon\E\.(png|xpm|svg)$};
    }

    # Look through all packages on this arch.  (And, if we're a binary arch
    # but there's a noarch available, look there too).
    my @arch = ( $f->arch );
    push @arch, 'noarch' if $f->grill->have_arch('noarch');

    for my $arch (@arch) {
        for my $rpm ( $f->grill->rpms( arch => $arch ) ) {
            for my $rpm_file ( $rpm->files ) {
                my $path = $rpm_file->path;

                if ( $path =~ /$icon_re/ ) {

                    # Found it.
                    dprintf "Found $icon ($path) in $rpm\n";

                    # Before we return, check perms: must be world-readable.
                    my $mode = $rpm_file->mode;
                    if ( $mode !~ /r..$/ ) {

                        # Not world-readable
                        $f->gripe(
                            {   code => 'DesktopIconFileUnreadable',
                                diag =>
                                    "Icon file <var>$path</var> is not world-readable (mode is <var>$mode</var>)",
                            }
                        );
                    }

                    # Readable or not, we've found it.  We're OK.
                    return;
                }
            }
        }
    }

    # Icon not found
    # FIXME: not found
    $f->gripe(
        {   code    => 'DesktopIconFileMissing',
            diag    => "Icon file <var>$icon</var> not found",
        }
    );
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

=item   DesktopFileValidation

rpmgrill invokes C<desktop-file-validate> on .desktop files.
This is the output from that command.

=item   DesktopExecFileMissing

Your .desktop file includes C<Exec=I<foo>>, but
there's no /usr/bin/I<foo> in this package or any of its subpackages.
This probably means that I<foo> is provided by a dependency.

=item   DesktopExecFileUnexecutable

Your .desktop file includes C<Exec=I<foo>>, but
the corresponding bin file is not world-executable.

=item   DesktopExecMissingReq

Your .desktop file uses htmlview or xdg-open, but your specfile
does not have a matching C<Require:> line for that tool.

=item   DesktopIconFileMissing

Your .desktop file specifies an icon which is not present in this package.

FIXME: this is probably a false alarm, because the icon may be in
another package. But there's not really any way for us to
know or test that. Should we just remove this test?

=item   DesktopIconFileUnreadable

Your .desktop file specifies an icon which is not world-readable.

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
