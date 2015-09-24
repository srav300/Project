#!/usr/bin/perl -w

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
use DBI;
warningsToBrowser(1);

use DBI; 
$driver = "SQLite"; 
$database = "project.db"; 
$dsn = "DBI:$driver:dbname=$database"; 
$userid = ""; $password = ""; 
$dbh = DBI->connect($dsn, $userid, $password, { RaiseError => 1 }) or die $DBI::errstr; 
$stmt = qq(select password from user where username = '$username'); 
 $rv = $dbh->do($stmt) or die $DBI::errstr; 
$dbh->disconnect();


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

$username = param('username');
$password = param('password');
$path = "project.db";

open F, "$path";

$u = 0;
foreach $line (<F>) {
    chomp $line;
    $line[$u] = $line;
    if ($line[$u] =~ /password/) {
          $y = $u;
    }
    $u = $u + 1;
}
$pwd = $line[$y+1];
$pwd =~ s/^\s+//;

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

$pinput = $row[0];


if ($pinput eq $password) {
        print <<EOF;
<body>
<div class="header">  
    <div class="header-top">
       <div class="wrap"> 
           <div class="logo">
        <a href="#"><img src="images/logo.png"/ width="200"></a>
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
    <div>&nbsp</div>
    <div>&nbsp</div>
    <div>&nbsp</div>
    <div>&nbsp</div>
    <div class="wrap">
     <div class="header-bottom" id="tour">
     <div class="wrap">
          <h1><span>Checking </span>Your Details</h1>
     </div>
  </div>
</div>
</body>
<META http-equiv="refresh" content="1;URL=home.cgi?username=$username">
EOF
    } else {
print <<EOF;
<META http-equiv="refresh" content="0;URL=index.cgi?login_screen=1&error=1">
EOF
}
