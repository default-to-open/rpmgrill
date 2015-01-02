# -*- perl -*-

use strict;
use warnings;

use Test::More;
use Test::Differences;

# Tests 1-4 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                     or exit;
use_ok 'RPM::Grill::RPM::SpecFile'      or exit;
use_ok 'RPM::Grill::Plugin::Patches'    or exit;

# FIXME: read DATA
my @tests;
while (my $line = <DATA>) {
    # Line of dashes: new test
    if ($line =~ /^-{10,}$/) {
        push @tests, {
            spec_string => '',
            status      => 0,
            name        => sprintf("[unnamed test %d]", scalar(@tests)),
        };
    }
    # Leading '>>' : metadata indicating test results
    elsif ($line =~ /^>>\s*(\S+)\s*=\s*(.*)/) {
        $tests[-1]->{$1} = $2;
    }

    # Leading '-|' : metadata indicating expected gripe results
    elsif ($line =~ /^-\|(.*)/) {
        $tests[-1]->{gripe_string} .= $1;
    }

    else {
        $tests[-1]->{spec_string} .= $line;
    }
}

# FIXME: run each test
for my $t (@tests) {
    my $spec_parsed = RPM::Grill::RPM::SpecFile->new( $t->{spec_string} );
    my $spec_obj    = bless { specfile => $spec_parsed }, 'RPM::Grill';

    my $expected_gripes;
    if ($t->{gripe_string}) {
        $expected_gripes = eval "{ Patches => [ $t->{gripe_string} ] }";
        die "eval failed:\n\n $t->{gripe_string} \n\n  $@\n"     if $@;
    }

    RPM::Grill::Plugin::Patches::analyze( $spec_obj );

    eq_or_diff $spec_obj->{gripes}, $expected_gripes, "$t->{name}";
##    use Data::Dumper; print Dumper($spec_obj);
}

done_testing();

__DATA__
-------------------------------------------------------------------------------
Summary: spec file containing patch errors
blah blah this is not a real spec
Source0: fixme.tar.gz
Patch0: foo1.patch
Patch1: foo2.patch

%prep
%setup -q
%patch0 -p1 -b .bz581661

%changelog
* Thu Jul 15 2010 Ed Santiago <santiago@redhat.com> 1.0-1
- blah blah

>> name   = unnamed
>> foo    = 1


-------------------------------------------------------------------------------
>> name   = badfuzz-1

%define _default_patch_fuzz 2

Summary: spec file containing patch errors
blah blah this is not a real spec
Source0: fixme.tar.gz
Patch0: foo1.patch
Patch1: foo2.patch

%prep
%setup -q
%patch0 -p1 -b .bz581661

-| { arch => 'src',
-|   code       => 'BadPatchFuzz',
-|   context => {
-|      excerpt => [ '%define _default_patch_fuzz 2' ],
-|      lineno => 2,
-|      path => '<string>',
-|    },
-|    diag => 'Do not override _default_patch_fuzz. Please redo your patches instead.',
-| }

-------------------------------------------------------------------------------
>> name   = badfuzz-2

%define _default_patch_fuzz 9

Summary: spec file containing patch errors
blah blah this is not a real spec
Source0: fixme.tar.gz
Patch0: foo1.patch
Patch1: foo2.patch

%prep
%setup -q
%patch0 -p1 -b .bz581661

-| { arch => 'src',
-|   code       => 'BadPatchFuzz',
-|   context => {
-|      excerpt => [ '%define _default_patch_fuzz 9' ],
-|      lineno => 2,
-|      path => '<string>',
-|    },
-|    diag => 'Do not override _default_patch_fuzz; *ESPECIALLY* not with anything >2. Please redo your patches instead.',
-| }

-------------------------------------------------------------------------------
>> name   = duppatch

Summary: spec file containing patch errors
blah blah this is not a real spec
Source0: fixme.tar.gz
Patch0: foo1.patch
Patch1: foo2.patch
Patch0: this-is-a-dup.patch

%prep
%setup -q
%patch0 -p1 -b .bz581661

-| { arch => 'src',
-|   code       => 'DuplicatePatch',
-|   context => {
-|      excerpt => [ "Patch0: foo1.patch\nPatch0: this-is-a-dup.patch" ],
-|      lineno => 7,
-|      path => '<string>',
-|    },
-|    diag => 'Duplicate definition of Patch0',
-| }
