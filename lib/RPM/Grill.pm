# -*- perl -*-
#
# RPM::Grill - scaffolding for analyzing, testing RPM builds
#
# $Id$
#
package RPM::Grill;

use strict;
use warnings;
our $VERSION = '0.01';

use Carp;
use Module::Pluggable
    except   => 'RPM::Grill::Plugin::AAATemplate',
    require  => 1,
    sub_name => '_plugins';

use List::Util        qw(max);
use HTML::Entities    qw(encode_entities);
use XML::Simple;
use YAML;

use RPM::Grill::dprintf;
use RPM::Grill::RPM;

###############################################################################
# BEGIN user-configurable section

# When a plugin calls ->gripe, these are the fields it can set. A '*'
# next to the name means 'this is a required field'.
our @Gripe_Fields = qw(code* arch subpackage context diag* severity confidence);

# Which of these are mandatory? DO NOT MOVE THIS LINE. Aside from defining
# the list of required fields, this also has the side effect of stripping
# the '*' (asterisk) from the field names. Failure to do this early will
# result in a very-much-not-what-you-want definition of %Is_Gripe_Field
our @Required_Gripe_Fields = grep { s/\*// } @Gripe_Fields;

# 'Context' is a subhash inside a gripe.
our @Gripe_Context_Fields = qw(path lineno sub excerpt);


# Convert that to a usable hash form
our %Is_Gripe_Field         = map { $_ => 1 } @Gripe_Fields;
our %Is_Gripe_Context_Field = map { $_ => 1 } @Gripe_Context_Fields;

# Name, Version, Release (NVR), in that order
our @NVR_Fields = qw(name version release);

# 32- and 64-bit architectures. Left-hand side of this table
# lists 32-bit ones, right-hand side 64.
our $Arch_Map = <<'END_ARCH_MAP';
i386 i586 i686 athlon  | x86_64 ia64
ppc                    | ppc64
s390                   | s390x
END_ARCH_MAP

# 2013-01-18 these are special Windows "architectures". They are not
# RPM-based, and have no RPMs. We care about them because we run AV scans.
our @Non_RPM_Arches = qw(maven win);
our %Is_Non_RPM_Arch = map { $_ => 1 } @Non_RPM_Arches;

our %Multilib_Peers;
our %Is_64bit;
for my $line (split "\n", $Arch_Map) {
    $line =~ s/^\s+//;          # Remove leading...
    $line =~ s/\s+$//;          # ...and trailing whitespace

    # Split into left and right sides, on the '|'
    my ($lhs, $rhs) = split( /\s+\|\s+/, $line);
    my @arch32 = split ' ', $lhs        or die "Internal error: LHS = '$lhs'";
    my @arch64 = split ' ', $rhs        or die "Internal error: RHS = '$rhs'";

    $Is_64bit{$_} = 0                   for @arch32;
    $Is_64bit{$_} = 1                   for @arch64;

    $Multilib_Peers{$_} = [ @arch64 ]   for @arch32;
    $Multilib_Peers{$_} = [ @arch32 ]   for @arch64;
}

# Special case for the non-RPM architectures
$Is_64bit{$_} = 0  for @Non_RPM_Arches;


# END   user-configurable section
###############################################################################

# Program name of our caller
( our $ME = $0 ) =~ s|.*/||;

###############################################################################
# BEGIN data-gathering code

#
# FIXME: what is $self going to be?
#
# Obviously it should have exactly one spec.  But for other packages
# we have trees of architecture, then subpackages (or vice-versa). Eg
#
#    x86_64/qpid-cpp-server/RPM.scripts
#    ->{by_arch}->{x86_64}->{qpid-cpp-server}->{RPMinfo}->{scripts}
#
# What methods do we provide?
#
#    ->rpminfo('scripts'), returning a list?  List must be xrefed to
#      include backlinks to arch and package?
#
sub new {
    my $proto = shift;                   # in: probably "RPM::Grill"
    my $class = ref($proto) || $proto;
    my $dir   = shift;                   # in: base directory to check

    my $self = bless { _dir => $dir }, $class;

    # FIXME: should our unpacker write a file with n-v-r ?

    # At top level we have one directory for each architecture:
    #
    #     i386/  src/  x86_64/
    #
    my @arches = sort _by_arch grep { -d "$dir/$_" } read_dir($dir);
    $self->{arches} = \@arches;

    # Under each architecture we have one or more subpackages:
    #
    #    i386/
    #      build.log  rpmdiff/  rpmdiff-adhoc-webui/  rpmdiff-cli/  ...
    #
    my %all_subpackages;
    for my $arch (@arches) {
        my @subp = grep { -d "$dir/$arch/$_" } read_dir("$dir/$arch")
            or die "FIXME: $dir/$arch has no subdirs";

        # Key = arch, value = list of subpackages, just like dir structure
        #
        #   {i386} => [ rpmdiff, rpmdiff-adhoc-webui, rpmdiff-cli, ... ]
        $self->{_subpackages_by_arch}->{$arch} = \@subp;

        # Key = subpackage, value = list of architectures:
        #
        #   {rpmdiff}             => [ i386, src, x86_64 ],
        #   {rpmdiff-adhoc-webui} => [ i386,      x86_64 ],
        #
        for my $subp (@subp) {
            push @{ $self->{_arches_by_subpackage}->{$subp} }, $arch;
        }

        # Track all the subpackages we encounter, for later
        $all_subpackages{$_}++ for @subp;

        # Initialize RPMs
        for my $subp (@subp) {
            my $rpm = RPM::Grill::RPM->new( "$dir/$arch/$subp/rpm.rpm" );

            $rpm->grill( $self );

            push @{ $self->{_rpms} }, $rpm;

            # Preserve the srpm
            my $arch = $rpm->arch;
            if ($arch eq 'src') {
                if (exists $self->{_srpm}) {
                    warn "$ME: WARNING! Multiple srpms! $self->{_srpm}{path} / $rpm->{path}";
                }
                $self->{_srpm} = $rpm;
            }
            elsif ($arch ne 'noarch') {
                exists $Is_64bit{$arch}
                    or warn "$ME: WARNING: Arch '$arch' not in my Is_64 table";
                $rpm->is_64bit( $Is_64bit{$arch} );
            }
        }
    }

    # FIXME: cross-reference 32- and 64-bit peers
    for my $rpm (@{ $self->{_rpms} }) {
        my $arch = $rpm->arch;
        if (my $peer_arches = $Multilib_Peers{$arch}) {
            my @peers;
          PEER:
            for my $peer (@{ $self->{_rpms} }) {
                next PEER unless $peer->subpackage eq $rpm->subpackage;
                next PEER unless grep { $peer->arch eq $_ } @$peer_arches;

                push @peers, $peer;
            }

            $rpm->multilib_peers( \@peers );
        }
    }

    $self->{subpackages} = [ sort keys %all_subpackages ];

    # FIXME: run sanity checks?  eg src has only one subpackage

    return $self;
}

sub DESTROY {}

##############
#  specfile  #  Finds the specfile, invokes subclass on it
##############
sub specfile {
    my $self = shift;

    # Read it in the first time; keep it cached for subsequent calls.
    $self->{specfile} ||= do {
        my $srpm = $self->srpm;         # Specfile is always in the srpm

        # If I understand rpm/lib/psm.c correctly, the specfile name
        # can be <anything>.spec
        my $specfile_dir = $srpm->dir . '/payload';
        -d $specfile_dir
            or die "$ME: Internal error: missing specfile dir: $specfile_dir";

        # Look for *.spec
        my @specfile = grep {/\.spec$/} read_dir($specfile_dir)
            or die "$ME: Internal error: no specfile found in $specfile_dir";
        @specfile == 1
            or die
            "$ME: Internal error: multiple specfiles in $specfile_dir: @specfile\n";

        require RPM::Grill::RPM::SpecFile;
        my $spec = RPM::Grill::RPM::SpecFile->new("$specfile_dir/$specfile[0]");
        $spec->{grill} = $self;

        $spec;
    };

    return $self->{specfile};
}

##########
#  srpm  #  The source rpm
##########
sub srpm {
    my $self = shift;

    defined $self->{_srpm}
        or croak "$ME: Internal error: no srpm found";
    return $self->{_srpm};
}

#########
#  nvr  #  Although this is a property of RPMs, all our RPMs must share it.
#########
sub nvr {
    my $self = shift;

    # Get it from the srpm, because other rpms might have a diff subpkg name
    return $self->srpm->nvr;
}

###################
#  major_release  #  Returns RHEL5, F14, etc
###################
sub major_release {
    my $self = shift;

    # Sigh. RHEL6 perl (5.10?) doesn't seem to have given/when
    my $release = $self->nvr( 'release' );
    return "RHEL$1"     if $release =~ /\.el(\d+)/;
    return "F$1"        if $release =~ /\.fc?(\d+)/;

    die "$ME: Cannot determine RHEL/Fedora release from '$release'";
}

###################
#  invoke_plugin  #  invokes a plugin
###################
sub invoke_plugin {
    my $self   = shift;
    my $plugin = shift;

    $plugin =~ m{^.*::Plugin::(.*)$}
        or croak "$ME: Internal error: unexpected plugin '$plugin'";
    my $module = $1;

    # 2013-01-18 "maven" and "win" don't have RPMs or build logs,
    # but we still need to run AV scans on them.
    if ((my @arches = $self->non_src_arches) == 1) {
        if ($Is_Non_RPM_Arch{$arches[0]}) {
            if ($plugin !~ /virus/i) {
                dprintf "xxxxx: $plugin (skipped)\n";
                return;
            }
        }
    }

    dprintf "vvvvv: $plugin\n";

    $self->{results}->{$module} = { status => 'running' };

    $self->{_gripe_state} = {};

    # FIXME: add some sort of extra info, eg for setxid checks,
    #   the path and version of the setxid file.  To preserve
    #   out-of-band info, versions, timestamps.

    # FIXME change $self
    bless $self, $plugin;

    # FIXME invoke under eval
    my $t0 = time;
    eval { $self->analyze() };
    my $t1 = time;
    $self->{results}->{$module}->{run_time} = $t1 - $t0;

    # FIXME if $@, set status to fail
    if ($@) {
        warn "$ME: $@\n";
        $self->{results}->{$module}->{status} = 'failed';

        # Log the error; this gets written to our XML results
        # FIXME: better name than 'fail', eg 'exception_message'?
        $self->{results}->{$module}->{fail}   = $@;
    }
    else {

        # No error
        $self->{results}->{$module}->{status} = 'completed';
    }

    # Done with this module; we can clean up our signature cache
    # FIXME: refactor this
    delete $self->{gripes_by_signature}{$module};

    dprintf "^^^^^: $plugin\n";

    # FIXME change gripe() so it goes into results->plugin->gripes

    return;
}

############
#  as_xml  #  returns results, formatted as an xml string
############
sub as_xml {
    my $self = shift;
    my $s    = '';      # out: xml string

    $s .= "<?xml version=\"1.0\"?>\n";

    # FIXME: version should match the rpm
    # FIXME! include the name of the package we're testing!
    # FIXME! include arches
    $s .= sprintf( "<results timestamp=\"%d\" tool=\"%s\" version=\"%s\">\n",
        $^T, $ME, _version() );

    # Package N-V-R
    my @nvr = $self->nvr;
    $s .= "  <package";
    for my $field (@NVR_Fields) {
        $s .= sprintf( ' %s="%s"', $field, shift(@nvr) );
    }
    $s .= "/>\n";

    # Pass 1: determine the string length of the longest module
    my $maxlen = max map { /.*::(.*)$/; length($1) } $self->plugins;

    # Pass 2: write the results of each plugin.  Write a <test> line for
    # each test, even if it has no gripes: that tells our reader that
    # the test existed at the time the XML file was written.
    #
    #   <test name="BuildLog" order="92" status="completed">
    #    <gripe ...>
    #
    for my $plugin ( $self->plugins ) {
        $plugin =~ m{^.*::Plugin::(.*)$}
            or croak "$ME: Internal error: unexpected plugin '$plugin'";
        my $module = $1;
        my $results = $self->{results}->{$module};

        # plugin name, execution order, test status
        $s .= sprintf("  <test name=\"%-*s order=\"%02d\" status=\"%s\"",
                      $maxlen+1, $module . '"', $plugin->order(),
                      $results->{status} || 'NOTRUN');

        # test time, in seconds
        $s .= sprintf(" run_time=\"%d\"", $results->{run_time})
            if defined $results->{run_time};

        # Failure in the test itself (e.g. a croak trapped by eval)
        if (my $fail = $results->{fail}) {
            $s .= sprintf(" fail=\"%s\"", encode_entities($fail));
        }

        if (my $gripes = $self->{gripes}->{$module}) {
            $s .= ">\n";

            # We have gripes.  Write them all, indented.
            for my $g (@$gripes) {

            # Indent 4 spaces for readability. But only XML! E.g.:
            #
            # |    <gripe code="RpmParseErrors" diag="Errors in rpmdiff.spec">
            # |      <excerpt>error: types must match
            # |error: rpmdiff.spec:89: parseExpressionBoolean returns -1
            # |error: query of specfile rpmdiff.spec failed, can't parse
            # |</excerpt>
            # |    </gripe>
            #
            # ...note that we don't want to indent the </excerpt>
                my $xml = '    ' . XMLout( $g, RootName => 'gripe' );
                $xml =~ s{(>\n)(\s*)(<)}{$1$2    $3}gm;

                $s .= $xml;
            }
            $s .= "  </test>\n";
        }
        else {

            # No gripes.  End the <test .... />
            $s .= "/>\n";
        }
    }
    $s .= "</results>\n";

    return $s;
}

##############
#  _version  #  Friendly version string
##############
sub _version {
    # use main version string as our baseline
    my $version = $VERSION;

    # If we're in a git dir, include a git version
    my $git_desc = qx{git describe --tags 2>&1};
    if ($? == 0) {
        if ($git_desc =~ /^(\S+)$/) {
            $version .= "-$1";
        }
    }

    return $version;
}


##############
#  from_xml  #  Parses xml string into a report struct
##############
sub from_xml {
    my $proto = shift;                   # in: probably "RPM::Grill"
    my $class = ref($proto) || $proto;
    my $xml   = shift;                   # in: xml filename or string

    my $ref = XMLin($xml);
    my $self = bless {}, $class;

    # N-V-R
    exists $ref->{package}
        or die "$ME: Internal error: no <package> found in $xml";
    for my $field (@NVR_Fields) {
        $self->{nvr}->{$field} = delete $ref->{package}->{$field}
            or die "$ME: Internal error: <package> has no $field, in $xml";
    }
    if ( my @unknown = keys( %{ $ref->{package} } ) ) {
        die
            "$ME: Internal error: unknown fields '@unknown' in <package> in $xml";
    }
    delete $ref->{package};

    # Timestamp, version, and tool name
    for my $field (qw(tool version timestamp)) {
        $self->{results}->{"_$field"} = delete $ref->{$field}
            or die "$ME: Internal error: no $field in $xml";
    }

    # Plugin results
    for my $plugin ( $self->plugins ) {
        $plugin =~ m{^.*::Plugin::(.*)$}
            or croak "$ME: Internal error: unexpected plugin '$plugin'";
        my $module = $1;

        if ( my $m = $ref->{test}->{$module} ) {
            $self->{results}->{$module}->{order} = delete( $m->{order} ) || 0;
            $self->{results}->{$module}->{status} = delete( $m->{status} )
                || 'UNKNOWN';
            if ( my $g = $m->{gripe} ) {
                if ( ref($g) eq 'ARRAY' ) {
                    $self->{gripes}->{$module} = $g;
                }
                else {
                    $self->{gripes}->{$module} = [$g];
                }
                delete $m->{gripe};
            }

            # Cleanup
            delete $ref->{test}->{$module} if !keys %$m;
        }
        else {

            # FIXME
        }
    }

    #    use Data::Dumper; print Dumper($ref);
    return $self;
}

#############
#  as_yaml  #  returns results, formatted as YAML
#############
sub as_yaml {
    my $self = shift;

    my @nvr = $self->nvr;

    my $y = {
        results => {
            timestamp => $^T,
            tool      => $ME,
            version   => _version(),
        },
        package => { },
    };
    YAML::Bless($y->{results})->keys( [ qw(timestamp tool version) ] );

    #
    $y->{package}{$_} = shift(@nvr)             for @NVR_Fields;
    YAML::Bless($y->{package})->keys( \@NVR_Fields );

    # Pass 1: determine the string length of the longest module
    my $maxlen = max map { /.*::(.*)$/; length($1) } $self->plugins;

    # Each plugin, in order
    for my $plugin ( $self->plugins ) {
        $plugin =~ m{^.*::Plugin::(.*)$}
            or croak "$ME: Internal error: unexpected plugin '$plugin'";
        my $module = $1;

        # Will show up in YAML as '010 SpecFileEncoding : completed (10s)'
        # (including the single quotes).
        my $key = sprintf("%03d %-*s : %s", $plugin->order, $maxlen, $module,
                          $self->{results}->{$module}->{status} || 'NOTRUN');

        # the " (10s)" part (10-second run time)
        if (defined (my $run_time = $self->{results}->{$module}->{run_time})) {
            $key .= sprintf(" (%ds)", $run_time);
        }

        # If the test code failed (eval itself, not a gripe), show the reason.
        if (my $fail = $self->{results}->{$module}->{fail}) {
            $key .= sprintf(" : \"%s\"", encode_entities($fail));
        }

        # Gripes (messages from the test itself)
        if (my $gripes = $self->{gripes}->{$module}) {
            # We have gripes.  Write them all, indented.
            push @{ $y->{tests} }, { $key => $gripes };
        }
        else {
            # No gripes. Just write a named array element, no subhash
            push @{ $y->{tests} }, $key;
        }
    }

    YAML::Bless($y)->keys( [ qw( results package tests ) ] );

    return Dump($y);
}

# END   data-gathering code
###############################################################################
# BEGIN reporting

sub gripe_report {
    my $self   = shift;
    my $format = shift;    # in: text, html

    my $want_html;
    if ( $format =~ /^te?xt$/i ) {
        $want_html = 0;
    }
    elsif ( $format =~ /^html$/i ) {
        $want_html = 1;
    }
    else {
        croak "$ME: ->gripe_report(): FORMAT must be 'text' or 'html'";
    }

    my $retval = '';

    # FIXME: summary of the fields that returned error
    # FIXME: return sorted in alpha order?
    my @run;
    my @failed;

PLUGIN:
    for my $plugin ( $self->plugins ) {
        $plugin =~ m{^.*::Plugin::(.*)$}
            or croak "$ME: Internal error: unexpected plugin '$plugin'";
        my $module = $1;

        my $results = $self->{results}->{$module}
            or next PLUGIN;
        push @run, $module;
        push @failed, $module if $results->{status} ne 'completed';
        if ( my $gripes = $self->{gripes}->{$module} ) {
            $retval .= "\n$module:\n";
            for my $g (@$gripes) {
                $retval .= "  " . $g->{diag} . "\n";

                # Excerpt: include, indented for readability
                if ( my $e = $g->{excerpt} ) {
                    $e =~ s/^/    /gm;
                    $retval .= $e;
                }
            }
        }
    }
    return $retval;
}

# END   reporting
###############################################################################
# BEGIN accessors

sub AUTOLOAD {
    my $self = shift;

    our $AUTOLOAD;
    ( my $field = lc($AUTOLOAD) ) =~ s/^.*:://;

    ref($self)
        or confess "$ME: Internal error: AUTOLOAD invoked on '$AUTOLOAD'";

    if ( $self->{$field} ) {
        my $val = $self->{$field};
        if ( ref($val) ) {
            if ( ref($val) eq 'ARRAY' ) {
                return @$val;
            }
        }

        return $val;
    }

    croak "$ME: Unknown field " . __PACKAGE__ . "->$field()";
}

##########
#  rpms  #  Returns list of RPM::Grill::RPM objects
##########
sub rpms {
    my $self = shift;

    my @rpms = @{ $self->{_rpms} };

    # Called with args?
    if (@_) {
        croak "$ME: ".__PACKAGE__."->rpms(): Bad invocation" if @_ % 2;

        my %keys = @_;
        my @filter;
        for my $field (qw(arch subpackage)) {
            if (my $want = delete $keys{$field}) {
                push @filter, "$field == '$want'";
                @rpms = grep { $_->{$field} eq $want } @rpms;
                if (! @rpms) {
                    my $filter = join(' && ', @filter);
                    carp "$ME: WARNING: No RPMs match $filter";
                    return;
                }
            }
        }
        if (my @unknown = sort keys %keys) {
            carp "$ME: WARNING: unknown rpm field(s) '@unknown'";
        }
    }

    return @rpms;
}

####################
#  non_src_arches  #  Return all arches except src/srpm
####################
sub non_src_arches {
    my $self = shift;

    return grep { $_ ne 'src' } @{ $self->{arches} };
}

###############
#  have_arch  #  Does our brew build include arch X? (eg noarch)
###############
sub have_arch {
    my $self = shift;
    my $arch = shift;    # in: desired arch

    return grep { $_ eq $arch } @{ $self->{arches} };
}

#################
#  subpackages  #  Subpackages for an arch, or all subpackages
#################
sub subpackages {
    my $self = shift;

    # Called with arguments?  It's an architecture.
    if (@_) {
        my $arch = shift;

        # No more args allowed.
        croak "$ME: Usage: " . __PACKAGE__ . "->subpackages( [arch?] )"
            if @_;

        if ( my $aref = $self->{_subpackages_by_arch}->{$arch} ) {
            return @$aref;
        }

        carp "$ME: WARNING: No subpackages for arch '$arch'";
        return;
    }

    my @subpackages = sort keys %{ $self->{subpackages} };
    return @subpackages;
}

##########
#  path  #  assemble a path
##########
sub path {
    my $self = shift;

    # FIXME: should we check for { arch, subpackage, etc } ?
    return join '/', $self->{_dir}, @_;
}

#############
#  plugins  #  Wrapper for Module::Pluggable; returns plugins, in order
#############
sub plugins {

    # Module::Pluggable does all the work, but we return the list
    # in execution order.
    my @plugins = sort { $a->order() <=> $b->order() } _plugins(@_);

    return @plugins;
}

######################
#  matching_plugins  #  Subset of plugins.  Accepts a list as input
######################
sub matching_plugins {
    my $self = shift;

    my @retval;    # Output list

    my @all_plugins = map { my $p = $_; $p =~ s/^.*:://; $p; } plugins();

    for my $p (@_) {

        # For a given arg Foo, look (in order, case-insensitive) for:
        #      exact match:     Foo
        #      match at start:  FooBar
        #      match anywhere:  SomeFoo
        my @match;
        @match = grep { lc($_) eq lc($p) } @all_plugins;
        @match = grep {/^$p/i} @all_plugins if !@match;
        @match = grep {/$p/i} @all_plugins  if !@match;

        # By this point, require exactly one match.
        croak "$ME: No plugin matches '$p'; aborting" if !@match;
        if ( @match > 1 ) {
            local $" = "', '";
            croak
                "$ME: plugin '$p' is ambiguous; matches '@match'.  Aborting";
        }

        # Exactly one match.  Get its exact name.
        push @retval, @match;
    }

    return @retval;
}

# END   accessors
###############################################################################

###########
#  gripe  #  Callback from a plugin; records a specific complaint
###########
sub gripe {
    my $self  = shift;    # in: ourself
    my $gripe = shift;    # in: what to gripe about

    # Validate input args
    _gripe_validate( $gripe, 'gripe' );

    # Get caller's package name; this must be one of our plugins, but
    # we might have a level or two of indirection.
    my $module;
    {
        my $level = 0;
        while (! defined $module) {
            my ( $package, undef ) = caller($level++);
            if (! defined $package) {
                croak "$ME: FATAL: did not find RPM::Grill::Plugin::<name> anywhere in call stack";
            }

            if ($package =~ m{^RPM::Grill::Plugin::(.*)$}) {
                $module = $1;
            }
        }
    }

    # FIXME: get the RPM package or subpackage name?

    # Any default state defined?  Use that, but override with current data
    my %actual_gripe;
    if ( exists $self->{_gripe_state} ) {
        %actual_gripe = ( %{ $self->{_gripe_state} }, %$gripe );
    }
    else {
        %actual_gripe = (%$gripe);
    }

    # Normalize excerpt string into an array.  This is partly for consistency,
    # but mostly so our output XML will be <excerpt>...</excerpt> instead of
    # <gripe excerpt="...">.  The latter does not preserve whitespace.
    if ( exists $actual_gripe{context} ) {
        if ( defined( my $e = $actual_gripe{context}{excerpt} ) ) {
            if ( !ref($e) ) {
                $actual_gripe{context}{excerpt} = [$e];
            }
        }
    }

    # Usability: aggregate similar gripes. For instance, if we get two or
    # more gripes that are identical except for the arch (i686,x86_64,...)
    # we combine them into one.
    my $sig = gripe_signature(\%actual_gripe);
    if (my $g = $self->{gripes_by_signature}{$module}{$sig}) {
        my $found = 0;

        # If this is a new arch or subpackage, append to that field in
        # the existing gripe. E.g. 'i686' becomes 'i686,x86_64'
        for my $k (qw(arch subpackage)) {
            if (my $new = $actual_gripe{$k}) {
                if (defined $g->{$k}) {
                    unless ($g->{$k} =~ /(^|,)$new(,|$)/) {
                        $g->{$k} .= ',' . $new;
                        $found++;
                        # FIXME: signal, somehow?
                    }
                }
            }
        }

        # Same gripe about a different file path? Append to existing one.
        #
        # FIXME FIXME FIXME! 2012-08-28 This is currently disabled because
        # I'm not entirely happy with the newline-separated results. To
        # reenable, remove 'path' from the qw() in gripe_signature() and
        # remove this comment. You will also need to fix the selftests,
        # and possibly change the database schema.
        if ($actual_gripe{context} && $g->{context}) {
            if (my $new_path = $actual_gripe{context}{path}) {
                $g->{context}{path} .= "\n" . $new_path;
                $found++;
            }
        }

        $found
            or warn "$ME: WARNING: Could not aggregate '$sig'";
    }
    else {
        # We haven't seen this gripe (or a similar one) before.
        # Push it onto an ordered list, keyed on the caller module.
        push @{ $self->{gripes}->{$module} }, \%actual_gripe;

        # Preserve signature in case we get a similar gripe later.
        $self->{gripes_by_signature}{$module}{$sig} = \%actual_gripe;
    }

    return;
}

#####################
#  gripe_signature  #  Returns a lookup key for detecting semi-identical gripes
#####################
sub gripe_signature {
    my $gripe = shift;
    my $sig   = '';

    # If two gripes have different codes or diags, they cannot be identical
    for my $k (qw(code diag)) {
        $sig .= "[$k:$gripe->{$k}]"             if $gripe->{$k};
    }

    # Same for context excerpts / line numbers
    if (exists $gripe->{context}) {
#        for my $k (qw(lineno sub excerpt)) {
        for my $k (qw(lineno sub excerpt path)) {
            if (my $v = $gripe->{context}{$k}) {
                $sig .= "[context:$k:$v]";
            }
        }
    }

    return $sig;
}

#################
#  gripe_state  #  Used by plugins to avoid clutter in gripe() calls
#################
#
# eg $self->gripe_state({ arch => $arch, subpackage => $subpackage });
sub gripe_state {
    my $self  = shift;
    my $state = shift;    # in: defaults for next gripe

    # Validate input args
    _gripe_validate( $state, 'gripe_state' );

    # Set new defaults.  Delete any that are undef.
    for my $k ( sort keys %$state ) {
        if ( defined( my $v = $state->{$k} ) ) {
            $self->{_gripe_state}{$k} = $v;
        }
        else {
            delete $self->{_gripe_state}{$k};
        }
    }

    return;
}

#####################
#  _gripe_validate  #  Basic sanity check on gripe args
#####################
sub _gripe_validate {
    my $gripe  = shift;
    my $whence = shift;

    # Validate input args
    defined $gripe
        or croak "$ME: ->$whence() invoked with no arguments";
    @_ == 0
        or croak "$ME: ->$whence() invoked with too many arguments";
    ref($gripe)
        or croak "$ME: argument to ->$whence() is not a hashref";
    ref($gripe) eq 'HASH'
        or croak "$ME: argument to ->$whence() is a ref, but not a hashref";

    # Validate the keys in the gripe arg
    for my $k ( sort keys %$gripe ) {
        $Is_Gripe_Field{$k}
            or carp "$ME: '$k' is not a valid gripe field";
    }

    # If there's a context, validate it too
    if ( my $ctx = $gripe->{context} ) {
        for my $k ( sort keys %$ctx ) {
            $Is_Gripe_Context_Field{$k}
                or carp "$ME: '$k' is not a valid gripe context field";
        }
    }

    # FIXME: the following gripe fields are required
    for my $required (@Required_Gripe_Fields) {
        exists $gripe->{$required}
            or croak "$ME: gripe missing required '$required' field";
    }

    return;
}

###############################################################################
# BEGIN reimplementing parts of File::Slurp because RHEL5 doesn't have it

##############
#  read_dir  #  returns sorted list of entries in a directory
##############
sub read_dir {
    my $dir = shift;

    opendir my $dir_fh, $dir
        or die "$ME: FATAL: could not opendir $dir: $!";
    my @ents;
    while ( my $ent = readdir $dir_fh ) {

        # Everything except '.' and '..'
        push @ents, $ent unless $ent =~ /^\.{1,2}$/;
    }
    closedir $dir_fh;

    @ents = sort @ents;

    return @ents;
}

# END   reimplementing parts of File::Slurp because RHEL5 doesn't have it
###############################################################################
# BEGIN sort helpers

# Define a custom sort order for arches.  Used by _by_arch() sort helper.
#
# src is first because some plugins (eg RpmMetadata) may report a problem
# only the first time.  For those, it seems sensible to make 'src' be
# the reporting architecture.
my %_arch_map = (
    x86_64 => 'i687',     # Put x86_64 immediately after i386/i686
    src    => 'aaaaa',    # Always put src first, before anything else
);

##############
#  _by_arch  #  Custom sort order for arches
##############
sub _by_arch {
    my $a1 = $_arch_map{$a} || $a;
    my $b1 = $_arch_map{$b} || $b;

    return $a1 cmp $b1;
}

# END   sort helpers
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
