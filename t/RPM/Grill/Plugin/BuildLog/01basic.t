# -*- perl -*-

use strict;
use warnings;

use Test::More;
use Test::Differences;

use File::Path                  qw(rmtree);
use File::Temp                  qw(tempdir);

# Tests 1-2 : load our modules.  If any of these fail, abort.
use_ok 'RPM::Grill'                     or exit;
use_ok 'RPM::Grill::Plugin::BuildLog'   or exit;

# FIXME: read DATA
my @tests;
while (my $line = <DATA>) {
    # Line of dashes: new test
    if ($line =~ /^-{10,}$/) {
        push @tests, {
            name         => sprintf("[unnamed test %d]", scalar(@tests)),
            arch         => 'noarch',
            build_log    => '',
            gripe_string => '',
        };
    }
    # Leading '>>' : metadata indicating test results
    elsif ($line =~ /^>>\s*(\S+)\s*=\s*(.*)/) {
        $tests[-1]->{$1} = $2;
    }
    elsif ($line =~ /^-\|(.*)/) {
        $tests[-1]->{gripe_string} .= $1;
    }
    else {
        $tests[-1]->{build_log} .= $line;
    }
}

# FIXME: run each test
my $tempdir = tempdir("t-BuildLog.XXXXXX", CLEANUP => 1);

for my $i (0 .. $#tests) {
    my $t = $tests[$i];

    # Create (or clean up) tmpdir
    my $temp_subdir = sprintf("%s/%02d", $tempdir, $i);
    mkdir $temp_subdir, 02755
        or die "mkdir $temp_subdir: $!\n";

    my $arch = $t->{arch};
    mkdir "$temp_subdir/$arch"
        or die "mkdir $temp_subdir/$arch: $!\n";

    # Write to arch/build.log
    open BUILD_LOG, '>', "$temp_subdir/$arch/build.log"
        or die "cannot create $temp_subdir/$arch/build.log : $!\n";
    print BUILD_LOG $t->{build_log};
    close BUILD_LOG
        or die "error writing $temp_subdir/$arch/build.log : $!\n";

    # parse gripe_string
    my $gripes = eval $t->{gripe_string};
    die "eval failed:\n\n $t->{gripe_string} \n\n  $@\n"     if $@;

    # invoke
    my $obj = bless {
        _dir   => $temp_subdir,
        arches => [ $t->{arch} ],
    }, 'RPM::Grill::Plugin::BuildLog';

    RPM::Grill::Plugin::BuildLog::analyze( $obj );

    eq_or_diff $obj->{gripes}, $gripes, "$i : $t->{name}";
##    use Data::Dumper; print Dumper($spec_obj);
}

done_testing();

__DATA__
-------------------------------------------------------------------------------
>> name = nogripes
this is a build log with no errors


-------------------------------------------------------------------------------
>> name = dereferencing type-punned pointer

blah blah
update.c: In function `update':
update.c:154: warning: dereferencing type-punned pointer will break strict-aliasing rules

-|
-| { BuildLog => [
-|  { arch    => 'noarch',
-|    code    => 'TypePun',
-|    diag    => 'gcc warnings',
-|    context => { lineno => 3, path => "noarch/build.log" },
-|    excerpt => [
-|         'update.c: In function `update\':',
-|         'update.c:154: warning: dereferencing type-punned pointer will break strict-aliasing rules',
-|        ],
-|  } ] }


-------------------------------------------------------------------------------
>> name = broken memset

from  packages/krb5/1.8.2/3.el6_0.1/data/logs/i686/build.log

