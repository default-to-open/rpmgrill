# -*- perl -*-
#
# RPM::Grill::RPM::Metadata - for reading and parsing rpm -qi
#
# $Id$
#
package RPM::Grill::RPM::Metadata;

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;

( our $ME = $0 ) =~ s|^.*/||;

###############################################################################
# BEGIN user-configurable section

# END   user-configurable section
###############################################################################

#########
#  new  #  Constructor, invoked with a path to a dir that contains RPM.info
#########
#
# Sample RPM.info file (with some spaces removed for readability):
#
#  Name        : git               Relocations: (not relocatable)
#  Version     : 1.7.1                  Vendor: Red Hat, Inc.
#  Release     : 2.el6_0.1          Build Date: Thu 16 Dec 2010 07:25:20 AM MST
#  Install Date: (not installed)    Build Host: x86-010.build.bos.redhat.com
#  Group       : Development/Tools  Source RPM: git-1.7.1-2.el6_0.1.src.rpm
#  Size        : 15189779              License: GPLv2
#  Signature   : (none)
#  Packager    : Red Hat, Inc. <http://bugzilla.redhat.com/bugzilla>
#  URL         : http://git-scm.com/
#  Summary     : Fast Version Control System
#  Description :
#  Git is a fast, scalable, distributed revision control system with an
#  unusually rich command set that provides both high-level operations
#  and full access to internals.
#
#  The git rpm installs the core tools with minimal dependencies.  To
#  install all git packages, including tools for integrating with other
#  SCMs, install the git-all meta-package.
#
# See below for explanation of how we parse this.
#
sub new {
    my $proto = shift;
    my $class = ref($proto) || $proto;

    my $self = bless {}, $class;

    my $rpminfo_dir;
    my $what = shift;           # in: something from which we get a path
    if (ref($what)) {
        if (ref($what) eq 'RPM::Grill::RPM') {
            $rpminfo_dir = $what->dir;
            $self->{_parent_rpm} = $what;
        }
        else {
            croak "$ME: ".__PACKAGE__."->new(): ref isn't RPM::Grill::RPM";
        }
    }
    elsif ($what =~ m{^(.*) / [^/]+\.rpm$}x) {
        $rpminfo_dir = $1;
    }
    elsif (-d $what) {
        $rpminfo_dir = $1;
    }
    else {
        croak "$ME: ".__PACKAGE__."->new(): cannot grok '$what'";
    }

    my $rpminfo_file = "$rpminfo_dir/RPM.info";

    $self->{_rpminfo_path} = $rpminfo_file;

    # Read the RPM.info file for this arch + subpackage
    open my $rpminfo_fh, '<', $rpminfo_file
        or confess "$ME: Internal error: Cannot read $rpminfo_file: $!";
    my $in_description;

LINE:
    while ( my $line = <$rpminfo_fh> ) {

        # Remove trailing newline and whitespace
        chomp $line;
        $line =~ s/\s+$//;

        # See above for a sample of what we're parsing.
        #
        # In particular, once we get to Description, everything after that
        # is Description.  There will be no other 'Label: Value' pairs.
        if ( $line =~ /^(Description)\s*:\s*$/ ) {
            $in_description = $1;
            push @{ $self->{_fields} }, $1;
            next LINE;
        }
        elsif ($in_description) {
            $self->{_data}->{Description} .= $line . "\n";
        }

        # We're not yet at Description.  We *must* see a 'Label: Value' pair.
        # Note that the right-hand side (value) may include another such pair.
        elsif ( $line =~ /^(\S[^:]+\S)\s*:\s*(.*)$/ ) {
            my ( $field, $value ) = ( $1, $2 );
            push @{ $self->{_fields} }, $field;

            # We have to handle the two-column lines (see sample above).
            # For that, we rely on the observed fact (as of rpm-4.8.1) that
            # there are always two or more spaces between the left-hand
            # value and the right-hand label:
            #
            #   Release     : %-27{RELEASE}   Build Date: %{BUILDTIME:date}\n\
            #
            # (from rpmpopt-4.8.1).  And for the right-hand labels, there's
            # never a space between the label and the colon.
            #
            # Yes, this is fragile.  Make it better if you can.
            #
            #               1  2     2 1      3       3    4    4
            if ( $value =~ /^(\S(.*?\S)?)\s{2,}(\S.*?\S):\s+(\S.*)/ ) {
                $value = $1;
                $self->{_data}->{$3} = $4;
                push @{ $self->{_fields} }, $3;
            }

            $self->{_data}->{$field} = $value;
        }
        else {

            # Not in Description section, and not a Label: Value pair.
            warn "$ME: Warning: $rpminfo_file:$.: Cannot grok '$line'";
        }
    }
    close $rpminfo_fh;

    return $self;
}

