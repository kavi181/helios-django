from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    format = models.CharField(max_length=50, default='ebook')  # added default
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='book_images/', blank=True, null=True)