gcc -fPIC -DSHARED -D_GSS_STATIC_LINK=1  -I../../../include -I../../../include -I. -I. -I./.. -I../generic -I./../generic -I../mechglue -I./../mechglue -DKRB5_DEPRECATED=1 -I/usr/include/et -O2 -g -pi
pe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m32 -march=i686 -mtune=atom -fasynchronous-unwind-tables -I/usr/include/et -fPIC -fno-strict-aliasing -fstack
-protector-all -Wall -Wcast-align -Wshadow -Wmissing-prototypes -Wno-format-zero-length -Woverflow -Wstrict-overflow -Wmissing-format-attribute -Wmissing-prototypes -Wreturn-type -Wmissing-braces -Wpa
rentheses -Wswitch -Wunused-function -Wunused-label -Wunused-variable -Wunused-value -Wunknown-pragmas -Wsign-compare -Werror=declaration-after-statement -Werror=variadic-macros -pthread -c k5sealv3io
v.c -o k5sealv3iov.so.o && mv -f k5sealv3iov.so.o k5sealv3iov.so
In file included from /usr/include/string.h:642,
                 from ../../../include/k5-platform.h:46,
                 from k5sealv3.c:32:
In function 'memset',
    inlined from 'gss_krb5int_make_seal_token_v3' at k5sealv3.c:162:
/usr/include/bits/string3.h:83: warning: call to '__warn_memset_zero_len' declared with attribute warning: memset used with constant zero length parameter; this could be due to transposed parameters
gcc -fPIC -DSHARED -D_GSS_STATIC_LINK=1  -I../../../include -I../../../include -I. -I. -I./.. -I../generic -I./../generic -I../mechglue -I./../mechglue -DKRB5_DEPRECATED=1 -I/usr/include/et -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m32 -march=i686 -mtune=atom -fasynchronous-unwind-tables -I/usr/include/et -fPIC -fno-strict-aliasing -fstack-protector-all -Wall -Wcast-align -Wshadow -Wmissing-prototypes -Wno-format-zero-length -Woverflow -Wstrict-overflow -Wmissing-format-attribute -Wmissing-prototypes -Wreturn-type -Wmissing-braces -Wparentheses -Wswitch -Wunused-function -Wunused-label -Wunused-variable -Wunused-value -Wunknown-pragmas -Wsign-compare -Werror=declaration-after-statement -Werror=variadic-macros -pthread -c k5unseal.c -o k5unseal.so.o && mv -f k5unseal.so.o k5unseal.so
gcc -fPIC -DSHARED -D_GSS_STATIC_LINK=1  -I../../../include -I../../../include -I. -I. -I./.. -I../generic -I./../generic -I../mechglue -I./../mechglue -DKRB5_DEPRECATED=1 -I/usr/include/et -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m32 -march=i686 -mtune=atom -fasynchronous-unwind-tables -I/usr/include/et -fPIC -fno-strict-aliasing -fstack-protector-all -Wall -Wcast-align -Wshadow -Wmissing-prototypes -Wno-format-zero-length -Woverflow -Wstrict-overflow -Wmissing-format-attribute -Wmissing-prototypes -Wreturn-type -Wmissing-braces -Wparentheses -Wswitch -Wunused-function -Wunused-label -Wunused-variable -Wunused-value -Wunknown-pragmas -Wsign-compare -Werror=declaration-after-statement -Werror=variadic-macros -pthread -c k5unsealiov.c -o k5unsealiov.so.o && mv -f k5unsealiov.so.o k5unsealiov.so

