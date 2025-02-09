# CSC289-Flashcard-Generator
Repository for CSC289 Flashcard Generator


### Classes Branch

In order to access the sqldatabase, you have to navigate to the file "settings.py" and fill in the correct info, including these 3 things:

DATABASES = {
    'default': {
        'NAME': 'flashcard_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
    }
}

^^^ This is before we have aws configured

What we have working:

We can now view these pages:

http://127.0.0.1:8000/create_deck/
http://127.0.0.1:8000/login_user
http://127.0.0.1:8000/home
http://127.0.0.1:8000/library
http://127.0.0.1:8000/settings

Things we can do (currently without user authentication):

- Add a flashcard deck
- View what decks we have in the library