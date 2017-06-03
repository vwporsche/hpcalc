#!/var/www/vhosts/rennlight.com/bin/perl 
# 2004/11/24 Thom Fitzpatrick
# cgi form to collect weight information

use strict;
use Fcntl qw(:DEFAULT :flock);
use CGI qw(:standard);
use CGI::Carp qw/fatalsToBrowser/;

my $DATA = "/var/www/vhosts/rennlight.com/www/cgi-bin/weight.txt";
my $SERVER="rennlight.com";
my %FORM;
my $CORRECTION=17;

print header();
print "<head>\n";
print "<link rel=stylesheet href=http://www.$SERVER/rennlight.css TYPE=text/css>\n";
print title("RennLight.com Butt Dyno");
print "<body>\n";
print h4("RennLight.com Butt Dyno");

foreach (CGI::param()) {
        $_ =~ s/|//g;
        $_ =~ s/\n/<br>/g;
        $_ =~ s/^M/<br>/g;
	$FORM{$_} = CleanInput(CGI::param($_));
}

if (!exists($FORM{'corr'})) {
	$FORM{'corr'} = $CORRECTION;
}

print "<p>Calculate the <i>perceived</i> horsepower increase or decrease for a given weight gain/loss</p>\n";

if ($FORM{'submit'}) {
	$FORM{'ohp'} = abs(int($FORM{'ohp'}));
	$FORM{'ow'} = abs(int($FORM{'ow'}));
	$FORM{'d'} = int($FORM{'d'});
	$FORM{'corr'} = abs(int($FORM{'corr'}));

	if ($FORM{'ohp'} == 0) {
		print "<font color=red>Need valid HP value</font>\n";
		ShowForm();
		exit 0;
	}
	if ($FORM{'ow'} == 0) {
		print "<font color=red>Need valid weight value</font>\n";
		ShowForm();
		exit 0;
	}
	Results();
	print "<p>\n";
	ShowForm();
	exit 0;
} else {
	ShowForm();
	exit 0;
}


sub ShowForm() {

print <<EOF;
<form action=http://$SERVER/cgi-bin/hp.cgi method=get>
<table border=1>
<tr>
	<th>Current HP</th>
	<td><input type=text name=ohp value=$FORM{'ohp'}></td>
</tr>
<tr>
	<th>Current Weight<br><font size=-2>(lbs)</th>
	<td><input type=text name=ow value=$FORM{'ow'}></td>
</tr>
<tr>
	<th>Weight Delta<br><font size=-2>- for weight loss, + for weight gain</th>
	<td><input type=text name=d value=$FORM{'d'}></td>
</tr>
<tr>
	<th>Comments<br><font size=-2></th>
	<td><input type=text name=com value=$FORM{'com'}></td>
</tr>
<tr>
	<th>Drivetrain Correction %<br><font size=-2>(drivetrain loss fudge-factor)</th>
	<td><input type=text name=corr value=$FORM{'corr'}></td>
</tr>

<tr>
	<td colspan=2 align=center><input type="submit" value="Submit" name=submit> &nbsp; &nbsp;<input type="reset" value="Clear Form"></td>
</tr>
</table>

<b><a href=http://rennlight.com><< Home</a></b>

EOF
}


sub CleanInput {
        my ($input) = (@_);

	chomp($input);
        $input =~ s/[()]//g;
        $input =~ s/\\//g;
        $input =~ s/[\[\]]//g;
        $input =~ s/[<>]//g;
        $input =~ s/\|//g;
        $input =~ s/\"/\'/g;
        $input =~ s/\`/\'/g;
        $input =~ s/  / /g;
        $input =~ s/\s+$//g;
        $input =~ s/^\s+//g;
        $input =~ s/%00//g; # null byte check
        $input =~ s/\x0//g; # null byte check

        return($input);
}

sub Results() {
	
	$FORM{'nw'} = $FORM{'ow'} + $FORM{'d'};
	my $old_qtr = (($FORM{'ow'} / ($FORM{'ohp'} - ($FORM{'ohp'} * ($FORM{'corr'} / 100))) ) ** .333 ) * 5.825;
	my $old_ratio = $FORM{'ow'} / $FORM{'ohp'};

	#NewHP = [ (oldHP X DeltaW) / (newWeight) ] + oldHP 
	#$FORM{'nhp'} = (($FORM{'ohp'} * abs($FORM{'d'})) / $FORM{'nw'}) + $FORM{'ohp'};

#print "Keith: $FORM{'nhp'}<p>\n";

	$FORM{'nhp'} = int(($FORM{'ow'} - $FORM{'d'}) / $old_ratio);
	
	my $new_qtr = (($FORM{'nw'} / ($FORM{'ohp'} - ($FORM{'ohp'} * ($FORM{'corr'} / 100))) ) ** .333 ) * 5.825;
	my $new_ratio = $FORM{'nw'} / $FORM{'ohp'};

	print "<table border=1>\n";

	print "<tr>\n";
	print "<th>&nbsp</th>\n";
	print "<th>Weight</th>\n";
	print "<th>HP</th>\n";
	print "<th>Lbs:HP</th>\n";
	print "<th>1/4-Mile <br><font size=-2>(theroetical)</th>\n";
	print "</tr>\n";

	print "<tr>\n";
	print "<th>Previous</th>\n";
	print "<td align=center>$FORM{'ow'}</td>\n";
	print "<td align=center>$FORM{'ohp'}</td>\n";
	printf "<td align=center>%.1f</td>\n", $old_ratio;
	printf "<td align=center>%.2fs</td>\n", $old_qtr;
	print "</tr>\n";

	print "<tr>\n";
	print "<th>New</th>\n";
	print "<td align=center>$FORM{'nw'}</td>\n";
	print "<td align=center>$FORM{'nhp'}</td>\n";
	printf "<td align=center>%.1f</td>\n", $new_ratio;
	printf "<td align=center>%.2fs</td>\n", $new_qtr;
	print "</tr>\n";

	print "<tr>\n";
	print "<th>Delta</th>\n";
	printf "<td align=center>%+d</td>\n", $FORM{'d'};
	printf "<td align=center>%+d</td>\n", $FORM{'nhp'} - $FORM{'ohp'};
	printf "<td align=center>%+.1f</td>\n", $new_ratio - $old_ratio;
	printf "<td align=center>%+.2fs</td>\n", $new_qtr - $old_qtr;
	print "</tr>\n";
	

	print "<tr>\n";
	print "<th>Comments</th>\n";
	print "<td colspan=4>$FORM{'com'}&nbsp;</td>\n";
	print "</tr>\n";

	print "</table>\n";
}

