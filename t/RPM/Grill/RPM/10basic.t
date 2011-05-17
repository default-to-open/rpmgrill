# -*- perl -*-

use strict;
use warnings;

use Test::More;

use_ok 'RPM::Grill::RPM';

# 32-bit arches
for my $arch qw(i386 i686 athlon ppc s390) {
    my $rpm = bless { arch => $arch }, 'RPM::Grill::RPM';
    is $rpm->is_64bit, undef, "is_64bit( $arch )";
}

# 64-bit arches
for my $arch qw(x86_64 ia64 ppc64 s390x) {
    my $rpm = bless { arch => $arch }, 'RPM::Grill::RPM';
    is $rpm->is_64bit, 1, "is_64bit( $arch )";
}

my $rpm = bless {
    nvr => {
        name => 'mypkg',
        version => '1.0',
        release => '3.el5',
    },
    arch => 'i686',
}, 'RPM::Grill::RPM';

is scalar($rpm->nvr), 'mypkg-1.0-3.el5', 'nvr';
is $rpm->nvr('name'),    'mypkg',        'nvr(name)';
is $rpm->nvr('version'), '1.0',          'nvr(name)';
is $rpm->nvr('release'), '3.el5',        'nvr(name)';

is "$rpm", 'mypkg-1.0-3.el5.i686.rpm',   'string overload';

done_testing();
