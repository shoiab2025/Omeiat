# forms.py

from django import forms
from .models import User

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'phone_number', 'education_level', 
            'experience', 'skills', 'profile_picture', 'location'
        ]
        widgets = {
            'skills': forms.Textarea(attrs={'rows': 3}),
        }
