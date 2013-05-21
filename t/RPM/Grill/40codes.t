# -*- perl -*-
#
# This tries to cross-reference gripe codes against tooltips.txt,
# making sure that each 'code => "BlahBlah"' tuple is documented
# and also making sure that each code in tooltips.txt has a
# corresponding 'code => ...'.
#
use strict;
use warnings;

use Test::More;

# First: read tooltips file.
my %tooltips = read_tooltips();

# Main loop: read all plugin .pm files, look for 'code => ...', and
# check that they're in tooltips.txt
my $dir = 'lib/RPM/Grill/Plugin';
opendir DDD, $dir or die "Cannot opendir $dir: $!\n";
for my $f (sort grep { /^[A-Z].*\.pm$/ } readdir DDD) {
    (my $plugin = $f) =~ s/\.pm$//;

    open my $fh, '<', "$dir/$f"     or die "Cannot read $dir/$f: $!\n";
    while (my $line = <$fh>) {
        if ($line =~ /code\s*=>\s*('|")(\S+)\1/) {
            my $code = $2;

            # The usual case: a literal code name ('FooBar')
            if (exists $tooltips{$plugin}{$code}) {
                $tooltips{$plugin}{$code} = 1;  # Mark as seen
                pass "$plugin :: $code is documented";
            }

            # The harder cases: variable interpolation ("${Foo}Bar", "Foo$Bar")
            elsif ($code =~ s/^(\$\{.*?\})//) {
                my $wildcard = $1;

                my $codes = $tooltips{$plugin};
                my @codes;
                for my $k (sort grep { /$code$/ } keys %{$codes}) {
                    $codes->{$k} = 1;
                    $k =~ s/$code//;
                    push @codes, $k;
                }
                my $names = join(',', @codes);
                pass "$plugin :: $wildcard$code {$names}";
            }
            elsif ($code =~ s/(\$.*)$//) {
                my $wildcard = $1;

                # BIG-TIME ASSUMPTION!
                my $codes = $tooltips{$plugin};
                my @codes;
                for my $k (sort grep { /^$code/ } keys %{$codes}) {
                    $codes->{$k} = 1;
                    $k =~ s/^$code//;
                    push @codes, $k;
                }
                my $names = join(',', @codes);
                pass "$plugin :: $code$wildcard {$names}";

            }

            # Nothing in tooltips.txt
            else {
                fail "No tooltip for $plugin :: $code";
            }
        }
    }
    close $fh;
}
closedir DDD;

# Next pass: look for anything in tooltips.txt that isn't in a .pm file
for my $p (sort keys %tooltips) {
    if (my @missing = sort grep { !$tooltips{$p}{$_} } keys %{$tooltips{$p}}) {
        fail "Not found in $p.pm :: @missing";
    }
}

done_testing;


sub read_tooltips {
    my %tooltips;

    my $plugin;
    my $code;
    my %seen;

    my $tooltips_file = 'doc/tooltips.txt';
    open my $fh, '<', $tooltips_file
        or die "Cannot read $tooltips_file: $!";
    while (my $line = <$fh>) {
        chomp $line;
        next if     $line =~ /^#/;
        next unless $line;

        # e.g.
        #    |VirusCheck                               <<<<<<--- plugin
        #    |  This module blah blah blah...
        #
        #    ClamAV                                    <<<<<<--- code
        #      <p>The <a href="http://www.clamav.net/">ClamAV</a> ....
        #
        if ($line =~ /^\|(\S+)/) {
            $plugin = $1;
        }
        elsif ($line =~ /^(\S+)$/) {
            $code = $1;
            $tooltips{$plugin}{$code} = undef;
            if (my $seen = $seen{$code}) {
                fail "Duplicate: $code is in $seen, $plugin";
            }
        }

        # Codes can be marked Deprecated. This is necessary because we
        # can't just go into the database and delete old runs/results.
        elsif ($line =~ /[Dd]eprecated/) {
            delete $tooltips{$plugin}{$code};
        }
    }
    close $fh;

    return %tooltips;
}
