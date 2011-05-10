# -*- perl -*-

use strict;
use warnings;

use Test::More                  (tests => 9);
use Test::Differences;

use Encode      qw(from_to);
use FindBin     qw( $Bin );
use lib "$Bin/../../../../lib";


# Tests 1-4 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                           or exit;
use_ok 'RPM::Grill::RPM::SpecFile'            or exit;
use_ok 'RPM::Grill::Plugin::SpecFileEncoding' or exit;
use_ok 'HTML::Entities'                       or exit;

#
# Simpleminded string which will be parsed as a specfile.  We use
# an HTML entity (&ntilde) to avoid any possible encoding problem.
#
my $spec_string = <<'END_SPEC_STRING';
Summary: spec file containing n-tilde
blah blah this is not a real spec

%changelog
* Thu Jul  1 2010 This is a test: Mu&ntilde;&oacute;z <santiago@redhat.com> 1.0-1
- blah blah
END_SPEC_STRING

# Convert the above to two strings in two different encodings.
#
# HTML::Entities::decode_entities() will convert to ISO-8859-1 ...
my $spec_string_iso88591 = decode_entities($spec_string);

# ...and Encode::from_to() converts a string in-place to UTF-8
my $spec_string_utf8     = $spec_string_iso88591;
from_to($spec_string_utf8, 'iso-8859-1', 'utf-8');

#
# (Sanity check: make sure the expected binary chars appear in each string)
#
ok( $spec_string_iso88591 =~ /\x{F1}/,
    "spec string(ISO-8859-1) contains chr(0xF1) [ntilde]");
ok( $spec_string_utf8 =~ /\x{C3}\x{B1}/,
    "spec string(UTF-8) contains chr(0xC3)chr(0xB1) [ntilde]");

# Build dummy BrewLint objects out of those dummy specs
my $spec_good = RPM::Grill::RPM::SpecFile->new( $spec_string_utf8 );
my $spec_bad  = RPM::Grill::RPM::SpecFile->new( $spec_string_iso88591 );

my $obj_good = bless { specfile => $spec_good }, 'RPM::Grill';
my $obj_bad  = bless { specfile => $spec_bad  }, 'RPM::Grill';

# Run our checker.  Nothing to look for in return status...
RPM::Grill::Plugin::SpecFileEncoding::analyze( $obj_good );
RPM::Grill::Plugin::SpecFileEncoding::analyze( $obj_bad );

# ...but make sure we get the expected gripes or lack thereof
ok !exists($obj_good->{gripes}), "No gripes for the UTF-8 string";
ok  exists($obj_bad->{gripes}),  "Error detected in the ISO-8859-1 string";

eq_or_diff $obj_bad->{gripes}, +{ SpecFileEncoding => [ {
    arch    => 'src',
    code    => 'NonUtf8',
    context => { path    => '<string>', lineno  => '5' },
    diag    => 'non-UTF8 content',
    excerpt => ["* Thu Jul  1 2010 This is a test: Mu<u>&ntilde;</u><u>&oacute;</u>z &lt;santiago\@redhat.com&gt; 1.0-1"],
} ] }, "Gripe message";
