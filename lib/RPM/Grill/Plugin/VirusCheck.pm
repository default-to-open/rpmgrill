# -*- perl -*-
#
# RPM::Grill::Plugin::VirusCheck - FIXME
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::VirusCheck;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;
use CGI                 qw(escapeHTML);
use File::Temp          qw(tempfile);
use IPC::Run            qw(run timeout);

###############################################################################
# BEGIN user-configurable section

# Sequence number for this plugin
sub order {2}

# One-line description of this plugin
sub blurb { return "runs antivirus checks" }

# FIXME
sub doc {
    return <<"END_DOC" }
This module runs clamav against files in an rpm. Silly as that may seem,
there may be customers who run clamav and may be concerned to see it trigger.
This module may help us avoid an embarrassment in the field.
END_DOC

# END   user-configurable section
###############################################################################

# Program name of our caller
( our $ME = $0 ) =~ s|.*/||;

#
# Calls $self->gripe() with problems
#
sub analyze {
    my $self = shift;    # in: RPM::Grill obj

    # UGH.  Normally we run a loop over arch then subpkg.  But clamscan
    # has a horrible startup cost, O(1-2 seconds), which adds up
    # over (e.g.) 5 arches * 3 subpackages.  Let's just run it once,
    # and pick out the arch/subpkg components
    $self->_analyze_clamscan();
    $self->_analyze_bdscan();
    $self->_analyze_avira();
}

#######################
#  _analyze_clamscan  #  Analyze using ClamAV
#######################
sub _analyze_clamscan {
    my $self = shift;

    my $d = $self->path;
    my @cmd = ( 'clamscan', '--recursive', '--infected', '--stdout', $d );
    my ( $stdout, $stderr );
    run \@cmd, \undef, \$stdout, \$stderr, timeout(3600);    # 1 hour!
    my $exit_status = $?;

    # FIXME: anything on stderr might mean an error running clamscan.
    # FIXME: develop a way to report this sort of thing to a maintainer
    if ($stderr) {
        # gripe
        warn "FIXME: $stderr\n" unless $stderr =~ /LibClamAV Warning:/;
    }

    # Preserve stdout; this can be helpful when debugging
    my $stdout_file = "$d/clamscan-results.txt";
    unlink $stdout_file;
    if (open OUT, '>', $stdout_file) {
        print OUT $stdout;
        close OUT;
    }

    # A clamscan positive result looks like:
    #
    #   payload/fake-virus-infectee.exe: Eicar-Test-Signature FOUND
    #
    #   ----------- SCAN SUMMARY -----------
    #   Known viruses: 851538
    #   Engine version: 0.96.4
    #   Scanned directories: 5
    #   Scanned files: 10
    #   Infected files: 1
    #   Data scanned: 0.00 MB
    #   Data read: 0.00 MB (ratio 0.00:1)
    #   Time: 1.870 sec (0 m 1 s)
    #
    # A negative result looks the same, with no initial path(s) and
    # with 'Infected files: 0'.
    #
    $stdout =~ m{
                    ^(.*)
                    ^---+\s+SCAN\s+SUMMARY\s+--+$
                    .*
                    ^Infected\s+files:\s+(\d+)\s*$
            }xms
        or die "$ME: FATAL: Unexpected output from clamscan: $stdout";
    my $infected_files   = $1;
    my $n_infected_files = $2;

    # FIXME: sanity check: split $infected_files, compare against $n
    # FIXME: what if @ == 0, $n > 0 ?
    my @infected_files = split( "\n", $infected_files );
    if ( @infected_files != $n_infected_files ) {
        warn
            "$ME: WARNING: clamscan conflict between # of infected files reported, and its computed total.  Going with the actual list";
    }

    #
    # Any infected files?  Report them.
    #
    my $clamscan_version_string;

INFECTED_FILE:
    for my $f (@infected_files) {

        # Start a new gripe
        my %gripe = ( code => 'ClamAV', );

        $f =~ m{^(.*?):\s+(.*)}
            or die;
        my ( $path, $msg ) = ( $1, escapeHTML($2) );

        # FIXME - this can't happen?
        $path =~ s{^$d/}{}
            or do {
            warn "$ME: Internal error: bad file path '$path'";
            $self->gripe(
                {   code    => 'FIXME-internal',
                    diag    => 'Internal error, FIXME',
                }
            );
            next INFECTED_FILE;
            };

        if ( $path =~ s{^([^/]+)/([^/]+)/(payload|nested)/}{/} ) {
            $gripe{arch}       = $1;
            $gripe{subpackage} = $2;

            # FIXME: figure out how to handle 'nested'
        }

        if ( $msg =~ s/\s+FOUND\s*$// ) {
            $gripe{diag} = "ClamAV <b>$msg</b> subtest triggered";
        }
        else {
            $gripe{diag} = "ClamAV <tt>$msg</tt> ????";
        }

        # 'clamscan --version' gives us something like:
        #     ClamAV 0.97.3/15062/Wed Jun 20 09:31:12 2012
        # (the date string is probably the database update version).
        # Include this in our diagnostic; it may come in handy if this
        # virus alert is hard to reproduce.
        $clamscan_version_string //= do {
            my $tmp = qx{clamscan --version};
            if ($?) {
                warn "$ME: WARNING: 'clamscan --version' exited with status $?";
                $tmp = 'clamscan --version unavailable';
            }
            chomp $tmp;
            escapeHTML($tmp);
        };
        $gripe{diag} .= " ($clamscan_version_string)";

        $gripe{context} = { path => $path, };

        $self->gripe( \%gripe );
    }
}


