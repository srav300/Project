#!/usr/bin/perl -w

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
use Date::Calc qw/check_date/;
use Date::Calc qw(Add_Delta_Days);
use WWW::Mechanize;
use DBI;
warningsToBrowser(1);

$bg_handler = "2";
$correct_input = 1;
$update_err = 0;
print page_header();

if (defined param('logout')) {
    print login_screen();
    $bg_handler = 3;
} elsif (defined param('register')) {
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
} elsif (defined param('username') && defined param('password')) {
	$bg_handler = 2;
	if (check_login()) {
        	print banner();
		if (defined param('settings') || defined param('cancel')) {
			print settings();
		} elsif (defined param('change_password')) {
			$pass_change_attempt = 1;
			$pass_error = change_check();
			if($pass_error == 0){
				update_password();
			}
			print change_password();
		} elsif (defined param('update_profile')) {
			$update_attempt = 1;
			@error_log = check_update();
			if (check_errors() == 0) {
 				update_profile();
 				print update();
			} else {
				print update();
			}
		} elsif (defined param('add_food_search')) {
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
		} elsif (defined param('insert_set')) {
			if (param('reps') =~ /\d+/ && defined param('reps') != 0) {
				if (param('weight') eq "" || param('weight') =~ /\d+/) {
					insert_set();
					print show_exercise();
				} else {
					$correct_input = 0;
					print show_exercise();
				}
			} else {
				$correct_input = 0;
				print show_exercise();
			}
		} elsif (defined param('insert_exercise')) {
			if (defined param('exercise_selected')) {
				insert_exercise();
			}
			print show_workout();
		} elsif (defined param('add_set')) {
			print show_exercise();
		} elsif (defined param('delete_set')) {
			delete_set();
			print show_exercise();
		} elsif (defined param('show_exercise')) {
			print show_exercise();
		} elsif (defined param('search_food')) {
			print add_food_screen();
		} elsif (defined param('search_exercise') || defined param('seaarch_again')) {
			print show_workout();
		} elsif (defined param('back_meal')){
			print show_meal();
		} elsif (defined param('back_exercise')) {
			print exercise_screen();
		} elsif (defined param('back_workout')) {
			print show_workout();
		} elsif (defined param('delete_meal')) {
			delete_meal();
			print diet_screen();
		} elsif (defined param('delete_food')) {
			delete_food();
			print show_meal();
		} elsif (defined param('delete_workout')) {
			delete_workout();
			print exercise_screen();
		} elsif (defined param('diet') || defined param('back_diet')) {
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
		} elsif (defined param('workout')) {
			print show_workout();
		} elsif ((defined param('add_meal') || defined param('meal_name')) && param('meal_name') ne "" && param('meal_name') !~ /"/) {
			insert_meal();
			print diet_screen();
		} elsif (defined param('add_workout') && (param('workout_name') ne "" || param('workout_selected') ne "")) {
			insert_workout();
			print exercise_screen();
		} elsif (defined param('login') || defined param('home')) {
			print home();
		} elsif (defined param('exercise_screen')) {
			print exercise_screen();
		} elsif (defined param('change_diet_date') || defined param('new_meal')) {
			print diet_screen();
		} elsif (defined param('change_exercise_date') || defined param('new_workout')) {
			print exercise_screen();
		} elsif (defined param('update')) {
			print update();
		} elsif (defined param('cancel')) {
			print cancel();
		} elsif (defined param('friend')) {
			print friend();
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

sub banner {
	my $css = qq(
	<div class="header-banner" id="banner">
	<h1 align="right"><form action="doyouevenfit.cgi" method="post">
	<input type="hidden" name="page" value="">
	<input type="submit" name="messages" value="MESSAGES" class="button_small">
	<input type="submit" name="settings" value="SETTINGS" class="button_small">
	<input type="submit" name="logout" value="LOG OUT" class="button_small">
	<input type="submit" name="buffer" value="" class="button_hide";><br>
	</h1>
	<h1>DoYouEvenFit</h1>
	<input type="hidden" name="page" value="">
	<input type="submit" name="diet" value="DIET" class="button" style="height:45px;">
	<input type="submit" name="exercise_screen" value="EXERCISE" class="button" style="height:45px;">
	<input type="submit" name="friend" value="FRIENDS" class="button" style="height:45px;">
	);
	$css .= hidden('username');
	$css .= hidden('password');
	$css .= qq(</form>   
	</div>
	);
	return $css;
}

sub settings() {
	my $html = qq(<div class="header-bottom" id="update">
	<form action="doyouevenfit.cgi" method="post">
	<input type="hidden" name="page" value="">
	<input type="submit" name="update" value="UPDATE PERSONAL DETAILS" class="button2" style="height:45px;">
	<pre> </pre> <pre> </pre>
	<input type="submit" name="change_password" value="CHANGE PASSWORD" class="button2" style="height:45px;">
	);
	$html .= hidden('username');
	$html .= hidden('password');
	$html .= qq(</form>   
	</h1>
	</div>
	);
	return $html;
}

sub update() {
	$driver = "SQLite";
	$database = "project.db";
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr;
	$stmt = qq(select * from user where username = '$username');
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr;
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	$height = $row[7];
	$weight = $row[8];
	$age = $row[9];
	$exercise = $row[10];
	$goal = $row[11];
	#$dbh->disconnect();
	my $html = qq(
	<div class="header-bottom" id="update">
	<form action="doyouevenfit.cgi" method="post">
	);
	if ($update_attempt == 1 && check_errors() == 0) {
		$html .= qq(<text style="color:white;font-size:32pt;><font color="white">Update Successful!</font></text> <pre> </pre> <pre> </pre>);
	}
	$html .= qq(<center><h3 style="color:white;">Height (cm)</h3></center></body>
	<input type="text" name="height" size=28 style="width:350px;text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="$height" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if($error_log[0] == 1){
		$html .= qq(<center><text style="color:white;">* height must be entered</text></center></body>);
	} elsif($error_log[0] == 2){
		$html .= qq(<center><text style="color:white;">* height must consist of numeric characters only</text></center></body>);
	}
	$html .= qq(<pre> </pre> <pre> </pre>
	<center><h3 style="color:white">Weight (kg)</h3></center></body>
	<input type="text" name="weight" size=28 style="width:350px;text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="$weight" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if($error_log[1] == 1){
		$html .= qq(<center><text style="color:white;">* weight must be entered</text></center></body>);
	} elsif($error_log[1] == 2){
		$html .= qq(<center><text style="color:white;">* weight must consist of numeric characters only</text></center></body>);
	}
	$html .= qq(<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">Age</h3></center></body>
	<input type="text" name="age" size=28 style="width:350px;text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="$age" onfocus="javascript:if(this.value=='')this.value='';"><br>);
	if($error_log[2] == 1){
		$html .= qq(<center><text style="color:white;">* age must be entered</text></center></body>);
	} elsif($error_log[2] == 2){
	   $html .= qq(<center><text style="color:white;">* age must consist of numeric characters only</text></center></body>);
	}
	$html .= qq(<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">What is your exercise level?</h3></center></body>
	<select name="exercise" size=28 class="styled-select" style="height:132px;"><br>
	<option);
	if ($exercise eq "Sedentary") {
		$html .= " selected";
	}
	$html .= qq(>Sedentary
		<option);
	if ($exercise eq "Lightly Active") {
		$html .= " selected";
	}
	$html .= qq(>Lightly Active
		<option);
	if ($exercise eq "Moderately Active") {
		$html .= " selected";
	}
	$html .= qq(>Moderately Active
		<option);
	if ($exercise eq "Very Active") {
		$html .= " selected";
	}
	$html .= qq(>Very Active
		<option);
	if ($exercise eq "Extremely Active") {
		$html .= " selected";
	}
 	$html .= qq(>Extremely Active
	</select>
	<pre> </pre> <pre> </pre>);
	if($error_log[3] == 1){
		$html .= qq(<center><text style="color:white;">* exercise level must be selected</text></center></body>);
	}
	$html .= qq(<center><h3 style="color:white;">What is goal?</h3></center></body>
	<select name="goal" size=28 class="styled-select" style="height:132px;"><br>
	<option);
	if ($goal eq "Extreme Weight Loss") {
		$html .= " selected";
	}
	$html .= qq(>Extreme Weight Loss
		<option);
	if ($goal eq "Weight Loss") {
		$html .= " selected";
	}
	$html .= qq(>Weight Loss
		<option);
	if ($goal eq "Maintain Weight") {
		$html .= " selected";
	}
	$html .= qq(>Maintain Weight
		<option);
	if ($goal eq "Weight Gain") {
		$html .= " selected";
	}
	$html .= qq(>Weight Gain
		<option);
	if ($goal eq "Extreme Weight Gain") {
		$html .= " selected";
	}
	$html .= qq(>Extreme Weight Gain
	</select>);
	if($error_log[4] == 1){
		$html .= qq(<center><text style="color:white;">* a weight goal must be selected</text></center></body>);
	} 
	$html .= qq(<pre> </pre> <pre> </pre>
	<input type="submit" name="update_profile" value="Update" class="button" style="height:45px;width:220px;"><br>
	<p>&nbsp</p>
	<input type="submit" name="cancel" value="Cancel" class="button" style="height:45px;width:220px;"><br>
	<p>&nbsp</p>);
	$html .= hidden('username');
	$html .= hidden('password');
	$html .= qq(</form>
	</div>
	);
}

sub check_update() {	
	my @errors = ("0", "0", "0", "0", "0");
	$username = param('username');
	my $height = param('height');
	my $weight = param('weight');
	my $age = param('age');
	my $exercise = param('exercise');
	my $goal = param('goal');

	if ($height eq "") {
		$errors[0] = 1;
	} elsif ($height !~ /^\d+$/) {
		$errors[0] = 2;
	}
	if ($weight eq "") {
		$errors[1] = 1;
	} elsif ($weight !~ /^\d+$/) {
		$errors[1] = 2;
	}
	if ($age eq "") {
		$errors[2] = 1;
	} elsif ($age !~ /^\d+$/) {
		$errors[2] = 2;
	}
	if ($exercise eq "") {
		$errors[3] = 1;
	}
	if ($goal eq "") {
		$errors[4] = 1;
	}
	return @errors;
}

sub check_errors(){
   foreach $value (@error_log) {
      if($value != 0){
         return 1;
      }
   }
   return 0;
}


sub update_profile() { # update user details into database
	$username = param('username');
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
	$stmt = qq(update user set height = "$height", weight = "$weight", age = "$age", exercise = "$exercise", goal = "$goal" where username = '$username'); 
	$rv = $dbh->do($stmt) or die $DBI::errstr; 
	$dbh->disconnect();
}

sub change_password() {
	my $html = qq(<div class="header-bottom" id="update">
	<form action="doyouevenfit.cgi" method="post">
	);
	
	if ($pass_change_attempt == 1 && $pass_error == 0) {
	   my $new_password = param('new_password1');
		$html .= qq(<h2><font color="black" size="3">Update Successful!</font></h2>);
		$html .= qq(<form action="doyouevenfit.cgi" method="post">
			<input type="text" name="password" value="$new_password" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;"><br>
			</form>);
	}
	
	$html .= qq(<center><h3 style="color:white;">Enter Old Password</h3></center></body>);
	if($pass_error == 1){
	   $html .= qq(<center><h3 style="color:red;">Old Password is Incorrect!</h3></center></body>);
	} 
	$html .= qq(<input type="password" name="old_password" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="********" onfocus="javascript:if(this.value=='********')this.value='';"><br>
	<pre> </pre>
	<center><h3 style="color:white">Enter New Password</h3></center></body>);
	if($pass_error == 2){
	   $html .= qq(<center><h3 style="color:red;">New Passwords do not match!</h3></center></body>);
	} 
	$html .= qq(<input type="password" name="new_password1" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="********" onfocus="javascript:if(this.value=='********')this.value='';"><br>
	<p>&nbsp</p>
	<center><h3 style="color:white">Re-Enter New Password</h3></center></body>
	<input type="password" name="new_password2" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="********" onfocus="javascript:if(this.value=='********')this.value='';"><br>
	<p>&nbsp</p>);
	
	$html .= qq(<input type="submit" name="change_password" value="Update" class="button" style="height:45px;width:220px;"><br>
	<p>&nbsp</p>
	<input type="submit" name="cancel" value="Cancel" class="button" style="height:45px;width:220px;"><br>
	<p>&nbsp</p>);
	$html .= param('username');
	$html .= param('password');
	$html .= qq(</form>
	</div>
	);
	return $html;
}


sub change_check(){
   my $old_password = param('old_password');
   my $new_password1 = param('new_password1');
   my $new_password2 = param('new_password2');
   my $current_password = param('password');
   if($old_password ne $current_password){
      return 1;
   } elsif ($new_password1 ne $new_password2){
      return 2;   
   }
   return 0;
}

sub update_password() { # update user details into database
	$username = param('username');
	my $new_password = param('new_password1');
	$driver = "SQLite"; 
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
	$stmt = qq(update user set password = "$new_password"); 
	$rv = $dbh->do($stmt) or die $DBI::errstr; 
	$dbh->disconnect();
   
}

sub friend() {
    print <<EOF;
    <div class="header-banner" id="banner">
    <h1>TEST</h1>    
    </div>
EOF
}

sub page_css {
	$css = qq(
	<link href="/css/style.css" rel="stylesheet" type="text/css" media="all" />
	<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	);

    if ($bg_handler eq 0) {
        
    } if ($bg_handler eq 1) {
        $css .= qq(<body background="/images/wood.jpg">);
    } if ($bg_handler eq 2) {
        $css .= qq(<body background="/images/wood.jpg">);
    } if ($bg_handler eq 3) {
 		$css .= qq(<body background="/images/banner.jpg">);
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
		$html .= qq(<h2><font color="white" size="2">Your login details seem to be incorrect.</font></h2>	);
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
    $driver = "SQLite";
	$database = "project.db";
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr;
	$stmt = qq(select fname from user where username = '$username');
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr;
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	 $existing_username = $row[0];

	my $html = qq(
    <div class="header-banner" id="tour">
	<div class="wrap">
    <h1>&nbsp;</h1>
    <h2>Welcome $row[0]!</h2>
	<pre> </pre>
    </div>
    </div>
	)
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
	<center><h3 style="color:white;">What is your exercise level?</h3></center></body>
	 <select name="exercise"  size=28 class="styled-select" style="height:132px;"><br> 
	<option>Sedentary
	<option>Lightly Active
	<option>Moderately Active
	<option>Very Active
	<option>Extremely Active
	</select>
	<pre> </pre> <pre> </pre>
	<center><h3 style="color:white;">What is your goal?</h3></center></body>
	<select name="goal"  size=28 class="styled-select" style="height:132px;"><br>
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
		<center><h3 style="color:white;">What is your exercise level?</h3></center></body>
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
	my $day = `date +%d`;
	chomp($day);
	my $month = `date +%m`;
	chomp($month);
	my $year = `date +%Y`;
	chomp($year);
	my $date = "$day/$month/$year";	# display current date if date is not already defined
	my $offset = 0;
	if (defined param('diet_date')) {
		$date = param('diet_date');
		($day, $month, $year) = split(/\//, $date);
		if (param('change_diet_date') eq "<") {
			$offset = -1;
			($year, $month, $day) = Add_Delta_Days($year, $month, $day, $offset);
			if ($day =~ /^(\d)$/) {
				$day = "0$day";
			}
			if ($month =~ /^(\d)$/) {
				$month = "0$month";
			}
			$date = "$day/$month/$year";
		} elsif (param('change_diet_date') eq ">") {
			$offset = 1;
			($year, $month, $day) = Add_Delta_Days($year, $month, $day, $offset);
			if ($day =~ /^(\d)$/) {
				$day = "0$day";
			}
			if ($month =~ /^(\d)$/) {
				$month = "0$month";
			}
			$date = "$day/$month/$year";
		}
	}
	my $html = qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<form action="doyouevenfit.cgi" method="post">
	<input type="hidden" name="page" value="">);
	if (defined param('diet_date') && !valid_date($date)) {	# notify user if they have entered an invalid date
		$html .= qq(<text style="color:white";> * invalid date (DD/MM/YYYY)<p></p>);
	}
	$html .= qq(<input type="submit" name="change_diet_date" value="" class="button_hide" style="height:0px;width;0px;"><br>
	<div class="container">
	<div class="column-center">
	<input type="submit" name="change_diet_date" value="<" class="button" style="height:50px;width:50px;">
	<input type="text" name="diet_date" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:22pt;height:40px;width:200px;font-family:AmbleRegular;"value="$date" onfocus="javascript:if(this.value=='')this.value='';">
	<input type="submit" name="change_diet_date" value=">" class="button" style="height:50px;width:50px;">
	</div>
	</div>
	<p>&nbsp</p>
	<p>&nbsp</p>);
	$html .= hidden('username');
	$html .= hidden('password');
	$html .= qq(</form>);
	if (!defined param('diet_date') || (defined param('diet_date') && valid_date($date))) {	# if valid date display calorie counter and meals
		$html .= qq(<h1>);
		$html .= getCalories($date);
		$html .= qq(</h1> <p>&nbsp</p>
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
			$html .= qq(<form action="doyouevenfit.cgi" method="post">
			<input type="text" name="mid" value="$row[0]" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;"><br>
			<input type="submit" name="meal" value="$row[1] ($row[2] calories)" class="button" style="height:45px;width:600px;"><br> <pre> </pre>
			<input type="text" name="diet_date" value="$date" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;"><br>
			);
			$html .= hidden('username');
			$html .= hidden('password');
			$html .= qq(</form>);
		}
		$html .= qq(<pre> </pre>);
		$html .= qq(<form action="doyouevenfit.cgi" method="post">);
		if (defined param('new_meal')) {
			$html .= 	qq(<input type="text" name="meal_name" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;width:300px;font-family:AmbleRegular;"value="New Meal" onfocus="javascript:if(this.value=='New Meal')this.value='';"><br>
			<pre> </pre>
			<input type="submit" name="add_meal" value="+ ADD MEAL" class="button" style="height:45px;width:200px;"><br>);
		} else {
			$html .= qq(<input type="submit" name="new_meal" value="NEW MEAL" class="button" style="height:45px;"><br>);
		}
		$html .= qq(<input type="text" name="diet_date" value="$date" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;"><br>);
		$html .= hidden('username');
		$html .= hidden('password');
		$html .= qq(</form>);
	}
	$html .= qq(</div>
	</div>
	);
	return $html;
}

sub show_meal() {	# displayed if user selects a meal from diet screen
	my $username = param('username');
	my $date = param('diet_date');
	my $meal = param('meal');
	my $mid = param('mid');
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
	$stmt = qq(select calories from meal where id = '$mid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $calories = $row[0];
	my $html = qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<h1>$meal ($calories calories)</h1>  
	<pre> </pre>);
	$stmt = qq(select fid, serving, id from meal_contains where mid = '$mid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	$i = 0;
	my @fid;
	my @serving;
	my @mcid;
	while (my @row = $sth->fetchrow_array()) {
		$fid[$i] = $row[0];
		$serving[$i] = $row[1];
		$mcid[$i] = $row[2];
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
		#$html .= qq(<text style="color:white";>$serving[$j] g of $name ($calories calories, $protein g of protein, $carbs g of carbs, $fat g of fat)<p></p>);
		$html .= qq(<form action="doyouevenfit.cgi" method="post">
		<input type="text" name="fid" value="$fid[$j]" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;">
		<input type="text" name="mcid" value="$mcid[$j]" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;">
		<input type="text" name="calories" value="$calories" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;">
		<input type="submit" name="food" value="$name ($calories calories)" class="button" style="font-size:16pt;height:45px;width:750px;">
		<input type="submit" name="delete_food" value="X" class="button" style="font-size:16pt;height:45px;width:50px;">
	<pre> </pre>);
		$html .= hidden('username');
		$html .= hidden('password');
		$html .= hidden('diet_date');
		$html .= hidden('meal');
		$html .= hidden('mid');
		$html.= qq(</form>);
		$j++;
	}
	$html .= qq(<pre> </pre> <pre> </pre>
	<form action="doyouevenfit.cgi" method="post">
	<input type="submit" name="add_food" value="+ ADD FOOD" class="button" style="height:45px;width:250px;"><br>
	<pre> </pre> <pre> </pre>
	<input type="submit" name="delete_meal" value="DELETE MEAL" class="button" style="height:45px;width:250px;"><br>
	<pre> </pre> <pre> </pre>
	<input type="submit" name="back_diet" value="BACK" class="button" style="height:45px;width:250px;"><br>
	<p>&nbsp</p>);
	$html .= hidden('username');
	$html .= hidden('password');
	$html .= hidden('diet_date');
	$html .= hidden('meal');
	$html .= hidden('mid');
	$html.= qq(</form>);
	return $html;
}

sub show_food() {	# displayed if user selects food from show meal
	my $username = param('username');
	my $date = param('diet_date');
	my $meal = param('meal');
	my $mid = param('mid');
	my $fid = param('fid');
	my $mcid = param('mcid');
	$meal =~ s/ \(\d+ calories\)$//;
	my $food = param('food');
	$food =~ s/ \((\d+) calories\)$//;
	my $calories = $1;
	$driver = "SQLite"; 
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr;
	$stmt = qq(select serving from meal_contains where id = '$mcid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	my @row = $sth->fetchrow_array();
	my $serving = $row[0];
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
	my $html = qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<h3> <text style="color:white";>$food ($calories calories)</h3>  
	<form action="doyouevenfit.cgi" method="post">
	<pre> </pre>
	<text style="color:white;font-size:20pt">Serving: $serving g
	<p>
	Protein: $protein g
	<p>
	Carbs: $carbs g
	<p>
	Fat: $fat g</text>
	<p></p>
	<pre> </pre>
	<input type="submit" name="delete_food" value="DELETE FOOD" class="button" style="height:45px;width:250px;"><br>
	<pre> </pre>
	<input type="submit" name="back_meal" value="BACK" class="button" style="height:45px;width:250px;"><br>
	<p>&nbsp</p>);
	$html .= hidden('username');
	$html .= hidden('password');
	$html .= hidden('diet_date');
	$html .= hidden('meal');
	$html .= hidden('food');
	$html .= hidden('mid');
	$html .= hidden('fid');
	$html .= hidden('mcid');
	$html .= qq(</form>);
	return $html;
}

sub delete_meal() {	# deletes meal and any relations from database and also updates daily calorie counter
	my $username = param('username');
	my $meal = param('meal');
	my $mid = param('mid');
	my $date = param('diet_date');
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
	$stmt = qq(select calories from meal where id = '$mid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $calories = $row[0];
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
	my $date = param('diet_date');
	my $mid = param('mid');
	my $fid = param('fid');
	my $mcid = param('mcid');
	my $food = param('food');
	$food =~ s/ \((\d+) calories\)$//;
	my $calories = $1;
	if (defined param('calories')) {
		$calories = param('calories');
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
	my @row = $sth->fetchrow_array();
	my $uid = $row[0];
	$stmt = qq(delete from meal_contains where id = '$mcid');
	$rv = $dbh->do($stmt) or die $DBI::errstr;
	if ($rv < 0) {
		print $DBI::errstr;
	}
	$stmt = qq(select calories from meal where id = '$mid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $mcalories = $row[0];
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
	my $html = qq(
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
		$html .= food_suggestions();
	}
	if (defined param('add_food_search') && $serving eq "") {	# if a user has attempted to add food without specifying a serving size notify them
		$html .= qq(<text style="color:white";> * a serving size must be entered for this food item<p></p>);
	} elsif (defined param('add_food_search') && $serving !~ /\d+/) {	# if entered incorrectly notify user that serving size must be a number
		$html .= qq(<text style="color:white";> * a serving size must consist of numeric characters only<p></p>);
	}
	$html .= qq(<pre> </pre> <pre> </pre>
	<input type="submit" name="add_food_man" value="MANUAL ENTRY" class="button" style="height:45px;width:350px;"><br>
	<pre> </pre> <pre> </pre>
	<input type="submit" name="back_meal" value="BACK" class="button" style="height:45px;width:350px;"><br>
	<p>&nbsp</p>
);
	$html .= hidden('username');
	$html .= hidden('password');
	$html .= hidden('diet_date');
	$html .= hidden('meal');
	$html .= hidden('mid');
	$html.= qq(</form>);
	return $html;	
}

sub add_food_man() {	# page for user to manual add food to meal
	my $html = qq(
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
	$html .= qq(<input type="submit" name="add_to_meal" value="ADD TO MEAL" class="button" style="height:45px;width:350px;"><br>
	<p>&nbsp</p>);
	$html .= hidden('username');
	$html .= hidden('password');
	$html .= hidden('diet_date');
	$html .= hidden('meal');
	$html .= hidden('mid');
	$html .= qq(</form>);
	return $html;
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
	$help .= hidden('diet_date');
	$help .= hidden('meal');
	$help .= hidden('mid');
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
	my $date = param('diet_date');
	$meal =~ s/ \((\d+) calories\)$//;
	my $mid = param('mid');
	$driver = "SQLite"; 
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
	$stmt = qq(insert into food(id,name,calories,protein,carbs,fat,fibre,sugars,monounsatfat,polyunsatfat,satfat,transfat,cholesterol) values(null,"$name",'$calories',$protein,'$carbs','$fat','$fibre','$sugars','$mono','$poly','$sat','$trans','$cholesterol'));
	$rv = $dbh->do($stmt) or die $DBI::errstr;
	$stmt = qq(select id from user where username = '$username'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $uid = $row[0];
	$stmt = qq(select calories from meal where id = '$mid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $updated = int(($row[0] + $calories * $serving / 100) + 0.5); 
	$stmt = qq(select id from food where name = "$name" and calories = '$calories' and protein = '$protein' and carbs = '$carbs' and fat = '$fat'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	$fid = $row[0];
	$stmt = qq(insert into meal_contains values(null,'$mid','$fid','$serving'));
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
	my $date = $_[0];
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

sub valid_date {	# checks if date entered is valid
	my $date = $_[0];
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
	my $date = param('diet_date');
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
	$stmt = qq(insert into meal values(null,'$uid',"$meal_name",0,'$date'));
	$rv = $dbh->do($stmt) or die $DBI::errstr;
}

sub exercise_screen() {
	my $day = `date +%d`;
	chomp($day);
	my $month = `date +%m`;
	chomp($month);
	my $year = `date +%Y`;
	chomp($year);
	my $date = "$day/$month/$year";	# display current date if date is not already defined
	my $offset = 0;
	if (defined param('exercise_date')) {
		$date = param('exercise_date');
		($day, $month, $year) = split(/\//, $date);
		if (param('change_exercise_date') eq "<") {
			$offset = -1;
			($year, $month, $day) = Add_Delta_Days($year, $month, $day, $offset);
			if ($day =~ /^(\d)$/) {
				$day = "0$day";
			}
			if ($month =~ /^(\d)$/) {
				$month = "0$month";
			}
			$date = "$day/$month/$year";
		} elsif (param('change_exercise_date') eq ">") {
			$offset = 1;
			($year, $month, $day) = Add_Delta_Days($year, $month, $day, $offset);
			if ($day =~ /^(\d)$/) {
				$day = "0$day";
			}
			if ($month =~ /^(\d)$/) {
				$month = "0$month";
			}
			$date = "$day/$month/$year";
		}
	}
	my $html = qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<form action="doyouevenfit.cgi" method="post">
	<input type="hidden" name="page" value="">);
	if (defined param('exercise_date') && !valid_date($date)) {	# notify user if they have entered an invalid date
		$html .= qq(<text style="color:white";> * invalid date (DD/MM/YYYY)<p></p>);
	}
	$html .= qq(<input type="submit" name="change_exercise_date" value="" class="button_hide" style="height:0px;width;0px;"><br>
	<div class="container">
	<div class="column-center">
	<input type="submit" name="change_exercise_date" value="<" class="button" style="height:50px;width:50px;">
	<input type="text" name="exercise_date" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:22pt;height:40px;width:200px;font-family:AmbleRegular;"value="$date" onfocus="javascript:if(this.value=='')this.value='';">
	<input type="submit" name="change_exercise_date" value=">" class="button" style="height:50px;width:50px;">
	</div>
	</div>
	<p>&nbsp</p>
	<p>&nbsp</p>);
	$html .= hidden('username');
	$html .= hidden('password');
	$html .= qq(</form>);
	if (!defined param('exercise_date') || (defined param('exercise_date') && valid_date($date))) {	# if valid date display calorie counter and meals
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
		$stmt = qq(select id from workout where uid = '$uid' and date = '$date'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		while (my @row = $sth->fetchrow_array()) {
			my $wid = $row[0];
			$stmt = qq(select name from workout where id = '$wid'); 
			my $hts = $dbh->prepare($stmt);
			$rv = $hts->execute() or die $DBI::errstr; 
			if ($rv < 0) {
				print $DBI::errstr;
			}
			my @wor = $hts->fetchrow_array();
			$html .= qq(<form action="doyouevenfit.cgi" method="post">
			<input type="text" name="wid" value="$wid" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;"><br>
			<input type="submit" name="workout" value="$wor[0]" class="button" style="height:45px;width:600px;"><br> <pre> </pre>
			<input type="text" name="exercise_date" value="$date" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;"><br>);
			$html .= hidden('username');
			$html .= hidden('password');
			$html .= qq(</form>);
		}
		$html .= qq(<pre> </pre>
		<form action="doyouevenfit.cgi" method="post">);
		if (defined param('new_workout')) {
			$html .= qq(<input type="text" name="workout_name" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;width:300px;font-family:AmbleRegular;"value="New Workout" onfocus="javascript:if(this.value=='New Workout')this.value='';"><br>
			<pre> </pre>
			<input type="submit" name="add_workout" value="+ ADD WORKOUT" class="button" style="height:45px;width:300px;"><br>);
		} else {
			# $html .= qq(<center><text style="color:white;font-size:20pt;">Saved Workouts</center></body>
			# <select name="workout_selected" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:100px;width:500px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
		 	# );
			#v$stmt = qq(select name from saved_workout where uid = '$uid'); 
			# $sth = $dbh->prepare($stmt);
			# $rv = $sth->execute() or die $DBI::errstr; 
			# if ($rv < 0) {
			#	print $DBI::errstr;
			#}
			#while (my @row = $sth->fetchrow_array()) {
			#	$html .= qq(<option>$row[0]);
			#}
			#$html .= qq(</select> <pre> </pre>);
			# <input type="submit" name="add_workout" value="+ ADD WORKOUT" class="button" style="height:45px;width:300px;"><br>
			# <pre> </pre> <pre> </pre>
			$html .= qq(<input type="submit" name="new_workout" value="NEW WORKOUT" class="button" style="height:45px;width:300px;"><br>);
		}
		$html .= qq(<input type="text" name="exercise_date" value="$date" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;"><br>);
		$html .= hidden('username');
		$html .= hidden('password');
		$html .= qq(</form>);
	}
	$html .= qq(</div>
	</div>);
	return $html;
}

sub insert_workout() {	# inserts workout into the database
	my $username = param('username');
	my $date = param('exercise_date');
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
	if (defined param('workout_selected')) {
		### need to insert new workout from saved workoit
	} else {
		my $name = param('workout_name');
		$stmt = qq(insert into workout values(null,'$uid',"$name",'$date'));
		$rv = $dbh->do($stmt) or die $DBI::errstr;
	}
}

sub show_workout() {
	my $username = param('username');
	my $date = param('exercise_date');
	my $wid = param('wid');
	my $workout = param('workout');
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
	my $html = qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<h1>$workout</h1>  
	<form action="doyouevenfit.cgi" method="post">
	<pre> </pre>);
	$stmt = qq(select id, eid from workout_contains where wid = '$wid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	$html .= hidden('username');
	$html .= hidden('password');
	$html .= hidden('exercise_date');
	$html .= hidden('workout');
	$html .= hidden('wid');
	$html .= qq(</form>);
	while (my @exercises = $sth->fetchrow_array()) {
		$html .= qq(<form action="doyouevenfit.cgi" method="post">);
		my $wcid = $exercises[0];
		my $eid = $exercises[1];
		$stmt = qq(select name from exercise where id = '$eid'); 
		$sth1 = $dbh->prepare($stmt);
		$rv = $sth1->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row1 = $sth1->fetchrow_array();
		my $name = $row1[0];
		$stmt = qq(select reps, weight from sets where wcid = '$wcid'); 
		$sth2 = $dbh->prepare($stmt);
		$rv = $sth2->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		my $n = 0;
		my @reps;
		my @weight;
		my $setsbool = 0;
		my $first;
		while (my @row2 = $sth2->fetchrow_array()) {
			if (@row2) {
				$setsbool = 1;
				$reps[$n] = $row2[0];
				$weight[$n] = $row2[1];
				$n++;
			} else {
				last;
			}
		}
		$html .= qq(<input type="text" name="eid" value="$eid" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;"><br>
		<input type="submit" name="show_exercise" value="$name);
		if ($setsbool) {
			$samereps = 1;
			$repsinset = $reps[0];
			foreach $rep (@reps) {
				if ($rep != $repsinset) {
					$samereps = 0;
				}
			}
			$html.= qq( \($n sets);
			if ($samereps) {
				$html .= qq( x $repsinset reps);
			} else {
				$html .= qq( - );
				my $i = 0;
				while ($i < $n) {
					$html .= qq($reps[$i]);
					if ($weight ne "" && $weight[$i] > 0) {
						$html .= qq( x $weight[$i] kg);
					}
					$html .= qq(, );
					$i++;
				}
			}
			$html =~ s/, $//;
			$html .= qq(\));
		}
		$html .= qq(" class="button" style="font-size:16pt;height:45px;width:750px;"><br>
		<pre> </pre>);
		$html .= hidden('username');
		$html .= hidden('password');
		$html .= hidden('exercise_date');
		$html .= hidden('workout');
		$html .= hidden('wid');
		$html .= qq(</form>);
	}
	my $search_term = param('search_term');
	$html .= qq(<form action="doyouevenfit.cgi" method="post">
	<pre> </pre> <pre> </pre>);
	if (!defined param('insert_exercise') || !defined param('exercise_selected')) {
		if (defined param('add_exercise') || defined param('search_again') || (defined param('search_exercise') && param('search_term') eq "" && !defined param('muscle'))) {
			$html .= qq(<text style="color:white;font-size:20pt;">Name<p></p>
			<input type="text" name="search_term" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;width:300px;font-family:AmbleRegular;"value="$search_term" onfocus="javascript:if(this.value=='')this.value='';"><br>
			<pre> </pre>
			<text style="color:white;font-size:20pt;">Muscle Group<p></p>
		      	<select name="muscle" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:392px;width:300px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
			 );
			$driver = "SQLite"; 
			$database = "project.db"; 
			$dsn = "DBI:$driver:dbname=$database";
			$userid = ""; $dbpassword = "";  
			$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr;
			$stmt = qq(select distinct muscle from exercise order by muscle); 
			$sth = $dbh->prepare($stmt);
			$rv = $sth->execute() or die $DBI::errstr; 
			if ($rv < 0) {
				print $DBI::errstr;
			}
			$muscle = param('muscle');
			while (my @row = $sth->fetchrow_array()) {
				if ($row[0] ne "") {
					$html .= qq(<option);
					if ($row[0] eq $muscle) {
						$html .= " selected";
					}
					$html .= qq(>$row[0]
					);
				}
			}
			$html .= qq(</select>
			<pre> </pre>
			<input type="submit" name="search_exercise" value="SEARCH EXERCISE" class="button" style="height:45px;width:350px;"><br>);
		} elsif (param('search_term') ne "" || defined param('muscle')) {
			$html .= qq(<text style="color:white;font-size:20pt;">Search Results<p></p>
		      	<select name="exercise_selected" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:210px;width:500px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
			 );
			$driver = "SQLite"; 
			$database = "project.db"; 
			$dsn = "DBI:$driver:dbname=$database";
			$userid = ""; $dbpassword = "";  
			$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr;
			if (param('search_term') ne "" && defined param('muscle')) {
				my $search = param('search_term');
				my $muscle = param('muscle');
				$stmt = qq(select name from exercise where name like "%$search%" and muscle = "$muscle"); 
				$sth = $dbh->prepare($stmt);
				$rv = $sth->execute() or die $DBI::errstr; 
				if ($rv < 0) {
					print $DBI::errstr;
				}
				my $n = 0;
				while (my @row = $sth->fetchrow_array()) {
					$html .= qq(<option>$row[0]);
					$n++;
				}
			} elsif (param('search_term') ne "") {
				my $search = param('search_term');
				$stmt = qq(select name from exercise where name like "%$search%"); 
				$sth = $dbh->prepare($stmt);
				$rv = $sth->execute() or die $DBI::errstr; 
				if ($rv < 0) {
					print $DBI::errstr;
				}
				my $n = 0;
				while (my @row = $sth->fetchrow_array()) {
					$html .= qq(<option>$row[0]);
					$n++;
				}
			} elsif (defined param('muscle')) {
				my $muscle = param('muscle');
				$stmt = qq(select name from exercise where muscle = "$muscle"); 
				$sth = $dbh->prepare($stmt);
				$rv = $sth->execute() or die $DBI::errstr; 
				if ($rv < 0) {
					print $DBI::errstr;
				}
				my $n = 0;
				while (my @row = $sth->fetchrow_array()) {
					$html .= qq(<option>$row[0]);
					$n++;
				}
			}
			$html .= qq(</select>
			<pre> </pre>
			<input type="submit" name="insert_exercise" value="ADD TO WORKOUT" class="button" style="height:45px;width:300px;"><br>
			<pre> </pre>
			<input type="submit" name="search_again" value="SEARCH AGAIN" class="button" style="height:45px;width:250px;"><br>);
			$html .= hidden('search_term');
			$html .= hidden('muscle');
		} else {
			$html .= qq(<input type="submit" name="add_exercise" value="+ ADD EXERCISE" class="button" style="height:45px;width:250px;"><br>);
		}
	} else {
		$html .= qq(<input type="submit" name="add_exercise" value="+ ADD EXERCISE" class="button" style="height:45px;width:250px;"><br>);
	}
	$html .= qq(<pre> </pre> <pre> </pre>);
	if ((!defined param('add_exercise') && !defined param('search_exercise') && !defined param('search_again') && !defined param('insert_exercise')) || (defined param('insert_exercise') && defined param('exercise_selected'))) {
		$html .= qq(<input type="submit" name="delete_workout" value="DELETE WORKOUT" class="button" style="height:45px;width:300px;"><br>
		<pre> </pre> <pre> </pre>);
	}
	$html .= qq(<input type="submit" name="back_exercise" value="BACK" class="button" style="height:45px;width:250px;"><br>
	<p>&nbsp</p>);
	$html .= hidden('username');
	$html .= hidden('password');
	$html .= hidden('exercise_date');
	$html .= hidden('workout');
	$html .= hidden('wid');
	$html.= qq(</form>);
	return $html;
}

sub show_exercise() {
	my $date = param('exercise_date');
	my $wid = param('wid');
	my $eid = param('eid');
	$driver = "SQLite"; 
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr;
	$stmt = qq(select name, muscle from exercise where id = '$eid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $name = $row[0];
	my $muscle = $row[1];
	$stmt = qq(select id from workout_contains where wid = '$wid' and eid = '$eid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $wcid = $row[0];
	my $html = qq(
	<div class="header-bottom" id="tour">
	<div class="wrap">
	<h1>$name [$muscle]</h1>
	<pre> </pre>);
	$stmt = qq(select id, reps, weight from sets where wcid = '$wcid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	my $n = 0;
	my @sid;
	my @reps;
	my @weight;
	my $setsbool = 0;
	my $first;
	while (my @row = $sth->fetchrow_array()) {
		if (@row && $row[1] != 0) {
			$setsbool = 1;
			$sid[$n] = $row[0];
			$reps[$n] = $row[1];
			$weight[$n] = $row[2];
			$n++;
		} else {
			last;
		}
	}
	if ($setsbool) {
		$html .= qq(<text style="color:white;font-size:24pt;">$n Set);
		if ($n > 1) {
			$html .= qq(s);
		}
		$html .= qq( Total <p> </p>
		<text style="color:white;font-size:24pt;"> <p> </p>
		);
		my $i = 0;
		while ($i < $n) {
			$html .= qq(<form action="doyouevenfit.cgi" method="post">
			<input type="text" name="sid" value="$sid[$i]" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;"><br>
			<input type="text" name="wcid" value="$wcid" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;"><br>
			<input type="submit" name="edit_set" value="$reps[$i] reps);
			if ($weight[$i] ne "" && $weight[$i] > 0) {
				$html .= qq( of $weight[$i] kg);
			}
			$html .= qq(" class="button" style="height:45px;width:300px;">
			<input type="submit" name="delete_set" value="X" class="button" style="height:45px;width:50px;"><br>);
			$html .= hidden('username');
			$html .= hidden('password');
			$html .= hidden('exercise_date');
			$html .= hidden('workout');
			$html .= hidden('wid');
			$html .= hidden('eid');
			$html .= qq(</form>
			<p> </p>
			);
			$i++;
		}
	}
	$html .= qq(<pre > </pre>
	<form action="doyouevenfit.cgi" method="post">
	<input type="text" name="wcid" value="$wcid" size=28 style="text-align:center;border:0px;solid:#ffffff;background-color:rgba(255,255,255,0);color:black;font-size:16pt;height:0px;width:0px;font-family:AmbleRegular;"><br>);
	if (defined param('add_set') || !$correct_input) {
		$html .= qq(<input type="text" name="reps" value="" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:36px;width:100px;font-family:AmbleRegular;><br>
		<text style="color:white;font-size:16pt;"> reps of </text>
		<input type="text" name="weight" value="" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:36px;width:100px;font-family:AmbleRegular;><br>
		<text style="color:white;font-size:16pt;"> kg</text> <pre> </pre>
		<input type="submit" name="insert_set" value="ADD TO EXERCISE" class="button" style="height:45px;width:300px;"><br>
		);
	} else {
		$html .= qq(<input type="submit" name="add_set" value="ADD SET" class="button" style="height:45px;width:250px;"><br>);
	}
	$html .= qq(<pre> </pre> <pre> </pre>
	<input type="submit" name="back_workout" value="BACK" class="button" style="height:45px;width:250px;"><br>
	<p>&nbsp</p>);
	$html .= hidden('username');
	$html .= hidden('password');
	$html .= hidden('exercise_date');
	$html .= hidden('workout');
	$html .= hidden('wid');
	$html .= hidden('eid');
	$html.= qq(</form>);
	return $html;
}

sub delete_set() {
	my $wcid = param('wcid');
	my $sid = param('sid');
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr;
	$stmt = qq(delete from sets where id = '$sid' and wcid = '$wcid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
}

sub insert_set() {
	my $wcid = param('wcid');
	my $reps = param('reps');
	my $weight = param('weight');
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr;
	$stmt = qq(insert into sets(id,wcid,reps,weight) values (null,'$wcid','$reps','$weight')); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
}

sub insert_exercise() {
	my $name = param('exercise_selected');
	my $wid = param('wid');
	$driver = "SQLite"; 
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
	$stmt = qq(select id from exercise where name = '$name'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	@row = $sth->fetchrow_array();
	my $eid = $row[0];
	$stmt = qq(insert into workout_contains values (null,'$wid','$eid')); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
}

sub delete_workout() {
	my $username = param('username');
	my $workout = param('workout');
	my $wid = param('wid');
	my $date = param('exercise_date');
	$stmt = qq(delete from workout where id = '$wid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	$stmt = qq(select id from workout_contains where wid = '$wid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
	while (my @row = $sth->fetchrow_array()) {
		$stmt = qq(delete from sets where wcid = '$row[0]'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
	}
	$stmt = qq(delete from workout_contains where wid = '$wid'); 
	$sth = $dbh->prepare($stmt);
	$rv = $sth->execute() or die $DBI::errstr; 
	if ($rv < 0) {
		print $DBI::errstr;
	}
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
	      	<select name="food_selected" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:$height;width:650px;font-family:AmbleRegular;"value="" onfocus="javascript:if(this.value=='')this.value='';"><br>
		 );
	$driver = "SQLite"; 
	$database = "project.db"; 
	$dsn = "DBI:$driver:dbname=$database";
	$userid = ""; $dbpassword = "";  
	$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
	$stmt = qq(select name from food where name like "%$userSearch%"); 
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
	$stmt = qq(select id, name, calories from food where name = "$search"); 
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
		my $mid = param('mid');
		my $date = param('diet_date');
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
		$stmt = qq(select calories from meal where id = '$mid'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		my $updated = int(($row[0] + $calories * $serving / 100) + 0.5);	# update meal calories
		$stmt = qq(insert into meal_contains values(null,'$mid','$fid','$serving'));
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
				fields => {'qlookup' => "$search",},);

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

		my $user_url = $food_urls{"$search"};
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
		my $mid = param('mid');
		my $date = param('diet_date');
		$meal =~ s/ \((\d+) calories\)$//;
		$driver = "SQLite"; 
		$database = "project.db"; 
		$dsn = "DBI:$driver:dbname=$database";
		$userid = ""; $dbpassword = "";  
		$dbh = DBI->connect($dsn, $userid, $dbpassword, { RaiseError => 1 }) or die $DBI::errstr; 
		$stmt = qq(insert into food(id,name,calories,protein,carbs,fat,fibre,sugars,monounsatfat,polyunsatfat,satfat,transfat,cholesterol) values(null,"$name",'$calories','$protein','$carbs','$fat','$fibre','$sugars','$mono','$poly','$sat','$trans','$cholesterol'));
		$rv = $dbh->do($stmt) or die $DBI::errstr;
		$stmt = qq(select id from user where username = '$username'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		my $uid = $row[0];
		$stmt = qq(select id from food where name = "$name" and calories = '$calories' and protein = '$protein' and carbs = '$carbs' and fat = '$fat'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		$fid = $row[0];
		$stmt = qq(insert into meal_contains values(null,'$mid','$fid','$serving'));
		$rv = $dbh->do($stmt) or die $DBI::errstr;
		$stmt = qq(select calories from meal where id = '$mid'); 
		$sth = $dbh->prepare($stmt);
		$rv = $sth->execute() or die $DBI::errstr; 
		if ($rv < 0) {
			print $DBI::errstr;
		}
		@row = $sth->fetchrow_array();
		my $updated = int(($row[0] + $calories * $serving / 100) + 0.5); 
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
		$stmt = qq(update calories set current = '$updated' where uid = '$uid' and date = '$date');
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
