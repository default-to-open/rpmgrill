# -*- perl -*-

use strict;
use warnings;

use Test::More                  (tests => 8);
use Test::Differences;

# DANGER WILL ROBINSON. This (in particular, "no utf8") is to make
# double-darn-sure that our chr() replacement below will work.
# With "use utf8", chr(0xF1) actually becomes the n-tilde code point.
# Oh how I wish I understood this.
no utf8;
use open qw(:std :utf8);

use Encode      qw(from_to);
use FindBin     qw( $Bin );
use lib "$Bin/../../../../lib";


# Tests 1-4 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                           or exit;
use_ok 'RPM::Grill::RPM::SpecFile'            or exit;
use_ok 'RPM::Grill::Plugin::SpecFileEncoding' or exit;

#
# Simpleminded string which will be parsed as a specfile. Single and
# double quotes below test our HTMLification; strings in [XX,YY] form
# are [iso8859-1,utf8] hex byte sequences.
#
my $spec_string = <<'END_SPEC_STRING';
Summary: spec file containing n-tilde
blah blah this is not a real spec

%changelog
* Thu Jul  1 2010 'test": Mu[F1,C3B1]oz [80,5B38305D]<santiago@redhat.com> 1.0-1
- blah blah
END_SPEC_STRING

# Convert the above to two strings in two different encodings.
sub binarify {
    my $which = shift;                          # in: 0 or 1

    my $s = $spec_string;
    $s =~ s{\[(.*?),(.*?)\]}{
        my @foo = ($1, $2);
        my $hexchars = $foo[$which];

        my $binchars = '';
        for (my $i=0; $i < length($hexchars); $i += 2) {
            $binchars .= chr(hex(substr($hexchars,$i,2)));
        }
        $binchars;
    }ge;

    return $s;
}

# Split the spec string into two
my $spec_string_iso88591 = binarify(0);
my $spec_string_utf8     = binarify(1);

# (Sanity check: make sure the expected binary chars appear in each string)
ok( $spec_string_iso88591 =~ /\x{F1}/,
    "spec string(ISO-8859-1) contains chr(0xF1) [ntilde]");
ok( $spec_string_utf8 =~ /\x{C3}\x{B1}/,
    "spec string(UTF-8) contains chr(0xC3)chr(0xB1) [ntilde]");

# Build dummy Grill objects out of those dummy specs
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

unified_diff;
eq_or_diff $obj_bad->{gripes}, +{ SpecFileEncoding => [ {
    arch    => 'src',
    code    => 'NonUtf8',
    diag    => 'non-UTF8 content',
    context => { path    => '<string>', lineno  => 5,
      excerpt => ["* Thu Jul  1 2010 &#39;test&quot;: Mu<u>&ntilde;</u>oz <u>[80]</u>&lt;santiago\@redhat.com&gt; 1.0-1"], },
} ] }, "Gripe message";
