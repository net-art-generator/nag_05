#!/usr/bin/perl
#--------------------------------------------------------------
# NAG - Net.Art Generator
#
# Author: Panos Galanis <pg@iap.de>
# Created: 16.04.2003
# Last: 10.06.2003
# License: GNU GPL (GNU General Public License. See LICENSE file) 
#
# Copyright (C) 2003 IAP GmbH 
# Ingenieurbüro für Anwendungs-Programmierung
# Mörkenstraße 9, D-22767 Hamburg
# Web: http://www.iap.de, Mail: info@iap.de 
#--------------------------------------------------------------

use strict;
use CGI;
use CGI::Carp 'fatalsToBrowser';
use LWP::UserAgent;
use Image::Magick;

my $q = new CGI;
my @ilinks;
my @err;
my $comment="<!--
# -----------------------------------
# NAG - Net.Art Generator
# 
# Author : Panos Galanis <pg\@iap.de>
# Using : Perl v". sprintf("%vd", $^V) .", LWP::UserAgent v". $LWP::UserAgent::VERSION .", ImageMagic v". $Image::Magick::VERSION ."
#
# Copyright (C) 2003 IAP GmbH 
# Ingenieurbüro für Anwendungs-Programmierung
# Mörkenstraße 9, D-22767 Hamburg
# Web: http://www.iap.de, Mail: info\@iap.de 
-->\n";

# $kunst=~ s/[^\w\d]/_/i;

require "modules/display.pl";
require "modules/netagent.pl";
require "modules/imageagent.pl";
require "modules/stats.pl";

# Parameter Security
my $ac=($q->param('ac'))?$q->param('ac'):"";
my $single=($q->param('file'))?$q->param('file'):"";
my $name=($q->param('name'))?$q->param('name'):"anonymous";
my $query=($q->param('query'))?$q->param('query'):"";
my $max=($q->param('max'))?$q->param('max'):0;
my $ext=($q->param('ext'))?$q->param('ext'):"";
my $comp=($q->param('comp'))?$q->param('comp'):0;
my $picas=($q->param('picas'))?$q->param('picas'):"";
my $picmax=($q->param('picmax'))?$q->param('picmax'):0;
my $noclick=($q->param('noclick'))?$q->param('noclick'):0;
$ac=&secCheck($ac,"home","display","create","single","stats");
$max=&secCheck($max,600,400,800,1000);
$ext=&secCheck($ext,"jpg","gif","png");
$comp=&secCheck($comp,4,2,6,8);


# Parameter Security

print "Content-type: text/html\n\n";
#print "$name - $query - $max - $ext - $comp";
print $comment;
print &startPage(ucfirst($ac) ." (Test period)");
print &startPanel("<b>.:: NAG :: Net.Art Generator</b>");
print &rowTabs(
		"#cccccc","#ffffff","left", 
		"Home", ($ac eq "home")? "":"/",
		"Display", ($ac eq "display")? "":"?ac=display",
		"Create", ($ac eq "create")? "":"?ac=create",
		"Stats", ($ac eq "stats")? "":"?ac=stats"
		);
print &endPanel;

if ($ac eq "home") {	
	print &startPanel("<b>Welcome to NAG</b>");
	print "<p>The net.art generator automatically produces net.art on demand.</p>\n";
	print "<p>This version of the net.art generator creates images. The resulting image
emerges as a collage of a number of images which have been collected on
the WWW in relation to the 'title' you have chosen. The original material
is processed in 12-14 randomly chosen and combined steps.</p>\n";
	print "<p>The net.art generator was programmed by Panos Galanis from IAP GmbH,
Hamburg, and was a commission by the Volksfürsorge art collection.</p>\n";
	print "<p>If you are facing serious problems and the generator does not work at all,
please contact Panos &lt;<a href='mailto:pg\@iap.de?Subject=NAG::Mail'>pg\@iap.de</a>&gt;, or Cornelia 
&lt;<a href='mailto:cornelia\@snafu.de?Subject=NAG::Mail'>cornelia\@snafu.de</a>&gt;</p>\n";
	print "<p>Have fun and become a net.artist!</p>\n";
	print &endPanel;
	print &startPanel("<b>Screenshots</b>");
	print "<p align='center'><img src='img/gen_shot_01_small.gif' class='ipreview'> \n";
	print "<img src='img/gen_shot_02_small.gif' class='ipreview'> \n";
	print "<img src='img/gen_shot_03_small.gif' class='ipreview'> </p>\n";
	print &endPanel;
	}