############
#  fields  #  Returns a list of all metadata fields seen for this package
############
sub fields {
    my $self = shift;

    return @{ $self->{_fields} };
}

#########
#  get  #  Returns a given field
#########
sub get {
    my $self  = shift;
    my $field = shift;    # eg Name, License, ...

    # Called with actual spelling?
    if ( exists $self->{_data}->{$field} ) {
        return $self->{_data}->{$field};
    }

    # No.  Look for a case-insensitive match
    my @match = grep { lc($_) eq lc($field) } @{ $self->{_fields} };
    if ( @match == 1 ) {
        return $self->{_data}->{ $match[0] };
    }

    # No.  Look for a case- and space-insensitive match.  This
    # allows our caller to do ->get("buildhost") or ->buildhost().
    @match = grep { ( my $tmp = $_ ) =~ s/\s//g; lc($tmp) eq lc($field) }
        @{ $self->{_fields} };
    if ( @match == 1 ) {
        return $self->{_data}->{ $match[0] };
    }

    # No match.  Issue a warning, _unless_ this is an optionally-shown field.
    #
    # Explanation: we parse the output of rpm -qi, which is a complicated
    # table hardcoded into rpm itself.  It has custom labels that don't
    # match the rpm tag names, so we can't just run 'rpm --querytags'
    # and compare.  E.g.:
    #
    #    Release     : %-27{RELEASE}   Build Date: %{BUILDTIME:date}\n\
    #
    # It also has several fields that only appear if non-null:
    #
    #    Size        : %-27{SIZE}%|LICENSE?{      License: %{LICENSE}}|\n\
    #    %|URL?{URL         : %{URL}\n}|\
    #
    # ...so we shouldn't gripe if we're called with those (we should
    # just return undef).
    #
    # The 'unless' fields below represent any rpm -qi fields which may
    # have _ever_, at any time, been optional or missing.  For example:
    #
    #                |  rpm-4.4.2.3    |  rpm-4.8.1
    #     -----------+-----------------+-------------
    #     License    |  optional       |  always
    #     Signature  |  (didn't exist) |  optional
    #
    # Since we can't really know what version of rpm we're calling,
    # or what fields are present in an RPM package, we include a
    # superset of all known optional/nonexistent fields between
    # our supported versions of rpm.
    #
    # To update, see /usr/lib/rpm/rpmpopt-$VERSION or rpm-src/rpmpopt.in
    #
    carp "$ME: WARNING: No match for metadata field '$field'"
        unless $field =~ /^(URL|Packager|License|Signature)$/i;

    return;
}

##############
#  AUTOLOAD  #  For accessing internal hash elements
##############
sub AUTOLOAD {
    my $self = shift;

    our $AUTOLOAD;
    ( my $field = $AUTOLOAD ) =~ s/^.*:://;

    return $self->get($field);
}

sub DESTROY { }

###############################################################################
# BEGIN gripe and context

sub rpm {
    exists $_[0]->{_parent_rpm}
        or confess "$ME: Internal error: no parent_rpm for metadata";

    return $_[0]->{_parent_rpm};
}

###########
#  gripe  #
###########
sub gripe {
    my $self  = shift;                  # in: RPM::Grill::RPM::SpecFile obj
    my $gripe = shift;                  # in: hashref with gripe info

    croak "$ME: ->gripe() called without args"        if ! $gripe;
    croak "$ME: ->gripe() called with too many args"  if @_;
    croak "$ME: ->gripe() called with a non-hashref"  if ref($gripe) ne 'HASH';

    my %gripe = (
        arch       => $self->rpm->arch,
        subpackage => $self->rpm->subpackage,
        context    => $self->context,

        %$gripe,
    );

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
        $context{path} = '[RPM metadata]',

        return \%context;
    }
}

# END   gripe and context
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
