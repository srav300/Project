#!/usr/bin/perl -w

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
warningsToBrowser(1);

use DBI;

print page_header();
print page_css();

if (defined param('register')) {
	print register_screen();
} else {
	if (defined param('username') && defined param('password') ) {
		if (check_login()) {
			if (defined param('login')) {
				print home_screen();
			} elsif (defined param('diet')) {
				print diet_screen();
			}
		} else {
			print wrong_login();	
		}
	} else {
		print login_screen();
	}
}

print page_footer();

sub page_header {
  return header,
      start_html("-title"=>"DoYouEvenFit"),
}

sub page_css {
	return qq(
		<link href="/css/style.css" rel="stylesheet" type="text/css" media="all" />
		<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
		<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
		<body background="/images/banner.jpg">
		<body link="white">
		)
}

sub login_screen(){
	return qq(
    	<div class="header-bottom" id="tour">
    	<div class="wrap">
        <h1><span>D</span>o<span>Y</span>ou<span>E</span>ven<span>F</span>it</h1>  
        <pre>
		</pre>
		<h2><font color="red" size="2">&nbsp</font></h2>		
		<p><center><small><marquee></marquee></center></p></body>
		<form action="doyouevenfit.cgi" method="post">
		<input type="hidden" name="page" value="">
		<input type="text" name="username" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="Username" onfocus="javascript:if(this.value=='Username')this.value='';"><br>
		<input type="password" name="password" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="********" onfocus="javascript:if(this.value=='********')this.value='';"><br>
		<p>&nbsp</p>
		<input type="submit" name="login" value="LOG IN" class="button" style="height:45px;"><br>
		<pre>
		</pre>
		<input type="submit" name="register" value="REGISTER" class="button" style="height:45px;"><br>
		<p>&nbsp</p>
		</form>
		</div>
		</div>
		)
}

sub check_login() {
	$username = param('username');
	chomp $username;
	$password_attempt = param('password');
	chomp $password_attempt;
	if ($username eq "" || $password_attempt eq "") {
		return 0;
	}	
	$driver = "SQLite"; 
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
	$stmt = qq(select password from user where username = '$username'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
    	print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	$password = $row[0];
	if ($password_attempt eq $password) {
		return 1;
	}
	return 0;
}

sub wrong_login() {
    return qq(
    	<div class="header-bottom" id="tour">
    	<div class="wrap">
        <h1><span>D</span>o<span>Y</span>ou<span>E</span>ven<span>F</span>it</h1>  
        <pre>
		</pre>
		<h2><font color="red" size="2">Your login details seem to be incorrect,</font></h2>		
		<p><center><small><marquee></marquee></center></p></body>
		<form action="doyouevenfit.cgi" method="post">
		<input type="hidden" name="page" value="">
		<input type="text" name="username" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="Username" onfocus="javascript:if(this.value=='Username')this.value='';"><br>
		<input type="password" name="password" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="Password" onfocus="javascript:if(this.value=='Password')this.value='';"><br>
		<p>&nbsp</p>
		<input type="submit" name="login" value="LOG IN" class="button" style="height:45px;"><br>
		<pre>
		</pre>
		<input type="submit" name="register" value="REGISTER" class="button" style="height:45px;"><br>
		<p>&nbsp</p>
		</form>
		</div>
		</div>
	)
}

sub register_screen() {

}

sub home_screen() {
	return qq(
    	<pre>
		</pre>
		<h2><font color="red" size="2">HOME PAGE.</font></h2>
		<form action="doyouevenfit.cgi" method="post">
		<input type="submit" name="diet" value="DIET" class="button" style="height:45px;"><br>
		),
		hidden('username'),
		hidden('password'),
		qq(</form>)
}

sub diet_screen() {
	if(check_login()){
		
	} else {
		wrong_login();	
	}
	#$u = param('username');	#just testing/showing how to pass through parameters using hidden()
	#$p = param('password'); #username and password need to be passed through every page for authentication
	#return "Username: ", $u, "Password: ", $p;
}

sub calorie_calculator() {
	my ($gender, $weight, $height, $age, $exeLevelID, $goalID) = @_;	
	if($gender eq 'Male'){
		$var = -5;
	} elsif($gender eq 'Female'){
		$var = 161;
	}

	$BMR = 10*$weight + 6.25*$height + 5*$age + $var;	
	
	if($exeLevelID eq 'Sedentary'){
		$exeLevel = 1.2;	
	} elsif($exeLevelID eq 'Lightly Active'){
		$exeLevel = 1.375;
	} elsif($exeLevelID eq 'Moderately Active'){
		$exeLevel = 1.550;
	} elsif($exeLevelID eq 'Very Active'){
		$exeLevel = 1.725;
	} elsif($exeLevelID eq 'Extremely Active'){
		$exeLevel = 1.900;
	}	

	$BMR *= $exeLevel;

	if($goalID eq 'Weight Loss'){
		$BMR *= 0.8;	
	} elsif($goalID eq 'Extreme Weight Loss'){
		$BMR *= 0.6;
		$minCalPday = 17.6*$weight;	
		if($BMR lt $minCalPday){
			$BMR = $minCalPday;		
		}
	} elsif($goalID eq 'Weight Gain'){
		$BMR *= 1.2;
	} elsif($goalID eq 'Extreme Weight Gain'){
		$BMR *= 1.4;
	}
	
	$cloriePday = $BMR;
			
	return $caloriePday;
}

sub page_footer() {
return qq(
	<div class="footer">
    <p class="copy" style="color:#f2f5f2;font-family:AmbleRegular;">Copyright &copy; 2015. All rights reserved.</p>
	</div>
	</div>
	</body>
	)
}