if ($ac eq "display") {	
	#push(@err, "Warn :: Generator parameters require <b>Query</b> input !!") if ($max && !$query && !$picas) ;
	print &startPanel("Display Generated Pictures");
	print "<form><table><tr><td nowrap>";
	foreach ("a".."z") {
		print "<a href='?ac=display&picas=-[$_". uc($_) ."]'>$_</a> \n";
		}
	my ($gsize,@glist)=&getDirInfo("gen/");
	$gsize = ($gsize > 1024*1024)? sprintf("%.2f Mb", $gsize/(1024*1024)) : sprintf("%.2f kb", $gsize/1024);
	print "</td><td width='99%' align='right'><b>Search</b> ". @glist ." pictures ($gsize) </td><td nowrap>";
	print "<input type='hidden' name='ac' value='display' /><input type='text' name='picas' value='$picas' /> ";
	print "<input type='submit' value='Search' /></td></tr></table></form>\n";
	#print "<p align='center'>\n";
	if ($picas) {
		my @tmp;
		foreach (@glist) { 
			push(@tmp, $_) if (m/$picas/i);}
		@glist=@tmp;
		}
	$picmax=(@glist < 20)? @glist : 20;
	my @rfiles = &randImgList($picmax, @glist);
	my ($mt,$ctd,$myf)=(0,0,"");
	foreach $myf (@rfiles) { 
		if (!-e "thumb/$myf"){
			push(@err, &makeThumb(120, $myf));
			$mt++;
			}
		#my ($c,$f,$l)=&getStat($myf);
		if (!$ctd) { $ctd++; print "\n<table width='100%'>\n<tr>"; }
		if ($ctd > 4 ) { $ctd=1; print "</tr>\n<tr>"; }
		print "<td align='center' class='small'>";
		print "<a href='?ac=single&file=$myf'><img src='thumb/$myf' title='$myf' vspace='10' hspace='10' class='ipreview' /></a>\n"; 
		my ($ti,$da)=split(m/\@/, $myf);
		my @d=split(m/_+/, $da);
		print "<br />$ti <br />\@ $d[0] $d[1] $d[2]";
		print "</td>";
		$ctd++;
		}
	print "</tr></table>";
	#print "</p>\n";
	print &endPanel;
	print "<small>Display ". @rfiles ." Thumbs :: $mt Updates.</small>\n";
	}

elsif ($ac eq "create") { 
	print &startPanel("Create Info");
	print "The generation of your piece of net.art takes 1-2 minutes. Please have a
little patience. If nothing has happenend after 2 minutes, please click
the 'stop'-button and try again.";
	print &endPanel;
	print &startPanel("Create Query ");
	print &inputForm($name,$query,$max,$ext,$comp);
	print &endPanel;
	if ($name && $query && $query =~ /[\w\s]+/i) {
		my @dt=split(" ", localtime(time));
		shift(@dt);
		my $imfile = $name ."-". $query ."@". join(" ", @dt);
		$imfile =~ s/[^\w\d\@\-\:]/_/g;
		$imfile =~ s/\:/\./g;
		print &startPanel("Searching the Net for <em>$query</em> :: Powered by <a href='http://www.google.com/imghp'>Google</a>");
		my @ilist=&getImgList($query);
		if (!@ilist) {
			push(@err,"Query [$query] returned no Images!");
			print "<center>Generator process canceled!</center>\n";
			print &endPanel;
			}else{
			my @mylist=&randImgList($comp,@ilist);
			print "Choosing  : ". @mylist . " / ". @ilist ."<br />\n";
			print "<ul>\n" if @mylist;
			foreach (@mylist) { print "<li>$_ :: <a href='http://$_'>view</a></li>\n"; }
			print "</ul>\n" if @mylist;
			print &endPanel;
			print &startPanel("Generator Usage");
			my @localist=&grabImg(@mylist);	

			my $cached=shift(@localist);
			print "<p>Composition: ". @localist . " :: New :". (@localist - $cached) ." :: Cached :$cached";
			print &endPanel;
			print &startPanel("Show");
			my $base=shift(@localist);
			push(@err, &genImg($imfile, $max, $max, $ext, $base, @localist));
			push(@err, &makeThumb(120, "$imfile.$ext"));
			print "<center><img src='gen/$imfile.$ext' title='$imfile' class='ipreview' /><br /><b>$imfile</b></center>";
			print &endPanel;
			my @clear=&clearOldies;
			print "<small>Cleaner Status :: [ $clear[0] / $clear[1] / $clear[2] ] ";
			print sprintf "%.2f kb", $clear[3]/1024;
			print ":: Last Date [". localtime($clear[4]) ."]" if ($clear[4]);
			print "</small>";
			}
		
		}else{
		push(@err,"No Artist ??") if (!$name);
		push(@err,"Query [$query] not accepted!") if ($query && $query !~ /[\w\s]+/i);
		}

	}

