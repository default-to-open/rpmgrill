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
use RPM::Grill::Util		qw(sanitize_text);
use Errno;
use File::Temp          qw(tempfile);
use Sort::Versions      qw(versioncmp);
use YAML::Syck;
use RPM::Grill::dprintf;

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

# Locally cached copy; see rpmgrill-update-ruby-advisory-db script to
# find out how that gets updated.
our $Ruby_Advisory_DB = "/usr/share/rpmgrill/ruby-advisory-db";

# Template for linking to rubysec. '%s' will be replaced by CVE ID.
our $Rubysec_URL_Template = 'http://rubysec.github.com/advisories/CVE-%s/';

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
        $self->_check_rubygem_cves($rpm);

        for my $f ($rpm->files) {
            if ( $f->is_reg && $f->{path} =~ m{^/usr/share/polkit-1/actions/}) {
                $self->_check_polkit_file($f);
            }
        }
    }
}

###############################################################################
# BEGIN bz876281 - polkit files

########################
#  _check_polkit_file  #  bz876281: look for 'self' in polkit files
########################
sub _check_polkit_file {
    my $self = shift;
    my $f    = shift;                           # in: file obj

    # Invoke magic xsltproc validation command provided by Miloslav Trmač.
    # Under normal circumstances this will exit 0 (success) with no output.
    my $xslt_file = _polkit_self_xslt();
    my $cmd       = "xsltproc --novalid $xslt_file " . $f->extracted_path;
    my $results   = qx{$cmd 2>&1};
    my $cmdstatus = $?;
    unlink $xslt_file;

    # Nonzero exit status indicates an unexpected error. Diagnose it with
    # a unique error code, and include the error output.
    if ($cmdstatus) {
        $f->gripe({
            code => 'PolkitError',
            diag => "Unexpected error running command: $cmd",
            context => { path => $f->path, excerpt => sanitize_text($results) },
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
            $context->{excerpt} = sanitize_text($1);
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
    # This file is used by an external program; it is our caller's
    # responsibility to delete after use.
    my ($fh, $path) = tempfile("polkit-self-XXXXXXX",
                               TMPDIR => 1,
                               SUFFIX => '.xslt',
                           );

    print { $fh } $XSLT;                # (Defined at top of this module)
    close $fh
        or die "$ME: Error writing $path: $!\n";

    return $path;
}

# END   bz876281 - polkit files
###############################################################################
# BEGIN bz928428 - ruby gems

#########################
#  _check_rubygem_cves  #  Check <gem>-<version> against list of Ruby Gem CVEs
#########################
#
# We keep a local cache of https://github.com/rubysec/ruby-advisory-db .
# Any time we analyze a package named "rubygem-foo-1.0-*", we look for
# CVEs against gem "foo" at the given version.
#
sub _check_rubygem_cves {
    my $self = shift;
    my $rpm  = shift;

    # Only interested in packages named 'rubygem-X'. We only need to check once.
    my $name = $rpm->nvr('name');
    return unless $name =~ s/^(ruby\S+-)?rubygem-//;
    return if $self->{_plugin_state}{nvr_checked}{$name}++;

    -d $Ruby_Advisory_DB
        or warn "$ME: WARNING: missing Ruby Advisory DB dir $Ruby_Advisory_DB";

    # Look for a subdirectory with the gem's name. ENOENT means the
    # subdirectory doesn't exist, which is OK (there might not be any
    # advisories against this gem). Any other error is bad news.
    my $dir = "$Ruby_Advisory_DB/gems/$name";
    opendir my $dir_fh, $dir
        or do {
            warn "$ME: WARNING: Cannot opendir $dir: $!\n" unless $!{ENOENT};
            return;
        };

    # There's a subdirectory for this gem. Read and process all *.yml files.
    for my $f (sort grep { /^\w[\w-]+\.yml$/ } readdir $dir_fh) {
        $self->_check_cve_file( $rpm, "$dir/$f" );
    }
    closedir $dir_fh;
}

#####################
#  _check_cve_file  #  Helper. Reads one .yml file, tests version strings
#####################
#
# This is what does all the work: it reads one .yml file containing
# a ruby gem vulnerability. That file will include a list such as:
#
#     patched_versions:
#       - ~> 3.0.12
#       - ~> 3.1.4
#       - ">= 3.2.2"
#
# We compare our package's version against each of those. If the version
# test is satisfied, we return. Otherwise, we look in the specfile's
# %changelog section to see if a fix has been backported. If it hasn't,
# we emit a warning.
#
sub _check_cve_file {
    my $self = shift;
    my $rpm  = shift;
    my $f    = shift;                           # in: path to CVE file

    my $cve = LoadFile($f)
        or die "Eeeek, internal error, could not read $f: $!";

    # CVE will probably include a list of versions which are safe.
    # FIXME: what if it's a new CVE and hasn't been fixed anywhere yet?
    my $patched_versions = $cve->{patched_versions}
        or do {
            warn "$ME: WEIRD: File has no {patched_versions}: $f";
            return;
        };

    # Internal sanity check. FIXME: Can this ever fail?
    (ref($patched_versions)||'') eq 'ARRAY'
        or do {
            warn "$ME: WEIRD: {patched_versions} is not an AREF: $f";
            return;
        };

    # Each of these should return true if it satisfies '<v1> <op> <v2>'
    my %ruby_vercmp = (
        '>'  => sub { versioncmp($_[0], $_[1]) >  0 },
        '>=' => sub { versioncmp($_[0], $_[1]) >= 0 },
        '~>' => \&ruby_pessimistic_ge,
    );
    my $ruby_version_operator = join('|', sort keys %ruby_vercmp);

    my $our_version = $rpm->nvr('version');

    # Iterate over each of the patched_versions.
  VERSION:
    for my $v (@$patched_versions) {
        $v =~ /^($ruby_version_operator)\s+(\S+)$/
            or do {
                warn "$ME: WEIRD: Cannot grok patched_version '$v' in $f";
                next VERSION;
            };

        my ($operator, $desired_version) = ($1, $2);    # eg '>=', '1.2'

        dprintf "[ $our_version $operator $desired_version : ";
        if ($ruby_vercmp{$operator}->( $our_version, $desired_version )) {
            dprintf "TRUE ]\n";
            return;     # all ok
        }
        dprintf "false ]\n";
    }

    # If we get here, our package version does not satisfy any of the
    # CVE version requirements. We *may* be vulnerable. Let's check
    # the specfile's %changelog, looking for 'Fix: CVE-id'. If we
    # find it, assume we're safe.
    my $spec = $self->specfile;
    if (my @changelog = $spec->lines('%changelog')) {
        for my $line (map { $_->content } @changelog) {
            while ($line =~ /\b[Ff]ix(es|ed)?\s*(CVEs?[\d\s,;-]+)/g) {
                my $cves = $2;
                if ($cves =~ /\b$cve->{cve}\b/) {
                    return;                     # We're safe.
                }
            }
        }
    }

    # Nothing found in %changelog. Issue a warning.
    my $diag = sprintf("<tt>%s</tt> gem may be affected by <var>CVE-%s</var>",
                       sanitize_text($cve->{gem}),
                       sanitize_text($cve->{cve}));
    my $url = sprintf($Rubysec_URL_Template, $cve->{cve});
    my $excerpt = sprintf("<a href=\"%s\">CVE-%s: %s</a>",
                          $url,
                          sanitize_text($cve->{cve}),
                          sanitize_text($cve->{title}));
    $self->gripe({
        code => 'RubyAdvisoryDB',
        diag => $diag,
        context => {
            excerpt => $excerpt,
        },
    });
}


#########################
#  ruby_pessimistic_ge  #  Handles the ruby '~>' version comparison operator
#########################
#
# See http://docs.rubygems.org/read/chapter/16
#
sub ruby_pessimistic_ge {
    my ($v1, $v2) = @_;                                 # in: 2 versions

    # Per above URL: ‘~> 2.2’ is equivalent to: [‘>= 2.2’, ‘< 3.0’].
    # So if our given $v1 is less than the minimum requirement, we fail.
    return 0 if versioncmp($v1, $v2) < 0;

    # The given $v1 is greater than or equal to the minimum requirement.
    # Now define a _maximum_ requirement by stripping off the last digit
    # (e.g. 2.2 becomes 2) then bumping up the now-rightmost digit (2->3).
    $v2 =~ s/(\d+)\.\d+$/$1 + 1/e
        or die "Internal error: Could not grok version string '$v2'";

    return 0 if versioncmp($v1, $v2) >= 0;
    return 1;
}

# END   bz928428 - ruby gems
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

=item	RubyAdvisoryDB

Package may be affected by a Ruby Gem CVE. This test compares the Gem
name and version (but not the release) against a master list of
L<known vulnerabilities|https://github.com/rubysec/ruby-advisory-db>.
If the name+version match a known CVE, this warning is triggered.

If you have backported a fix, please include the string
C<Fix CVE-YYYY-NNNN> in your specfile's %changelog section. This
will silence the warning for a given CVE.

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
