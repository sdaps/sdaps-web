This is absolutely experimental code. It is just public in case someone
is interested in development.

This repository contains the beginning of a django application that can be
used as a frontend for SDAPS and is written in Python 3.

There is a public instance of this code running on https://demo.sdaps.org.
You can log in using the username "demo" and the password "sdapsdemo". Please
do not rely on this service for any production use.

To contribute you can create issues and pull requests or join our
irc/matrix chat you can find on the project site https://sdaps.org

---

What is working (sort of):

- Running background tasks using celery
- Uploading scans and importing them into projects
- Running recognition
- Building a questionnaire (LaTeX document)
- Changing the questionnaire ussing angular.js
- pdf.js based preview is working
- Basic UI for reviewing the recognition
- Downloading results as CSV and reports

What is missing:

- PDF Preview widget needs proper UI
- All pages (especially editing page) need a proper stylesheet/structure.
- Django templats need to be reworked
- Slow tasks should get a less important queue
- User/rights management
- General thoughts about usability:
  - How are surveys managed?
  - Should they be grouped?
  - How should they be sorted?
  - What should be done about surveys that are finished?
  - What kind of permission management could be interesting?

## Installation (Docker setup)

First, you have to install `docker` and `docker-compose`: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

After doing that, run:

```shell
easy/init
```

This will setup the docker environment for you.

After this is finished, start the server by running:

```shell
easy/server
```

You can stop the server by running:

```shell
easy/stop-server
```

To see the logs for the currently running services and build pipelines, take a look at the following scripts:

```shell
easy/django-log
```

```shell
easy/celery-log
```

```shell
easy/svelte-log
```

If you wanna have a fresh start and wipe everything, just run:

```shell
easy/reset
```

If you want to execute arbitrary commands, you should always do it using the `easy/exec` script e.g.

```shell
easy/exec python manage.py test tests
```

to run the tests
