# LanMomo-Website
Website for LanMomo

## Hacking on the project

### Setup the project
 * You need `python3`, `pip` and `virtualenv`.
 * Clone the repository, `git clone ...`.
 * Run `virtualenv -p /usr/bin/python3 ./` inside the project's folder to create a virtual environment inside of it.
 * Activate the environment, `source bin/active`.
 * Install the requirements, `pip install -r requirements.txt`.
 * Create a [secret key](https://docs.djangoproject.com/en/1.7/ref/settings/#secret-key) inside the file `lanmomo/lanmomo/secret.key`.
 * Create the django database `python lanmomo/manage.py migrate`.

### When working on the project

* Use `source bin/activate` to active your `virtualenv` session.
* Use `deactive` to close your `virtualenv` sesssion.