-| { BuildLog => [
-|  { arch    => 'noarch',
-|    code    => 'BrokenMemset',
-|    diag    => 'Possible build error',
-|    context => { lineno => 13, path => "noarch/build.log" },
-|    excerpt => [
-|         '                 from ../../../include/k5-platform.h:46,',
-|         '                 from k5sealv3.c:32:',
-|         'In function \'memset\',',
-|         '    inlined from \'gss_krb5int_make_seal_token_v3\' at k5sealv3.c:162:',
-|         '/usr/include/bits/string3.h:83: warning: call to \'__warn_memset_zero_len\' declared with attribute warning: memset used with constant zero length parameter; this could be due to transposed parameters',
-|         'gcc -fPIC -DSHARED -D_GSS_STATIC_LINK=1  -I../../../include -I../../../include -I. -I. -I./.. -I../generic -I./../generic -I../mechglue -I./../mechglue -DKRB5_DEPRECATED=1 -I/usr/include/et -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m32 -march=i686 -mtune=atom -fasynchronous-unwind-tables -I/usr/include/et -fPIC -fno-strict-aliasing -fstack-protector-all -Wall -Wcast-align -Wshadow -Wmissing-prototypes -Wno-format-zero-length -Woverflow -Wstrict-overflow -Wmissing-format-attribute -Wmissing-prototypes -Wreturn-type -Wmissing-braces -Wparentheses -Wswitch -Wunused-function -Wunused-label -Wunused-variable -Wunused-value -Wunknown-pragmas -Wsign-compare -Werror=declaration-after-statement -Werror=variadic-macros -pthread -c k5unseal.c -o k5unseal.so.o && mv -f k5unseal.so.o k5unseal.so',
-|         'gcc -fPIC -DSHARED -D_GSS_STATIC_LINK=1  -I../../../include -I../../../include -I. -I. -I./.. -I../generic -I./../generic -I../mechglue -I./../mechglue -DKRB5_DEPRECATED=1 -I/usr/include/et -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m32 -march=i686 -mtune=atom -fasynchronous-unwind-tables -I/usr/include/et -fPIC -fno-strict-aliasing -fstack-protector-all -Wall -Wcast-align -Wshadow -Wmissing-prototypes -Wno-format-zero-length -Woverflow -Wstrict-overflow -Wmissing-format-attribute -Wmissing-prototypes -Wreturn-type -Wmissing-braces -Wparentheses -Wswitch -Wunused-function -Wunused-label -Wunused-variable -Wunused-value -Wunknown-pragmas -Wsign-compare -Werror=declaration-after-statement -Werror=variadic-macros -pthread -c k5unsealiov.c -o k5unsealiov.so.o && mv -f k5unsealiov.so.o k5unsealiov.so',
-|        ],
-|  } ] }


-------------------------------------------------------------------------------
>> name = bz642228 (assuming signed overflow does not occur)

from packages/xulrunner/1.9.2.12/1.el6_0/data/logs/i686/build.log

