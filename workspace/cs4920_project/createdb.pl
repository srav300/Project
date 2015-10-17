#!/usr/bin/perl

use DBI;
use strict;

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
	muscle TEXT,
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

$dbh->disconnect();
