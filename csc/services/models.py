from django.db import models
from ckeditor.fields import RichTextField

class Service(models.Model):
    name = models.CharField(max_length=150)
    image = models.ImageField(upload_to="service_image/", null=True, blank=True)
    description = RichTextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name