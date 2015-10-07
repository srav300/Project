#!/usr/bin/perl -w

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
use Date::Calc qw/check_date/;
use WWW::Mechanize;
warningsToBrowser(1);

use DBI;

print page_header();
print page_css();

if (defined param('register')) {
	print register_screen();
} elsif (defined param('create_account')) {
	if (check_register()) {
		create_account();
		print registered();
	} else {
		print register_help();
	}
} elsif (defined param('username') && defined param('password') ) {
	if (check_login()) {
		if (defined param('meal')) {
			print add_food();
		} elsif (defined param('add_meal') && param('meal_name') ne "") {
			insert_meal();
			print diet_screen();
		} elsif (defined param('login')) {
			print diet_screen();
		} elsif (defined param('date')) {
			print diet_screen();
		}
	} else {
		print wrong_login();	
	}
} else {
	print login_screen();
}

print page_footer();

sub page_header {
	return header,
	start_html("-title"=>"DoYouEvenFit"),
}

sub page_css {
	$css = qq(
	<link href="/css/style.css" rel="stylesheet" type="text/css" media="all" />
	<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	);
	if (defined param('meal') || defined param('register') || (defined param('create_account') && !check_register())) {
		$css .= qq(<body background="/images/wood.jpg">);
	} else {
		$css .= qq(<body background="/images/banner.jpg">);
	}	
	$css .= qq(<body link="white">);
	return $css;
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
	<input type="text" name="username" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="username" onfocus="javascript:if(this.value=='username')this.value='';"><br>
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
	$password_attempt = param('password');
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
	<h2><font color="red" size="2">&nbsp</font></h2>		
	<center><small><font color="white">Your login details seem to be incorrect.</font></center></body>
	<form action="doyouevenfit.cgi" method="post">
	<input type="hidden" name="page" value="">
	<input type="text" name="username" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="username" onfocus="javascript:if(this.value=='username')this.value='';"><br>
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
	);
}

sub register_screen() {
	return qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<h1>Fill in your details</h1>  
	<h2><font color="red" size="2">&nbsp</font></h2>		
	<p><center><small><marquee></marquee></center></p></body>
	<form action="doyouevenfit.cgi" method="post">
	<pre> </pre>
	<p><center><h3 style="color:white;">Username</h3></center></p></body>
	<input type="text" name="new_username" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<p><center><h3 style="color:white;">Password</h3></center></p></body>
	<input type="password" name="password1" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Re-enter Password</h3></center></body>
	<input type="password" name="password2" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">First Name</h3></center></body>
	<input type="text" name="fname" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Last Name</h3></center></body>
	<input type="text" name="lname" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Email</h3></center></body>
	<input type="text" name="email" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Gender</h3></center></body>
	<select name="gender" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:47px;width:150px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<option>Male
	<option>Female
	</select>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Height (cm)</h3></center></body>
	<input type="text" name="height" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Weight (kg)</h3></center></body>
	<input type="text" name="weight" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Age</h3></center></body>
	<input type="text" name="age" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">What is your level of exercise?</h3></center></body>
	<select name="exercise" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:116px;width:350px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<option>Sedentary
	<option>Lightly Active
	<option>Moderately Active
	<option>Very Active
	<option>Extremely Active
	</select>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">What is your goal?</h3></center></body>
	<select name="goal" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:116px;width:350px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<option>Extreme Weight Loss
	<option>Weight Loss
	<option>Maintain Weight
	<option>Weight Gain
	<option>Extreme Weight Gain
	</select>
	<p>&nbsp</p>
	<pre>
	</pre>
	<input type="submit" name="create_account" value="CREATE ACCOUNT" class="button" style="height:45px;width:350px;"><br>
	<p>&nbsp</p>
	</form>
	);
}

