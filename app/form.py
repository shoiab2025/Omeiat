from django import forms
from .models import (
    OmeiatZone, Institution, InstitutionAddress, InstitutionStrength, InstitutionContact,
    User, UserAddress, Education, WorkExperience, Skill, Language,
    Job, JobApplication, JobShortlist, Notification, InstitutionApproval
)


# ----------------------------
# Omeiat Zone Form
# ----------------------------
class OmeiatZoneForm(forms.ModelForm):
    class Meta:
        model = OmeiatZone
        fields = ["name"]


# ----------------------------
# Institution Form
# ----------------------------
class InstitutionForm(forms.ModelForm):
    class Meta:
        model = Institution
        fields = [
            "name", "category", "email", "phone", "website", "logo",
            "year_established", "board", "omeiat_zone", "is_omeiat_member",
            "omeiat_member_since", "otp", "is_otp_verified", "password"
        ]
        widgets = {
            "password": forms.PasswordInput(),
        }


# ----------------------------
# Institution Address Form
# ----------------------------
class InstitutionAddressForm(forms.ModelForm):
    class Meta:
        model = InstitutionAddress
        fields = [
            "building_no", "street", "area", "city", "district",
            "state", "country", "pincode",
        ]


# ----------------------------
# Institution Strength Form
# ----------------------------
class InstitutionStrengthForm(forms.ModelForm):
    class Meta:
        model = InstitutionStrength
        fields = [
            "students_male", "students_female", "teachers_male",
            "teachers_female", "non_teaching_staff",
        ]


# ----------------------------
# Institution Contact Form
# ----------------------------
class InstitutionContactForm(forms.ModelForm):
    class Meta:
        model = InstitutionContact
        fields = ["contact_type", "name", "phone", "email"]


# ----------------------------
# User Form
# ----------------------------
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "username", "first_name", "last_name", "email", "dob", "age",
            "phone", "father_name", "spouse_name", "profile_picture",
            "profile_visibility", "profile_percentage", "is_deleted",
        ]
        widgets = {
            "dob": forms.DateInput(attrs={"type": "date"}),
        }


# ----------------------------
# User Address Form
# ----------------------------
class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        fields = [
            "building_no", "street", "area", "district", "state", "pincode"
        ]


# ----------------------------
# Education Form
# ----------------------------
class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = [
            "user", "level", "institution", "degree",
            "percentage", "certificate"
        ]


# ----------------------------
# Work Experience Form
# ----------------------------
class WorkExperienceForm(forms.ModelForm):
    class Meta:
        model = WorkExperience
        fields = [
            "user", "company", "role", "start_date", "end_date",
            "is_current", "description"
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }


# ----------------------------
# Skill Form
# ----------------------------
class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ["user", "name", "level"]


# ----------------------------
# Language Form
# ----------------------------
class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ["user", "name", "proficiency"]


# ----------------------------
# Job Form
# ----------------------------
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title", "post", "category", "subcategory", "job_type", "no_of_openings",
            "posted_by", "description", "min_salary", "max_salary", "experience_needed",
            "candidate_gender", "qualifications_required", "degree_required",
            "skills_required", "certifications_required", "location", "location_range_km",
            "application_deadline", "interview_date", "job_timing", "status",
            "is_verified", "is_active",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "qualifications_required": forms.Textarea(attrs={"rows": 3}),
            "application_deadline": forms.DateInput(attrs={"type": "date"}),
            "interview_date": forms.DateInput(attrs={"type": "date"}),
            "job_timing": forms.TextInput(attrs={"placeholder": "9 AM - 5 PM"}),
            "skills_required": forms.SelectMultiple(attrs={"size": 6}),
            "certifications_required": forms.SelectMultiple(attrs={"size": 6}),
        }


# ----------------------------
# Job Application Form
# ----------------------------
class JobApplicationForm(forms.ModelForm):
    class Meta:
        model = JobApplication
        fields = [
            "applicant", "job", "institution", "job_match_percentage", "expire_date",
            "response", "joining_availability", "commute_distance_km", "status"
        ]
        widgets = {
            "expire_date": forms.DateInput(attrs={"type": "date"}),
            "joining_availability": forms.DateInput(attrs={"type": "date"}),
        }


# ----------------------------
# Job Shortlist Form
# ----------------------------
class JobShortlistForm(forms.ModelForm):
    class Meta:
        model = JobShortlist
        fields = ["job", "institution", "users"]


# ----------------------------
# Notification Form
# ----------------------------
class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = [
            "recipient", "sender", "notification_type",
            "message", "url", "is_read",
        ]


# ----------------------------
# Institution Approval Form
# ----------------------------
class InstitutionApprovalForm(forms.ModelForm):
    class Meta:
        model = InstitutionApproval
        fields = ["institution", "approved_by", "is_approved", "remarks"]
