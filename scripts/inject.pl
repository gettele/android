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

sub spew {
    my ($p, $d) = @_;
    open(my $f, '>:raw', $p) or die "write $p: $!";
    print $f $d;
    close $f;
}

my $data = slurp($file);
my $crlf = (index($data, "\r\n") >= 0) ? 1 : 0;

sub normalize {
    my ($d, $crlf) = @_;
    $d =~ s/\r?\n$//;
    if ($crlf) {
        $d =~ s/\n/\r\n/g;
    } else {
        $d =~ s/\r//g;
    }
    return $d;
}

my $anchor = normalize(slurp($anchorFile), $crlf);
my $block = normalize(slurp($blockFile), $crlf);

my $count = () = $data =~ /\Q$anchor\E/g;
die "anchor count $count (need 1) in $file\n" unless $count == 1;

my $eol = $crlf ? "\r\n" : "\n";
if ($mode eq 'replace') {
    $data =~ s/\Q$anchor\E/$block/;
} else {
    $data =~ s/\Q$anchor\E/$anchor$eol$block/;
}

my $lf = () = $data =~ /\n/g;
my $cr = () = $data =~ /\r/g;
if ($crlf) {
    die "mixed endings lf=$lf crlf=$cr in $file\n" unless $lf == $cr;
} else {
    die "stray CR in $file\n" if $cr;
}

spew($file, $data);
print "ok $file\n";
