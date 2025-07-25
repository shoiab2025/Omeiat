
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Permission, Group

# ---------------------
# User Manager
# ---------------------
class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "admin")
        return self.create_user(email, username, password, **extra_fields)

# ---------------------
# USER Model
# ---------------------
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
        ('employer_staff', 'Employer Staff'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('hide', 'Hide'),
    ]

    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)

    gender = models.CharField(max_length=10, choices=[
        ('Male','Male'),
        ('Female', 'Female'), 
        ('Other', 'Other'),
    ], default = 'Male')     
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='job_seeker')
    phone_number = models.CharField(max_length=15)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    education_level = models.CharField(max_length=100, blank=True, null=True)
    experience = models.IntegerField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)

    job_type = models.CharField(max_length=50, choices=[
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
    ], default='full-time')

    expected_salary = models.PositiveIntegerField(blank=True, null=True)
    resume_details = models.JSONField(default=dict, blank=True)
    language_proficiency = models.JSONField(default=dict, blank=True)
    portfolio_links = models.JSONField(default=dict, blank=True)

    dob = models.DateField(blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    profile_visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')

    registration_otp = models.CharField(max_length=6, blank=True, null=True)
    verified = models.BooleanField(default=False)

    parent_employer = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='staff_members'
    )

    has_company_profile = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name='custom_user_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions', blank=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.role})"


# ---------------------
# Organization Model
# ---------------------
class Organization(models.Model):
    ORG_TYPE_CHOICES = [
        ('company', 'Company'),
        ('school', 'School'),
        ('college', 'College'),
        ('university', 'University'),
        ('training_center', 'Training Center'),
        ('ngo', 'NGO'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organizations')
    name = models.CharField(max_length=255)
    org_type = models.CharField(max_length=50, choices=ORG_TYPE_CHOICES, default='company')
    email = models.EmailField()
    phone = models.CharField(max_length=20)       
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    address = models.TextField()
    description = models.TextField()
    industry_type = models.CharField(max_length=100, blank=True, null=True)
    education_board = models.CharField(max_length=100, blank=True, null=True)
    affiliated_university = models.CharField(max_length=255, blank=True, null=True)
    established_year = models.IntegerField(blank=True, null=True)
    org_size = models.CharField(max_length=50, blank=True, null=True)
    social_links = models.JSONField(default=dict, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.org_type})"

# ---------------------
# Job Category Models
# ---------------------
class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class JobSubCategory(models.Model):
    category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('category', 'name')

    def __str__(self):
        return f"{self.category.name} - {self.name}"

# ---------------------
# Job Post Model
# ---------------------
class JobPost(models.Model):
    JOB_TYPE_CHOICES = [
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
        ('contract', 'Contract'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('fresher', 'Fresher'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
    ]

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='job_posts')
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='posted_jobs')

    title = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full-time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='fresher')
    experience= models.PositiveIntegerField(blank=True, null=True, help_text="Experience in years")   
    salary_min = models.PositiveIntegerField(blank=True, null=True)
    salary_max = models.PositiveIntegerField(blank=True, null=True)
    skills_required = models.JSONField(default=list, blank=True)
    qualifications = models.TextField(blank=True, null=True)
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True)
    subcategory = models.ForeignKey(JobSubCategory, on_delete=models.SET_NULL, null=True, blank=True)

    application_deadline = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} at {self.organization.name}"

# ---------------------
# Job Application Model
# ---------------------
class JobApplication(models.Model):
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name='applications')
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')

    class Meta:
        unique_together = ('applicant', 'job_post')

    def __str__(self):
        return f"{self.applicant.username} applied to {self.job_post.title}"

