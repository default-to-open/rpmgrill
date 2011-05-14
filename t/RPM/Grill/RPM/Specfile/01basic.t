# -*- perl -*-

use strict;
use warnings;

use Test::More;
use Test::Differences;

use_ok 'RPM::Grill::RPM::SpecFile';

my $spec_string = do { local $/ = undef; <DATA> };

my $spec = RPM::Grill::RPM::SpecFile->new( $spec_string );

is ref($spec), 'RPM::Grill::RPM::SpecFile', 'ref($spec)';

# List of sections in the spec file
my @sections = $spec->sections;
is scalar(@sections), 5, 'num. of sections in specfile';
eq_or_diff \@sections,
    [ qw(%preamble %description %prep %build %changelog) ],
    'sections in specfile';

# Compare what the module read, to what we read
my $all_lines = join("\n", map { $_->content } $spec->lines) . "\n";
is $all_lines, $spec_string, "spec contents : string comparison";

# Test one of the sections
my $sub_lines = join("\n", map { $_->content } $spec->lines("prep")) . "\n";
is $sub_lines, "%prep\n%setup -q\n\n", "spec contents (%prep)";

done_testing();

__END__

Summary: A summary
Name: mytool
Version: 1.0-1
Release: 1%{?mydist}
Source: mytool-%{version}.tar.bz2
License: Red Hat internal.  Do not redistribute.
Group: Development/Tools
BuildRoot: %{_tmppath}/%{name}-root

%description
This is a description.

%prep
%setup -q

%build
make clean
make

%changelog
* Thu Jul  1 2010 Eduardo Santiago <santiago@redhat.com> 1.0-1
- blah blah
