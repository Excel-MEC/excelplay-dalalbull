# DalalBull

## STEPS

## 1-Virtual environment
```
Create a virtual environment($ virtualenv -p python3 env_name)
Activate the environment ($ source env_name/bin/activate)
```

## 2-Install the requirements
```
pip install -r requirements.txt
```

## 3-Set up the Database 
```
Create a user (>>>CREATE USER <username> IDENTIFIED BY 'password';)
Grant all privileges (>>>GRANT ALL PRIVILEGES ON * . * TO 'USER';)
Create a database (>>>CREATE DATABASE <databasename>;)
Create a file named database.conf(Inside the directory where settings.py is present)
The contents of database.conf should be in the same format as it is give in database.conf.example
```

## 4-Migrations
```
$ python manage.py makemigrations
$ python manage.py migrate
```
## 5-Setting up Redis Server 
```
$ sudo apt-get install redis-server
$ redis-server --port <portno>
```
## 6-Start the worker in a new terminal

```
celery -A dalalbull worker -l info

(In a different terminal)
python manage.py shell 
	$ from excelplay_dalalbull.tasks import *
	$ stock_update.delay()
```

## 7-Run the server
```
$ python manage.py runserver
```