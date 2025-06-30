from django.contrib.auth.models import AbstractUser
#from django.contrib.auth.models import User
from django.conf import settings 
from django.db import models

class CustomUser(AbstractUser):
      background_choice = models.CharField(max_length=20, blank=True, null=True)
class Book(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    image_path = models.CharField(max_length=200, default='', blank=True)  # ✅ New
    content = models.TextField()  # HTML/text version of book
    order = models.PositiveIntegerField(default=1)  # To unlock in sequence
    has_quiz = models.BooleanField(default=True)  # ✅ New

# models.py
class UserBookProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    has_read = models.BooleanField(default=False)
    quiz_completed = models.BooleanField(default=False)
    purchased = models.BooleanField(default=False)  # ✅ Add this field
# models.py
class PageReadProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    page_number = models.IntegerField()
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'book', 'page_number')
