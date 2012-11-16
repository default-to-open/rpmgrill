# -*- perl -*-
#
# RPM::Grill::Plugin::SecurityPolicy - tests for various security-related issues
#
# $Id$
#
# Real-world packages that trigger errors in this module:
# See t/RPM::Grill/Plugin/90real-world.t
#
package RPM::Grill::Plugin::SecurityPolicy;

use base qw(RPM::Grill);

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;
use CGI                 qw(escapeHTML);
use File::Slurp         qw(write_file);

###############################################################################
# BEGIN user-configurable section

# Order in which this plugin runs.  Set to a unique number [0 .. 99]
sub order { 16 }

# One-line description of this plugin
sub blurb { return "checks for potential security-related problems" }

sub doc {
    return <<"END_DOC" }
FIXME: see bz876281
END_DOC

# Contents of a magic file that checks for magic something. See bz876281
our $XSLT = <<'END_XSLT';
<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="xml" indent="yes"/>

  <xsl:template match="/policyconfig">
    <xsl:apply-templates select="action"/>
  </xsl:template>

  <xsl:template match="/policyconfig/action">
    <!-- At least one of the "defaults" elements contains 'self' -->
    <xsl:if test="boolean(defaults/*[contains(text(), 'self')])">
      <action id="{@id}">
        <xsl:copy-of select="defaults"/>
      </action>
      <xsl:text>
</xsl:text>
    </xsl:if>
  </xsl:template>
</xsl:stylesheet>
END_XSLT

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

    for my $rpm ($self->rpms) {
        for my $f ($rpm->files) {
            if ( $f->is_reg && $f->{path} =~ m{^/usr/share/polkit-1/actions/}) {
                $self->_check_polkit_file($f);
            }
        }
    }
}

########################
#  _check_polkit_file  #  bz876281: look for 'self' in polkit files
########################
sub _check_polkit_file {
    my $self = shift;
    my $f    = shift;                           # in: file obj

    # Invoke magic xsltproc validation command provided by Miloslav Trmač.
    # Under normal circumstances this will exit 0 (success) with no output.
    my $xslt = _polkit_self_xslt();
    my $cmd     = "xsltproc --novalid $xslt " . $f->extracted_path;
    my $results = qx{$cmd 2>&1};

    # Nonzero exit status indicates an unexpected error. Diagnose it with
    # a unique error code, and include the error output.
    if ($?) {
        $f->gripe({
            code => 'PolkitError',
            diag => "Unexpected error running command: $cmd",
            context => { path => $f->path, excerpt => escapeHTML($results) },
        });
        return;
    }

    # Successful run. If there was any output, it means we need to gripe.
    if ($results) {
        # The full output from xsltproc is a very long multi-line XML string.
        # The end user doesn't want to see all that. But if the string
        # includes '<action id="org.foo.bar.etc.etc">', excerpt it.
        my $context = { path => $f->path };
        if ($results =~ /(<action\s+id=.*>)/) {
            $context->{excerpt} = escapeHTML($1);
        }

        $f->gripe({
            code => 'PolkitSelf',
            diag => "Suspicious polkit authorization result (any user accepted)",
            context => $context,
        });
    }
}

#######################
#  _polkit_self_xslt  #  Returns path to a file used by xsltproc
#######################
sub _polkit_self_xslt {
    my $xslt = "polkit-self.xslt";

    # First time through: create the file
    if (! -e $xslt) {
        write_file($xslt, $XSLT);
    }

    return $xslt;
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

=item   PolkitError

Unexpected error. We run xsltproc against a polkit file; the command
is always expected to return with exit code 0 (success). This error
indicates that we got nonzero (error) status.

=item   PolkitSelf

The policy shipped in your package contains a default result
<tt>auth_self</tt> or <tt>auth_self_keep</tt>.  These will allow <b>any</b>
user to perform the action by supplying their own password, which they
presumably know because they were able to log in and invoke the action
in the first place.  The <tt>auth_self*</tt> results are therefore
inappropriate for any actions that could affect the
system-wide behavior or other users.

Usually, a more appropriate default result is <tt><b>auth_admin</b></tt>
or <tt><b>auth_admin_keep</b></tt>; these protect the system against
unprivileged users.  (Single-user desktops can still be configured
to only use the user's password by adding the user to the "wheel" group.)

See L<bz876281|https://bugzilla.redhat.com/show_bug.cgi?id=876281>

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
