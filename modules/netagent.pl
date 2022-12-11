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
#
# Netagent.pl
#


sub getImgList {
	my $query="@_";
	my $ua = LWP::UserAgent->new;
	#$ua->proxy(http  => 'http://proxy.server:80');
	$ua->agent("Mozilla/5.0");
	my $req = HTTP::Request->new(GET => "http://images.google.com/images?btnG=Search&site=images&q=". $query);
	my $page = $ua->request($req)->as_string;  
	return () if ($page !~ m/imgurl=/);
	my @lines = split(m/imgurl=/, $page);
	my @ilinks=();
	foreach my $line (@lines) {
		$line =~ m/^(.*?)\&/g;
		if ($1) {
			#print "<a href='http://$1'><img src='http://$1' title='$1' height=160 border=4></a>\n";
			push(@ilinks, "$1");
			}
		}
	return @ilinks;
	}

sub grabImg {
	my @list=();
	my $no=0;
	my $ua = LWP::UserAgent->new;
	#$ua->proxy(http  => 'http://proxy.server:80');
	$ua->agent("Mozilla/5.0");
	foreach (@_) {
		my $file = $_;
		my $chk=0;
		my $chkd=0;
		$file =~ s/[^\w\d\.]/_/g;
		if (-e "grab/$file") { 
			# Check if the cache is a week old
			# If is this a week old replace it from the net !
			$chkd=time - (stat("grab/$file"))[9];
			$chkd=($chkd > (60*60*24*7))? 1:0; 
			}
			
		if (!-e "grab/$file" || $chkd) {
			#print "Getting <b>http://$_</b> saving as <em>$file</em><br>\n";
			my $req = HTTP::Request->new(GET => "http://$_");
			my $pic = $ua->request($req);  
			$chk=($pic->headers->as_string =~ m/content-type: image\//i);
			if ($chk) {
				open(FH, ">grab/$file") || die "Cant Open grab/$file :$!\n";
				#binmode FH;  # for MSDOS derivations.
				print FH $pic->content;
				close(FH);
				}
			}else{
			$chk=1;
			$no++;
			}
		push(@list, "grab/$file") if $chk;
		}
	return ($no, @list);
	}
	
1;
