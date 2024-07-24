from django.db import models
from django.utils.text import slugify
from services.models import Service
from products.models import Product

from django.urls import reverse

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
    name = models.CharField(max_length=150)
    slug = models.SlugField()
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

    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while CscCenter.objects.filter(slug = slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug 
        super().save(*args, **kwargs)

    @property
    def full_name(self):
        return f"{self.name} {self.type}, {self.location}"
    
    @property
    def partial_address(self):
        return f"{self.block}, {self.district}, {self.state}"
    
    @property
    def full_address(self):
        return f"{self.landmark_or_building_name}, {self.street}, {self.location} {self.zipcode}, {self.block}, {self.district}, {self.state}"
    
    @property
    def get_absolute_url(self):
        return reverse('csc_admin:csc_center', kwargs={"slug": self.slug})
    
    @property
    def get_services(self):
        if self.services:
            service_list = []
            for service in self.services.all():
                service_list.append(service.name)
            return service_list
        return None
    
    @property
    def get_products(self):
        if self.products:
            product_list = []
            for product in self.products.all():
                product_list.append(product.name)
            return product_list
        return None

    @property
    def get_keywords(self):
        if self.keywords:
            keyword_list = []
            for keyword in self.keywords.all():
                keyword_list.append(keyword.keyword)
            return keyword_list
        return None
    

    class Meta:
        db_table = 'csc_center'

    def __str__(self):
        return self.name
    


class Image(models.Model):
    name = models.CharField(max_length=150, default="No Image")
    image = models.ImageField(upload_to="rough/", blank=True, null=True)
    banner = models.ImageField(upload_to="rough_banner/", blank=True, null=True)

