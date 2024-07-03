from django import forms
from services.models import Service
from ckeditor.widgets import CKEditorWidget

class UpdateServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["description"]

        widgets = {
            'description': CKEditorWidget(attrs={
                'name': 'description',
                'id': 'description'           
            }),            
        }

    class Media:
        js = (
            'ckeditor/ckeditor-init.js',
            'ckeditor/ckeditor/ckeditor.js',
        )


class CreateServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["description"]

        widgets = {
            'description': CKEditorWidget(attrs={
                'name': 'description',
                'id': 'description'           
            }),            
        }

    class Media:
        js = (
            'ckeditor/ckeditor-init.js',
            'ckeditor/ckeditor/ckeditor.js',
        )