sub check_register() {
	my $new_username = param('new_username');
	my $password1 = param('password1');
	my $password2 = param('password2');
	my $fname = param('fname');
	my $lname = param('lname');
	my $email = param('email');
	my $gender = param('gender');
	my $height = param('height');
	my $weight = param('weight');
	my $age = param('age');
	my $exercise = param('exercise');
	my $goal = param('goal');
	if ($new_username eq "") {
		return 0;
	} elsif (length($new_username) < 6) {
		return 0;
	}
	if ($new_username !~ /^[a-zA-Z0-9]+$/) {
		return 0;
	}
	$driver = "SQLite";
	$database = "project.db";
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr;
	$stmt = qq(select username from user where username = '$new_username');
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr;
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	$existing_username = $row[0];
	if ($new_username eq $existing_username) {
		return 0;
	}
	if ($password1 eq "") {
		return 0;
        } elsif (length($password1) < 6) {
		return 0;
	}
	if ($password1 ne $password2) {
		return 0;
	}
	if ($fname eq "") {
		return 0;
	} elsif ($fname !~ /^[a-zA-Z-]*\n*$/) {
		return 0;
	}
	if ($lname eq "") {
		return 0;
	} elsif ($lname !~ /^[a-zA-Z-]*\n*$/) {
		return 0;
	}
	if ($email eq "") {
		return 0;
	} elsif ($email !~ /^\w+\@\w+(\.\w+)+$/) {
		return 0;
	}
	if ($gender eq "") {
		return 0;
	}
	if ($height eq "") {
		return 0;
	} elsif ($height !~ /^\d+$/) {
		return 0;
	}
	if ($weight eq "") {
		return 0;
	} elsif ($weight !~ /^\d+$/) {
		return 0;
	}
	if ($age eq "") {
		return 0;
	} elsif ($age !~ /^\d+$/) {
		return 0;
	}
	if ($exercise eq "") {
		return 0;
	}
	if ($goal eq "") {
		return 0;
	}
	return 1;
}

sub create_account() {
	my $username = param('new_username');
	my $password = param('password1');
	my $fname = param('fname');
	my $lname = param('lname');
	my $email = param('email');
	my $gender = param('gender');
	my $height = param('height');
	my $weight = param('weight');
	my $age = param('age');
	my $exercise = param('exercise');
	my $goal = param('goal');
	$driver = "SQLite"; 
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
	$stmt = qq(insert into user values(null,'$fname','$lname','$username','$password', '$email', '$gender', $height, $weight, $age, '$exercise', '$goal')); 
	$rv = $dbh->do($stmt) or die $DBI::errstr; 
	$dbh->disconnect();
}

