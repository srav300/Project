# CLICK EDIT TO VIEW READABLE FORMAT


FOR LINUX (go to this link for windows or mac http://www.tutorialspoint.com/sqlite/sqlite_installation.htm)

To install SQLite3
Go to this page http://www.sqlite.org/download.html and download sqlite-autoconf-3081101

$ tar xvfz sqlite-autoconf-3081101.tar.gz
$ cd sqlite-autoconf-3081101
$ ./configure
$ make
$ sudo make install

FOR LINUX  (go to this link for windows or mac http://www.tutorialspoint.com/sqlite/sqlite_perl.htm)

To install the Perl DBI API
$ wget http://search.cpan.org/CPAN/authors/id/T/TI/TIMB/DBI-1.634.tar.gz
$ tar xvfz DBI-1.634.tar.gz
$ cd DBI-1.634
$ perl Makefile.PL
$ make
$ sudo make install

To install SQLite driver for DBI
$ wget http://search.cpan.org/CPAN/authors/id/M/MS/MSERGEANT/DBD-SQLite-1.14.tar.gz
$ tar xvfz DBD-SQLite-1.14.tar.gz
$ cd DBD-SQLite-1.14
$ perl Makefile.PL
$ make
$ sudo make install

To run CGI script locally in ubuntu

sudo apt-get install apache2

DOWNLOAD PROJECT ZIP ON GITHUB
UNZIP AND THEN GO INTO PROJECT DIRECTORY

DOYOUEVENFIT.CGI AND CREATEDB.PL SHOULD BE IN /usr/lib/cgi-bin
sudo mv doyouevenfit.cgi /usr/lib/cgi-bin

RUN CREATEDB.PL TO CREATE DATABASE FILE PROJECT.DB
sudo perl createdb.pl

ACCOMPANYING FILES SHOULD BE IN /var/www/html
sudo mv images /var/www/html
sudo mv css /var/www/html
sudo mv fonts /var/www/html
sudo mv js /var/www/html
cd /var/www/html
sudo chmod 755 *
cd /usr/lib/cgi-bin
sudo chmod 755 *.cgi
sudo a2enmod cgi
sudo service apache2 restart

CGI SCRIPT NEEDS PERMISSION TO WRITE TO DATABASE
sudo chown www-data:www-data /usr/lib/cgi-bin/project.db

URL TO VIEW IN BROWSER
http://localhost/cgi-bin/doyouevenfit.cgi

NEED TO INSTALL THESE MODULES (HOW TO INSTALL IN READMEs)
http://search.cpan.org/~stbey/Carp-Clan-6.04/lib/Carp/Clan.pod
http://search.cpan.org/~stbey/Date-Calc-6.4/lib/Date/Calc.pod
http://search.cpan.org/~ether/WWW-Mechanize-1.75/lib/WWW/Mechanize.pm


//inserting null into an 'integer primary key' will autoincrement
