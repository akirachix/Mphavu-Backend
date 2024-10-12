# analysis/forms.py
from django import forms
from .models import FootballVideo

class VideoUploadForm(forms.ModelForm):
    class Meta:
        model = FootballVideo
        fields = ['video_file']
