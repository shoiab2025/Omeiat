from rest_framework import serializers
from .models import (
    OmeiatZone, Institution, InstitutionAddress, InstitutionStrength,
    InstitutionContact, User, UserAddress, Education, WorkExperience,
    Skill, Language, Job, JobApplication, JobShortlist,
    Notification, InstitutionApproval, EmployerReviews
)

# ----------------------------
# Zone & Institution
# ----------------------------
class OmeiatZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = OmeiatZone
        fields = "__all__"


class InstitutionAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionAddress
        fields = "__all__"


class InstitutionStrengthSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionStrength
        fields = "__all__"


class InstitutionContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionContact
        fields = "__all__"


class InstitutionSerializer(serializers.ModelSerializer):
    address = InstitutionAddressSerializer(read_only=True)
    strength = InstitutionStrengthSerializer(read_only=True)
    contacts = InstitutionContactSerializer(many=True, read_only=True)

    class Meta:
        model = Institution
        fields = "__all__"


# ----------------------------
# User & Related
# ----------------------------
class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = "__all__"


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = "__all__"


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = "__all__"


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = "__all__"


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    address = UserAddressSerializer(read_only=True)
    educations = EducationSerializer(many=True, read_only=True)
    experiences = WorkExperienceSerializer(many=True, read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    languages = LanguageSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = "__all__"


# ----------------------------
# Jobs
# ----------------------------
class JobSerializer(serializers.ModelSerializer):
    skills_required = SkillSerializer(many=True, read_only=True)
    certifications_required = EducationSerializer(many=True, read_only=True)

    class Meta:
        model = Job
        fields = "__all__"


class JobApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    job = JobSerializer(read_only=True)
    institution = InstitutionSerializer(read_only=True)

    class Meta:
        model = JobApplication
        fields = "__all__"


class JobShortlistSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = JobShortlist
        fields = "__all__"


# ----------------------------
# Notifications & Approvals
# ----------------------------
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


class InstitutionApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionApproval
        fields = "__all__"


class EmployerReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployerReviews
        fields = "__all__"