c++ -o nsJohabToUnicode.o -c -I../../../dist/system_wrappers -include ../../../config/gcc_hidden.h -DMOZILLA_INTERNAL_API -D_IMPL_NS_COM -DEXPORT_XPT_API -DEXPORT_XPTC_API -D_IMPL_NS_COM_OBSOLETE -D_I
MPL_NS_GFX -D_IMPL_NS_WIDGET -DIMPL_XREAPI -DIMPL_NS_NET -DIMPL_THEBES  -DOSTYPE=\"Linux2.6.18-194.17.1\" -DOSARCH=Linux -I./../util -I. -I. -I../../../dist/include -I../../../dist/include/nsprpub  -I
/usr/include/nspr4 -I/usr/include/nss3         -fPIC   -fno-rtti -fno-exceptions -Wall -Wpointer-arith -Woverloaded-virtual -Wsynth -Wno-ctor-dtor-privacy -Wno-non-virtual-dtor -Wcast-align -Wno-inval
id-offsetof -Wno-long-long -pedantic -O2 -g -pipe -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m32 -march=i686 -mtune=atom -fasynchronous-unwind-tables -fno-strict
-aliasing -fshort-wchar -pthread -pipe  -DNDEBUG -DTRIMMED -Os -freorder-blocks -fno-reorder-functions    -DMOZILLA_CLIENT -include ../../../mozilla-config.h -Wp,-MD,.deps/nsJohabToUnicode.pp nsJohabT
oUnicode.cpp
nsUnicodeToJamoTTF.cpp
c++ -o nsUnicodeToJamoTTF.o -c -I../../../dist/system_wrappers -include ../../../config/gcc_hidden.h -DMOZILLA_INTERNAL_API -D_IMPL_NS_COM -DEXPORT_XPT_API -DEXPORT_XPTC_API -D_IMPL_NS_COM_OBSOLETE -D
_IMPL_NS_GFX -D_IMPL_NS_WIDGET -DIMPL_XREAPI -DIMPL_NS_NET -DIMPL_THEBES  -DOSTYPE=\"Linux2.6.18-194.17.1\" -DOSARCH=Linux -I./../util -I. -I. -I../../../dist/include -I../../../dist/include/nsprpub
-I/usr/include/nspr4 -I/usr/include/nss3         -fPIC   -fno-rtti -fno-exceptions -Wall -Wpointer-arith -Woverloaded-virtual -Wsynth -Wno-ctor-dtor-privacy -Wno-non-virtual-dtor -Wcast-align -Wno-inv
alid-offsetof -Wno-long-long -pedantic -O2 -g -pipe -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m32 -march=i686 -mtune=atom -fasynchronous-unwind-tables -fno-stri
ct-aliasing -fshort-wchar -pthread -pipe  -DNDEBUG -DTRIMMED -Os -freorder-blocks -fno-reorder-functions    -DMOZILLA_CLIENT -include ../../../mozilla-config.h -Wp,-MD,.deps/nsUnicodeToJamoTTF.pp nsUn
icodeToJamoTTF.cpp
nsUnicodeToJamoTTF.cpp: In member function 'virtual nsresult nsUnicodeToJamoTTF::composeHangul(char*)':
nsUnicodeToJamoTTF.cpp:561: warning: suggest parentheses around '&&' within '||'
nsUnicodeToJamoTTF.cpp:876: warning: assuming signed overflow does not occur when assuming that (X + c) < X is always false
rm -f libucvko_s.a
ar cr libucvko_s.a nsEUCKRToUnicode.o nsUnicodeToEUCKR.o nsISO2022KRToUnicode.o nsUnicodeToISO2022KR.o nsCP949ToUnicode.o nsUnicodeToCP949.o nsUnicodeToJohab.o nsJohabToUnicode.o nsUnicodeToJamoTTF.o
ranlib libucvko_s.a


-| { BuildLog => [
-|  { arch    => 'noarch',
-|    code    => 'IntegerOverflow',
-|    diag    => 'Possible integer overflow (this may be a security problem)',
-|    context => { lineno => 18, path => "noarch/build.log" },
-|    excerpt => [
-|         'nsUnicodeToJamoTTF.cpp:876: warning: assuming signed overflow does not occur when assuming that (X + c) < X is always false'
-|        ],
-|  } ] }

-------------------------------------------------------------------------------
>> name = RFE 438709 (missing header for unified diff)

from packages/cpufreq-utils/005/2.el5/data/logs/i386/build.log


+ echo 'Patch #0 (disable-gsic.patch):'
Patch #0 (disable-gsic.patch):
+ patch -p1 -s
+ echo 'Patch #1 (cpufrequtils-fix-parallel-build-of-ccdv.patch):'
Patch #1 (cpufrequtils-fix-parallel-build-of-ccdv.patch):
+ patch -p1 -s
Patch #2 (cpufrequtils-aperf-makefile.patch):
+ echo 'Patch #2 (cpufrequtils-aperf-makefile.patch):'
+ patch -p1 -s
missing header for unified diff at line 3 of patch
+ exit 0
Executing(%build): /bin/sh -e /var/tmp/rpm-tmp.19153
+ umask 022
+ cd /builddir/build/BUILD
+ cd cpufrequtils-005

-| { BuildLog => [
-|  { arch    => 'noarch',
-|    code    => 'PatchApply',
-|    diag    => 'Possible failure to apply a patch',
-|    context => { lineno => 13, path => "noarch/build.log" },
-|    excerpt => [
-|         '+ echo \'Patch #2 (cpufrequtils-aperf-makefile.patch):\'',
-|         '+ patch -p1 -s',
-|         'missing header for unified diff at line 3 of patch',
-|        ],
-|  } ] }


-------------------------------------------------------------------------------
>> name = RFE 157465 (will always overflow)

