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
our $VERSION = "0.01";

use Carp;
use IPC::Run qw(run timeout);

###############################################################################
# BEGIN user-configurable section

# Sequence number for this plugin
sub order {2}

# One-line description of this plugin
sub blurb { return "runs antivirus checks" }

# FIXME
sub doc {
    return <<"END_DOC" }
FIXME FIXME FIXME
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
INFECTED_FILE:
    for my $f (@infected_files) {

        # Start a new gripe
        my %gripe = ( code => 'ClamAV', );

        $f =~ m{^(.*?):\s+(.*)}
            or die;
        my ( $path, $msg ) = ( $1, $2 );

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
            $gripe{diag} = $msg;
        }
        else {
            $gripe{diag} = "$msg ????";
        }

        $gripe{context} = { path => $path, };

        $self->gripe( \%gripe );
    }
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

The ClamAV "antivirus" tool has found something suspicious in
your package. This is so unlikely, so rare, so exceptional, that
it's gotta be worth looking into.

FIXME

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
