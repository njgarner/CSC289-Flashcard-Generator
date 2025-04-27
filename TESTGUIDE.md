# Flashcard Generator Test Guide

## Overview

This guide outlines how to access the Flashlite project both locally and through a cloud-based server hosted on AWS. It details the key differences between the two environments, the corresponding testing procedures, and relevant information for each setup.

---

> ## **``Table of Contents``**

> ### <br>*Server Details*: <small>The characteristics of the separate servers</small>
> ### <br>*Testing Protocol*: <small>Guide to testing and pushing changes</small>


> ### <br>*User Instructions*: <small>Directions for accessing local and cloud servers</small>
> ### <br>*Using local*: <small>How to start a local server</small>
> ### <br>*Using AWS*: <small>How to start a AWS server</small>
> ### <br>*Using GitHub Desktop*: <small>How to use GitHub Desktop for testing</small>

> ### <br>*Database Templates*: <small>Backup code for database credentials</small>


---

# <a name="_x7m16otabon9"></a><a name="_64tqgr9am01"></a>**Server Details** 

|**Server**|**Provider**|**URL**|
| :- | :- | :- |
|Local|Django|http://127.0.0.1:8000|
|Cloud|AWS|http://ec2-54-172-119-63.compute-1.amazonaws.com:8000/login_user?next=/home|

## Testing Protocol
Think of the local server as your personal testing environment. Any changes you make locally will only affect your own machine. This is the space to test, debug, and experiment with new code. Always verify that your code works locally before pushing it to the shared cloud server.

The cloud-based server (AWS) is a shared environment—with a shared site and database. If broken or untested code is pushed here, it can disrupt everyone’s workflow. To maintain stability, only push to AWS after your changes have been fully tested and confirmed to work locally.

Code should only reach the main branch when it is functional, error-free, and does not conflict with existing code.

* **Remember** use the **local server** for testing, learning, and developing.


* **Remember** use the **cloud server** only after successful local testing.

## User Instructions

To run the project correctly, you’ll need to provide your own database credentials. This is done by editing the **__init__.py** and **settings.py** files located in your mysite folder.

### Using Local Server
Step-by-Step
1. Open the **__init__.py** and **settings.py** files in the mysite directory using your code editor.

2. Look for the sections that require database configuration (usually under DATABASES in settings.py).

3. Enter your personal MySQL credentials (username, password, host, etc.).

4. Save the changes.

**Important:** These credentials are specific to your machine. If you push them to the repository, the AWS server will crash when trying to use them.

You should follow the same CMD procedures for running a local project:

``py manage.py makemigrations ``

``py manage.py migrate ``

``py manage.py runserver ``

**Remember** the files contained within your **local folder** are now the original **AWS** files.

If successful, you can proceed with using the local server. Doing this will not affect your access to the AWS site, as the local server exists separately. Once you finish or are ready to push changes, proceed to the next section on **Using AWS**.  


### Using AWS

Keep your AWS-compatible **settings.py** and **__init__.py** in a backup or version control branch, separate from your local testing configuration.

Before pushing these files **(if ever needed)**, make sure they contain the correct AWS database credentials.

Double-check every push using **GitHub Desktop** to avoid breaking the cloud server.

The original **AWS** files should go in the **mysite** folder.


### Using GitHub Desktop

GitHub Desktop allows you to selectively push changes. Here’s how to avoid accidentally pushing sensitive credentials:

1. After committing your changes locally, open GitHub Desktop.

2. Review the changed files—you’ll see a list of everything modified.

3. Uncheck settings.py and __init__.py if they contain your personal database info.

4. Only push safe, non-sensitive code to the remote repository.

 **Push:** feature updates, bug fixes, frontend improvements, etc.
 **Don’t push:** personal database settings or any files with hardcoded local credentials.

# Database Templates

This section serves as a **backup and reference.**

Use it only as a **precaution** in case original database credentials are lost, overwritten, or misconfigured.

Below are the credential templates for both the local and AWS cloud databases.

## Django / Local Database


### \_\_init__.py

``

    database_cred = {

        "host": "localhost",

        "user": "root",

        "password": "waketech",

        "database": "flashcard_db",

        "autocommit": True,

        "cursorclass": pymysql.cursors.DictCursor,

    }
``

### settings.py

``

    DATABASES = {
      'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'flashcard_db',
        'USER': 'root',
        'PASSWORD': 'waketech',
        'HOST': 'localhost',
        'PORT': '3306',
    }

``

## AWS Database 

### \_\_init__.py

``

    database_cred = {

        "host": "localhost",

        "user": "flashcarduser",

        "password": "Group1!!",

        "database": "flashcard_db",

        "autocommit": True,  # making sure updated, inserts, deletions are commited for every query

        "cursorclass": pymysql.cursors.DictCursor,

    }

``

### settings.py

``

    DATABASES = {
      'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'flashcard_db',
        'USER': 'flashcarduser',
        'PASSWORD': 'Group1!!',
        'HOST': 'localhost',
        'PORT': '3306',
    }
``
