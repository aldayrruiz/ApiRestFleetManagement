# Django Fleet Management Server

Django API REST server to fleet management.

## Setup
### Install dependencies
To install packages and libraries, use the following command:
```shell
pip install -r requirements.txt
```

### Config env

To configure the variables you must edit the `.env` file

### Create Database

To create database use the following commands:

```shell
python manage.py makemigrations
python manage.py migrate
```

## Develop

### Dump initial data

```shell
python manage.py dumpdata -e contenttypes -e auth --format yaml -o fixtures/fixture.yaml
```

### Load initial data (Optional)

If you want to load initial data, use the following command.

```shell
python manage.py loaddata fixtures/fixture.yaml
```
