use strict;
use warnings;

my ($file, $anchorFile, $blockFile, $mode) = @ARGV;
$mode //= 'insert';

sub slurp {
    my ($p) = @_;
    open(my $f, '<:raw', $p) or die "open $p: $!";
    local $/;
    my $d = <$f>;
    close $f;
    return $d;
}

sub crlf {
    my ($d) = @_;
    $d =~ s/\r?\n$//;
    $d =~ s/\n/\r\n/g;
    return $d;
}

my $anchor = crlf(slurp($anchorFile));
my $block = crlf(slurp($blockFile));
my $data = slurp($file);

my $count = () = $data =~ /\Q$anchor\E/g;
die "anchor count $count (need 1) in $file\n" unless $count == 1;

if ($mode eq 'replace') {
    $data =~ s/\Q$anchor\E/$block/;
} else {
    $data =~ s/\Q$anchor\E/$anchor\r\n$block/;
}

my $lf = () = $data =~ /\n/g;
my $crlf = () = $data =~ /\r\n/g;
die "mixed endings lf=$lf crlf=$crlf in $file\n" unless $lf == $crlf;

open(my $out, '>:raw', $file) or die "write $file: $!";
print $out $data;
close $out;
print "ok $file\n";
