from django.db import models
from django.contrib.auth.models import User  # Import the built-in User model
from datetime import timedelta, date, datetime


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.username

class FlashcardSet(models.Model):
    set_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, null=False)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title  # Display the title of the deck

class Flashcard(models.Model):
    card_id = models.AutoField(primary_key=True)
    flashcard_set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE)
    question = models.TextField(null=False)
    answer = models.TextField(null=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_learned = models.BooleanField(default=False)
    level = models.IntegerField(default=1)  # Flashcard's current review level
    next_review_date = models.DateTimeField(default=datetime.now)

    def promote(self):
        """Move the flashcard to the next level and update review date."""
        if self.level < 5:
            self.level += 1

        # Define review intervals based on levels
        review_intervals = [1, 2, 4, 7, 14]  # Days until next review
        self.next_review_date = date.today() + timedelta(days=review_intervals[self.level - 1])
        self.save()

    def demote(self):
        """Reset the flashcard to level 1 if answered incorrectly."""
        self.level = 1
        self.next_review_date = date.today() + timedelta(days=1)
        self.save()

class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.TextField(null=False)

class ProgressTracking(models.Model):
    progress_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Reference to the built-in User model
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE)
    correctly_answered = models.IntegerField(default=0)
    last_reviewed = models.DateTimeField(auto_now=True)

class FavoriteSet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'set')

    def __str__(self):
        return f"{self.user.username} - {self.set.title}"
