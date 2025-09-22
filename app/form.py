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

class InstitutionRegisterForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = [
            "name", "address", "category", "email", "phone", "website",
            "omeiat_zone", "city", "state", "country", "pincode", "district",
            "year_established", "member_since", "board",
            "no_of_students", "no_of_boys", "no_of_girls",
            "no_of_gents_staff", "no_of_ladies_staff", "no_of_non_teaching_staff",
            "avg_salary_teaching", "avg_salary_non_teaching",
            "recruitment_contact", "principal_name", "coordinator_name",
            "correspondent_name", "founder_name"
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
        }
