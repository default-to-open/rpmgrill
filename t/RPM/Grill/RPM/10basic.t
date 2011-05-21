# -*- perl -*-

use strict;
use warnings;

use Test::More;

use_ok 'RPM::Grill::RPM';

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
