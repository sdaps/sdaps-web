This is absolutely experimental code. It is just public in case someone
is interested in development.

This repository contains the beginning of a django application that can be
used as a frontend for SDAPS and is written in Python 3.

There is a public instance of this code running on https://demo.sdaps.org.
You can log in using the username "demo" and the password "sdapsdemo". Please
do not rely on this service for any production use.

Anyone interested in moving this forwared please drop me a line. Note that I
have not yet attached a license to it (probably GPLv3+, but I am thinking
about using some AGPL like license).

Well, that is about it for now.


----

What is working (sort of):
 * Running background tasks using celery
 * Uploading scans and importing them into projects
 * Running recognition
 * Building a questionnaire (LaTeX document)
 * Changing the questionnaire ussing angular.js
 * pdf.js based preview is working
 * Basic UI for reviewing the recognition
 * Downloading results as CSV and reports

What is missing:
 * PDF Preview widget needs proper UI
 * All pages (especially editing page) need a proper stylesheet/structure.
 * Django templats need to be reworked
 * Slow tasks should get a less important queue
 * User/rights management
 * General thoughts about usability:
   * How are surveys managed?
   * Should they be grouped?
   * How should they be sorted?
   * What should be done about surveys that are finished?
   * What kind of permission management could be interesting?

## Installation

Clone this repo:

`git clone https://github.com/sdaps/sdaps_web`

`cd sdaps_web`

`virtualenv .venv`

`source .venv/bin/activate`

`pip install -r requirements.txt`

Clone sdaps (core) in sdaps\_web repo:

`git clone https://github.com/sdaps/sdaps --recursive`

`ln -s /usr/lib/python3.7/site-packages/DistUtilsExtra .venv/lib/python3.7/site-packages/DistUtilsExtra`

`cd sdaps`

`python setup.py build`

`python setup.py install`

`export PYTHONPATH="${PYTHONPATH}:/absolute_path_to_repo_of/sdaps_web/.venv/lib/python3.7/site-packages/sdaps"` path to sdaps repo

`cd ..`

Install 'rabbitmq' and start it:

ArchLinux: `pacman -S rabbitmq` `systemctl start rabbitmq`

`cp sdaps_web/settings_sample.py sdaps_web/settings.py`

`mkdir /tmp/projects` This is our default directory for all our sdaps projects.

`python manage.py migrate` setup sqlite3 database

`python manage.py createsuperuser --username "admin"` Create an admin account.

`python manage.py runserver localhost:8080` Run the local webserver of django.

Then open another terminal window, repeat `source .venv/bin/activate` in the
same directory and the export of the PYTHONPATH above in the new terminal and
run:

`python -m celery -A sdaps_web worker -Q background,default -E`

If both (celery and django) are running, you can open `localhost:8080` in your
browser.