php.c:474: warning: ignoring return value of 'write', declared with attribute warn_unused_result
if gcc -DHAVE_CONFIG_H -I. -I. -I./config     -I/usr/include/net-snmp -I/usr/include/net-snmp/.. -I/usr/include/mysql -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=
ssp-buffer-size=4 -m32 -march=i386 -mtune=generic -fasynchronous-unwind-tables -MT keywords.o -MD -MP -MF ".deps/keywords.Tpo" -c -o keywords.o keywords.c; \
        then mv -f ".deps/keywords.Tpo" ".deps/keywords.Po"; else rm -f ".deps/keywords.Tpo"; exit 1; fi
ping.c: In function 'ping_icmp':
ping.c:341: warning: pointer targets in passing argument 6 of 'recvfrom' differ in signedness
ping.c:220: warning: 'begin_time' may be used uninitialized in this function
poller.c: In function 'poll_host':
poller.c:485: warning: call to __builtin___snprintf_chk will always overflow destination buffer
if gcc -DHAVE_CONFIG_H -I. -I. -I./config     -I/usr/include/net-snmp -I/usr/include/net-snmp/.. -I/usr/include/mysql -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m32 -march=i386 -mtune=generic -fasynchronous-unwind-tables -MT error.o -MD -MP -MF ".deps/error.Tpo" -c -o error.o error.c; \
        then mv -f ".deps/error.Tpo" ".deps/error.Po"; else rm -f ".deps/error.Tpo"; exit 1; fi
/bin/sh ./libtool --tag=CC --mode=link gcc  -I/usr/include/net-snmp -I/usr/include/net-snmp/.. -I/usr/include/mysql -O2 -g -pipe -Wall -Wp,-D_FORTIFY_SOURCE=2 -fexceptions -fstack-protector --param=ssp-buffer-size=4 -m32 -march=i386 -mtune=generic -fasynchronous-unwind-tables  -L/usr/lib -L/usr/lib/mysql  -o spine  sql.o spine.o util.o snmp.o locks.o poller.o nft_popen.o php.o ping.o keywords.o error.o  -lnetsnmp -lmysqlclient_r -lmysqlclient_r -lcrypto -lz -lpthread -lm -lnsl

-| { BuildLog => [
-|  { arch    => 'noarch',
-|    code    => 'BufferOverflow',
-|    diag    => 'Possible build error',
-|    context => { lineno => 9, path => "noarch/build.log" },
-|    excerpt => [
-|         'poller.c:485: warning: call to __builtin___snprintf_chk will always overflow destination buffer'
-|        ],
-|  } ] }


-------------------------------------------------------------------------------
>> name = make errors

from packages/glibc/2.3.4/2.51/data/logs/i686/build.log

make[2]: Leaving directory `/builddir/build/BUILD/glibc-2.3.6/crypt'
make -s -C linuxthreads tests
make[2]: Entering directory `/builddir/build/BUILD/glibc-2.3.6/linuxthreads'
Starting process a
Starting process b
make[2]: *** [/builddir/build/BUILD/glibc-2.3.6/build-i686-linux/linuxthreads/tst-clock1.out] Error 1
Starting process b
Starting process a
make[2]: Target `tests' not remade because of errors.
make[2]: Leaving directory `/builddir/build/BUILD/glibc-2.3.6/linuxthreads'
make[1]: *** [linuxthreads/tests] Error 2
make -s -C c_stubs tests
make[2]: Entering directory `/builddir/build/BUILD/glibc-2.3.6/c_stubs'
make[2]: Leaving directory `/builddir/build/BUILD/glibc-2.3.6/c_stubs'
make -s -C resolv tests
make[2]: Entering directory `/builddir/build/BUILD/glibc-2.3.6/resolv'
make[2]: Leaving directory `/builddir/build/BUILD/glibc-2.3.6/resolv'
make -s -C nss tests
make[2]: Entering directory `/builddir/build/BUILD/glibc-2.3.6/nss'
make[2]: Leaving directory `/builddir/build/BUILD/glibc-2.3.6/nss'
...
...
...
make[1]: Target `check' not remade because of errors.
make[1]: Leaving directory `/builddir/build/BUILD/glibc-2.3.6'
+ sleep 10s
make: *** [check] Error 2
++ ps -eo ppid,pid,command
++ awk '($1 == 4838 && $3 ~ /^tee/) { print $2 }'


