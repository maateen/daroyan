# Daroyan

Daroyan is a modern utility tool which integrates CloudFlare with Fail2Ban. It is written in Python3 and use MySQL/MariaDB as database. 

Fail2Ban can monitor every hit over NginX web server from NginX `access.log`. By parsing this log file, we can detect which IP is launching DDOS attack to the server. If you are using CloudFlare, you can block these IP at Web Application Firewall level. Thus CloudFlare will stop these hit before reaching at your server. Daroyan used to do this job.

The name 'Daroyan' has been derived from Bengali dictionary, which means 'Gatekeeper' in English.

# Requirements

- python3
- python3-pip
- mysql-client
- mysql-server
- fail2ban
- unzip

# Installation

For **Ubuntu 16.04 LTS**, we need to run the following command on terminal to install all requirements:

```
sudo apt-get install python3 python3-pip mysql-client mysql-server fail2ban unzip
```

Now we will install Daroyan. Please run these commands on terminal:

```
wget https://github.com/maateen/daroyan/archive/master.zip
```
```
unzip master.zip
```
```
mv daroyan-master /etc/daroyan
```
```
sudo pip3 install -r /etc/daroyan/requirements.txt
```

So Daroyan has been installed in **/etc/daroyan** directory.

# Configuration

At first, we will configure our Fail2Ban. Please, open `jail.local` with this command:

```
nano /etc/fail2ban/jail.local
```

Let's add these section in it:

```
[fail2ban-daroyan]
enabled  = true
filter   = nginx-ddos
action   = daroyan
logpath  = /var/log/nginx/access.log
maxretry = 300
findtime = 60
bantime  = 604800
```

Now run the following command on terminal:

```
nano /etc/fail2ban/action.d/daroyan.conf
```

Paste the following lines in it:

```
# Fail2Ban configuration file for Daroyan integration

[Definition]

# Option:  actionstart
# Notes.:  command executed once at the start of Fail2Ban.
# Values:  CMD
#
actionstart = touch /var/log/daroyan/fail2ban.log

# Option:  actionstop
# Notes.:  command executed once at the end of Fail2Ban
# Values:  CMD
#
actionstop = 

# Option:  actioncheck
# Notes.:  command executed once before each actionban command
# Values:  CMD
#
actioncheck = 

# Option:  actionban
# Notes.:  command executed when banning an IP. Take care that the
#          command is executed with Fail2Ban user rights.
# Tags:    See jail.conf(5) man page
# Values:  CMD
#
actionban = printf "<ip>\n" >> /var/log/daroyan/fail2ban.log

# Option:  actionunban
# Notes.:  command executed when unbanning an IP. Take care that the
#          command is executed with Fail2Ban user rights.
# Tags:    See jail.conf(5) man page
# Values:  CMD
#
actionunban = 

[Init]
```

Now run the following command on the terminal:

```
nano /etc/fail2ban/filter.d/fail2ban-daroyan.conf
```

Paste the following lines in it:

```
[Definition]
 
# Option:  failregex
#          host must be matched by a group named "host". The tag "<HOST>" can
#          be used for standard IP/hostname matching and is only an alias for
#          (?:::f{4,6}:)?(?P<host>\S+)
# Values:  TEXT
#
failregex = ^<HOST> -*
 
# Option:  ignoreregex
# Notes.:  regex to ignore. If this regex matches, the line is ignored.
# Values:  TEXT
#
ignoreregex =
```

Fail2Ban has been configured. Now we have to configure Daroyan. Open its `config.py` with following command:

```
nano /etc/daroyan/config.py
```

Please create a MySQL database and user. Then set them properly in `config.py`. 

Now we will use Upstart to ensure that Daroyan runs automatically every time the server is booted or rebooted. So, please run the following command on terminal:

```
nano /etc/init/daroyan.conf
```

Paste the following lines in it:

```bash
start on runlevel [2345]
stop on runlevel [016]
 
respawn
 
script
    python3 /etc/daroyan/daroyan.py
end script
```

Now run daroyan with following command:

```
sudo service daroyan start
```

That's all. 