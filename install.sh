#! /bin/bash
sudo apt update
sudo apt install python3-pip python3 nodejs postgresql postgresql-contrib
sudo pip3 install uvicorn
cp pgscript.sql /var/lib/postgresql
cd /var/lib/postgresql
sudo -i -u postgres psql -f pgscript.sql
sudo sed -i "s/#logging_collector = off/logging_collector = on/g" /etc/postgresql/*/main/postgresql.conf
sudo sed -i "s/#log_destination = 'stderr'/log_destination = 'jsonlog'/g" /etc/postgresql/*/main/postgresql.conf
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/*/main/postgresql.conf
sudo service postgresql restart
echo Successfully updated config and restarted service!
echo "(if there were no errors)"