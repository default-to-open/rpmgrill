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
our $VERSION = '0.01';

use Carp;
use Algorithm::Diff                     qw(diff sdiff);
use RPM::Grill::Util		qw(sanitize_text);
use File::Basename;
use IPC::Run                            qw(run timeout);
use Time::ParseDate;
use Time::Piece;

###############################################################################
# BEGIN user-configurable section

# Sequence number for this plugin
sub order {5}

# One-line description of this plugin
sub blurb { return "checks for problems in spec file" }

sub doc {
    return <<"END_DOC" }
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
    my $self = shift;

    _check_for_other_specfile_problems( $self );
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
        if ($s =~ /^(\s*#.*[^%])%(patch|if|else|endif|define)/o) {
            my ($lhs, $match, $rhs) = ($1, $2, $');
            $self->gripe(
                {   code    => "MacroSurprise",
                    diag    => "RPM <tt>%$match</tt> macro in comments; this may cause unexpected behavior",
                    context => {
                        path    => $specfile_basename,
                        lineno  => $lineno,
                        excerpt => sanitize_text($lhs) . "<b>%$match</b>"
                                 . sanitize_text($rhs),
                    },
                });
        }
    }

    $self->_check_changelog_version();
    $self->_check_changelog_macros();
}


##############################
#  _check_changelog_version  #  Check version in first %changelog line
##############################
sub _check_changelog_version {
    my $self = shift;

    my $spec  = $self->specfile;
    my $specfile_basename = basename($spec->path);

    my @changelog = $spec->lines('%changelog')
        or do {
            # No %changelog??
            $self->gripe({
                code => 'ChangelogMissing',
                diag => 'No <b>%changelog</b> section in specfile',
                context => { path => $specfile_basename },
            });
            return;
        };

    #
    # Check changelog. In particular, look for mismatch
    # between the reported version and the actual NVR
    #
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
        excerpt => sanitize_text($cl_first),
    };

    # Parse out the V-R, eg "* <date> <author> 1.2-4"
    if ($cl_first =~ /^\*\s+.*\s(\S+)\s*$/) {
        my $vr = $1;                # eg 1.2-4
        my @nvr = $self->nvr;       # eg foo, 1.2, 4.el5

        # Some people include package name, e.g. qemu-kvm-0.12.1.2
        if ($vr =~ s{^(\d+:)?$nvr[0]-}{$1 || ''}e) {
            $self->gripe({
                code => 'ChangelogOnlyNeedsVR',
                diag => "%changelog entries should only include Version-Release, not package name; try just <var>$vr</var>",
                context => $context,
            });
        }

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

            # It's OK to use %{?dist} in the release string
            $r =~ s/\%\{\?dist\}$/.*/;

            if ($v ne $nvr[1]) {
                # Version does not match. But can we match partially?
                if ($v =~ /^(.+)\b$nvr[1]$/) {
                    # Yes: there's a prefix before the version.
                    $self->gripe({
                        code => 'ChangelogCruftInVersion',
                        diag => "First %changelog entry includes unnecessary cruft (<var>$1</var>) in the version string; You only need <var>$nvr[1]</var>.",
                        context => $context,
                    });
                }
                else {
                    # No. Something completely unexpected
                    $self->gripe({
                        code => 'ChangelogBadVersion',
                        diag => "First %changelog entry is for <var>$v-$r</var>; I was expecting <var>$nvr[1]</var> as the version, not $v",
                        context => $context,
                    });
                }
            }
            elsif ($nvr[2] !~ /^$r\b/) {
                $self->gripe({
                    code => 'ChangelogBadRelease',
                    diag => "First %changelog entry is for <var>$v-<u>$r</u></var>; I was expecting <var>$nvr[1]-<u>$nvr[2]</u></var>",
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


#############################
#  _check_changelog_macros  #  Check for macros in %changelog
#############################
sub _check_changelog_macros {
    my $self = shift;

    my $spec  = $self->specfile;
    my $specfile_basename = basename($spec->path);

    # (assume that previous code has already barfed if there's no changelog)
    my @changelog = $spec->lines('%changelog')
        or return;

    # First line is just '%changelog'. Remove it.
    shift @changelog;
    return if !@changelog;

    my @cl_orig = map { $_->content } @changelog;
    my @cl_post = $self->srpm->changelog;

    # rpm -q --changelog usually adds a trailing blank line. Remove it.
    # (from specfile, too, just in case).
    for my $aref (\@cl_orig, \@cl_post) {
        while (@$aref && $aref->[-1] =~ /^\s*$/) {
            pop @$aref;
        }

        # And, sigh, remove trailing spaces from both.
        s/\s+$//                    for @$aref;
    }

    # AUGH. rpm strips leading spaces, but only on the first line
    # after a '*' line. This specfile entry:
    #
    #   * Mon Aug 21 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-5jpp
    #     From Andrew Overholt <overholt@redhat.com>:
    #   - Silence post common-lib and server-lib.
    #
    # ...will become:
    #
    #   * Mon Aug 21 2006 Fernando Nasser <fnasser@redhat.com> 0:5.5.17-5jpp
    #   From Andrew Overholt <overholt@redhat.com>:
    #   - Silence post common-lib and server-lib.
    #
    my $lineno = $changelog[0]->lineno;
    for (my $i=1; $i <= $#cl_orig; $i++) {
        if ($cl_orig[$i-1] =~ /^\*\s/) {
            if ($cl_orig[$i] =~ s/^(\s+)//) {
                my $whitespace = $1;
                # FIXME: should we warn the user? Make it INFO somehow?
                $self->gripe({
                    code => 'ChangelogLeadingWhitespace',
                    diag => "Leading whitespace in this %changelog entry will be lost",
                    context => {
                        path    => $specfile_basename,
                        lineno  => $lineno + $i,
                        excerpt => $whitespace . sanitize_text($cl_orig[$i]),
                    },
                });
            }
        }
    }

    # rpm converts double-percent to single. Let's do the same to
    # our input, on the assumption that a developer who writes '%%'
    # understands rpm specfile parsing.
    s/%%/%/g                    for @cl_orig;

    # Normalize dates in the input specfile. 'rpm -q --changelog' always
    # shows dates with a leading zero (Wed Dec 05 2012), even if the
    # specfile input has none. Let's fix those up in our copy of the
    # specfile lines, so they won't trigger as false diffs.
    #
    # While we're at it, gripe about weekdays. 'rpm -q --changelog' always
    # displays the correct weekday for a given date. Human developers are
    # less accurate.
    $lineno = $changelog[0]->lineno;
  LINE:
    for my $line (@cl_orig) {
        # Changelog lines begin with asterisk, then a date, then more.
        # eg '* Fri Oct 15 2010 Ed Santiago <santiago@redhat.com> 1.4.50-1'
        #
        #              1     12   2   3               34    4
        if ($line =~ /^(\*\s+)(\w+)\s+(\w+\s+\d+\s+\d+)(\s.*)$/) {
            my ($lhs, $wday, $date, $rhs) = ($1, $2, $3, $4);

            # If we can't grok $date as a date, skip this line.
            my ($t, $err) = parsedate($date);
            if (! defined $t) {
                warn "$ME: WARNING: $specfile_basename:$lineno: Error parsing '$date' as date: $err\n";
                ++$lineno;
                next LINE;
            }

            # It's a valid date. Now check that the date & weekday match.
            my $lt = localtime($t);
            if (lc($lt->wdayname) ne lc($wday)) {
                # Try to offer a helpful message. The likely correction is
                # the weekday, but it could also be the date that's wrong.
                my $diag = "$date is actually a <b>".$lt->fullday . "</b>.";
                $diag .= _date_suggestion($lt, $wday);

                $self->gripe({
                    code => 'ChangelogWrongWeekday',
                    diag => $diag,
                    context => {
                        path    => $specfile_basename,
                        lineno  => $lineno,
                        excerpt => sanitize_text($lhs)
                            . "<u>" . sanitize_text($wday) . "</u> "
                            . sanitize_text($date . $rhs),
                    },
                });
            }

            # Normalize it
            local $ENV{LC_ALL} = 'C';
            $line = $lhs . $lt->strftime("%a %b %d %Y") . $rhs;
        }

        ++$lineno;
    }

    # Get the diffs between the original (specfile) changelog and the
    # parsed one. Gripe about any that involve macros.
    $lineno = $changelog[0]->lineno;
    my @diffs = diff( \@cl_orig, \@cl_post );
#    use Data::Dumper; print STDERR Dumper(\@diffs);
    for my $diff (@diffs) {
        if (my $excerpt = _is_macro_diff($diff)) {
            $self->gripe({
                code => 'ChangelogMacros',
                # FIXME: better diagnostic!
                # FIXME: "Unescaped percent signs (%) in specfiles may be expanded unexpectedly"
                diag => "Percent signs (%) in specfile changelog should be escaped",
                context => {
                    path    => $specfile_basename,
                    lineno  => $lineno + $diff->[0][1],
                    excerpt => $excerpt,
                },
            });
        }
    }
}

######################
#  _date_suggestion  #  Offer ideas for fixing a date/weekday mismatch
######################
sub _date_suggestion {
    my $lt   = shift;                           # in: Time::Piece
    my $wday = shift;                           # in: what the user wrote

    my $hint = " Or did you mean";

    # Eg " Or Mar <b>29</b>?", or " Or <b>Apr 1</b>?"
    for my $i (-3 .. 3) {
        my $lt2 = $lt + $i * 86400;
        if ($lt2->wdayname eq $wday) {
            $hint .= " ";

            my $same_mon  = ($lt2->mon  == $lt->mon);
            my $same_year = ($lt2->year == $lt->year);
            $hint .= "<b>"                      if !$same_mon;
            $hint .= $lt2->monname;
            $hint .= " ";
            $hint .= "<b>"                      if $same_mon;
            $hint .= $lt2->mday;
            $hint .= " " . $lt2->year           if !$same_year;
            $hint .= "</b>?";
        }
    }

    return $hint;
}

####################
#  _is_macro_diff  #  Returns the change between two specfile lines
####################
#
# If diff element is one that involves macros (%), returns a friendly
# excerpt message of the form:
#
#    spec: blah blah %foo
#    rpm : blah blah /expanded-value-of-foo
#
# Otherwise, returns undef.
#
sub _is_macro_diff {
    my $diff = shift;                           # in: Algorithm::Diff entry

    # We're only interested in changes (-/+), not deleted or added lines.
    return unless @$diff == 2;
    return unless $diff->[0][0] eq '-' && $diff->[1][0] eq '+';

    # Only interested if the previous (changed) line has a percent sign
    return unless $diff->[0][2] =~ /%/;

    # Split into two arrays, each divided into its component words.
    my @ante = map {sanitize_text($_)} grep($_ ne '',split(/(\W)/,$diff->[0][2]));
    my @post = map {sanitize_text($_)} grep($_ ne '',split(/(\W)/,$diff->[1][2]));

    for my $d (diff( \@ante, \@post )) {
        for my $delta (@$d) {
            # Removing a char? Highlight it on the left
            if ($delta->[0] eq '-') {
                $ante[$delta->[1]] =
                    "<var>$ante[$delta->[1]]</var>";
            }
            # Adding a char?  Highlight on the right
            elsif ($delta->[0] eq '+') {
                $post[$delta->[1]] =
                    "<var>$post[$delta->[1]]</var>";
            }

            # Anything else?  Should never happen.
            else {
                warn "$.: Unknown delta char '$delta->[0]'\n";
            }
        }
    }

    # FIXME
    (my $ante = join('', @ante)) =~ s|</var><var>||g;
    (my $post = join('', @post)) =~ s|</var><var>||g;

    # It's ok to use %{?dist} in any line that begins with '*':
    #  * Mon Jan 07 2013 Matthias Clasen <mclasen@redhat.com> - 0.109-2%{?dist}
    # FIXME: this assumes that there won't be any %-macros anywhere else
    # in that line. Sounds like a reasonable assumption, but just you wait.
    return if $ante =~ m{^\*\s .* <var>\%\{\?dist\}\s*</var>\s*$}x;

    # Return a human-friendly string highlighting the diffs.
    return "spec: $ante\nrpm : $post";
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

=item   MacroSurprise

Did you know that RPM expands macros even inside comments?

Sometimes this is OK: %{name}, %{version}. But when %{foo} is
a multi-line macro, or %if, or %patch, this can cause unpleasant
surprises. As of May 2012 this test will only trigger on a
certain well-defined list of hazardous macros: patch, if, else,
endif, define. (It used to trigger on %anything, but that gave
way too much noise). This list may need to be refined over time.

B<Recommendation>: Double-percent all macros in comments: %%{name}

=item   ChangelogMissing

There is no %changelog section in your specfile. Can this happen?

=item   ChangelogEmpty

The %changelog section in your specfile is empty. This error doesn't
sound like it could happen, but it does.

=item   ChangelogOnlyNeedsVR

You included your package name in the %changelog entry. All you need
is the Version-Release.
See L<http://fedoraproject.org/wiki/Packaging:Guidelines#Changelogs>

=item   ChangelogCruftInVersion

The version string in your first %changelog entry includes unnecessary
cruft.

=item   ChangelogWrongEpoch

You included an epoch in your %changelog entry, but it's the wrong one.

=item   ChangelogUnexpectedEpoch

You included an epoch in your %changelog entry, but the specfile itself
does not define an Epoch.

=item   ChangelogBadVersion

The version string in your first %changelog entry does not match the
one defined in the package specfile.

=item   ChangelogBadRelease

The release string in your first %changelog entry does not match the
one defined in the package specfile.

=item   ChangelogWeirdLine

I could not parse the first line of the %changelog section in your specfile.
See L<http://fedoraproject.org/wiki/Packaging:Guidelines#Changelogs>

=item   ChangelogLeadingWhitespace

You've indented a line in a changelog message, perhaps for clarity,
but that indentation will not survive rpmbuild. Customers who run
C<rpm -q --changelog> will see that line without any leading whitespace.
This is probably not a cataclysmic source of confusion, but please
check anyway.

=item   ChangelogMacros

Percent signs in .spec files get expanded as macros. When you
write "Replaced /bin with %{bindir}", C<rpm -q --changelog> will
show "Replaced /bin with /bin". Confusing. The excerpt in the
gripe message shows you what you wrote and what customers will see.

Solution: B<double up percent signs: %%{foo}>.

=item   ChangelogWrongWeekday

A specfile %changelog entry has a mismatch between the weekday
and the date. There is no automated way to know which is correct.
This needs human intervention.

=back

=head1	SEE ALSO

L<>

=head1	AUTHOR

Ed Santiago <santiago@redhat.com>

=cut
