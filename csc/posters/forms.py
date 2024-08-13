from django import forms
from .models import Poster
from ckeditor.widgets import CKEditorWidget

class PosterDescriptionForm(forms.ModelForm):
    class Meta:
        model = Poster
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