-| { BuildLog => [
-|  { arch    => 'noarch',
-|    code    => 'MakeError',
-|    diag    => 'Possible error from \'make\'',
-|    context => { lineno => 8, path => "noarch/build.log" },
-|    excerpt => [
-|         'make[2]: Entering directory `/builddir/build/BUILD/glibc-2.3.6/linuxthreads\'',
-|         'Starting process a',
-|         'Starting process b',
-|         'make[2]: *** [/builddir/build/BUILD/glibc-2.3.6/build-i686-linux/linuxthreads/tst-clock1.out] Error 1',
-|        ],
-|  },
-|  { arch    => 'noarch',
-|    code    => 'MakeError',
-|    diag    => 'Possible error from \'make\'',
-|    context => { lineno => 13, path => "noarch/build.log" },
-|    excerpt => [
-|         'Starting process a',
-|         'make[2]: Target `tests\' not remade because of errors.',
-|         'make[2]: Leaving directory `/builddir/build/BUILD/glibc-2.3.6/linuxthreads\'',
-|         'make[1]: *** [linuxthreads/tests] Error 2',
-|        ],
-|  },
-|  { arch    => 'noarch',
-|    code    => 'MakeError',
-|    diag    => 'Possible error from \'make\'',
-|    context => { lineno => 29, path => "noarch/build.log" },
-|    excerpt => [
-|         'make[1]: Target `check\' not remade because of errors.',
-|         'make[1]: Leaving directory `/builddir/build/BUILD/glibc-2.3.6\'',
-|         '+ sleep 10s',
-|         'make: *** [check] Error 2',
-|        ],
-|  } ] }

-------------------------------------------------------------------------------
>> name = aclocal errors

from packages/rsyslog/3.22.1/3.el5_5.1/data/logs/i386/*

Building target platforms: i386
Building for target i386
Executing(%prep): /bin/sh -e /var/tmp/rpm-tmp.83208
+ umask 022
+ cd /builddir/build/BUILD
+ LANG=C
+ export LANG
+ unset DISPLAY
...
+ echo 'Patch #4 (rsyslog-3.22.1-createdirs-init.patch):'
Patch #4 (rsyslog-3.22.1-createdirs-init.patch):
+ patch -p1 -b --suffix .createdirs-init -s
+ aclocal
configure.ac:4: error: Autoconf version 2.61 or higher is required
configure.ac:4: the top level
autom4te: /usr/bin/m4 failed with exit status: 63
aclocal: autom4te failed with exit status: 63
+ exit 0
Executing(%build): /bin/sh -e /var/tmp/rpm-tmp.33278

-| { BuildLog => [
-|  { arch    => 'noarch',
-|    code    => 'MiscBuildError',
-|    diag    => 'Possible error in build',
-|    context => { lineno => 18, path => "noarch/build.log", sub => '(in %prep)' },
-|    excerpt => [
-|         '+ aclocal',
-|         'configure.ac:4: error: Autoconf version 2.61 or higher is required',
-|         'configure.ac:4: the top level',
-|         'autom4te: /usr/bin/m4 failed with exit status: 63',
-|        ],
-|  },
-|  { arch    => 'noarch',
-|    code    => 'MiscBuildError',
-|    diag    => 'Possible error in build',
-|    context => { lineno => 19, path => "noarch/build.log", sub => '(in %prep)' },
-|    excerpt => [
-|         'configure.ac:4: error: Autoconf version 2.61 or higher is required',
-|         'configure.ac:4: the top level',
-|         'autom4te: /usr/bin/m4 failed with exit status: 63',
-|         'aclocal: autom4te failed with exit status: 63',
-|        ],
-|  } ] }
