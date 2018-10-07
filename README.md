This is absolutely experimental code. It is just public in case someone
is interested in development.

This repository contains the beginning of a django application that can be
used as a frontend for SDAPS.

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

Clone this repo:
`git clone https://github.com/sdaps/sdaps_web`
`virtualenv .venv`
`source bin/activate`
`pip install -r`requirements.txt`

Enter it `cd sdaps_web` and clone sdaps:
`git clone https://github.com/sdaps/sdaps`
`ln -s /usr/lib/python3.7/site-packages/DistUtilsExtra .venv/lib/python3.7/site-package/DistUtilsExtra`
`cd sdaps`
`python setup.py`
`export PYTHONPATH="${PYTHONPATH}:/path_of_whatever/sdaps_web/sdaps"` path to sdaps repo

Install 'rabbitmq' and start it:
ArchLinux: `pacman -S rabbitmq` `systemctl start rabbitmq`
`cp sdaps_web/settings.sample.py sdaps_web/settings.py`
`python manage.py runserver 0.0.0.0:8080`
`python -m celery -A sdaps_web worker -Q background,default`