sub register_help() {
	my $new_username = param('new_username');
	my $password1 = param('password1');
	my $password2 = param('password2');
	my $fname = param('fname');
	my $lname = param('lname');
	my $email = param('email');
	my $gender = param('gender');
	my $height = param('height');
	my $weight = param('weight');
	my $age = param('age');
	my $exercise = param('exercise');
	my $goal = param('goal');
	$help .= qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<h1>Fill in your details</h1>  
	<h2><font color="red" size="2">&nbsp</font></h2>		
	<p><center><small><marquee></marquee></center></p></body>
	<form action="doyouevenfit.cgi" method="post">
	<pre> </pre>
	<p><center><h3 style="color:white;">Username</h3></center></p></body>
	<input type="text" name="new_username" value=");
	$help .= param('new_username');
	$help .= qq("size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($new_username eq "") {
		$help .= qq(<text style="color:white";> * a username must be entered<p></p>);
	} elsif (length($new_username) < 6) {
		$help .= qq(<text style="color:white";> * username must be at least 6 characters long<p></p>);
	}
	if ($new_username !~ /^[a-zA-Z0-9]+$/ && $new_username ne "") {
		$help .= qq(<text style="color:white";> * username must consist of alphanumeric characters only<p></p>);
	}
	$driver = "SQLite";
	$database = "project.db";
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr;
	$stmt = qq(select username from user where username = '$new_username');
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr;
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	$existing_username = $row[0];
	if ($new_username eq $existing_username && $new_username ne "") {
		$help .= qq(<text style="color:white";> * username already exists<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<p><center><h3 style="color:white;">Password</h3></center></p></body>
		<input type="password" name="password1" value=");
	$help .= param('password1');
	$help .= qq("size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($password1 eq "") {
		$help .= qq(<text style="color:white";> * a password must be entered<p></p>);
	} elsif (length($password1) < 6) {
		$help .= qq(<text style="color:white";> * password must be at least 6 characters long<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">Re-enter Password</h3></center></body>
		<input type="password" name="password2" value=");
	$help .= param('password2');
	$help .= qq("size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($password1 ne $password2) {
		$help .= qq(<text style="color:white";> * passwords do not match<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">First Name</h3></center></body>
		<input type="text" name="fname" value=");
	$help .= param('fname');
	$help .= qq("size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($fname eq "") {
		$help .= qq(<text style="color:white";> * a first name must be entered<p></p>);
	} elsif ($fname !~ /^[a-zA-Z-]*\n*$/) {
		$help .= qq(<text style="color:white";> * first name must consist of alphabetic characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">Last Name</h3></center></body>
		<input type="text" name="lname" value=");
	$help .= param('lname');
	$help .= qq("size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($lname eq "") {
		$help .= qq(<text style="color:white";> * a last name must be entered<p></p>);
	} elsif ($lname !~ /^[a-zA-Z-]*\n*$/) {
		$help .= qq(<text style="color:white";> * last name must consist of alphabetic characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">Email</h3></center></body>
		<input type="text" name="email" value=");
	$help .= param('email');
	$help .= qq("size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($email eq "") {
		$help .= qq(<text style="color:white";> * an email must be entered<p></p>);
	} elsif ($email !~ /^\w+\@\w+(\.\w+)+$/) {
		$help .= qq(<text style="color:white";> * invalid email address<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">Gender</h3></center></body>
		<select name="gender" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:47px;width:150px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
		<option);
	if ($gender eq "Male") {
		$help .= " selected";
	}
	$help .= qq(>Male
		<option);
	if ($gender eq "Female") {
		$help .= " selected";
	}
	$help .= qq(>Female
		</select><p></p>);
	if ($gender eq "") {
		$help .= qq(<text style="color:white";> * a gender must be selected<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">Height (cm)</h3></center></body>
		<input type="text" name="height" value=");
	$help .= param('height');
	$help .= qq("size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($height eq "") {
		$help .= qq(<text style="color:white";> * a height must be entered<p></p>);
	} elsif ($height !~ /^\d+$/) {
		$help .= qq(<text style="color:white";> * height must consist of numeric characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">Weight (kg)</h3></center></body>
		<input type="text" name="weight" value=");
	$help .= param('weight');
	$help .= qq("size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($weight eq "") {
		$help .= qq(<text style="color:white";> * a weight must be entered<p></p>);
	} elsif ($weight !~ /^\d+$/) {
		$help .= qq(<text style="color:white";> * weight must consist of numeric characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">Age</h3></center></body>
		<input type="text" name="age" value=");
	$help .= param('age');
	$help .= qq("size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($age eq "") {
		$help .= qq(<text style="color:white";> * an age must be entered<p></p>);
	} elsif ($age !~ /^\d+$/) {
		$help .= qq(<text style="color:white";> * age must consist of numeric characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">What is your level of exercise?</h3></center></body>
		<select name="exercise" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:116px;width:350px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
		<option);
	if ($exercise eq "Sedentary") {
		$help .= " selected";
	}
	$help .= qq(>Sedentary
		<option);
	if ($exercise eq "Lightly Active") {
		$help .= " selected";
	}
	$help .= qq(>Lightly Active
		<option);
	if ($exercise eq "Moderately Active") {
		$help .= " selected";
	}
	$help .= qq(>Moderately Active
		<option);
	if ($exercise eq "Very Active") {
		$help .= " selected";
	}
	$help .= qq(>Very Active
		<option);
	if ($exercise eq "Extremely Active") {
		$help .= " selected";
	}
	$help .= qq(>Extremely Active
		</select><p></p>);
	if ($exercise eq "") {
		$help .= qq(<text style="color:white";> * an exercise level must be selected<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">What is your goal?</h3></center></body>
		<select name="goal" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:116px;width:350px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
		<option);
	if ($goal eq "Extreme Weight Loss") {
		$help .= " selected";
	}
	$help .= qq(>Extreme Weight Loss
		<option);
	if ($goal eq "Weight Loss") {
		$help .= " selected";
	}
	$help .= qq(>Weight Loss
		<option);
	if ($goal eq "Maintain Weight") {
		$help .= " selected";
	}
	$help .= qq(>Maintain Weight
		<option);
	if ($goal eq "Weight Gain") {
		$help .= " selected";
	}
	$help .= qq(>Weight Gain
		<option);
	if ($goal eq "Extreme Weight Gain") {
		$help .= " selected";
	}
	$help .= qq(>Extreme Weight Gain
	</select><p></p>);
	if ($goal eq "") {
		$help .= qq(<text style="color:white";> * a weight goal must be selected<p></p>);
	}
	$help .= qq(<p>&nbsp</p>
		<pre>
		</pre>
		<input type="submit" name="create_account" value="CREATE ACCOUNT" class="button" style="height:45px;width:350px;"><br>
		<p>&nbsp</p>
		</form>
	);
	return $help;
}

sub registered(){
	return qq(
    	<div class="header-bottom" id="tour">
    	<div class="wrap">
    	<h1><span>D</span>o<span>Y</span>ou<span>E</span>ven<span>F</span>it</h1>
        <pre>
	</pre>
	<h2><font color="white" size="2">&nbsp</font></h2>		
	<p><center><font color="white"><small>Registration successful. You can now proceed to log in.</font></center></p></body>
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
	);
}

sub diet_screen() {
	$day = `date +%d`;
	chomp($day);
	$month = `date +%m`;
	chomp($month);
	$year = `date +%Y`;
	chomp($year);
	$date = "$day/$month/$year";
	$output .= qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<form action="doyouevenfit.cgi" method="post">
	<input type="hidden" name="page" value="">);
	if (defined param('date') && !valid_date()) {
		$output .= qq(<text style="color:white";> * invalid date (DD/MM/YYYY)<p></p>);
	}
	$output .= qq(<input type="text" name="date" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;width:200px;font-family:AmbleRegular;"value=");
	if (defined param('date')) {
		$date = param('date');
	}
	$output .= $date;
	$output .= qq(" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	$output .= qq(<input type="submit" name="change_date" value="" class="button" style="height:0px;width;0px;"><br>);
	$output .= qq(<p>&nbsp</p>
	<p>&nbsp</p>);
	if (!defined param('date') || (defined param('date') && valid_date())) {
		$output .= qq(<h1>);
		$output .= getCalories();
		$output .= qq(</h1> <p>&nbsp</p>
		<pre> </pre>
		<p>&nbsp</p>);
		my $username = param('username');
		$driver = "SQLite"; 
		$database = "project.db"; 
		$dsn = "DBI:$driver:dbname=$database";
		$userid = ""; $dbpassword = "";  
		$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
		$stmt = qq(select id from user where username = '$username'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		my $uid = $row[0]; 
		$stmt = qq(select id, name, calories from meal where uid = '$uid' and date = '$date'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		while (my @row = $sth->fetchrow_array()) {
			$output .= qq(<input type="submit" name="meal" value="$row[1] ($row[2] calories)" class="button" style="height:45px;width:600px;"><br> <pre> </pre>);
		}
		$output .= qq(<pre> </pre>);
		if (defined param('new_meal')) {
			$output .= 	qq(<input type="text" name="meal_name" minLength="1" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;width:300px;font-family:AmbleRegular;"value="New Meal" onfocus="javascript:if(this.value=='New Meal')this.value='';"><br>
			<pre> </pre>
			<input type="submit" name="add_meal" value="+ ADD MEAL" class="button" style="height:45px;width:200px;"><br>);
		} else {
			$output .= qq(<input type="submit" name="new_meal" value="NEW MEAL" class="button" style="height:45px;"><br>);
		}
	}
	$output .= hidden('username');
	$output .= hidden('password');
	$output .= qq(</form>
	</div>
	</div>
	);
	return $output;
}

sub add_food() {
	$meal_header = param('meal');
	#$meal_header =~ s/ \((\d+) calories\)$/<p>($1 calories)<\/p>/;
	my $output = qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<h3><text style="color:white";>$meal_header</h3>  
	<form action="doyouevenfit.cgi" method="post">
	<pre> </pre> <pre> </pre>
	<input type="submit" name="add_food" value="+ ADD FOOD" class="button" style="height:45px;width:350px;"><br>
	<p>&nbsp</p>);
	$output .= hidden('username');
	$output .= hidden('password');
	$output .= hidden('date');
	$output .= hidden('meal');
	$output.= qq(</form>);
	return $output;
}

sub getCalories() {
	$username = param('username');
	if (defined param('date')) {
		$date = param('date');
	}
	$driver = "SQLite"; 
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
	$stmt = qq(select id from user where username = '$username'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	$uid = $row[0];
	$stmt = qq(select current from calories where uid = '$uid' and date = '$date'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	$currentCal = $row[0];
	if ($currentCal eq "") {
		$currentCal = 0;
		$stmt = qq(select gender, height, weight, age, exercise, goal from user where username = '$username'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		$goalCal = calorie_calculator(@row);
		$stmt = qq(insert into calories values('$uid','$currentCal','$goalCal','$date'));
		$rv = $dbh->do($stmt) or die $DBI::errstr;
	} else {
		$stmt = qq(select goal from calories where uid = '$uid' and date = '$date'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		$goalCal = $row[0];
	}
	$counter = "$currentCal of $goalCal calories";
	return $counter;
}

sub valid_date() {
	my $date = param('date');
	if ($date eq "") {
		return 0;
	}
	if ($date =~ /^(\d{2})\/(\d{2})\/(\d{4})$/) {
		return check_date($3,$2,$1);
	} else {
		return 0;
	}
	return 1;
}

sub insert_meal() {
	my $username = param('username');
	my $date = param('date');
	my $meal_name = param('meal_name');
	$driver = "SQLite"; 
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
	$stmt = qq(select id from user where username = '$username'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	$uid = $row[0];
	$stmt = qq(insert into meal values(null,'$uid','$meal_name',0,'$date'));
	$rv = $dbh->do($stmt) or die $DBI::errstr;
}

sub calorie_calculator() {
	my ($gender, $height, $weight, $age, $exercise, $goal) = @_;	
	if ($gender eq 'Male') {
		$var = 5;
	} elsif ($gender eq 'Female') {
		$var = -161;
	}

	$BMR = 10*$weight + 6.25*$height + 5*$age + $var;	
	
	if ($exercise eq 'Sedentary') {
		$multiplier = 1.2;	
	} elsif ($exercise eq 'Lightly Active') {
		$multiplier = 1.375;
	} elsif ($exercise eq 'Moderately Active') {
		$multiplier = 1.55;
	} elsif ($exercise eq 'Very Active') {
		$multiplier = 1.725;
	} elsif ($exercise eq 'Extremely Active') {
		$multiplier = 1.9;
	}	

	$calories = $BMR*$multiplier;

	if ($goal eq 'Extreme Weight Loss') {
		$calories *= 0.6;
		$minCalories = 17.6*$weight;	
		if ($calories lt $minCalories) {
			$calories = $minCalories;		
		}
	} elsif ($goal eq 'Weight Loss') {
		$calories *= 0.8;	
	} elsif ($goal eq 'Weight Gain') {
		$calories *= 1.2;
	} elsif ($goal eq 'Extreme Weight Gain') {
		$calories *= 1.4;
	}

	return int($calories+0.5);
}

sub extractInfo () {
	#if the search bar param is checked then this function is called.
	#the search bar is search of Food and amount in grams 
	#the results will add the food to the DB
	
	
	my %info = nutriInfo(param(Search), param(amount of food));
	my @infoNeeded = ("Energy", "Water", "Protein", "Total lipid", "Carbohydrate, by difference", "Fiber, total dietary", "Sugars, total", 			"Calcium", "Iron", "Magnesium", "Phosphorus", "Potassium", "Zinc", "Vitamin C", "Thiamin", "Riboflavin", "Niacin", "Vitamin B-6", 			"Folate", 	"Vitamin E", "Vitamin K");	
	my @keys = keys %info;

	my %diff;

	@diff{ @keys } = undef;
	delete @diff{ @infoNeeded };

	my @keys2 = keys %diff;
	
	my $driver = "SQLite"; 
	my $database = "project.db"; 
	my $dsn = "DBI:$driver:dbname=$database";
	my $userid = ""; my $dbpassword = "";  
	my $dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
	my $stmt = qq(insert into food values(null,'$keys2[0]','$infoNeeded[0]', '$infoNeeded[1]', '$infoNeeded[2]', '$infoNeeded[3]', '$infoNeeded[4]', '$infoNeeded[5]', '$infoNeeded[6]')); 
	my $rv = $dbh->do($stmt) or die $DBI::errstr; 
	
	#Still gotta figure out how to add them
	$stmt = qq(insert into minarels values(null,'$keys2[0]','$infoNeeded[0]', '$infoNeeded[1]', '$infoNeeded[2]', '$infoNeeded[3]', '$infoNeeded[4]', '$infoNeeded[5]', '$infoNeeded[6]')); 
	$rv = $dbh->do($stmt) or die $DBI::errstr; 
	
	$stmt = qq(insert into vitamins values(null,'$keys2[0]','$infoNeeded[0]', '$infoNeeded[1]', '$infoNeeded[2]', '$infoNeeded[3]', '$infoNeeded[4]', '$infoNeeded[5]', '$infoNeeded[6]')); 
	$rv = $dbh->do($stmt) or die $DBI::errstr; 

	$dbh->disconnect();

}

sub nutriInfo(){
	my $mech = WWW::Mechanize->new;
	
	my @input = @_;
	print "@input\n";
	my $search = $input[0];
	#print "$search\n";
	$mech->get('http://ndb.nal.usda.gov/ndb/foods');
	$mech->submit_form(
			form_name => 'quickform', 
			fields => {'qlookup' => $search,},);

	my $content = $mech->content;
	
	my @matches = ($content =~ m/<a href=.*?Click to view reports for this food\">\D+[0-9]*\D*?<\/a>/gi);
	my %food_urls;
	my $food;
	my $url;
	my $match;
	foreach $match (@matches){
		$match =~ m/Click to view reports for this food\">(\D+[0-9]*\D*?)<\/a>/;
		$food = $1;
		$match =~ m/<a href=\"(.*?)\"/;
		$url = $1;	
		$food_urls{$food} = $url;
		#print "$food ($url)\n";
	}
	
	#my $userSelection = "BURGER KING, WHOPPER, with cheese";
	my @foods = keys %food_urls;
	my $userSelection = $foods[0];
	my $user_url = $food_urls{$userSelection};
	$mech->get("http\:\/\/ndb\.nal\.usda\.gov$user_url");
	
	$content = $mech->content;

	my $oneServing;
	$content =~ m/item\n.*?<br\/>(.*)/;
	$oneServing = $1;
	$oneServing =~ s/g//;
	print "One Serving $oneServing\n";

	my $userServing = $oneServing;

	if($input[1]=~ m/\d/){
		$userServing = $input[1];
	}

	print "User Serving $userServing\n";
	my %nutritionalInfo;
	$nutritionalInfo{$userSelection} = $oneServing;
	my @infoNeeded = ("Energy", "Water", "Protein", "Total lipid", "Carbohydrate, by difference", "Fiber, total dietary", "Sugars, total", 			"Calcium", "Iron", "Magnesium", "Phosphorus", "Potassium", "Zinc", "Vitamin C", "Thiamin", "Riboflavin", "Niacin", "Vitamin B-6", 			"Folate", 	"Vitamin E", "Vitamin K");
	#my @values;
	
	my $serving;

	foreach my $info (@infoNeeded){
		#@values = ();
		#$content =~ m/$info.*\n.*\n.*\n.*?<\/td>.*\n.*?<td.*?<\/td>\n.*?<td.*?>(.*?)<\/td>/;
		#push @values, $1;
		if($content =~ m/$info.*\n.*\n.*\n.*?<\/td>.*\n.*?<td.*?<\/td>\n.*?<td.*?>.*?<\/td>\n.*\n.*\n.*\n.*<td.*?>(.*?)<\/td>/){
		#push @values, $1;
		#$nutritionalInfo{$info} = \@values;		
			$serving = $1;
			$nutritionalInfo{$info} = ($userServing*$serving)/$oneServing;
			#print "$nutritionalInfo{$info}\n";
		}
	}

	return %nutritionalInfo;
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
