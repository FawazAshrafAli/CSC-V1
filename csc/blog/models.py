from django.db import models
from authentication.models import User
from ckeditor.fields import RichTextField
from django.utils.text import slugify

class Blog(models.Model):
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)  # If you want a featured image
    title = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = RichTextField()
    summary = models.TextField(max_length=500, blank=True)  # A short summary of the post
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)  # When the post is published
    status = models.CharField(max_length=20, default="Draft")
    categories = models.ManyToManyField('Category', related_name='blog_posts')
    tags = models.ManyToManyField('Tag', related_name='blog_posts')

    def save(self, *args, **kwargs):        
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def get_tags(self):
        tags = self.tags.all()
        tag_count = self.tags.count()
        tag_string = ''
        for i in range(tag_count): 
            if i != tag_count - 1:
                tag_string += tags[i].name + ', '
            else:
                tag_string += tags[i].name
        return tag_string
    
    @property
    def get_categories(self):
        categories = self.categories.all()
        category_count = self.categories.count()
        category_string = ''
        for i in range(category_count):
            if i != category_count - 1:
                category_string += categories[i].name + ', '
            else:
                category_string += categories[i].name
        return category_string

            

    class Meta:
        ordering = ['-created_at']
        db_table = 'blog'

    def __str__(self):
        return self.title

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'blog_category'

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if self.name not in ['', ' '] and self.name is not None:
            if not self.slug:
                self.slug = slugify(self.name)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name
