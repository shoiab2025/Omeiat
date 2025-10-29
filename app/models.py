from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
# ----------------------------
# Core Models (No Dependencies)
# ----------------------------

class OmeiatZone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Omeiat Zones"
        ordering = ['name']

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    Defines main roles: JobSeeker, Institution, Admin
    """
    ROLE_CHOICES = [
        ('job_seeker', 'Job Seeker'),
        ('institution', 'Institution'),
        ('admin', 'Admin'),
    ]
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.get_name_display()


class Permission(models.Model):
    """
    Atomic permissions that can be assigned to roles
    """
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Permissions"

    def __str__(self):
        return self.code


# ----------------------------
# User Model (Depends on Role)
# ----------------------------

class User(AbstractUser):
    dob = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    father_name = models.CharField(max_length=100, blank=True, null=True)
    spouse_name = models.CharField(max_length=100, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    profile_percentage = models.PositiveIntegerField(default=0)
    profile_visibility = models.BooleanField(default=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_otp_verified = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    def save(self, *args, **kwargs):
        from app.utils import calculate_profile_completion
        self.profile_percentage = calculate_profile_completion(self)
        super().save(*args, **kwargs)

# ----------------------------
# Institution Models (Depends on OmeiatZone)
# ----------------------------

class Institution(models.Model):
    CATEGORY_CHOICES = [
        ('Kindergarten', 'Kindergarten'),
        ('Nursery & Primary', 'Nursery & Primary'),
        ('High School', 'High School'),
        ('College', 'College'),
        ('University', 'University'),
        ('Vocational', 'Vocational'),
        ('Other', 'Other'),
    ]

    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    about = models.TextField(null=True, blank=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to="institution_logos/", blank=True, null=True)
    year_established = models.PositiveIntegerField()
    board = models.CharField(max_length=100, blank=True, null=True)
    omeiat_zone = models.ForeignKey(OmeiatZone, on_delete=models.SET_NULL, null=True, blank=True)
    is_omeiat_member = models.BooleanField(default=False)
    omeiat_member_since = models.PositiveIntegerField(blank=True, null=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    is_otp_verified = models.BooleanField(default=False)
    password = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class InstitutionAddress(models.Model):
    institution = models.OneToOneField(Institution, on_delete=models.CASCADE, related_name="address")
    building_no = models.CharField(max_length=50, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    area = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="India")
    pincode = models.CharField(max_length=10)


class InstitutionStrength(models.Model):
    institution = models.OneToOneField(Institution, on_delete=models.CASCADE, related_name="strength")
    students_male = models.PositiveIntegerField(default=0)
    students_female = models.PositiveIntegerField(default=0)
    teachers_male = models.PositiveIntegerField(default=0)
    teachers_female = models.PositiveIntegerField(default=0)
    non_teaching_staff = models.PositiveIntegerField(default=0)


class InstitutionContact(models.Model):
    CONTACT_TYPE_CHOICES = [
        ("HR", "HR"),
        ("Admin", "Admin"),
        ("Principal", "Principal"),
        ("Coordinator", "Coordinator"),
        ("Correspondent", "Correspondent"),
        ("Founder", "Founder"),
    ]
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="contacts")
    contact_type = models.CharField(max_length=50, choices=CONTACT_TYPE_CHOICES)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)


# ----------------------------
# User Profile Models (Depends on User)
# ----------------------------

class UserAddress(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="address")
    building_no = models.CharField(max_length=50, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    area = models.CharField(max_length=255, blank=True, null=True)
    district = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)


class Education(models.Model):
    LEVEL_CHOICES = [
        ("SSLC", "SSLC"),
        ("HSS", "HSS"),
        ("Diploma", "Diploma"),
        ("Bachelor", "Bachelor"),
        ("Master", "Master"),
        ("PhD", "PhD"),
        ("Other", "Other"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="educations")
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES)
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255, blank=True, null=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    certificate = models.FileField(upload_to="certificates/", blank=True, null=True)


class WorkExperience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="experiences")
    company = models.CharField(max_length=255, blank=True, null=True)
    role = models.CharField(max_length=200)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)


class Skill(models.Model):
    LEVEL_CHOICES = [
        ("Beginner", "Beginner"),
        ("Intermediate", "Intermediate"),
        ("Expert", "Expert"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="skills")
    name = models.CharField(max_length=100)
    level = models.CharField(max_length=50, choices=LEVEL_CHOICES, blank=True, null=True)


class Language(models.Model):
    PROFICIENCY_CHOICES = [
        ("Basic", "Basic"),
        ("Fluent", "Fluent"),
        ("Native", "Native")
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="languages")
    name = models.CharField(max_length=50)
    proficiency = models.CharField(max_length=50, choices=PROFICIENCY_CHOICES, blank=True, null=True)


# ----------------------------
# Job Models (Depends on User, Institution, Skill, Education)
# ----------------------------

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
    ]
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Closed', 'Closed'),
        ('Pending', 'Pending'),
        ('Cancelled', 'Cancelled'),
    ]
    GENDER_CHOICES = [
        ('Any', 'Any'),
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]
    CATEGORY_CHOICES = [
        ('teaching', 'Teaching'),
        ('non-teaching', 'Non-Teaching'),
        ('admin', 'Administration'),
        ('technical', 'Technical/IT Support'),
        ('support', 'Support Staff'),
        ('medical', 'Medical & Welfare'),
    ]
    DEPARTMENT_CHOICES = [
        ('Languages', (
            ('english', 'English'),
            ('hindi', 'Hindi'),
            ('french', 'French'),
            ('other-languages', 'Other Languages'),
        )),
        ('Science', (
            ('physics', 'Physics'),
            ('chemistry', 'Chemistry'),
            ('biology', 'Biology'),
            ('general-science', 'General Science'),
        )),
        ('Mathematics', (
            ('mathematics', 'Mathematics'),
        )),
        ('Social Studies', (
            ('history', 'History'),
            ('geography', 'Geography'),
            ('civics', 'Civics / Political Science'),
            ('economics', 'Economics'),
        )),
        ('Commerce & Business', (
            ('accounting', 'Accounting'),
            ('business-studies', 'Business Studies'),
            ('commerce', 'Commerce'),
        )),
        ('Computer / IT', (
            ('computer-science', 'Computer Science'),
            ('information-technology', 'Information Technology'),
        )),
        ('Arts & Humanities', (
            ('fine-arts', 'Fine Arts'),
            ('music', 'Music'),
            ('dance', 'Dance'),
            ('philosophy', 'Philosophy'),
            ('psychology', 'Psychology'),
        )),
        ('Vocational / Skill Development', (
            ('vocational', 'Vocational Studies'),
        )),
        ('Physical Education', (
            ('physical-education', 'Physical Education / Sports'),
        )),
        ('Administration & Support', (
            ('administration', 'Administration'),
            ('admissions', 'Admissions & Enrollment'),
            ('examinations', 'Examination Cell'),
            ('hr', 'Human Resources'),
            ('finance', 'Finance & Accounts'),
            ('library', 'Library & Information Center'),
            ('counseling', 'Counseling & Guidance'),
            ('placement', 'Placement / Career Services'),
            ('student-welfare', 'Student Welfare / Affairs'),
            ('hostel', 'Hostel / Residential Life'),
            ('it-support', 'IT Support / EdTech'),
            ('laboratories', 'Laboratory Services'),
            ('transport', 'Transport'),
            ('maintenance', 'Maintenance & Facilities'),
            ('security', 'Security & Safety'),
            ('medical', 'Medical / Health Center'),
        )),
    ]

    title = models.CharField(max_length=200)
    post = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    subcategory = models.CharField(max_length=100, blank=True, null=True)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    no_of_openings = models.PositiveIntegerField(default=1)
    posted_by = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="jobs")
    description = models.TextField()
    min_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    experience_needed = models.PositiveIntegerField(blank=True, null=True)
    candidate_gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='Any')
    qualifications_required = models.TextField(blank=True, null=True)
    degree_required = models.CharField(max_length=255, blank=True, null=True)
    skills_required = models.ManyToManyField('Skill', blank=True)
    certifications_required = models.ManyToManyField('Education', blank=True)
    location = models.CharField(max_length=200)
    location_range_km = models.PositiveIntegerField(default=0)
    application_deadline = models.DateField(default=timezone.now)
    interview_date = models.DateField(blank=True, null=True)
    job_timing = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Open')
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)


class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    ]
    RESPONSE_CHOICES = [
        ('applied', 'Applied'),
        ('interviewed', 'Interviewed'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="job_applications")
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="job_applications")
    job_match_percentage = models.PositiveIntegerField(default=0)
    cover_letter = models.TextField(blank=True, null=True)
    expire_date = models.DateField(blank=True, null=True)
    response = models.CharField(max_length=50, choices=RESPONSE_CHOICES, default='applied')
    communication_skills = models.CharField(max_length=50, null=True, blank=True)
    technical_skills = models.CharField(max_length=50, null=True, blank=True)
    experience = models.PositiveIntegerField(blank=True, null=True)
    joining_availability = models.CharField(max_length=50, blank=True, null=True)
    qualification = models.CharField(max_length=50, null=True, blank=True)
    commute_distance_km = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('applicant', 'job')


class JobShortlist(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    users = models.ManyToManyField(User, related_name='shortlisted_jobs')
    timestamp = models.DateTimeField(auto_now_add=True)


# ----------------------------
# Notification & Other Models (Depends on User, Institution)
# ----------------------------

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('job_posted', 'Job Posted'),
        ('application_status', 'Application Status Updated'),
        ('shortlisted', 'Shortlisted for Job'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('system', 'System Alert'),
        ('info', 'Info')
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    url = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']


class InstitutionApproval(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="approvals")
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    remarks = models.TextField(blank=True, null=True)
    approved_at = models.DateTimeField(auto_now_add=True)


class EmployerReviews(models.Model):
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField()
    review = models.TextField(blank=True, null=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Employer Reviews"
        ordering = ['-posted_at']

    def __str__(self):
        return f"Review for {self.institution} - {self.rating}/5"


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="permissions")
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="roles")

    class Meta:
        unique_together = ('role', 'permission')
        verbose_name_plural = "Role Permissions"

    def __str__(self):
        return f"{self.role.name} -> {self.permission.code}"