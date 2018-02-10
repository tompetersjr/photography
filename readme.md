# Photography

The goal of this site is to allow a photographer to share photos securely with friends, family and clients.  It also allows for a photographer to share their work publically.

Be warned this is a work in progress.  Feel free to contribute pull requests.  As of right now most of the functionality is missing.  Any feedback is welcome as well.

## Helpfull Utilities

The docker config installs the following helpful utilities.

- [pgAdmin](http://localhost:5050/browser/) - Database Administation
- [Flower](http://localhost:5555/) - Celery Task Management
- [RabbitMQ](http://localhost:15672/#/) - Manage Queues for Celery
- [Mailhog](http://localhost:5050) - Development Email Server

## Installation

### Clone the Repository

```bash
git clone git@github.com:tompetersjr/photography.git
```

### Start the Application

This application can be brought up vai the docker-compose command.

```bash
cd photography
docker-compose up
```

Once everything is downloaded and running [http://localhost](http://localhost) will pull up the site.

A couple of accounts are created to test with.

Name | Username | Password | Role
-----| -------- | -------- | ----
Photo Administrator | photo | password | Administator
John Dow | jdoe | password | Administator
Dan Powers | dpowers | password | Friends
Gary Smith | gsmith | password | Freinds
Ray Winter | rwinter | password | Client, Family
Gary Sanders | gsanders | password | Family

### Optional Virtual Environment

If you would like a local virtual environment use the following assuming a debian based environment.  Handy for local IDE's like PyCharm.

```bash
python3 -m venv ~/envs/photography
source ~/envs/photography/bin/activate
pip install --upgrade pip setuptools
# Linux or OSX?
# sudo apt install exiftool 
# brew install exiftool
cd www
pip install -e ".[testing]"
```

## Development Notes

Using Alembic for database updates

```bash
alembic -c development.ini revision --autogenerate -m "initial database"
alembic -c development.ini upgrade head
```
