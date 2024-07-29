from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify

class Service(models.Model):
    name = models.CharField(max_length=150, unique=True)
    image = models.ImageField(upload_to="service_image/", null=True, blank=True)
    description = RichTextField(null=True, blank=True)

    slug = models.SlugField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'services'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    @property
    def first_name(self):
        if self.name.endswith(' in India'):
            return self.name.split(' in India')[0]

    def __str__(self):
        return self.name

