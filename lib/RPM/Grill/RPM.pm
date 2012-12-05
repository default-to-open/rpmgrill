# -*- perl -*-
#
# FIXME  -  add package description here
#
# $Id$
#
package RPM::Grill::RPM;

use strict;
use warnings;

our $VERSION = '0.01';

use Carp;
use File::Basename      qw(dirname);

###############################################################################
# BEGIN user-configurable section

# Name, Version, Release (NVR), in that order
our @NVR_Fields = qw(name version release);

# END   user-configurable section
###############################################################################

# Program name of our caller
(our $ME = $0) =~ s|.*/||;

#########
#  new  #  Constructor.
#########
sub new {
    my $proto = shift;
    my $class = ref($proto) || $proto;

    my $path = shift			# in: mandatory arg
	or croak "Usage: ".__PACKAGE__."->new( PATH-TO-RPM )";

    $path =~ /\.rpm$/
        or croak "$ME: Input arg must have a .rpm extension ($path)";

    -e $path
        or croak "$ME: RPM path does not exist: $path";

    my ($arch, $subpackage) = $path =~ m{/ ([^/]+) / ([^/]+) / [^/]+\.rpm$}x
        or croak "$ME: path '$path' does not include /<arch>/<subpkg>/";

    my $self = {
        path       => $path,
        arch       => $arch,
        subpackage => $subpackage,
        dir        => dirname($path),
    };

    return bless $self, $class;
}


###########
#  grill  #  Used for referring to our parent RPM::Grill object
###########
sub grill {
    my $self  = shift;

    if (@_) {
        my $grill = shift;
        ref($grill)
            or croak "$ME: ->grill() invoked with non-ref";
        ref($grill) eq 'RPM::Grill'
            or croak "$ME: ->grill(): arg is not a RPM::Grill ref";
        $self->{grill} = $grill;
    }

    return $self->{grill};
}

sub arch       { return $_[0]->{arch}       }
sub subpackage { return $_[0]->{subpackage} }
sub dir        { return $_[0]->{dir}        }
sub path       { return $_[0]->{path}       }

sub is_64bit {
    my $self  = shift;

    if (@_) {
        $self->{is_64bit} = shift;
    }

    return $self->{is_64bit};
}


sub multilib_peers {
    my $self  = shift;

    if (@_) {
        my $peers = shift;
        ref($peers)
            or croak "$ME: ->multilib_peers() invoked with non-ref";
        ref($peers) eq 'ARRAY'
            or croak "$ME: ->multilib_peers(): arg is not ARRAY ref";
        grep { ref($_) ne 'RPM::Grill::RPM' } @$peers
            and croak "$ME: ->multilib_peers(): non-RPM ref in array";
        $self->{multilib_peers} = $peers;
    }

    return wantarray ? @{$self->{multilib_peers}} : $self->{multilib_peers};
}

#########
#  nvr  #  Returns n-v-r as string or list
#########
sub nvr {
    my $self = shift;

    # First time through
    if ( !exists $self->{nvr} ) {

        my $m = $self->metadata;

        for my $field (@NVR_Fields) {
            my $value = $m->get($field);
            defined $value
                or die "$ME: Internal error: No '$value' in RPM metadata";
            $self->{nvr}->{ lc $field } = $value;
        }
    }

    # Invoked with an arg?  Return just one of the fields.
    if (@_) {

        # This is the only arg we accept
        my $want = shift;
        croak "$ME: Invalid extra args (@_) in ->nvr()" if @_;

        my @match = grep {/^$want/i} @NVR_Fields
            or croak "$ME: ->nvr('$want'): Unknown N-V-R field";
        return $self->{nvr}->{ lc $match[0] };
    }

    # Return to caller, either as (n, v, r) or "n-v-r"
    my @nvr = map { $self->{nvr}->{$_} } @NVR_Fields;

    return wantarray
        ? @nvr
        : join( '-', @nvr );
}


##############
#  metadata  #  'rpm -qi' (info) for one specific rpm
##############
sub metadata {
    my $self       = shift;

    use    RPM::Grill::RPM::Metadata;
    return RPM::Grill::RPM::Metadata->new( $self );
}


