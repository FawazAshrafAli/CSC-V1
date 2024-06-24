from django import forms
from services.models import Service

class UpdateServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "image", "description"]


class CreateServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["name", "image", "description"]
