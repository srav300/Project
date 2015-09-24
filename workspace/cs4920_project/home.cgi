#!/usr/bin/perl -w

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
warningsToBrowser(1);
use DBI;

# print start of HTML ASAP to assist debugging if there is an error in the script
print page_header();
print <<EOF;
<link href="css/style.css" rel="stylesheet" type="text/css" media="all" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
EOF

#
# HTML placed at bottom of every screen
#
sub page_header {
  return header,
      start_html("-title"=>"DoYouEvenFit"),
}

$username = param('username');
$password = param('password');

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

$systemid = $row[0];
$fName = $row[1];
$lName = $row[2];
$password = $row[4];
$email = $row[5];
$height = $row[6];
$weight = $row[7];
$dob = $row[8];
$goal = $row[9];


#
# HTML placed at bottom of every screen
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
  my $html = "";
  $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
  $html .= end_html;
  return $html;
}


        print <<EOF;
<body>
<div class="header">  
    <div class="header-top">
       <div class="wrap"> 
           <div class="logo">
        <a href="index.cgi"><img src="images/logo.png"/ width="200"></a>
       </div>
       <div class="cssmenu">
        <ul>
           <li class="active"><a href="#tour" class="scroll"></a></li>
           <li>YU, Xuange - 3439233</li>
        </ul>
        </div>
        <div class="clear"></div>
     </div>
   </div>
    <div class="wrap">
     <div class="header-bottom" id="tour">
     <div class="wrap">
          <h1><span>HOMEPAGE</span></h1>
          <h2>Hello $fName $lName, your userid is $username, email is $email.</h2>
          <h2>systemid = $systemid</h2>
          <h2>password = $password</h2>
          <h2>height = $height cm</h2>
          <h2>weight = $weight kg</h2>
          <h2>dob = $dob</h2>
          <h2>goal = $goal</h2>
EOF







print <<EOF;
     </div>
  </div>
</div>
</body>
EOF
