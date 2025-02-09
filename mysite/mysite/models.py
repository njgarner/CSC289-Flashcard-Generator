from django.db import models

class Users(models.Model):
    user_id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=50, unique=True, null=False)
    email = models.EmailField(max_length=100, unique=True, null=False)
    password_hash = models.CharField(max_length=255, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username
    userAuth_objects = models.Manager()

class FlashcardSet(models.Model):
    set_id = models.AutoField(primary_key=True)
    #user = models.ForeignKey(Users, on_delete=models.CASCADE)
    title = models.CharField(max_length=100, null=False)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, null=True)

class Flashcard(models.Model):
    card_id = models.AutoField(primary_key=True)
    flashcard_set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE)
    question = models.TextField(null=False)
    answer = models.TextField(null=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.TextField(null=False)

class ProgressTracking(models.Model):
    progress_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    correctly_answered = models.IntegerField(default=0)
    last_reviewed = models.DateTimeField(auto_now=True)

