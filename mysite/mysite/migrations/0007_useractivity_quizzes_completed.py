# Generated by Django 5.2 on 2025-04-07 00:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mysite", "0006_useractivity"),
    ]

    operations = [
        migrations.AddField(
            model_name="useractivity",
            name="quizzes_completed",
            field=models.IntegerField(default=0),
        ),
    ]
