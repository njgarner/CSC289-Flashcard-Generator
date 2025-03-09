from django.db import models
from django.contrib.auth.models import User  # Import the built-in User model


class FlashcardSet(models.Model):
    set_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, null=False)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.title  # Display the title of the set


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
    user = models.ForeignKey(
        User, on_delete=models.CASCADE
    )  # Reference to the built-in User model
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    correctly_answered = models.IntegerField(default=0)
    last_reviewed = models.DateTimeField(auto_now=True)


class FavoriteSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "set")

    def __str__(self):
        return f"{self.user.username} - {self.set.title}"
