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
EOF

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


print <<EOF;
<body>
<div class="header">	
    <div class="header-top">
       <div class="wrap"> 

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
		   	  <h1>You Are Now<span> Logged Off</span></h1>
		   	  <h2>Thank you!</h2>
		 </div>
	</div>
<META http-equiv="refresh" content="2;URL=index.html">
</div>
</body>
EOF
