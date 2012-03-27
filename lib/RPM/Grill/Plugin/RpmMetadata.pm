# -*- perl -*-
#
# RPM::Grill::Plugin::RpmMetadata - check for possible problems in rpm info
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#   [ FIXME: vdsm22-4.5-63.10.el5_6 ]
#
package RPM::Grill::Plugin::RpmMetadata;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;
use Net::DNS;
use LWP::UserAgent;

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order {4}    # run early

# One-line description of this plugin
sub blurb { return "check for problems in RPM metadata" }

# FIXME
sub doc {
    return <<"END_DOC" }
FIXME FIXME FIXME
END_DOC

# Expected metadata fields.
our @Metadata_Fields = (
    'Name',     'Version', 'Release',     'Vendor',
    'Packager', 'Summary', 'Description', 'Group',
    'License'
);

# External nameservers.  We use these to see if a hostname resolves
# outside our network (if it doesn't, it's an internal hostname that
# shouldn't be exposed).
#
# The addresses below are ns1/ns2.rh.c as of 2011-01-19
our @External_NS = qw(172.16.48.210 10.5.19.1);

# Standard protocols for the URL field
our @Valid_URL_Protocols = qw(http https ftp git);

our %Is_Valid_URL_Protocol = map { $_ => 1 } @Valid_URL_Protocols;

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

    my @nvr = $self->nvr;
    my %nvr = map { $_ => shift(@nvr) } qw(Name Version Release);

    #
    # Loop over each arch and subpackage
    #
    my %by_value;
    for my $rpm ( $self->rpms ) {
        # FIXME
        my $metadata = $rpm->metadata;
        my $arch     = $rpm->arch;
        my $subpkg   = $rpm->subpackage;

        # Name, Version and Release must always match
        $nvr{Name} = $subpkg;
        for my $field (qw(Name Version Release)) {
            my $actual = $metadata->get($field) // '[empty]';
            my $expect = $nvr{$field};
            $actual eq $expect
                or $metadata->gripe(
                    {
                        code       => "Wrong$field",
                        diag       => "$field: expected $expect, got $actual",
                    }
                );
        }

        # Farm off the individual checks.
        # FIXME: Each of these sets gripe state/context
        _check_vendor($metadata);
        _check_build_host($metadata);
        _check_url($metadata);

        # Preserve values for consistency between RPMs
        # FIXME
        for my $field ( $metadata->fields ) {
            my $value = $metadata->get($field);    # FIXME
            $by_value{$field}{$value}{$arch}{$subpkg} = 1;
        }
    }

    # FIXME: now check %by_value
    delete $by_value{$_}
        for (
        'Build Date', 'Build Host', 'Install Date',
        'Signature',  'Size',       'Relocations'
        );

    for my $k ( sort keys %by_value ) {
        my $v = $by_value{$k};
        next if keys(%$v) == 1;

        #        use Data::Dumper; print Dumper($v);
    }
}

###############################################################################
# BEGIN individual checks

###################
#  _check_vendor  #  Vendor must be "Red Hat, Inc."
###################
sub _check_vendor {
    my $metadata = shift;

    my $vendor = $metadata->vendor
        or do {
            $metadata->gripe(
                {   code    => 'NoVendor',
                    diag    => 'Vendor field is missing/empty',
                }
            );
            return;
        };

    if ($vendor ne 'Red Hat, Inc.') {
        my $diag = 'Vendor field must be "Red Hat, Inc."';

        $diag .= ' (case matters)'      if lc($vendor) eq 'red hat, inc.';
        $diag .= ' (the dot matters)'   if    $vendor  eq 'Red Hat, Inc';
        $diag .= ' (the comma matters)' if    $vendor  =~ /^Red Hat Inc/;

        $metadata->gripe(
            {   code    => 'WrongVendor',
                diag    => $diag,
                context => {
                    path    => '[RPM metadata]',
                    excerpt => "Vendor: $vendor"
                },
            }
        );

        return;
    }
}

#######################
#  _check_build_host  #  Build Host must be defined and within .redhat.com
#######################
sub _check_build_host {
    my $metadata = shift;

    # FIXME: is this OK for srpms?
    my $buildhost = $metadata->get('Build Host')
        or do {
        $metadata->gripe(
            {   code    => 'NoBuildHost',
                diag    => 'Build Host field is missing/empty',
                context => { path => '[RPM metadata]' },
            }
        );
        return;
        };

    $buildhost =~ /\S+\.redhat\.com$/
        or do {
        $metadata->gripe(
            {   code    => 'BadBuildHost',
                diag    => 'Build Host is not within .redhat.com',
                context => {
                    path    => '[RPM metadata]',
                    excerpt => "Build Host: $buildhost"
                },
            }
        );
        return;
        };
}

