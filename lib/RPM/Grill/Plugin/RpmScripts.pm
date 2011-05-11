# -*- perl -*-
#
# RPM::Grill::Plugin::RpmScripts - FIXME
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::RpmScripts;

use base qw(RPM::Grill);

use strict;
use warnings;
use version; our $VERSION = qv( '0.0.1' );

use Carp;
use Getopt::Long                qw(:config gnu_getopt);
use Text::ParseWords;
use RPM::Grill::dprintf;

###############################################################################
# BEGIN user-configurable section

# Sequence number for this plugin
sub order {90}

# One-line description of this plugin
sub blurb { return "checks for problems with useradd, etc" }

# FIXME
sub doc {
    return <<"END_DOC" }
FIXME FIXME FIXME
END_DOC


# This is a direct copy-paste from shadow-utils-4.1.4.2-9.el6
# This is a direct copy-and-paste from shadow-4.1.4.2/src/useradd.c .
# FIXME: handle earlier versions of useradd?
our $Useradd_Opts = <<'END_USERADD_OPTS';
		static struct option long_options[] = {
			{"base-dir", required_argument, NULL, 'b'},
			{"comment", required_argument, NULL, 'c'},
			{"home-dir", required_argument, NULL, 'd'},
			{"defaults", no_argument, NULL, 'D'},
			{"expiredate", required_argument, NULL, 'e'},
			{"inactive", required_argument, NULL, 'f'},
			{"gid", required_argument, NULL, 'g'},
			{"groups", required_argument, NULL, 'G'},
			{"help", no_argument, NULL, 'h'},
			{"skel", required_argument, NULL, 'k'},
			{"key", required_argument, NULL, 'K'},
			{"create-home", no_argument, NULL, 'm'},
			{"no-create-home", no_argument, NULL, 'M'},
			{"no-log-init", no_argument, NULL, 'l'},
			{"no-user-group", no_argument, NULL, 'N'},
			{"non-unique", no_argument, NULL, 'o'},
			{"password", required_argument, NULL, 'p'},
			{"system", no_argument, NULL, 'r'},
			{"shell", required_argument, NULL, 's'},
#ifdef WITH_SELINUX
			{"selinux-user", required_argument, NULL, 'Z'},
#endif
			{"uid", required_argument, NULL, 'u'},
			{"user-group", no_argument, NULL, 'U'},
			{NULL, 0, NULL, '\0'}
END_USERADD_OPTS

# Convert that
my @Useradd_Opts;
USERADD_OPT:
for my $line ( split "\n", $Useradd_Opts ) {
    $line =~ m|^\s+ \{\s* "(.*?)",\s* (.*?)_argument,\s* .*?,\s* '(.)'\s*\}|x
        or next USERADD_OPT;
    my ( $long, $type, $short ) = ( $1, $2, $3 );
    $type eq 'required' || $type eq 'no'
        or die "Internal error: option '$long': unknown ${type}_argument";

    my $x = "$long|$short";
    $x .= ":s" if $type eq 'required';

    push @Useradd_Opts, $x;
}

use Data::Dumper; print Dumper(\@Useradd_Opts);

# END   user-configurable section
###############################################################################

# Program name of our caller
( our $ME = $0 ) =~ s|.*/||;

#
# Calls $self->gripe() with problems
#
sub analyze {
    my $self = shift;    # in: FIXME

    # FIXME: read spec, check specs-and-triggers,
    # FIXME: check for shell other than /bin/noshell(?)
    # FIXME: check for missing UID/GID

    # FIXME: read all the RPM.scripts files, not the spec

    # FIXME: read a file containing uid mappings

    #
    # find the specfile
    #
    my $spec  = $self->specfile;
    my @lines = $spec->lines;

  LINE:
    for my $i (0 .. $#lines) {
        my $line = $lines[$i];

        my $s       = $line->content;
        my $section = $line->section;
        my $lineno  = $line->lineno;

        # changelog is the end, and contains no executable code
        last LINE               if $section eq 'changelog';

        if ($s =~ /\b((user|group)add\b.*)/) {
            my $cmd = $1;

            # Concatenate continuation lines
            $cmd .= $lines[++$i]->content       while $cmd =~ s{\s*\\$}{ };

            # Remove redirection, eg '2>/dev/null'
            $cmd =~ s{\s+\d*>\s*\S+}{ }g;

            # Remove trailing whitespace
            $cmd =~ s/\s+$//;

            # useradd/groupadd only valid in %pre
            warn "$ME: specfile:$lineno: script in '$section' section: $s\n"
                if $section ne 'pre';

            dprintf "%d : %s : %s\n", $line->lineno, $line->section, $cmd;

            $spec->context({ lineno => $lineno, excerpt => $cmd });
            _check_add_command( $spec, $cmd );
        }
    }
}


sub _check_add_command {
    my $spec = shift;
    my $cmd  = shift;

    my @words = quotewords('\s+', 0, $cmd); shift @words;
    local (@ARGV) = @words;
#    use Data::Dumper; print Data::Dumper->Dump([ \@ARGV ], [ '@ARGV' ]);

    my %args;
    GetOptions( \%args, @Useradd_Opts);
    use Data::Dumper; print Data::Dumper->Dump([ \%args ], [ '%args' ]);
#    use Data::Dumper; print Data::Dumper->Dump([ \@ARGV ], [ '@ARGV' ]);

    my $arg = shift(@ARGV)
        or do {
            # FIXME: this deserves a gripe
            warn "$ME: WARNING: no user/group/etc in '$cmd'";
            return;
        };
    warn "$ME: WARNING: command '$cmd' left \@ARGV with '@ARGV'" if @ARGV;

    # FIXME
    # Home Directory : required
    if (my $homedir = $args{'home-dir'}) {
    }
    else {
        $spec->gripe({
            code => 'UseraddNoHomedir',
            diag => "Invocation of <tt>useradd</tt> without a home dir",
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

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
