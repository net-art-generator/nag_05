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
# Satistics Module 
#

use File::Copy;
my $fstat="stats/statfile.txt";
my $flast="stats/last.txt";

sub clickStat {
	my $rec=shift;
	my $r,$c,$f,$l,$found;
	if (!-e "$fstat"){
		open(FH, ">$fstat") || die "I can't Open $fstat :$!\n";
		close(FH);
		}
	open(FH, "$fstat") || die "I can't Open $fstat :$!\n";
	open(NFH, ">$fstat.back") || die "I can't Open ~$fstat :$!\n";
	while (<FH>) {
		chop if (m/\n/);
		($r,$c,$f,$l) = split(m/°/, $_);
		if ($rec eq $r) {
			$found=1;
			$c++;
			print NFH "$r°$c°$f°".time."\n";
			} else {
			print NFH "$r°$c°$f°$l\n";
			}
		}
	if (!$found) {
		$r=$rec;
		$c=1;
		$f=$l=time;
		print NFH "$r°$c°$f°$l\n";
		}
	close(NFH);
	close(FH);
	move("$fstat.back","$fstat") == 1 or die "Error::While moving : $!"; 
	open(FH, ">$flast") || die "I can't Open $flast :$!\n";
	print FH "$ENV{'REMOTE_ADDR'}°$ENV{'HTTP_REFERER'}°$ENV{'REQUEST_URI'}";
	close(FH);
	return ($c,$f,$l);
	}

sub getStat {
	my $rec=shift;
	if (!-e "$fstat"){
		return (0, 0, 0);
		}
	open(FH, "$fstat") || die "I can't Open $fstat :$!\n";
	while (<FH>) {
		chop if (m/\n/);
		my ($r,$c,$f,$l) = split(m/°/, $_);
		if ($rec eq $r) {
			close(FH);
			return ($c,$f,$l);
			}
		}
	close(FH);
	return (0, 0, 0);
	}
	
sub getStatTop {
	my $no=shift;
	return () if (!-e "$fstat");
	my @REC,@lim;
	open(FH, "$fstat") || die "I can't Open $fstat :$!\n";
	while (<FH>) {
		chop if (m/\n/);
		my ($r,$c,$f,$l) = split(m/°/, $_);
		push(@REC, [$r,$c,$f,$l]);
		}
	close(FH);
	@REC=sort { @$b[1] cmp @$a[1] } @REC;
	foreach (my $i=1; ($i<=$no && @REC > 0); $i++) {
		push(@lim, shift(@REC));
		}
	return @lim;
	}

sub getLast {
	my $no=shift;
	return () if (!$no);
	opendir(DIR, "gen/") || die "I Can't Opendir [gen/] : $!\n";
	my @list=readdir(DIR);
	closedir(DIR);

	my @REC,@lim;
	@REC=@lim=();
	foreach (@list) {
		if ($_ !~ m/^\.{1,2}/) {
			my ($f,$d) = ($_, (stat("gen/$_"))[9]);
			push(@REC, [$f,$d]);
			}
		}
	@REC=sort { @$b[1] cmp @$a[1] } @REC;
	foreach (my $i=1; ($i<=$no && @REC > 0); $i++) {
		push(@lim, shift(@REC));
		}
	return @lim;
	}

sub isLast {
	my $rec="$ENV{'REMOTE_ADDR'}°$ENV{'HTTP_REFERER'}°$ENV{'REQUEST_URI'}";
	return 0 if (!-e "$flast");
	open(FH, "$flast") || die "I can't Open $flast :$!\n";
	@lines=<FH>;
	close(FH);
	chop $lines[0] if (m/\n/);
	return 1 if ($lines[0] eq $rec);
	return 0;
	}
	
sub clearOldies {
	#Get the statistics file.
	my @STAT, @list, @FL, $max, $is, $smax;
	$is=0;
	$max=70*1024*1024; # 70 Mb
	$smax=40; # Keep the <number> first photos from the statistic file
	open(FH, "$fstat") || die "I can't Open $fstat :$!\n";
	while (<FH>) {
		chop if (m/\n/);
		my ($r,$c,$f,$l) = split(m/°/, $_);
		push(@STAT, [$r,$c,$f,$l]);
		}
	close(FH);

	opendir(DIR, "gen") || die "I Can't Opendir [gen] : $!\n";
	@list=readdir(DIR);
	closedir(DIR);

	foreach (@list) {
		if ($_ !~ m/^\.{1,2}/) {
			$is += (stat("gen/$_"))[7];
			push(@FL, [$_, (stat("gen/$_"))[7],(stat("gen/$_"))[9]]);
			}
		}
	
	opendir(DIR, "grab") || die "I Can't Opendir [grab] : $!\n";
	@list=readdir(DIR);
	closedir(DIR);

	foreach (@list) {
		if ($_ !~ m/^\.{1,2}/) {
			$is += (stat("grab/$_"))[7];
			push(@FL, [$_, (stat("grab/$_"))[7],(stat("grab/$_"))[9]]);
			}
		}
	
	# Sort the lists (Older first)
	@STAT=sort { @$a[1] cmp @$b[1] } @STAT;
	@FL=sort { @$a[2] cmp @$b[2] } @FL;

	while (@STAT > $smax) { shift(@STAT); }

	#print "<hr>IS: $is MAX: $max<hr>\n";

	my $all, $cno, $csize, $ldate;
	$del=$all=$cno=$csize=0;
	$all=@FL;
	foreach (@FL) { 
		if (@$_[0] !~ /\.(gif|jpeg|jpg|png)$/i && -e "gen/@$_[0]")	{
			$del += unlink("gen/@$_[0]");
			}
		if ($is > $max) {
			$is -= @$_[1];
			$csize += @$_[1];
			$ldate = @$_[2];
			$cno++;
			if (-e "grab/@$_[0]") {
				$del += unlink("grab/@$_[0]");
				}
			elsif (-e "gen/@$_[0]") {
				$del += unlink("gen/@$_[0]");
				}
			# print "*** ";
			} #end if ($is > $max)
		#print "(". ++$cno .") @$_\n"; 
		} # end foreach
	#print "<hr>NOW -- IS: $is MAX: $max<hr>\n";
	return ($del, $cno, $all, $csize, $ldate);
	}

1;