from django.db import models  # brings the models module from the django.db package
from user_profile.models import User
from django.utils.text import slugify
# from .slugs import generate_unique_slug
from ckeditor.fields import RichTextField
from ckeditor_uploader.fields import RichTextUploadingField  # allows users to upload images and other files directly within the rich text editor.

# Create your models here.

class Category(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(null=True, blank=True)
    created_date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    #Blog is a Django model that defines the structure of a blog post in the database
class Blog(models.Model): #Blog is the "many
    user = models.ForeignKey(
        User,
        related_name='user_blogs',
        on_delete=models.CASCADE #If the user is deleted, all their associated blog posts will also be deleted.
    )
    category = models.ForeignKey(
        Category,
        related_name='category_blogs',
        on_delete=models.CASCADE # category is deleted, all associated blogs will also be deleted.
    )
  
    title = models.CharField(
        max_length=500
    )
    slug = models.SlugField(null=True, blank=True)
    banner = models.ImageField(upload_to='blog_banners')
    description = RichTextField()
    created_date = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class Comment(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user_comments',
        on_delete=models.CASCADE
    )
    blog = models.ForeignKey(
        Blog,
        related_name='blog_comments',
        on_delete=models.CASCADE
    )
    text = models.TextField()

    sentiment = models.CharField(max_length=50, null=True, blank=True)  # Add this field
    created_date = models.DateTimeField(auto_now_add=True)
    

    def __str__(self) -> str:
        return self.text
    
class Reply(models.Model):
    user = models.ForeignKey(
        User,
        related_name='user_replies',
        on_delete=models.CASCADE
    )
    comment = models.ForeignKey(
        Comment,
        related_name='comment_replies',
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.text