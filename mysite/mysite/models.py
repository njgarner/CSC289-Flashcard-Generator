from django.db import models
from django.contrib.auth.models import User  # Import the built-in User model
from datetime import timedelta, date, datetime
import random, string

class FlashcardSet(models.Model):
    set_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100, null=False)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    is_shared = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.title  # Display the title of the flashcard set

class Flashcard(models.Model):
    card_id = models.AutoField(primary_key=True)
    flashcard_set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE)
    question = models.TextField(max_length=200, null=False)
    answer = models.TextField(max_length=200, null=False)
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
    
class UserActivity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    quizzes_completed = models.PositiveIntegerField(default=0)
    time_spent = models.PositiveIntegerField(default=0)
    cards_viewed = models.PositiveIntegerField(default=0)
    recent_flashcard = models.ForeignKey('Flashcard', null=True, blank=True, on_delete=models.SET_NULL)
    learned_cards = models.ManyToManyField('Flashcard', related_name='learned_by', blank=True)


    def __str__(self):
        return f"Activity for {self.user.username} on {self.date_created}"
    
class Classroom(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_classrooms")
    code = models.CharField(max_length=10, unique=True, blank=True, null=True)  # Field to store join code
    students = models.ManyToManyField(User, related_name="classrooms", blank=True)  # Many-to-many relationship for students
    flashcard_sets = models.ManyToManyField('FlashcardSet', related_name='classrooms', blank=True)  # Many-to-many relationship for flashcard sets

    def save(self, *args, **kwargs):
        # Generate a unique code if it's not provided
        if not self.code:
            self.code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name} ({self.user.username})'  # Show the classroom's name and creator
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=[('student', 'Student'), ('teacher', 'Teacher')])
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
