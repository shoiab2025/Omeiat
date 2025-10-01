# forms.py

from django import forms
from .models import User, Job, Institution

class InstitutionRegisterForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = [
            "name", "address", "category", "email", "phone", "website",
            "omeiat_zone", "city", "state", "district", "country", "pincode",
            "year_established", "omeiat_member_since", "board",
            "no_of_students", "no_of_boys", "no_of_girls",
            "no_of_gents_staff", "no_of_ladies_staff", "no_of_non_teaching_staff",
            "recruitment_contact", "principal_name", "coordinator_name",
            "correspondent_name", "founder_name", "password"
        ]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "password": forms.PasswordInput(),
        }
        
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "name",
            "category",
            "subcategory",
            "post",
            "job_type",
            "experience_needed",
            "description",
            "location",
            "salary_min",
            "salary_max",
            "skills_required",
            "qualifications",
            "application_deadline",
            "is_active",
        ]
        widgets = {
            "application_deadline": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4}),
            "skills_required": forms.Textarea(attrs={"rows": 3}),
            "qualifications": forms.Textarea(attrs={"rows": 3}),
        }