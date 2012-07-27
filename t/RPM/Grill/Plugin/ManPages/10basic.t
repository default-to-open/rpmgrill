# -*- perl -*-
#
# Tests for the ManPages plugin
#
use strict;
use warnings;

use Test::More;
use Test::Differences;
use File::Temp                  qw(tempdir);

# Slurp in the DATA section, which defines the tests we'll run
my @tests;
while (my $line = <DATA>) {
    if ($line =~ /^-{10,}([^-].*[^-])-+$/) {
        push @tests, { name => $1 };
    }
    elsif (@tests) {
        if (exists $tests[-1]->{expect}) {
            $tests[-1]->{expect} .= $line;
        }
        elsif ($line =~ /^\.\.+expect:$/) {
            $tests[-1]->{expect} = '';
        }
        else {
            $tests[-1]->{setup} .= $line;
        }
    }
}

plan tests => 3 + @tests;

# Load required libraries
use_ok 'RPM::Grill'                     or exit;
use_ok 'RPM::Grill::Plugin::ManPages'   or exit;

ok(require("t/lib/FakeTree.pm"), "loaded FakeTree.pm") or exit;

# Make a temp dir
my $tempdir = tempdir("t-ManPages.XXXXXX", CLEANUP => !$ENV{DEBUG});

my $i = 0;
for my $t (@tests) {
    my $temp_subdir = sprintf("%s/%02d", $tempdir, ++$i);

    my $g = FakeTree::make_fake_tree( $temp_subdir, $t->{setup} );

#    use Data::Dumper; print STDERR Dumper($g);

    # FIXME
    bless $g, 'RPM::Grill::Plugin::ManPages';
    eval { $g->analyze() };
    if ($@) {
        fail "$t->{name} : ERROR: $@";
    }
    else {
        my $expected_gripes = eval $t->{expect};
        die "eval failed:\n\n $t->{expect} \n\n $@" if $@;

        if ($expected_gripes) {
            # FIXME
        }

        eq_or_diff $g->{gripes}, $expected_gripes, $t->{name};
    }
}

__DATA__

------------binary-needs-manpage------------

>> -rwxr-xr-x  root root 0 /i386/mypkg/usr/sbin/foo

...expect:

{
  ManPages => [
    {
      arch => 'i386',
      code => 'ManPageMissing',
      diag => 'No man page for /usr/sbin/foo',
      subpackage => 'mypkg'
    }
  ]
}


-------------no-manpage-needed---------------------

>> -rwxr-xr-x  root root 0 /i386/mypkg/usr/bin/foo

...expect:

------------manpage-in-same-package----------------

>> -rwxr-xr-x  root root 0 /i386/mypkg/usr/sbin/foo
>> -rw-r--r--  root root 0 /i386/mypkg/usr/share/man/man1/foo.1
.SH to make it look like a valid man page

...expect:


------------manpage-in-another-subpackage----------------

>> -rwxr-xr-x  root root 0 /i386/mypkg/usr/sbin/foo
>> -rw-r--r--  root root 0 /i386/mypkg-docs/usr/share/man/man1/foo.1
.Dd to make it look like a valid man page

...expect:

------------manpage-in-another-arch----------------

>> -rwxr-xr-x  root root 0 /i386/mypkg/usr/sbin/foo
>> -rw-r--r--  root root 0 /x86_64/mypkg-docs/usr/share/man/man1/foo.1
.\" blah blah
.so to make it look like a valid man page

...expect:

{
  ManPages => [
    {
      arch => 'i386',
      code => 'ManPageMissing',
      diag => 'No man page for /usr/sbin/foo',
      subpackage => 'mypkg'
    }
  ]
}

------------manpage-in-noarch----------------

>> -rwxr-xr-x  root root 0 /i386/mypkg/usr/sbin/foo
>> -rw-r--r--  root root 0 /noarch/mypkg-docs/usr/share/man/man1/foo.1
.\" blah blah
.so to make it look like a valid man page

...expect:

------------bad-gzip-manpage-------------------

>> -rw-r--r--  root root 0 /i386/mypkg-docs/usr/share/man/man1/foo.1.gz
sdfsdfsdf

...expect:

{
    ManPages => [
        {
            arch => 'i386',
            subpackage => 'mypkg-docs',
            code => 'ManPageBadGzip',
            context => { path => '/usr/share/man/man1/foo.1.gz' },
            diag => "gunzip failed: \ngzip: /usr/share/man/man1/foo.1.gz: not in gzip format\n (&#39;file&#39; classifies this file as: ASCII text)",
        }
    ]
}

------------bad-manpage-content-------------------

>> -rwxr-xr-x  root root 0 /i386/mypkg-docs/usr/share/man/man1/foo.1
#!/bin/nosh

...expect:

{
    ManPages => [
        {
            arch => 'i386',
            subpackage => 'mypkg-docs',
            code => 'ManPageNoContent',
            context => { path => '/usr/share/man/man1/foo.1' },
            diag => "No .SH, .Dd, or .so macros found; is this really a man page? (\'file\' classifies this file as: a /bin/nosh script, ASCII text executable)",
        }
    ]
}

------------bad-file-extension-------------------

>> -rwxr-xr-x  root root 0 /i386/mypkg-docs/usr/share/man/man1/foo.p
.\" blah blah
.so to make it look like a valid man page

...expect:

{
    ManPages => [
        {
            arch => 'i386',
            subpackage => 'mypkg-docs',
            code => 'ManPageUnknownExtension',
            context => { path => '/usr/share/man/man1/foo.p' },
            diag => "Man pages are expected to end in .[0-9n][a-z]*.gz",
        }
    ]
}

--------------config-file-missing-manpage------------------

>> -rw-r--r--   root root 1 /noarch/mypkg/etc/foo.rc

...expect:

{
  ManPages => [
    {
      arch => 'noarch',
      code => 'ManPageMissing',
      diag => 'No man page for /etc/foo.rc',
      subpackage => 'mypkg'
    }
  ]
}
