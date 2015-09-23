#!/usr/bin/perl -w

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;  
use List::Util qw/min max/;
warningsToBrowser(1);

print page_header();
print <<EOF;
<link href="css/style.css" rel="stylesheet" type="text/css" media="all" />
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<body background="images/banner.jpg">
<body link="white">
EOF

# some globals used through the script
$debug = 1;
$database_dir = "./database";

master_screen();


sub master_screen(){
print <<EOF;
     <div class="header-bottom" id="tour">
     <div class="wrap">
          <h1><span>D</span>o<span>Y</span>ou<span>E</span>ven<span>F</span>it</h1>
     
EOF

if (param('error') eq 1) {
  print <<EOF
<pre>

</pre>
<h2><font color="red" size="2">Your login details seems to be incorrect.</font></h2>
EOF
} else {
print <<EOF
<pre>

</pre>
<h2><font color="red" size="2">&nbsp</font></h2>
EOF
}

if ((param('login_screen') eq 1)){
print <<EOF;    
<form action="check_login.cgi" method="GET">

<input type="hidden" name="page" value="">

<input type="text" name="username" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="Username" onfocus="javascript:if(this.value=='Username')this.value='';"><br>

<input type="password" name="password" size=28 style="text-align:center;border:1px;solid:#ffffff;background-color:rgba(255,255,255,0.5);color:black;font-size:16pt;height:40px;font-family:AmbleRegular;"value="Password" onfocus="javascript:if(this.value=='Password')this.value='';"><br>

<p>&nbsp</p>

<input type="submit" value="LOG IN" class="button" style="height:45px;"><br><pre> 
</pre>
<a href="register.cgi" class="button1" class="button1" style="height:28px;">SIGN UP</a>
<p>&nbsp</p>
</form>



EOF

} else {
print <<EOF;
          <pre>
       
</pre>
<p><center><small><marquee><h2 style="color:white;">Welcome</h2></marquee></center></p></body>
<pre>

          </pre>
            <a href="?login_screen=1" class="button" role="button">GET FIT NOW</a>
     </div>
  </div>
</div>
EOF
}

print <<EOF;
<div class="footer">
    <p class="copy" style="color:#f2f5f2;font-family:AmbleRegular;">Copyright &copy; 2015. All rights reserved.</p>
</div>
  </div>
</body>
EOF
}

sub browse_screen {
  my $n = param('n') || 0;
  my @database = glob("$database_dir/*");
  $n = min(max($n, 0), $#database);
  param('n', $n + 1);
  my $student_to_show  = $database[$n];
  my $profile_filename = "$student_to_show/profile.txt";
  open my $p, "$profile_filename" or die "can not open $profile_filename: $!";
  $profile = join '', <$p>;
  close $p;
  
  return p,
    start_form, "\n",
    pre($profile),"\n",
    hidden('n', $n + 1),"\n",
    submit('Next student'),"\n",
    end_form, "\n",
    p, "\n";
}


sub page_header {
  return header,
      start_html("-title"=>"DoYouEvenFit"),
}

sub page_trailer {
  my $html = "";
  $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
  $html .= end_html;
  return $html;
}