#####################
#  _analyze_bdscan  #  Analyze using BitDefender
#####################
sub _analyze_bdscan {
    my $self = shift;

    # bdscan is a commercial product, and is not available everywhere.
    return unless -e '/usr/bin/bdscan';

    my $d = $self->path;

    # We need to force bdscan to write to a file. Although bdscan does
    # write to stdout, it compresses long paths:
    #
    #    /home/esm ... n/myfile1  infected: EICAR-Test-File (not a virus)
    #
    # ...which makes it unusable for our purposes. When writing to log file,
    # bdscan writes the full path.
    my (undef, $tmpfile) = tempfile("$ME.bdscan.XXXXXX", TMPDIR=>1,OPEN=>0);

    my @cmd = ( 'bdscan', '--exclude-ext=rpm', '--no-list', "--log=$tmpfile", '--verbose', $d );
    my ( $stdout, $stderr );
    run \@cmd, \undef, \$stdout, \$stderr, timeout(3600);    # 1 hour!
    my $exit_status = $?;

    # First: check to see if bdscan found anything.
    open my $bdscan_fh, '<', $tmpfile
        or do {
            my %gripe;
            if ($exit_status) {
                $gripe{code} = 'BdScanFailed';
                $gripe{diag} = "bdscan exited with error status $exit_status";

                if ($stderr) {
                    $gripe{context} = { excerpt => $stderr };
                }
            }
            else {                      # Normal (non-error) exit
                %gripe = (
                    code => 'BdScanMissingResults',
                    diag => 'bdscan failed to write output file',
                );
            }

            $self->gripe(\%gripe);
            return;
        };

    # Output file exists. Read it.
    my $bdscan_version_string = 'bdscan version unavailable';
    while (my $line = <$bdscan_fh>) {
        if ($line =~ m{^//\s+Core\s*:\s+(.*)}) {        # bdscan version
            $bdscan_version_string = $1;
        }
        elsif ($line =~ m{^//\s}) {                     # Comment
            next;
        }
        elsif ($line =~ m{^(/\S+)\t(.*)$}) {            # File status
            my ($path, $status) = ($1, escapeHTML($2));
            # FIXME: bdscan will say things like 'ok <- gzip.xmd'
            if ($status !~ /^ok(\s+.*)?$/) {
                my %gripe = (
                    code => 'BitDefender',
                );

                if ( $path =~ s{(^/.*)?$d/([^/]+)/([^/]+)/(payload|nested)/}{/} ) {
                    $gripe{arch}       = $2;
                    $gripe{subpackage} = $3;
                }
                else {
                    warn "WEIRD: VirusCheck: Unknown path '$path'";
                }

                $gripe{context}{path} = escapeHTML($path);
                $gripe{diag} = "$status ($bdscan_version_string)";


                $self->gripe(\%gripe);
            }
        }
    }

    close $bdscan_fh;

    # Clean up.
    unlink $tmpfile;
}


####################
#  _analyze_avida  #  Analyze using Avira
####################
sub _analyze_avira {
    my $self = shift;

    # avscan is a commercial product, and is not available everywhere.
    my $avscan = '/usr/bin/avscan';
    return unless -e $avscan;

    my $d = $self->path;

    # We need to force avscan to write to a file.    #
    my (undef, $tmpfile) = tempfile("$ME.avscan.XXXXXX", TMPDIR=>1,OPEN=>0);

    my @cmd = ($avscan, '--scan-mode=all',
               '--detect-prefixes=alltypes',
               '-s',
               '--scan-in-archive',
               '--batch',
               "--log-file=$tmpfile",
               $d);
    my ( $stdout, $stderr );
    run \@cmd, \undef, \$stdout, \$stderr, timeout(3600);    # 1 hour!
    my $exit_status = $?;

    # First: check to see if bdscan found anything.
    open my $avscan_fh, '<', $tmpfile
        or do {
            my %gripe;
            if ($exit_status) {
                $gripe{code} = 'AvScanFailed';
                $gripe{diag} = "avscan exited with error status $exit_status";

                if ($stderr) {
                    $gripe{context} = { excerpt => $stderr };
                }
            }
            else {                      # Normal (non-error) exit
                %gripe = (
                    code => 'AvScanMissingResults',
                    diag => 'avscan failed to write output file',
                );
            }

            $self->gripe(\%gripe);
            return;
        };

    my $avscan_version_string = 'bdscan version unavailable';
    while (my $line = <$avscan_fh>) {
        next unless $line =~ s/^.*: (ALERT|WARNING)\s+//;
        my $type = $1;

        chomp $line;

        my %gripe = (
            code => 'AvScan',
        );
        if ($line =~ s/^"(.*?)"/file/) {
            $gripe{context}{path} = $1;
            # FIXME: get arch, subpackage
        }

        $gripe{diag} = $line;
        $self->gripe(\%gripe);
    }

    close $avscan_fh;

    # Clean up
    #unlink $tmpfile;
}


# FIXME: aggregator?

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

=item   ClamAV

The L<ClamAV|http://www.clamav.net/> antivirus tool has found
something suspicious in your package. This is so unlikely, so
rare, so exceptional, that it's gotta be worth looking into.

A warning from this test needs investigating. First, because there are
customers who run automated virus scans on incoming software and might
not appreciate having to investigate a trigger coming from Red Hat
software. Second, and much less likely (but not impossible) because
it might be a real problem.

=item   BitDefender

The L<BitDefender antivirus tool|http://www.bitdefender.com/> has
claimed to have found a problem. As of 2012-10-23 this is EXPERIMENTAL.

A warning from this test needs investigating. First, because there are
customers who run automated virus scans on incoming software and might
not appreciate having to investigate a trigger coming from Red Hat
software. Second, and much less likely (but not impossible) because
it might be a real problem.

=item   BdScanFailed

The L<BitDefender antivirus tool|http://www.bitdefender.com/>
failed to run. As of December 2012 this is because we don't have
a license. Ignore this.

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
