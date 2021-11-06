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

### Manage tenants

To see all tenants...

````shell
python manage.py showtenants
````

To create a tenant...

````shell
python manage.py createtenant <tenant_name>
````

After create a tenant, you should create a superuser for that tenant...

````shell
python manage.py createsuperuser
````

While superuser creation you will be asked for tenant's id. So, copy and paste the id from `createtenant` output or
using `showtenants` scripts.

## Develop

### Dump initial data

If you want to make a backup of current state of database use ...

```shell
python manage.py dumpdata -e contenttypes -e auth --e authtoken -format yaml -o fixtures/fixture.yaml
```

### Load initial data (Optional)

If you want to load initial data, use the following command.

```shell
python manage.py loaddata fixtures/fixture.yaml
```
