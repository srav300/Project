#!/usr/bin/perl

use DBI;
use strict;
use WWW::Mechanize;

my $driver   = "SQLite"; 
my $database = "project.db";
my $dsn = "DBI:$driver:dbname=$database";
my $userid = "";
my $password = "";
my $dbh = DBI->connect($dsn, $userid, $password, { RaiseError => 1 }) 
                      or die $DBI::errstr;

print "Opened database successfully\n";

my $stmt = qq(CREATE TABLE user (
	id INTEGER PRIMARY KEY,
	fName TEXT,
	lName TEXT,
	username TEXT,
	password TEXT,
	email TEXT,
	gender TEXT,
	height INTEGER,
	weight INTEGER,
	age INTEGER,
	exercise TEXT,
	goal TEXT
););
my $rv = $dbh->do($stmt);
if($rv < 0){
   /*print $DBI::errstr;*/
} else {
   print "Table created successfully\n";
}

my $stmt = qq(CREATE TABLE weight (
	id INTEGER PRIMARY KEY,
	uid INTEGER,
	value INTEGER,
	date TEXT,
	FOREIGN KEY(uid) REFERENCES user(id)
););
my $rv = $dbh->do($stmt);
if($rv < 0){
   print $DBI::errstr;
} else {
   print "Table created successfully\n";
}

my $stmt = qq(create TABLE meal (
	id INTEGER PRIMARY KEY,
	uid INTEGER,
	name TEXT,
	calories INTEGER,
	date TEXT,
	FOREIGN KEY(uid) REFERENCES user(id)
););
my $rv = $dbh->do($stmt);
if($rv < 0){
   print $DBI::errstr;
} else {
   print "Table created successfully\n";
}

my $stmt = qq(create TABLE food (
	id INTEGER PRIMARY KEY,
	name TEXT,
	calories TEXT,
	protein TEXT,
	carbs TEXT,
	fat TEXT,
	fibre TEXT,
	sugars TEXT,
	monounsatfat TEXT,
	polyunsatfat TEXT,
	satfat TEXT,
	transfat TEXT,
	cholesterol TEXT
););
my $rv = $dbh->do($stmt);
if($rv < 0){
   print $DBI::errstr;
} else {
   print "Table created successfully\n";
}

my $stmt = qq(create TABLE minerals (
	fid INTEGER,
	calcium TEXT,
	iron TEXT,
	magnesium TEXT,
	manganese TEXT,
	phosphorous TEXT,
	potassium TEXT,
	sodium TEXT,
	zinc TEXT,
	FOREIGN KEY(fid) REFERENCES food(id)
););
my $rv = $dbh->do($stmt);
if($rv < 0){
   print $DBI::errstr;
} else {
   print "Table created successfully\n";
}

my $stmt = qq(create TABLE vitamins (
	fid INTEGER,
	A TEXT,
	B1 TEXT,
	B2 TEXT,
	B3 TEXT,
	B5 TEXT,
	B6 TEXT,
	B7 TEXT,
	B9 TEXT,
	B12 TEXT,
	C TEXT,
	D TEXT,
	E TEXT,
	K TEXT,
	FOREIGN KEY(fid) REFERENCES food(id)
););
my $rv = $dbh->do($stmt);
if($rv < 0){
   print $DBI::errstr;
} else {
   print "Table created successfully\n";
}

my $stmt = qq(create TABLE meal_contains (
	mid INTEGER,
	fid INTEGER,
	serving INTEGER,
	FOREIGN KEY(mid) REFERENCES meal(id),
	FOREIGN KEY(fid) REFERENCES food(id)
););
my $rv = $dbh->do($stmt);
if($rv < 0){
   print $DBI::errstr;
} else {
   print "Table created successfully\n";
}

my $stmt = qq(CREATE TABLE calories (
	uid INTEGER,
	current INTEGER,
	goal INTEGER,
	date TEXT,
	FOREIGN KEY(uid) REFERENCES user(id)
););
my $rv = $dbh->do($stmt);
if($rv < 0){
   /*print $DBI::errstr;*/
} else {
   print "Table created successfully\n";
}

my $stmt = qq(create TABLE routine (
	id INTEGER PRIMARY KEY,
	uid INTEGER,
	name TEXT,
	FOREIGN KEY(uid) REFERENCES user(id)
););
my $rv = $dbh->do($stmt);
if($rv < 0){
   print $DBI::errstr;
} else {
   print "Table created successfully\n";
}

my $stmt = qq(create TABLE exercise (
	id INTEGER PRIMARY KEY,
	name TEXT,
	muscle TEXT
););
my $rv = $dbh->do($stmt);
if($rv < 0){
   print $DBI::errstr;
} else {
   print "Table created successfully\n";
}

my $stmt = qq(create TABLE routine_contains (
	rid INTEGER,
	eid INTEGER,
	weight INTEGER,
	reps INTEGER,
	sets INTEGER,
	duration INTEGER,
	measurement TEXT,
	FOREIGN KEY(rid) REFERENCES routine(id),
	FOREIGN KEY(eid) REFERENCES exercise(id)
););
my $rv = $dbh->do($stmt);
if($rv < 0){
   print $DBI::errstr;
} else {
   print "Table created successfully\n";
}

my $stmt = qq(create TABLE day_routines (
	uid INTEGER,
	rid INTEGER,
	date TEXT,
	timestamp INTEGER,
	FOREIGN KEY(uid) REFERENCES user(id),
	FOREIGN KEY(rid) REFERENCES routine(id)
););
my $rv = $dbh->do($stmt);
if($rv < 0){
   print $DBI::errstr;
} else {
   print "Table created successfully\n";
}

for my $alpha ('a'..'z') {
	my $mech = WWW::Mechanize->new;
	$mech->get("http:\/\/www\.bodybuilding\.com\/exercises\/list\/index\/selected\/$alpha");
	my $content = $mech->content;
	my @matches = ($content =~ m/<h3><a.*?>(.*?)<\/a>.*\n*.*?<p>.*?<span><a.*?>(.*?)<\/a>/g);
	my $size = @matches;
	for my $curr (0..$size-1){
		if($curr%2 ne 0){
			my $name = $matches[$curr-1];
			$name =~ s/^\s*//;
			$name =~ s/\s*$//;
			my $muscle = $matches[$curr];
			$muscle =~ s/^\s*//;
			$muscle =~ s/\s*$//;
			$stmt = qq(insert into exercise (id, name, muscle) values (null, "$name", '$muscle'));					
			my $rv = $dbh->do($stmt) or die $DBI::errstr;		
		}	
	}
}

$stmt = qq(insert into user values(null,'admin','istrator','admin','doyoueven', 'doyouevenfit.com', 'Male', 183, 85, 21, 'Moderately Active', 'Maintain Weight')); 
my $rv = $dbh->do($stmt) or die $DBI::errstr; 

$dbh->disconnect();