elsif ($ac eq "single") { 
	if (-e "gen/$single") {
		#print "$ENV{'REMOTE_ADDR'}°$ENV{'HTTP_REFERER'}°$ENV{'REQUEST_URI'}\n";
		my ($c, $f, $l)=(&isLast||$noclick)? &getStat($single) : &clickStat($single);
		print &startPanel("Display Single File :: $c click(s) from ". localtime($f));
		print "<center><img src='gen/$single' border='0' class='ipreview' /><br /><a href='gen/$single'>$single</a></center>";
		print &endPanel;
		}else{
		push(@err, "File :: $single :: Not found ????");
		}
	}

elsif ($ac eq "stats") { 
		my ($dif,$no);
		my ($size,@clist)=&getDirInfo("grab/");
		$size = ($size > 1024*1024)? sprintf("%.2f Mb", $size/(1024*1024)) : sprintf("%.2f kb", $size/1024);
		my ($gsize,@glist)=&getDirInfo("gen/");
		$gsize = ($gsize > 1024*1024)? sprintf("%.2f Mb", $gsize/(1024*1024)) : sprintf("%.2f kb", $gsize/1024);
		print &startPanel("Picture Base Status");
		print "Net Cached: ". @clist ." ($size)";
		print " :: Generator: ". @glist ." ($gsize)</p>\n";
		print &endPanel;
		print &startPanel("Statistics <b>Top 10</b>");
		print "<table width='100%' cellspacing='1'>\n";
		my $cl=0;
		my $top;
		foreach $top (&getStatTop(10)) {
			$no++;
			if (!$cl) { print "<tr>";  }
			$dif=($dif eq "#dddddd")? "#eeeeee" : "#dddddd";
			my ($ti,$da)=split(m/\@/, @$top[0]);
			my @d=split(m/_+/, $da);
			print "<td valign='top' bgcolor='$dif'>";
			print "<a href='?ac=single&file=@$top[0]&noclick=1'><img src='thumb/@$top[0]' border='1' vspace='4' hspace='4' class='ipreview'/></a></td>";
			print "<td bgcolor='$dif'><font size='+2'>$no</font><br />\n";
			print "<b>$ti </b><br />\@ $d[0] $d[1] $d[2]<br />";
			print "<br /><b>@$top[1]</b> click(s) <br />First click: ". localtime(@$top[2]) ." <br /> last: ". localtime(@$top[3]);
			print "</td>";
			if ($cl >= 1) {	print "</tr>\n"; $cl=0; }else{ $cl++; }
			}
		print "</table>\n";
		print "<center>Empty Statistics table!</center>\n" if (!$no);
		print &endPanel;

		print &startPanel("Statistics <b>Last 20</b>");
		print "<table width='100%' cellspacing='1'>\n";
		my $last;
		$no=$cl=0;
		foreach $last (&getLast(20)) {
			$no++;
			if (!$cl) { $cl++; print "\n<tr>";  }
			my ($ti,$da)=split(m/\@/, @$last[0]);
			my @d=split(m/_+/, $da);
			print "<td align='center' class='small'>";
			print "<a href='?ac=single&file=@$last[0]'><img src='thumb/@$last[0]' title='@$last[0]' vspace='10' hspace='10' class='ipreview' /></a>\n";  
			print "<br />$ti <br />\@ $d[0] $d[1] $d[2]";
			print "</td>";
			if ($cl >= 4) {	print "</tr>\n"; $cl=0; }else{ $cl++; }
			}
		print "</table>\n";
		print "<center>Empty Statistics table!</center>\n" if (!$no);
		print &endPanel;
	}

if (@err) {
	print &startPanel("Generator :: Warnings & Errors");
	print "<ul>\n";
	foreach (@err) { print "<li>$_</li>"; }
	print "</ul>\n";
	print &endPanel;
	}

print &endPage();

exit;
	
