# Django Fleet Management Server

Django API REST server to fleet management.

## Setup
### Install dependencies
To install packages and libraries, use the following command:
```
pip install -r requirements.txt
```

### Create Database
To create database use the following commands:
```
python manage.py makemigrations
python manage.py migrate
```

### Load initial data (Optional)

If you want to load initial data, use the following command.
```
python manage.py loaddata fixtures/fixture.yaml
```
