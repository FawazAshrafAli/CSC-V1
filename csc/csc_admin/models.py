from django.db import models
from django.utils.text import slugify

from csc_center.models import CscCenter

class CscCenterAction(models.Model):
    csc_center = models.ForeignKey(CscCenter, on_delete=models.CASCADE)
    rejection_reason = models.TextField()
    feedback = models.TextField()

    slug = models.SlugField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.csc_center.name)
            self.slug = base_slug
            count = 1
            while CscCenter.objects.filter(slug = self.slug).exists():
                self.slug = f"{self.slug}-{count}"
                count += 1

        super().save(*args, **kwargs)

    class Meta:
        ordering = ["-updated"]
        db_table = 'csc_center_action'

    def __str__(self):
        return self.csc_center.name