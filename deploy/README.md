# Use in production

This website is highly configured to be used by our organization, but you can alter the source code and use it for yourself. Please keep in mind that respecting the GPL is required or you will be liable to law suits.

Instructions are for Debian Jessie. Should be cloned in /opt as nginx is configured for this path.

It is recommended to install and run the application as a dedicated and unprivileged `lanmomo` user.

You are strongly advised to run this application inside a container/VM. Python dependencies will be installed on the system and may cause versioning issues if used with other applications. Contributions are welcomed to use uwsgi and virtualenv.

**Windows is not supported.** See `Windows Help` section in main README.

### Install base dependencies
* `sudo apt-get install npm python3 python3-pip nginx uwsgi uwsgi-plugin-python3 libssl-dev libffi-dev mysql-server-5.5`
* `sudo npm install grunt-cli -g`

### Install lanmomo-website
* `Create a MySQL DB 'lanmomo'`
* `cd /opt`
* `git clone https://github.com/lanmomo/lanmomo-website.git`
* `cd lanmomo-website`
* `sudo pip3 install -r requirements.txt`
* `sudo pip3 install mysql-connector-python --allow-external mysql-connector-python`
* `bower install`
* `(cd deploy && npm install)`
* `sudo cp deploy/nginx/lanmomo.org /etc/nginx/sites-enabled/`
* `cp deploy/lanmomo.service /etc/systemd/system/`
* Change config/prod_config.py to your needs
* `grunt build`
* `sudo systemctl enable lanmomo`
* `sudo systemctl start lanmomo`
* `sudo systemctl reload nginx`

## Upgrading lanmomo
* `sudo systemctl stop lanmomo`
* `cd /opt/lanmomo-website/`
* `git pull`
* Run DB migration scripts TODO
* Change config/prod_config.py to your needs
* `sudo cp deploy/lanmomo.org /etc/nginx/sites-enabled/`
* `sudo pip3 install -r requirements.txt`
* `bower install`
* `grunt build`
* `sudo systemctl start lanmomo`
* `sudo systemctl reload nginx`
