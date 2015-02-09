# LanMomo-Website
Website for LanMomo

## Hacking on the project

### Setup the project
 * You need `python3`, `pip` and `virtualenv`.
 * For `mysqlclient`, you need `python3-dev`, `libssl-dev` and `libmariadbclient-dev` or `libmysqlclient-dev`.
 * Clone the repository, `git clone ...`.
 * Run `virtualenv -p /usr/bin/python3 ./` inside the project's folder to create a virtual environment inside of it.
 * Activate the environment, `source bin/active`.
 * Install the requirements, `pip install -r requirements.txt`.
 * Create an environment file in `lanmomo/lanmomo/settings/env.py` (file is git ignored).
  ```python
  SETTINGS = 'lanmomo.settings.devel' # or 'lanmomo.settings.prod' or another module if you want
  SECRET_KEY = '...' # https://docs.djangoproject.com/en/1.7/ref/settings/#secret-key
  DB_USER = '...' # optional, when using mysql
  DB_PASS = '...' # optional, when using mysql
  ```
 * Create the django database `python lanmomo/manage.py migrate`.

### When working on the project

* Use `source bin/activate` to active your `virtualenv` session.
* Use `deactive` to close your `virtualenv` sesssion.
