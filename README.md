# Django Fleet Management Server

Django API REST server to fleet management.

## Setup
### Install dependencies
To install packages and libraries, use the following command:
```shell
pip install -r requirements.txt
```

### Create env

To configure the variables you must create / edit an `.env` file. Content should be something like...
```shell
SECRET_KEY = 'eizc1oq6sfdb+&cjvj7z8_#=_=qdfgwc!a6%w8qs6ln3!9_whr'

SMTP_PORT = 465
SMTP_SERVER = 'smtp.gmail.com'

EMAILS_STATUS = 'disabled'
SENDER_EMAIL = 'testing@gmail.com'
SENDER_PASSWORD = 'password'

TRACCAR_URL = 'http://localhost'
TRACCAR_PORT = 8082
TRACCAR_USER = 'admin'
TRACCAR_PASSWORD = 'admin'

SERVER_URL = 'https://fleetmanagement.com'

# Fake admin
FAKE_ADMIN_FULLNAME = 'Fake Admin'
FAKE_ADMIN_EMAIL = 'adminFake@fake.com'
FAKE_ADMIN_PASSWORD = 'fakePassword'
```

Now, I'm going to explain the env variables, and what values can be set.

* `SECRET_KEY`: A key for Django, you can generate one [here](https://djecrety.ir/)
* `SMTP_PORT`: Port number for smtp. It's recommended to use Gmail server, 465.
* `SMTP_SERVER`: Url for smtp. It's recommended to use Gmail server, "smtp.gmail.com".
* `EMAILS_STATUS`: It's possible to enable or disable emails with this variable. Set "enabled" or "disabled".
* `SENDER_EMAIL`: Email account to send emails, i.e. "email_sender@gmail.com"
* `SENDER_PASSWORD`: Email account password. It must be an app password.
* `TRACCAR_URL`: Traccar url or ip. If you are using localhost, set "http://localhost"
* `TRACCAR_PORT`: Traccar port, by default Traccar use 8082, so set it.
* `TRACCAR_USER`: Traccar user, by default Traccar use "admin". If you have replaced it, do it here too.
* `TRACCAR_PASSWORD`: Traccar password, by default Traccar use "admin". If you have replaced it, do it here too.
* `SERVER_URL`: Url or server. This will be used in emails to know where to connect.

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
python manage.py dumpdata -e contenttypes -e auth --e authtoken --format yaml -o fixtures/fixture.yaml
```

Here, we are excluding `authtoken`. So user's tokens aren't saved. Why? Because, tokens are created each time 
a user is created automatically. If we save tokens and users into `fixture.yaml`. Then, if you load it, users 
are going to be created with respectively tokens. After that, tokens of `fixture.yaml` will fail being created 
because it cannot exist two tokens for same user.

### Load initial data (Optional)

If you want to load initial data, use the following command.

```shell
python manage.py loaddata fixtures/fixture.yaml
```
