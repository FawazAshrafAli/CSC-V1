from django.db import models
from django.utils.text import slugify
from services.models import Service
from products.models import Product

class State(models.Model):
    state = models.CharField(max_length=150)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.state


class District(models.Model):
    district = models.CharField(max_length=150)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'districts'

    def __str__(self):
        return self.district


class Block(models.Model):
    block = models.CharField(max_length=150)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blocks'

    def __str__(self):
        return self.block

class CscNameType(models.Model):
    type = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.type)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'csc_name_type'
        ordering = ["type"]

    def __str__(self):
        return self.type


class CscKeyword(models.Model):
    keyword = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.keyword)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'csc_keywords'
        ordering = ["keyword"]

    def __str__(self):
        return self.keyword

class SocialMediaLink(models.Model):
    csc_center_id = models.ForeignKey('CscCenter', on_delete=models.CASCADE)
    social_media_name = models.CharField(max_length=150)
    social_media_link = models.URLField()

    def __str__(self):
        return f"{self.social_media_name} for {self.csc_center_id.name}"

class CscCenter(models.Model):
    name = models.CharField(max_length=150, unique=True)
    type = models.ForeignKey(CscNameType, on_delete=models.CASCADE)
    keywords = models.ManyToManyField(CscKeyword)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    location = models.TextField()
    zipcode = models.CharField(max_length=15)
    landmark_or_building_name = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    
    logo = models.ImageField(upload_to='csc_center_logos/')
    banner = models.ImageField(upload_to='csc_center_banners/')

    description = models.TextField()
    contact_number = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    website = models.URLField(max_length=100, null=True, blank=True)
    services = models.ManyToManyField(Service)
    products = models.ManyToManyField(Product)

    mon_opening_time = models.TimeField(null=True, blank=True)
    tue_opening_time = models.TimeField(null=True, blank=True)
    wed_opening_time = models.TimeField(null=True, blank=True)
    thu_opening_time = models.TimeField(null=True, blank=True)
    fri_opening_time = models.TimeField(null=True, blank=True)
    sat_opening_time = models.TimeField(null=True, blank=True)
    sun_opening_time = models.TimeField(null=True, blank=True)

    mon_closing_time = models.TimeField(null=True, blank=True)
    tue_closing_time = models.TimeField(null=True, blank=True)
    wed_closing_time = models.TimeField(null=True, blank=True)
    thu_closing_time = models.TimeField(null=True, blank=True)
    fri_closing_time = models.TimeField(null=True, blank=True)
    sat_closing_time = models.TimeField(null=True, blank=True)
    sun_closing_time = models.TimeField(null=True, blank=True)

    social_media_links = models.ManyToManyField(SocialMediaLink)

    location_latitude = models.CharField(max_length=50)
    location_longitude = models.CharField(max_length=50)

    class Meta:
        db_table = 'csc_center'

    def __str__(self):
        return self.name