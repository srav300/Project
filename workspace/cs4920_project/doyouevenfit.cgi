#!/usr/bin/perl -w

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
use Date::Calc qw/check_date/;
#use WWW::Mechanize;
warningsToBrowser(1);

use DBI;

$bg_handler = "2";

print page_header();

if (defined param('register')) {
	print register_screen();
    $bg_handler = 2;
} elsif (defined param('create_account')) {
	if (check_register()) {
		create_account();
		print login_screen();
        $bg_handler = 3;
	} else {
		print register_help();
        $bg_handler = 3;
	}
} elsif (defined param('username') && defined param('password') ) {
    $bg_handler = 2;
	if (check_login()) {
		if (defined param('add_food_search')) {
			if (defined param('food_selected')) {
				if (check_serving()) {
					insert_food();
					print show_meal();
				} else {
					print add_food_screen();
				}
			} else {
				print add_food_screen();
			}
		} elsif (defined param('search_food')) {
			print add_food_screen();
		} elsif (defined param('back_meal')){
			print show_meal();
		} elsif (defined param('delete_meal')) {
			delete_meal();
			print diet_screen();
		} elsif (defined param('delete_food')) {
			delete_food();
			print show_meal();
		} elsif (defined param('back_diet')) {
			print diet_screen();
		} elsif (defined param('add_to_meal')) {
			if (check_food()) {
				insert_food_man();
				print show_meal();
			} else {
				print food_help();
			}
		} elsif (defined param('add_food_man')) {
			print add_food_man();
		} elsif (defined param('add_food')) {
			print add_food_screen();
		} elsif (defined param('food')) {
			print show_food();
		} elsif (defined param('meal')) {
			print show_meal();
		} elsif (defined param('add_meal') && param('meal_name') ne "") {
			insert_meal();
			print diet_screen();
		} elsif (defined param('login') || defined param('home')) {
			print home();
		} elsif (defined param('diet')) {
			print diet_screen();
		} elsif (defined param('exercise')) {
			print exercise_screen();
		} elsif (defined param('date')) {
			print diet_screen();
		}
	} else {
		print login_screen();
        $bg_handler = "3"	
	}
} else {
	print login_screen();
    $bg_handler = 3;
}
print page_css();
print page_footer();

sub page_header {
	return header,
	start_html("-title"=>"DoYouEvenFit"),
}

sub page_css {
	$css = qq(
	<link href="css/style.css" rel="stylesheet" type="text/css" media="all" />
	<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	);

    if ($bg_handler eq 0) {
        
    } if ($bg_handler eq 1) {
        $css .= qq(<body background="images/wood.jpg">);
    } if ($bg_handler eq 2) {
        $css .= qq(<body background="images/green.jpg">);
    } if ($bg_handler eq 3) {
 		$css .= qq(<body background="images/banner.jpg">);
    }       
	$css .= qq(<body link="white">);
	return $css;
}

sub login_screen(){
	my $html = qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<h1><span>D</span>o<span>Y</span>ou<span>E</span>ven<span>F</span>it</h1>  
	<pre>
	</pre>
	<h2><font color="red" size="2">&nbsp</font></h2>);
	if (defined param('username') && defined param('password') && !check_login()) {	# if user has failed to log in notify them	
		$html .= qq(<h2><font color="red" size="2">Your login details seem to be incorrect.</font></h2>	);
	} elsif (defined param('create_account')) {	# if user has successfully created an account notify them
		$html .= qq(<h2><font color="white" size="2">Registration successful. You can now proceed to log in.</font></h2>	);
	} else {
		$html .= qq(<h2><font color="red" size="2">&nbsp;</font></h2>);
	}
	$html .= qq(<form action="doyouevenfit.cgi" method="post">
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
	);
	return $html;
}

sub home() {
	my $html = qq(
    <div class="header-bottom" id="tour">
	<div class="wrap">
	<pre> </pre>
	<form action="doyouevenfit.cgi" method="post">
	<input type="hidden" name="page" value="">
	<pre> </pre>
	<input type="submit" name="diet" value="DIET" class="button" style="height:45px;">&nbsp;
	<input type="submit" name="exercise" value="EXERCISE" class="button" style="height:45px;">
    <p>&nbsp</p>;
    <input type="submit" name="update" value="UPDATE PROFILE" class="button" style="height:45px;width:350px;">
    <p>&nbsp</p>;
    <a href="logout.cgi" class="button" role="button" style="height:27px;">LOG OUT</a><br>
	<p>&nbsp</p>);
	$html .= hidden('username');
	$html .= hidden('password');
	$html .= qq(</form>
	</div>
	</div>);
}

