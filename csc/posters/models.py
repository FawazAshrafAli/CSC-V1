from django.db import models
from django.utils.text import slugify
from ckeditor.fields import RichTextField

class Poster(models.Model):
    title = models.CharField(max_length=100)
    poster = models.ImageField(upload_to="posters/")
    description = RichTextField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            count = 1
            while Poster.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1

            self.slug = slug
        
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['title']
        db_table = 'poster'


    def __str__(self):
        return self.title