################
#  capability  #  Returns the contents of one of the RPM.xxx files
################
sub capability {
    my $self = shift;
    my $cap  = shift;           # in: 'requires', 'provides', etc

    # memoize
    $self->{_capability_cache}{$cap} //= do {
        # eg ..../arch/subpackage/RPM.requires
        my $cap_file = $self->dir . '/RPM.' . $cap;
        -e $cap_file
            or croak "$ME: Capability file $cap_file does not exist";

        my @results;
        open my $cap_fh, '<', $cap_file
            or die "$ME: Internal error: Cannot read $cap_file: $!";
        while (<$cap_fh>) {
            chomp;
            s/\s+$//;                       # Remove trailing whitespace
            push @results, $_;
        }
        close $cap_fh;

        @results;
    };

    return @{ $self->{_capability_cache}{$cap} };
}

# Direct shortcut methods for the above capabilities files
sub requires  { push @_, 'requires';  goto &capability; }
sub provides  { push @_, 'provides';  goto &capability; }
sub obsoletes { push @_, 'obsoletes'; goto &capability; }
sub conflicts { push @_, 'conflicts'; goto &capability; }
sub changelog { push @_, 'changelog'; goto &capability; }

###########
#  files  #  Returns a list of RPM::Grill::RPM::File objects, from manifest
###########
sub files {
    my $self       = shift;

    use RPM::Grill::RPM::Files;
    $self->{files} ||= RPM::Grill::RPM::Files::gather( $self );

    return wantarray ? @{ $self->{files} } : $self->{files};
}


##################
#  daemon_files  #  Identifies the files in this RPM which may be daemons
##################
sub _find_daemon_files {
    my $self = shift;

    my @all_files = $self->files;
    my %is_daemon;

    #
    # Find all /etc/init.d/* or /lib/systemd/* files in _this_ RPM.
    #
    for my $f (@all_files) {
        # Old-style /etc/init.d file.
        if ($f->path =~ m{^/etc(/rc\.d)?/init\.d/([^/]+)$}) {
            my $initfile_basename = $2;

            # If this RPM includes a bin file with the same name as
            # the init file, or with a 'd' suffix, assume it's a daemon.
            # e.g. /etc/init.d/syslog -> /sbin/syslogd
            #      /etc/init.d/acpid  -> /usr/sbin/acpid
            $_->{_is_daemon} = 1
                for grep { $_->path =~ m{/s?bin/${initfile_basename}d?$} } @all_files;

            # Read through the file, looking for lines of the form
            #     [ -x /usr/sbin/whatever ] || exit 5
            if (open my $initfile_fh, '<', $f->extracted_path) {
              LINE:
                while (my $line = <$initfile_fh>) {
                    next LINE   if $line =~ /^\s*\#/;

                    if ($line =~ m{\s-\w\s+(/\S+)\s.*\sexit\s5}) {
                        my $daemon = $1;

                        $_->{_is_daemon} = 1
                            for grep { $_->path eq $daemon } @all_files;
                    }
                }
                close $initfile_fh;
            }
        }

        # New-style (RHEL7 and up) systemd file
        elsif ($f->path =~ m{/lib(64)?/systemd(/.*)?/([^/]+)$}) {
            # Read through the file, looking for lines of the form
            #     ExecStart=/usr/bin/fubar, mark fubar as daemon
            if (open my $initfile_fh, '<', $f->extracted_path) {
              LINE:
                while (my $line = <$initfile_fh>) {
                    next LINE   if $line =~ /^\s*\#/;

                    if ($line =~ m{\s*ExecStart=-?(\S+)}) {
                        my $daemon = $1;
                        $_->{_is_daemon} = 1
                            for grep { $_->path eq $daemon } @all_files;
                    }
                }
                close $initfile_fh;
            }
        }
    }

    # No return value
    return;
}


use overload '""' => \&_as_string;

sub _as_string {
    my $self = shift;

    my $nvr = $self->nvr;
    return sprintf("%s.%s.rpm", $nvr, $self->arch);
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

=head1	SEE ALSO

L<Some::OtherModule>

=head1	AUTHOR

Ed Santiago <ed@edsantiago.com>

=cut