sub check_login() {	# checks to see if username and password are correct
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
        if (@row) {
	        $password = $row[0];
        } else {
            $password = "++";
        }	
    if ($password_attempt eq $password) {
		return 1;
	}
	return 0;
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

sub check_register() {	# checks to see if details entered are correct and adhere to database types
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
        if (@row) {
	        $existing_username = $row[0];
        } else {
            $existing_username = "++";
        }	
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

sub create_account() {	# inserts user and details into database
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

sub register_help() {	# notifies user of details entered incorrectly
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
	<input type="text" name="new_username" value="$new_username"size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
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
        if (@row) {
	        $existing_username = $row[0];
        } else {
            $existing_username = "++";
        }	
    	if ($new_username eq $existing_username) {
		return 0;
	}

	if ($new_username eq $existing_username && $new_username ne "") {
		$help .= qq(<text style="color:white";> * username already exists<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<p><center><h3 style="color:white;">Password</h3></center></p></body>
		<input type="password" name="password1" value="$password1"size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($password1 eq "") {
		$help .= qq(<text style="color:white";> * a password must be entered<p></p>);
	} elsif (length($password1) < 6) {
		$help .= qq(<text style="color:white";> * password must be at least 6 characters long<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">Re-enter Password</h3></center></body>
		<input type="password" name="password2" value="$password2"size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($password1 ne $password2) {
		$help .= qq(<text style="color:white";> * passwords do not match<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">First Name</h3></center></body>
		<input type="text" name="fname" value="$fname"size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($fname eq "") {
		$help .= qq(<text style="color:white";> * a first name must be entered<p></p>);
	} elsif ($fname !~ /^[a-zA-Z-]*\n*$/) {
		$help .= qq(<text style="color:white";> * first name must consist of alphabetic characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">Last Name</h3></center></body>
		<input type="text" name="lname" value="$lname"size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($lname eq "") {
		$help .= qq(<text style="color:white";> * a last name must be entered<p></p>);
	} elsif ($lname !~ /^[a-zA-Z-]*\n*$/) {
		$help .= qq(<text style="color:white";> * last name must consist of alphabetic characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">Email</h3></center></body>
		<input type="text" name="email" value="$email"size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
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
		<input type="text" name="height" value="$height"size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($height eq "") {
		$help .= qq(<text style="color:white";> * a height must be entered<p></p>);
	} elsif ($height !~ /^\d+$/) {
		$help .= qq(<text style="color:white";> * height must consist of numeric characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">Weight (kg)</h3></center></body>
		<input type="text" name="weight" value="$weight"size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($weight eq "") {
		$help .= qq(<text style="color:white";> * a weight must be entered<p></p>);
	} elsif ($weight !~ /^\d+$/) {
		$help .= qq(<text style="color:white";> * weight must consist of numeric characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
		<center><h3 style="color:white;">Age</h3></center></body>
		<input type="text" name="age" value="$age"size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
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


sub diet_screen() {	# displays current calories out of goal calories and a list of meals for date selected
	$day = `date +%d`;
	chomp($day);
	$month = `date +%m`;
	chomp($month);
	$year = `date +%Y`;
	chomp($year);
	$date = "$day/$month/$year";	# display current date if date is not already defined
	if (defined param('date')) {
		$date = param('date');
	}
	$output .= qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<form action="doyouevenfit.cgi" method="post">
	<input type="hidden" name="page" value="">);
	if (defined param('date') && !valid_date()) {	# notify user if they have entered an invalid date
		$output .= qq(<text style="color:white";> * invalid date (DD/MM/YYYY)<p></p>);
	}
	$output .= qq(<input type="text" name="date" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;width:200px;font-family:AmbleRegular;"value="$date" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	$output .= qq(<input type="submit" name="change_date" value="" class="button" style="height:0px;width;0px;"><br>);
	$output .= qq(<p>&nbsp</p>
	<p>&nbsp</p>);
	if (!defined param('date') || (defined param('date') && valid_date())) {	# if valid date display calorie counter and meals
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
			$output .= 	qq(<input type="text" name="meal_name" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;width:300px;font-family:AmbleRegular;"value="New Meal" onfocus="javascript:if(this.value=='New Meal')this.value='';"><br>
			<pre> </pre>
			<input type="submit" name="add_meal" value="+ ADD MEAL" class="button" style="height:45px;width:200px;"><br>);
		} else {
			$output .= qq(<input type="submit" name="new_meal" value="NEW MEAL" class="button" style="height:45px;"><br>);
		}
	}
	$output .= qq(<pre> </pre> <pre> </pre>
	<input type="submit" name="home" value="HOME" class="button" style="height:45px;"><br>);
	$output .= hidden('username');
	$output .= hidden('password');
	$output .= qq(</form>
	</div>
	</div>
	);
	return $output;
}

sub show_meal() {	# displayed if user selects a meal from diet screen
	my $username = param('username');
	my $date = param('date');
	my $meal = param('meal');
	$meal =~ s/ \(\d+ calories\)$//;
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
	$stmt = qq(select id, calories from meal where uid = '$uid' and name = '$meal' and date = '$date'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $mid = $row[0];
	my $calories = $row[1];
	my $output = qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<h1>$meal ($calories calories)</h1>  
	<form action="doyouevenfit.cgi" method="post">
	<pre> </pre>);
	$stmt = qq(select fid, serving from meal_contains where mid = '$mid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	$i = 0;
	my @fid;
	my @serving;
	while (my @row = $sth->fetchrow_array()) {
		$fid[$i] = $row[0];
		$serving[$i] = $row[1];
		$i++;
	}
	$j = 0;
	while ($j < $i) {	# display all food linked to this meal
		$stmt = qq(select name, calories, protein, carbs, fat from food where id = '$fid[$j]'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		my @info = $sth->fetchrow_array();
		my $name = $info[0];
		my $calories = int(($info[1] * $serving[$j] / 100) + 0.5);
		my $protein = $info[2] * $serving[$j] / 100;
		my $carbs = $info[3] * $serving[$j] / 100;
		my $fat = $info[4] * $serving[$j] / 100;
		#$output .= qq(<text style="color:white";>$serving[$j] g of $name ($calories calories, $protein g of protein, $carbs g of carbs, $fat g of fat)<p></p>);
		$output .= qq(<input type="submit" name="food" value="$name ($calories calories)" class="button" style="font-size:16pt;height:45px;width:750px;"><br>
	<pre> </pre>);
		$j++;
	}
	$output .= qq(<pre> </pre> <pre> </pre>
	<input type="submit" name="add_food" value="+ ADD FOOD" class="button" style="height:45px;width:250px;"><br>
	<pre> </pre> <pre> </pre>
	<input type="submit" name="delete_meal" value="DELETE MEAL" class="button" style="height:45px;width:250px;"><br>
	<pre> </pre> <pre> </pre>
	<input type="submit" name="back_diet" value="BACK" class="button" style="height:45px;width:250px;"><br>
	<p>&nbsp</p>);
	$output .= hidden('username');
	$output .= hidden('password');
	$output .= hidden('date');
	$output .= hidden('meal');
	$output.= qq(</form>);
	return $output;
}

sub show_food() {	# displayed if user selects food from show meal
	my $username = param('username');
	my $date = param('date');
	my $meal = param('meal');
	$meal =~ s/ \(\d+ calories\)$//;
	my $food = param('food');
	$food =~ s/ \((\d+) calories\)$//;
	my $calories = $1;
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
	my @row = $sth->fetchrow_array();
	my $uid = $row[0];
	$stmt = qq(select id from meal where uid = '$uid' and name = '$meal' and date = '$date'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $mid = $row[0];
	$stmt = qq(select fid, serving from meal_contains where mid = '$mid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	my $fid;
	my $serving;
	while (my @row = $sth->fetchrow_array()) {	# making sure food with proper serving size is selected (accounting for duplicates)
		$serving = $row[1];	
		$stmt = qq(select calories from food where id = $row[0]);
		$hts = $dbh->prepare($stmt);
		$rv = $hts->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@wor = $hts->fetchrow_array();
		if ($calories == int(($wor[0] * $serving / 100) + 0.5)) {
			$fid = $row[0];
			last;
		}
	}
	my $output = qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<h3> <text style="color:white";>$food ($calories calories)</h3>  
	<form action="doyouevenfit.cgi" method="post">
	<pre> </pre>);
	$stmt = qq(select protein, carbs, fat from food where id = '$fid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	my @row = $sth->fetchrow_array();
	my $protein = $row[0] * $serving / 100;
	my $carbs = $row[1] * $serving / 100;
	my $fat = $row[2] * $serving / 100;
	$output .= qq(<text style="color:white;font-size:20pt">Serving: $serving g
		<p>
		Protein: $protein g
		<p>
		Carbs: $carbs g
		<p>
		Fat: $fat g</text>
		<p></p>);
	$output .= qq(<pre> </pre>
	<input type="submit" name="delete_food" value="DELETE FOOD" class="button" style="height:45px;width:250px;"><br>
	<pre> </pre>
	<input type="submit" name="back_meal" value="BACK" class="button" style="height:45px;width:250px;"><br>
	<p>&nbsp</p>);
	$output .= hidden('username');
	$output .= hidden('password');
	$output .= hidden('date');
	$output .= hidden('meal');
	$output .= hidden('food');
	$output .= qq(</form>);
	return $output;
}

sub delete_meal() {	# deletes meal and any relations from database and also updates daily calorie counter
	my $username = param('username');
	my $meal = param('meal');
	my $date = param('date');
	$meal =~ s/ \((\d+) calories\)$//;
	my $serving = param('serving');
$stmt = qq(select id from user where username = '$username'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $uid = $row[0];
	$stmt = qq(select id, calories from meal where uid = '$uid' and name = '$meal' and date = '$date'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $mid = $row[0];
	my $calories = $row[1];
	$stmt = qq(select current from calories where uid = '$uid' and date = '$date'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $updated = int(($row[0] - $calories) + 0.5);
	$stmt = qq(update calories set current = $updated where uid = '$uid' and date = '$date');
	$rv = $dbh->do($stmt) or die $DBI::errstr;
	if ($rv < 0) {
		print $DBI::errstr;
	}
	$stmt = qq(delete from meal where id = $mid);
	$rv = $dbh->do($stmt) or die $DBI::errstr;
	if ($rv < 0) {
		print $DBI::errstr;
	}
	$stmt = qq(delete from meal_contains where mid = $mid);
	$rv = $dbh->do($stmt) or die $DBI::errstr;
	if ($rv < 0) {
		print $DBI::errstr;
	}
}

sub delete_food() {	# deletes table relating food to meal from database and updates meal calories and daily calorie counter
	my $username = param('username');
	my $date = param('date');
	my $meal = param('meal');
	$meal =~ s/ \(\d+ calories\)$//;
	my $food = param('food');
	$food =~ s/ \((\d+) calories\)$//;
	my $calories = $1;
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
	my @row = $sth->fetchrow_array();
	my $uid = $row[0];
	$stmt = qq(select id, calories from meal where uid = '$uid' and name = '$meal' and date = '$date'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $mid = $row[0];
	my $mcalories = $row[1];
	$stmt = qq(select fid, serving from meal_contains where mid = '$mid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	my $fid;
	my $serving;
	while (my @row = $sth->fetchrow_array()) {
		$serving = $row[1];	
		$stmt = qq(select calories from food where id = $row[0]);
		$hts = $dbh->prepare($stmt);
		$rv = $hts->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@wor = $hts->fetchrow_array();
		if ($calories == int(($wor[0] * $serving / 100) + 0.5)) {
			$fid = $row[0];
			last;
		}
	}
	$stmt = qq(delete from meal_contains where fid = '$fid' and mid = '$mid');
	$rv = $dbh->do($stmt) or die $DBI::errstr;
	if ($rv < 0) {
		print $DBI::errstr;
	}
	my $updated = int(($mcalories - $calories) + 0.5);
	$stmt = qq(update meal set calories = $updated where id = '$mid');
	$rv = $dbh->do($stmt) or die $DBI::errstr;
	if ($rv < 0) {
		print $DBI::errstr;
	}
	$stmt = qq(select current from calories where uid = '$uid' and date = '$date'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $dcalories = $row[0];
	$updated = int(($dcalories - $calories) + 0.5);
	$stmt = qq(update calories set current = $updated where uid = '$uid' and date = '$date');
	$rv = $dbh->do($stmt) or die $DBI::errstr;
	if ($rv < 0) {
		print $DBI::errstr;
	}
}

sub add_food_screen() {	# page for user to search for food to add or proceed to add food manually
	my $meal_name = param('meal');
	my $search_term = param('search_term');
	my $serving = param('serving');	
	$meal_name =~ s/ \(\d+ calories\)$//;
	my $output = qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<h3><text style="color:white";>Adding food to $meal_name</h3>  
	<form action="doyouevenfit.cgi" method="post">
	<pre> </pre> <pre> </pre>
	<input type="text" name="search_term" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;width:300px;font-family:AmbleRegular;"value="$search_term" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre>
	<input type="submit" name="search_food" value="SEARCH FOOD" class="button" style="height:45px;width:350px;"><br>
	<pre> </pre> <pre> </pre>);
	if(defined param('search_term')){	# if a user has searched display the food suggestions
		$output .= food_suggestions();
	}
	if (defined param('add_food_search') && $serving eq "") {	# if a user has attempted to add food without specifying a serving size notify them
		$output .= qq(<text style="color:white";> * a serving size must be entered for this food item<p></p>);
	} elsif (defined param('add_food_search') && $serving !~ /\d+/) {	# if entered incorrectly notify user that serving size must be a number
		$output .= qq(<text style="color:white";> * a serving size must consist of numeric characters only<p></p>);
	}
	$output .= qq(<pre> </pre> <pre> </pre>
	<input type="submit" name="add_food_man" value="MANUAL ENTRY" class="button" style="height:45px;width:350px;"><br>
	<pre> </pre> <pre> </pre>
	<input type="submit" name="back_meal" value="BACK" class="button" style="height:45px;width:350px;"><br>
	<p>&nbsp</p>
);
	$output .= hidden('username');
	$output .= hidden('password');
	$output .= hidden('date');
	$output .= hidden('meal');
	$output.= qq(</form>);
	return $output;	
}

sub add_food_man() {	# page for user to manual add food to meal
	my $output = qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<h1>Enter nutritional information</h1>  
	<h2><font color="red" size="2">&nbsp</font></h2>		
	<p><center><small><marquee></marquee></center></p></body>
	<form action="doyouevenfit.cgi" method="post">
	<pre> </pre>
	<p><center><h3 style="color:white;">Name</h3></center></p></body>
	<input type="text" name="name" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Serving Size (g)</h3></center></body>
	<input type="text" name="serving" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Calories per 100g</h3></center></body>
	<input type="text" name="calories" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Protein (g) per 100g</h3></center></body>
	<input type="text" name="protein" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Carbohydrates (g) per 100g</h3></center></body>
	<input type="text" name="carbs" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Fat (g) per 100g</h3></center></body>
	<input type="text" name="fat" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre> <pre> </pre>);
	#<center><h3 style="color:white;">Fibre (g) per 100g (optional)</h3></center></body>
	#<input type="text" name="fibre" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	#<pre> </pre> <pre> </pre>
	#<center><h3 style="color:white;">Sugars (g) per 100g (optional)</h3></center></body>
	#<input type="text" name="sugars" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	#<pre> </pre> <pre> </pre>
	#<center><h3 style="color:white;">Monounsaturated fat (g) per 100g (optional)</h3></center></body>
	#<input type="text" name="mono" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	#<pre> </pre> <pre> </pre>
	#<center><h3 style="color:white;">Polyunsaturated fat (g) per 100g (optional)</h3></center></body>
	#<input type="text" name="poly" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	#<pre> </pre> <pre> </pre>
	#<center><h3 style="color:white;">Saturated fat (g) per 100g (optional)</h3></center></body>
	#<input type="text" name="sat" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	#<pre> </pre> <pre> </pre>
	#<center><h3 style="color:white;">Trans fat (g) per 100g (optional)</h3></center></body>
	#<input type="text" name="trans" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	#<pre> </pre> <pre> </pre>
	#<center><h3 style="color:white;">Cholesterol (mg) per 100g (optional)</h3></center></body>
	#<input type="text" name="cholesterol" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	#<pre> </pre> <pre> </pre>
	$output .= qq(<input type="submit" name="add_to_meal" value="ADD TO MEAL" class="button" style="height:45px;width:350px;"><br>
	<p>&nbsp</p>);
	$output .= hidden('username');
	$output .= hidden('password');
	$output .= hidden('date');
	$output .= hidden('meal');
	$output .= qq(</form>);
	return $output;
}

sub check_food() {	# checks that food details manually entered are correct
	my $name = param('name');
	my $serving = param('serving');
	my $calories = param('calories');
	my $protein = param('protein');
	my $carbs = param('carbs');
	my $fat = param('fat');
	#my $fibre = param('fibre');
	#my $sugars = param('sugars');
	#my $mono = param('mono');
	#my $poly = param('poly');
	#my $sat = param('sat');
	#my $trans = param('trans');
	#my $cholesterol = param('cholesterol');
	if ($name eq "") {
		return 0;
	}
	if ($serving eq "") {
		return 0;
	} elsif ($serving !~ /^\d+(\.\d)?$/) {
		return 0;
	}
	if ($calories eq "") {
		return 0;
	} elsif ($calories !~ /^\d+(\.\d)?$/) {
		return 0;
	}
	if ($protein eq "") {
		return 0;
	} elsif ($protein !~ /^\d+(\.\d)?$/) {
		return 0;
	}
	if ($carbs eq "") {
		return 0;
	} elsif ($carbs !~ /^\d+(\.\d)?$/) {
		return 0;
	}
	if ($fat eq "") {
		return 0;
	} elsif ($fat !~ /^\d+(\.\d)?$/) {
		return 0;
	}
	#if ($fibre !~ /^\d*$/) {
	#	return 0;
	#}
	#if ($sugars !~ /^\d*$/) {
	#	return 0;
	#}
	#if ($mono !~ /^\d*$/) {
	#	return 0;
	#}
	#if ($poly !~ /^\d*$/) {
	#	return 0;
	#}
	#if ($sat !~ /^\d*$/) {
	#	return 0;
	#}
	#if ($trans !~ /^\d*$/) {
	#	return 0;
	#}
	#if ($cholesterol !~ /^\d*$/) {
	#	return 0;
	#}
	return 1;
}

sub food_help() {	# notifies user of fields that are incorrect
	my $name = param('name');
	my $serving = param('serving');
	my $calories = param('calories');
	my $protein = param('protein');
	my $carbs = param('carbs');
	my $fat = param('fat');
	#my $fibre = param('fibre');
	#my $sugars = param('sugars');
	#my $mono = param('mono');
	#my $poly = param('poly');
	#my $sat = param('sat');
	#my $trans = param('trans');
	#my $cholesterol = param('cholesterol');
	my $help = qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<h1>Enter nutritional information</h1>  
	<h2><font color="red" size="2">&nbsp</font></h2>		
	<p><center><small><marquee></marquee></center></p></body>
	<form action="doyouevenfit.cgi" method="post">
	<pre> </pre>
	<p><center><h3 style="color:white;">Name</h3></center></p></body>
	<input type="text" name="name" value="$name" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($name eq "") {
		$help .= qq(<text style="color:white";> * a name must be entered<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Serving Size (g)</h3></center></body>
	<input type="text" name="serving" value="$serving" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($serving eq "") {
		$help .= qq(<text style="color:white";> * a serving must be entered<p></p>);
	} elsif ($serving !~ /^\d+(\.\d)?$/) {
		$help .= qq(<text style="color:white";> * serving must consist of numeric characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Calories per 100g</h3></center></body>
	<input type="text" name="calories" value="$calories" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($calories eq "") {
		$help .= qq(<text style="color:white";> * calories must be entered<p></p>);
	} elsif ($calories !~ /^\d+(\.\d)?$/) {
		$help .= qq(<text style="color:white";> * calories must consist of numeric characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Protein (g) per 100g</h3></center></body>
	<input type="text" name="protein" value="$protein" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($protein eq "") {
		$help .= qq(<text style="color:white";> * protein must be entered<p></p>);
	} elsif ($protein !~ /^\d+(\.\d)?$/) {
		$help .= qq(<text style="color:white";> * protein must consist of numeric characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Carbohydrates (g) per 100g</h3></center></body>
	<input type="text" name="carbs" value="$carbs" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($carbs eq "") {
		$help .= qq(<text style="color:white";> * carbohydrates must be entered<p></p>);
	} elsif ($carbs !~ /^\d+(\.\d)?$/) {
		$help .= qq(<text style="color:white";> * carbohydrates must consist of numeric characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Fat (g) per 100g</h3></center></body>
	<input type="text" name="fat" value="$fat" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if ($fat eq "") {
		$help .= qq(<text style="color:white";> * fat must be entered<p></p>);
	} elsif ($fat !~ /^\d+(\.\d)?$/) {
		$help .= qq(<text style="color:white";> * fat must consist of numeric characters only<p></p>);
	}
	$help .= qq(<pre> </pre> <pre> </pre>);
	#<center><h3 style="color:white;">Fibre (g) per 100g (optional)</h3></center></body>
	#<input type="text" name="fibre" value="$fibre" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	#if ($fibre !~ /^\d*$/) {
	#	$help .= qq(<text style="color:white";> * fibre must consist of numeric characters only<p></p>);
	#}
	#$help .= qq(<pre> </pre> <pre> </pre>
	#<center><h3 style="color:white;">Sugars (g) per 100g (optional)</h3></center></body>
	#<input type="text" name="sugars" value="$sugars" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	#if ($sugars !~ /^\d*$/) {
	#	$help .= qq(<text style="color:white";> * sugars must consist of numeric characters only<p></p>);
	#}
	#$help .= qq(<pre> </pre> <pre> </pre>
	#<center><h3 style="color:white;">Monounsaturated fat (g) per 100g (optional)</h3></center></body>
	#<input type="text" name="mono" value="$mono" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	#if ($mono !~ /^\d*$/) {
	#	$help .= qq(<text style="color:white";> * monounsaturated fat must consist of numeric characters only<p></p>);
	#}
	#$help .= qq(<pre> </pre> <pre> </pre>
	#<center><h3 style="color:white;">Polyunsaturated fat (g) per 100g (optional)</h3></center></body>
	#<input type="text" name="poly" value="$poly" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	#if ($poly !~ /^\d*$/) {
	#	$help .= qq(<text style="color:white";> * polyunsaturated fat must consist of numeric characters only<p></p>);
	#}
	#$help .= qq(<pre> </pre> <pre> </pre>
	#<center><h3 style="color:white;">Saturated fat (g) per 100g (optional)</h3></center></body>
	#<input type="text" name="sat" value="$sat" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	#if ($sat !~ /^\d*$/) {
	#	$help .= qq(<text style="color:white";> * saturated fat must consist of numeric characters only<p></p>);
	#}
	#$help .= qq(<pre> </pre> <pre> </pre>
	#<center><h3 style="color:white;">Trans fat (g) per 100g (optional)</h3></center></body>
	#<input type="text" name="trans" value="$trans" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	#if ($trans !~ /^\d*$/) {
	#	$help .= qq(<text style="color:white";> * trans fat must consist of numeric characters only<p></p>);
	#}
	#$help .= qq(<pre> </pre> <pre> </pre>
	#<center><h3 style="color:white;">Cholesterol (mg) per 100g (optional)</h3></center></body>
	#<input type="text" name="cholesterol" value="$cholesterol" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	#if ($cholesterol !~ /^\d*$/) {
	#	$help .= qq(<text style="color:white";> * cholesterol must consist of numeric characters only<p></p>);
	#}
	#$help .= qq(<pre> </pre> <pre> </pre>
	$help .= qq(<input type="submit" name="add_to_meal" value="ADD TO MEAL" class="button" style="height:45px;width:350px;"><br>
	<p>&nbsp</p>);
	$help .= hidden('username');
	$help .= hidden('password');
	$help .= hidden('date');
	$help .= hidden('meal');
	$help .= qq(</form>);
	return $help;
}

sub insert_food_man() {	# inserts manually entered food into the database
	my $name = param('name');
	my $serving = param('serving');
	my $calories = param('calories');
	my $protein = param('protein');
	my $carbs = param('carbs');
	my $fat = param('fat');
	my $fibre = param('fibre');
	my $sugars = param('sugars');
	my $mono = param('mono');
	my $poly = param('poly');
	my $sat = param('sat');
	my $trans = param('trans');
	my $cholesterol = param('cholesterol');
	my $meal = param('meal');
	my $date = param('date');
	$meal =~ s/ \((\d+) calories\)$//;
	$driver = "SQLite"; 
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
	$stmt = qq(insert into food(id,name,calories,protein,carbs,fat,fibre,sugars,monounsatfat,polyunsatfat,satfat,transfat,cholesterol) values(null,'$name','$calories',$protein,'$carbs','$fat','$fibre','$sugars','$mono','$poly','$sat','$trans','$cholesterol'));
	$rv = $dbh->do($stmt) or die $DBI::errstr;
	$stmt = qq(select id from user where username = '$username'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $uid = $row[0];
	$stmt = qq(select id, calories from meal where uid = '$uid' and name = '$meal' and date = '$date'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $mid = $row[0];
	my $updated = int(($row[1] + $calories * $serving / 100) + 0.5); 
	$stmt = qq(select id from food where name = '$name' and calories = '$calories' and protein = '$protein' and carbs = '$carbs' and fat = '$fat'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	$fid = $row[0];
	$stmt = qq(insert into meal_contains(mid,fid,serving) values('$mid','$fid','$serving'));
	$rv = $dbh->do($stmt) or die $DBI::errstr;
	$stmt = qq(update meal set calories = $updated where id = '$mid');
	$rv = $dbh->do($stmt) or die $DBI::errstr;
	if ($rv < 0) {
		print $DBI::errstr;
	}
	$stmt = qq(select current from calories where uid = '$uid' and date = '$date'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	$updated = int(($row[0] + $calories * $serving / 100) + 0.5);
	$stmt = qq(update calories set current = $updated where uid = '$uid' and date = '$date');
	$rv = $dbh->do($stmt) or die $DBI::errstr;
	if ($rv < 0) {
		print $DBI::errstr;
	}
}

sub getCalories() {	# returns the calorie counter as a string i.e. *current* of *goal* calories
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

sub valid_date() {	# checks if date entered is valid
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

sub insert_meal() {	# inserts meal into the database
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

sub exercise_screen() {

}

sub calorie_calculator() {	# calculates calories of user based on personal details entered
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

sub food_suggestions () {	# returns a scroll menu of foods containing the search query from the database and an external website
	my $userSearch = param('search_term');
		    
	#my %info = insert_food($userSearch);
	my $mech = WWW::Mechanize->new;
	
	#print "$search\n";
	$mech->get('http://ndb.nal.usda.gov/ndb/foods');
	$mech->submit_form(
			form_name => 'quickform', 
			fields => {'qlookup' => $userSearch,},);

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
	
	my @foods = keys %food_urls;
	my $key_size = @foods;
	my $height = 30*$key_size;
	if($height > 210){
	     	$height = 210;
	} elsif ($height < 30) {
		$height = 30;
	}
	$height .= "px";
   	my $out = qq(<center><h2 style="color:white;">Suggestions</h2></center></body>
	      	<select name="food_selected" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:$height;width:500px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
		 );
	$driver = "SQLite"; 
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
	$stmt = qq(select name from food where name like '%$userSearch%'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	my $selected = param('food_selected');
	while (my @row = $sth->fetchrow_array()) {	# add foods from database to the scroll menu
		$out .= qq(<option);
		if ($row[0] eq $selected) {
			$out .= " selected";
		}
		$out .= qq(>$row[0]
		);
	}
	foreach $food (@foods){	# add foods from website to the scroll menu
		$out .= qq(<option);
		if ($food eq $selected) {
			$out .= " selected";
		}
		$out .= qq(>$food
     		);
	}
	$out .= qq(</select>
	<pre> </pre>
	<center><h2 style="color:white;">Serving Size (g)</h2></center></body>
	<input type="text" name="serving" value="" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
	<pre> </pre>
	<input type="submit" name="add_food_search" value="ADD TO MEAL
" class="button" style="height:45px;width:350px;"><br>
	);
 	return $out;    
}

sub check_serving() {	# checks if a correct serving has been entered
	my $serving = param('serving');
	if ($serving eq "") {
		return 0;
	} elsif ($serving !~ /\d+/) {
		return 0;
	}
	return 1;
}

sub insert_food() {	# adds food from search to meal and updates meal calories and daily calorie counter, if not already in database insert into database
	my $search = param('food_selected');
	$driver = "SQLite"; 
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
	$stmt = qq(select id, name, calories from food where name = '$search'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	my @row = $sth->fetchrow_array();
	my $fid = $row[0];
	my $name = $row[1];
	my $calories = $row[2];
	if ($fid ne "") {	# if already in database add to meal
		my $username = param('username');
		my $meal = param('meal');
		my $date = param('date');
		$meal =~ s/ \((\d+) calories\)$//;
		my $serving = param('serving');
$stmt = qq(select id from user where username = '$username'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		my $uid = $row[0];
		$stmt = qq(select id, calories from meal where uid = '$uid' and name = '$meal' and date = '$date'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		my $mid = $row[0];
		my $updated = int(($row[1] + $calories * $serving / 100) + 0.5);	# update meal calories
		$stmt = qq(insert into meal_contains(mid,fid,serving) values('$mid','$fid','$serving'));
		$rv = $dbh->do($stmt) or die $DBI::errstr;
		$stmt = qq(update meal set calories = $updated where id = '$mid');
		$rv = $dbh->do($stmt) or die $DBI::errstr;
		if ($rv < 0) {
			print $DBI::errstr;
		}
		$stmt = qq(select current from calories where uid = '$uid' and date = '$date'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		$updated = int(($row[0] + $calories * $serving / 100) + 0.5);	# update daily calorie counter
		$stmt = qq(update calories set current = $updated where uid = '$uid' and date = '$date');
		$rv = $dbh->do($stmt) or die $DBI::errstr;
		if ($rv < 0) {
			print $DBI::errstr;
		}
	} else {	# if not in database extract details from website and insert into database
		my $mech = WWW::Mechanize->new;
		my $serving = param('serving');
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
		}
	
		my @foods = keys %food_urls;

		my $user_url = $food_urls{$search};
		$mech->get("http\:\/\/ndb\.nal\.usda\.gov$user_url");
	
		$content = $mech->content;
		#if($serving eq 0){
		#	my $oneServing = 100;
		#	$content =~ m/item\n.*?<br\/>(.*)/;
			#$content =~ m/.*?<br\/>(\n+?)g/;
		#	$oneServing = $1;
		#	$oneServing =~ s/g//;
		#	$serving = $oneServing;
		#}

		my %nutritionalInfo;
		my @infoNeeded = ("Energy", "Water", "Protein", "Total lipid", "Carbohydrate, by difference", "Fiber, total dietary", "Sugars, total", 			"Calcium", "Iron", "Magnesium", "Phosphorus", "Potassium", "Zinc", "Vitamin C", "Thiamin", "Riboflavin", "Niacin", "Vitamin B-6", 			"Folate", 	"Vitamin E", "Vitamin K", "total saturated", "total monounsaturated", "total polyunsaturated", "trans", "Cholestrol");
	
		foreach my $info (@infoNeeded){
			if($content =~ m/$info.*\n.*\n.*\n.*?<\/td>.*\n.*?<td.*?<\/td>\n.*?<td.*?>(.*?)<\/td>/){;	
				$nutritionalInfo{$info} = $1;
			}
		}

		#add to db
		my $search = param('food_selected');
		my $name = $search;
		my $username = param('username');
		my $calories = int(($nutritionalInfo{$infoNeeded[0]}/4.186)+0.5);
		my $protein = $nutritionalInfo{$infoNeeded[2]};
		my $carbs = $nutritionalInfo{$infoNeeded[4]};
		my $fat = $nutritionalInfo{$infoNeeded[3]};
		my $meal = param('meal');
		my $date = param('date');
		$meal =~ s/ \((\d+) calories\)$//;
		$driver = "SQLite"; 
		$database = "project.db"; 
		$dsn = "DBI:$driver:dbname=$database";
		$userid = ""; $dbpassword = "";  
		$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
		$stmt = qq(insert into food(id,name,calories,protein,carbs,fat,fibre,sugars,monounsatfat,polyunsatfat,satfat,transfat,cholesterol) values(null,'$name','$calories','$protein','$carbs','$fat','$fibre','$sugars','$mono','$poly','$sat','$trans','$cholesterol'));
		$rv = $dbh->do($stmt) or die $DBI::errstr;
		$stmt = qq(select id from user where username = '$username'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		my $uid = $row[0];
		$stmt = qq(select id, calories from meal where uid = '$uid' and name = '$meal' and date = '$date'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		my $mid = $row[0];
		my $updated = int(($row[1] + $calories * $serving / 100) + 0.5); 
		$stmt = qq(select id from food where name = '$name' and calories = '$calories' and protein = '$protein' and carbs = '$carbs' and fat = '$fat'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		$fid = $row[0];
		$stmt = qq(insert into meal_contains(mid,fid,serving) values('$mid','$fid','$serving'));
		$rv = $dbh->do($stmt) or die $DBI::errstr;
		$stmt = qq(update meal set calories = $updated where id = '$mid');
		$rv = $dbh->do($stmt) or die $DBI::errstr;
		if ($rv < 0) {
			print $DBI::errstr;
		}
		$stmt = qq(select current from calories where uid = '$uid' and date = '$date'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		$updated = int(($row[0] + $calories * $serving / 100) + 0.5);
		$stmt = qq(update calories set current = $updated where uid = '$uid' and date = '$date');
		$rv = $dbh->do($stmt) or die $DBI::errstr;
		if ($rv < 0) {
			print $DBI::errstr;
		}
	}
}

sub page_footer() {
	return qq(
	<div class="footer">
	<p class="copy" style="color:#f2f5f2;font-family:AmbleRegular;font-size:12pt">Copyright &copy; 2015. All rights reserved.</p>
	</div>
	</div>
	</body>
	)
}
