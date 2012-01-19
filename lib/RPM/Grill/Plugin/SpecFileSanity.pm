# -*- perl -*-
#
# RPM::Grill::Plugin::SpecFileSanity - runs rpm -q to look for errors
#
# FIXME: Should this be combined with SpecFileEncoding.pm ?
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::SpecFileSanity;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = "0.01";

use Carp;
use File::Basename;
use IPC::Run qw(run timeout);

###############################################################################
# BEGIN user-configurable section

# Sequence number for this plugin
sub order {5}

# One-line description of this plugin
sub blurb { return "checks for problems in spec file" }

# FIXME
sub doc {
    return <<"END_DOC" }
* runs 'rpm -q' against specfile, for sanity check
* looks for commented-out macros (which don't do what you think)
END_DOC

# END   user-configurable section
###############################################################################

# Program name of our caller
( our $ME = $0 ) =~ s|.*/||;

#
# run 'rpm -q ....' on the specfile; report any errors found
#
sub analyze {
    my $self = shift;    # in: FIXME

    _run_actual_rpm_command( $self );

    _check_for_other_specfile_problems( $self );
}


#############################
#  _run_actual_rpm_command  #
#############################
sub _run_actual_rpm_command {
    my $self = shift;
    my $specfile_path     = $self->specfile->path;
    my $specfile_basename = basename($specfile_path);

    my @rpm = qw(rpm -q --specfile);
    my @cmd = ( @rpm, $specfile_path );
    my ( $stdout, $stderr );
    run \@cmd, \undef, \$stdout, \$stderr, timeout(600);    # 10 min.
    my $exit_status = $?;

    # Good exit status, and nothing in stderr: woot!  Nothing to report!
    if ( $exit_status == 0 && !$stderr ) {
        return;
    }

    # Either exit status was nonzero (bad), or something was in stderr.
    # Hopefully both.
    if ( !$stderr ) {

        # Bad exit status, but nothing in stderr
        if ( $exit_status == -1 ) {

            # Unable to run command
            $self->gripe(
                {   code => 'CannotRunRpm',
                    diag => "Unable to run rpm command",
                }
            );
            return;
        }

        my ( $rc, $sig, $core )
            = ( $exit_status >> 8, $exit_status & 127, $exit_status & 128 );

        my $msg = '';
        $msg .= " exited with status $rc" if $rc;
        $msg .= " exited on signal $sig"  if $sig;
        $msg .= " (core dumped)"          if $core;

        $self->gripe(
            {   code => 'BadExitStatusFromRpm',
                diag => "command '@rpm $specfile_basename' $msg",
            }
        );
        return;
    }

    # FIXME: we have stderr.  if exit status == 0, treat as warnings?
    my $what = ( $exit_status == 0 ? 'Warnings' : 'Errors' );

    # FIXME: if we see specfile:NN: , excerpt that line?

    # FIXME: replace pathname in $stderr with just $basename
    $stderr =~ s{\b$specfile_path\b}{$specfile_basename}g;

    my %notfound;
    while ($stderr =~ s{\s*(sh:\s+.*?:\s+(No such file or directory|command not found))\n}{}) {
        $notfound{$1}++;
    }
    for my $msg (sort keys %notfound) {
        if ((my $n = $notfound{$msg}) > 1) {
            $msg .= " ($n instances)";
        }
        $self->gripe(
            { code => 'RpmParseDependency',
              diag => "Possible macro expansion failure running '@rpm $specfile_basename'",
              context => {
                  excerpt => $msg,
                  path    => $specfile_basename,
              },
              # FIXME: hint => "maybe (pkg) is not installed"?
          }
        );

    }

    # No more errors?
    return if ! $stderr;


    $self->gripe(
        {   code    => "RpmParse$what",
            diag    => "$what running '@rpm $specfile_basename'",
            context => {
                excerpt => $stderr,
                path    => $specfile_basename,
            },
        }
    );
}

########################################
#  _check_for_other_specfile_problems  #
########################################
sub _check_for_other_specfile_problems {
    my $self = shift;

    my $spec  = $self->specfile;
    my @lines = $spec->lines;

    my $specfile_basename = basename($spec->path);

  LINE:
    for (my $i=0; $i < @lines; $i++) {
        my $line = $lines[$i];

        my $s       = $line->content;
        my $section = $line->section;
        my $lineno  = $line->lineno;

        # Look for macros in comments
        # FIXME: also look in %changelog, in %if, ...
        if ($s =~ /^\s*#.*[^%]%[^%]/o) {
            $self->gripe(
                {   code    => "MacroSurprise",
                    diag    => "RPM macros in comments; possible unexpected behavior",
                    context => {
                        path    => $specfile_basename,
                        lineno  => $lineno,
                        excerpt => $s,
                    },
                });
        }
    }

    #
    # Check changelog. In particular, look for mismatch
    # between the reported version and the actual NVR
    #
    if (my @changelog = $spec->lines('%changelog')) {
        my $cl_lineno = $changelog[0]->lineno;

        # Get the first non-blank line
        shift @changelog;               # (first one is '%changelog')
        while (@changelog && ! $changelog[0]->content) {
            shift @changelog;
        }
        if (! @changelog) {
            $self->gripe({
                code    => 'ChangelogEmpty',
                diag    => 'Empty %changelog section in spec file',
                context => {
                    path   => $specfile_basename,
                    lineno => $cl_lineno,
                },
            });
            return;
        }

        my $cl_first  = $changelog[0]->content; # [0] is %changelog

        # Gripe context
        my $context = {
            path   => $specfile_basename,
            lineno => $cl_lineno,
            excerpt => $cl_first,
        };

        # Parse out the V-R, eg "* <date> <author> 1.2-4"
        if ($cl_first =~ /^\*\s+.*\s(\S+)\s*$/) {
            my $vr = $1;                # eg 1.2-4
            my @nvr = $self->nvr;       # eg foo, 1.2, 4.el5

            # FIXME FIXME FIXME: handle epoch
            if ($vr =~ s/^(\d+)://) {
                my $epoch_cl = $1;              # epoch in changelog
                if (defined (my $epoch_spec = $spec->epoch)) {
                    if ($epoch_cl != $epoch_spec) {
                        $self->gripe({
                            code => 'ChangelogWrongEpoch',
                            diag => "Wrong epoch <var>$epoch_cl</var> in first %changelog entry; expected <var>$epoch_spec</var>",
                            context => $context,
                        });
                    }
                }
                else {                          # no epoch in specfile
                    $self->gripe({
                            code => 'ChangelogUnexpectedEpoch',
                            diag => "First %changelog entry specifies epoch <var>$epoch_cl</var>, but specfile defines no Epoch",
                            context => $context,
                        });
                }
            }

            # FIXME: explain
            if ($vr =~ m{^(.*)-(.*)$}) {
                my ($v, $r) = ($1, $2);
                if ($v ne $nvr[1]) {
                    $self->gripe({
                        code => 'ChangelogBadVersion',
                        diag => "First %changelog entry is for <var>$v-$r</var>; I was expecting <var>$nvr[1]</var> as the version, not $v",
                        context => $context,
                    });
                }
                elsif ($nvr[2] !~ /^$r\b/) {
                    $self->gripe({
                        code => 'ChangelogBadRelease',
                        diag => "First %changelog entry is for <var>$v-$r</var>; I was expecting <var>$nvr[1]-<u>$nvr[2]</u></var>",
                        context => $context,
                    });

                }
            }
            else {
                # FIXME: %changelog only has version, no -release?
            }
        }
        else {
            # First changelog line does not match our expectation
            $self->gripe({
                code => 'ChangelogWeirdLine',
                diag => 'Unexpected first line in <b>%changelog</b> section',
                context => $context,
            });
        }
    }
    else {
        # No %changelog??
        $self->gripe({
            code => 'ChangelogMissing',
            diag => 'No <b>%changelog</b> section in specfile',
            context => { path => $specfile_basename },
        });
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

=item   CannotRunRpm

rpmgrill tries to run C<rpm -q --specfile I<path>>. This error code
indicates that there was a failure invoking the C<rpm> command. There
is no stderr available, so it's probably impossible to know what
happened. If you're seeing this error, it means something very
weird and unexpected has happened.

=item   BadExitStatusFromRpm

rpmgrill tries to run C<rpm -q --specfile I<path>>. This error code
indicates that there was a failure invoking the C<rpm> command. There
is no stderr available, but rpmgrill was able to get an exit code.
If you're seeing this error, it means something very
weird and unexpected has happened.

=item   RpmParseDependency

rpmgrill runs C<rpm -q --specfile I<path>> and reports
any problems it finds. This warning usually means that your specfile
has a macro that invokes I<ruby>, I<python>, or some
other tool which is not installed on this system. B<I know>:
you probably have that tool as a package dependency. But remember,
this is the B<specfile>. In the B<SRPM>. People viewing
the SRPM may not have all your prereqs installed.

=item   RpmParseWarnings

rpmgrill runs C<rpm -q --specfile I<path>> and reports
any problems it finds. Typical problems:

  sh: ...fg: no job control
  You probably have a stray % (percent sign) somewhere

=item   RpmParseErrors

rpmgrill runs C<rpm -q --specfile I<path>> and reports
any problems it finds. This error means that the rpm command failed.
This may affect someone who downloads your SRPM for viewing.

=item   MacroSurprise

Did you know that RPM expands macros even inside comments?

Sometimes this is OK: %{name}, %{version}. But when %{foo} is
a multi-line macro, this can cause unpleasant surprises.

B<Recommendation>: Double-percent them all: %%{name}, etc.

=item   ChangelogEmptyFIXME

FIXME

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