################
#  _check_url  #  Perform checks against the URL field, if present
################
sub _check_url {
    my $metadata = shift;

    # It's OK if there's no URL.
    my $url = $metadata->get('URL')
        or return;

    # Include context for any gripes we emit
    $metadata->context({ excerpt => "URL: $url" });

    # E.g. http://my.host, git://another.host/foo.git
    my ( $protocol, $host ) = ( $url =~ m{^(\w+)://([^/]+)} )
        or do {
        $metadata->gripe(
            {   code => 'InvalidURL',
                diag => "URL must be of the form <protocol>://<host>...",
            }
        );
        return;
        };

    # Gripe about ftp, or anything else unknown, but continue to host check.
    if ( !$Is_Valid_URL_Protocol{$protocol} ) {
        our $valid = join( '/', @Valid_URL_Protocols );
        $metadata->gripe(
            {   code => 'UnknownProtocol',
                diag =>
                    "Unknown protocol '$protocol' in URL; expected $valid",
            }
        );
    }

    # Hostname must include at least one dot. If it doesn't, gripe & bail out.
    if ( $host !~ /\./ ) {
        $metadata->gripe(
            {   code => 'InvalidURL',
                diag => "URL hostname contains no dots",
            }
        );
        return;
    }

    # DNS check on the host. If it doesn't exist, bail out.
    if ( my ( $code, $diag ) = _check_host($host) ) {
        $metadata->gripe(
            {   code => $code,
                diag => $diag,
            }
        );
        return;
    }

    # Actually connect, and make sure URL works, but only for http
    return if $protocol ne 'http';

    my $ua  = LWP::UserAgent->new;
    my $req = HTTP::Request->new( 'GET' => $url );
    my $res = $ua->request($req);

    return if $res->is_success;

    my $http_status = $res->status_line;
    $metadata->gripe(
        {   code => 'BadURL',
            diag => "HTTP GET failed for URL ($http_status)",
        }
    );
}

sub _check_host {
    my $host     = shift;    # in: hostname

    use feature 'state';
    state %host_done;
    # Cache: avoid retesting the same hostname
    return if $host_done{$host}++;

    my %res;

    $res{int} = Net::DNS::Resolver->new();
    $res{ext} = Net::DNS::Resolver->new( nameservers => \@External_NS );

    my %found;
    for my $where (qw(int ext)) {
        if ( my $query = $res{$where}->search($host) ) {
            for my $rr ( $query->answer ) {
                if ( $rr->type =~ /^(A|CNAME)$/ ) {
                    $found{$where} = 1;
                }
            }
        }
    }

    # Truth table:
    #
    #        Int \ Ext  |  found  |  not found           |
    #        -----------+---------+----------------------+
    #        found      |  ok     |  BAD: internal host  |
    #        not found  |  WEIRD  |  BAD: no such host   |
    #        -----------+---------+----------------------+
    #
    if ( !$found{int} ) {
        if ( !$found{ext} ) {
            return ( 'NoSuchHost', "Host <var>$host</var> does not resolve." );
        }
        else {
            return ( 'WeirdHost',
                "WEIRD. Host <var>$host</var> resolves externally, but not inside redhat.com."
            );
        }
    }
    else {
        if ( !$found{ext} ) {
            return ( 'HostnameLeak',
                "Host <var>$host</var> appears to be internal-only." );
        }
    }

    return;
}

# END   individual checks
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

=item   WrongName

FIXME

=item   WrongVersion

FIXME

=item   WrongRelease

FIXME

=item   NoVendor

FIXME - can this happen?

=item   WrongVendor

The B<Vendor> field in the RPM specfile is expected to be C<Red Hat, Inc.>
exactly like that, with the comma and the period.

Yes, we know this is nitpicky.

=item   NoBuildHost

The C<Build Host> field in the rpm metadata is empty. Can this happen?

=item   BadBuildHost

The C<Build Host> field in the rpm metadata is expected to be a host
in the C<.redhat.com> domain.

=item   InvalidURL

The C<URL> field in the rpm specfile is expected to be of the form
C<protocol://host...>. This code indicates that the URL does not
conform to that requirement.

=item   UnknownProtocol

The C<URL> field in the rpm specfile is expected to be of the form
C<protocol://host...>. This code indicates that C<protocol> is not
one that rpmgrill recognizes (http, https, ftp, git).

This is probably OK. It probably just means that rpmgrill needs to
be taught about a new protocol. But it could also be a typo.

=item   InvalidURL2222

FIXME: no dots

=item   BadURL

rpmgrill tried to do an HTTP GET on the URL, but it failed. Maybe the
host is unreachable?

FIXME: Every so often, for reasons I don't understand, it gets a
timeout and reports a problem with a host that is clearly
reachable. Suggestions welcome.

=item   NoSuchHost

The hostname in the rpm specfile URL does not resolve. This probably
means your URL is invalid.

=item   WeirdHost

The hostname in the rpm specfile URL resolves externally (outside
redhat.com) but not internally. This is weird. It is not expected
to happen. If it does, Ed would love to hear about it.

=item   HostnameLeak

The hostname in the rpm specfile URL resolves inside redhat.com
but not outside. This probably means that you're using an
B<internal-only host>. If this package has any external visibility,
you may want to consider changing the URL.

This test is a good candidate for a whitelist: some sort of
small database indicating which packages (eg errata, rpmdiff)
we should silently excuse.

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
