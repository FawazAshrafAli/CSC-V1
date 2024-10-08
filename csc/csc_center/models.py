from django.db import models
from django.utils.text import slugify
from services.models import Service
from products.models import Product
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
import base64
from django.conf import settings
from django.utils import timezone
from datetime import timedelta, datetime

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
    

class Banner(models.Model):
    csc_center = models.ForeignKey('CscCenter', on_delete=models.CASCADE, related_name = "banner_csc_center")
    banner_image = models.ImageField(upload_to='csc_center_banners/')
    


class CscCenter(models.Model):
    qr_code_image = models.ImageField(upload_to='csc_qr_codes/', blank=True, null=True)

    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True, blank=True, null=True)
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
    banners = models.ManyToManyField(Banner)

    description = models.TextField()
    owner = models.CharField(max_length=150)
    email = models.EmailField(max_length=100)
    website = models.URLField(max_length=100, null=True, blank=True)
    contact_number = models.CharField(max_length=20)
    mobile_number = models.CharField(max_length=20)
    whatsapp_number = models.CharField(max_length=20)
    services = models.ManyToManyField(Service)
    products = models.ManyToManyField(Product)

    show_opening_hours = models.BooleanField(default=True)

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

    show_social_media_links = models.BooleanField(default = True)

    social_media_links = models.ManyToManyField(SocialMediaLink)

    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=False)

    status = models.CharField(max_length=100, default="Not Viewed")

    def save(self, *args, **kwargs):
        self.generate_qr_code_image()

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
        return f"{self.name} {self.type} {self.location}"

    @property
    def type_and_location(self):
        return f"{self.type} {self.location}"

    @property
    def partial_address(self):
        return f"{self.block}, {self.district}, {self.state}"
    
    @property
    def full_address(self):
        return f"{self.landmark_or_building_name}, {self.street}, {self.location} {self.zipcode}, {self.block}, {self.district}, {self.state}"
    
    @property
    def get_absolute_url(self):
        return reverse('home:csc_center', kwargs={"slug": self.slug})
    
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
    
    @property
    def get_keywords_as_string(self):
        if self.keywords and self.get_keywords is not None:            
            return ", ".join(self.get_keywords)
        return None

    @property
    def qr_code(self):            
        url = self.get_absolute_url
        protocol = settings.SITE_PROTOCOL  # e.g., 'http' or 'https'
        domain = settings.SITE_DOMAIN     # e.g., 'example.com'
        full_url = f"{protocol}://{domain}{url}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(full_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return qr_code_base64
    
    @property
    def live_days(self):
        today = timezone.now().date()
        created_date = self.created.date()
        return (today - created_date).days
    
    def generate_qr_code_image(self):
        url = self.get_absolute_url  
        protocol = settings.SITE_PROTOCOL 
        domain = settings.SITE_DOMAIN    
        full_url = f"{protocol}://{domain}{url}"

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10, 
            border=4,
        )
        qr.add_data(full_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        filename = f'qr_code_{self.pk}.png'
        self.qr_code_image.save(filename, ContentFile(buffer.read()), save=False)

    class Meta:
        db_table = 'csc_center'
        ordering = ["name"]

    def __str__(self):
        return self.name
    


class Image(models.Model):
    name = models.CharField(max_length=150, default="No Image")
    image = models.ImageField(upload_to="rough/", blank=True, null=True)
    banner = models.ImageField(upload_to="rough_banner/", blank=True, null=True)

