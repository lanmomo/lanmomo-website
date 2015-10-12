# lanmomo-website
Website for LAN Montmorency.

* Concurrent ticket reservation
* HTML5 seat picker

## Hacking on the project

Please read the license provided in LICENSE before modifying this software.

`TL;DR` Modifying the software requires that you render your code open-source. Using this software or any part of it in another application requires the application to be fully open-source. Please read the license for more legal information.

**Windows is not supported.** See `Windows Help` section below.

### Dependencies
 * `MySQL` or `SQLite` (MySQL required for ticket reservation)
 * `Python 3`
 * `npm`
 * `bower`

#### Installing bower
 * Using npm : `npm install -g bower`

### Setup the project
 * Clone the project using `git clone ...`
 * Create a virtualenv `virtualenv env`
 * Activate virtualenv `. env/bin/activate`
 * Back-end dependencies `pip install -r requirements.txt`
 * Front-end dependencies  `bower install`
 * For MySQL, `pip3 install mysql-connector-python --allow-external mysql-connector-python`

### Working on the project
* Launch the back-end app using `./app.py`

## Using in production

**More instructions in `deploy/`**

## Windows Help
Windows is not supported. If you are not familiar with Linux, now is the time !

You can dual-boot or use a virtualisation software like VirtualBox and install a user-friendly distribution.
