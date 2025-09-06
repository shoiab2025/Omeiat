from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# ----------------------------
# Institution Model
# ----------------------------
class Institution(models.Model):
    SCHOOLS_CATEGORIES = [
        ('Nursery', 'Nursery'),
        ('Primary', 'Primary'),
        ('High School', 'High School'),
        ('College', 'College'),
        ('University', 'University'),
        ('Vocational', 'Vocational'),
        ('Other', 'Other'),
    ]
    name = models.CharField(max_length=200)
    address = models.TextField()
    category = models.CharField(max_length=50, choices=SCHOOLS_CATEGORIES)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    omeiat_zone = models.ForeignKey('OmeiatZones', on_delete=models.SET_NULL, null=True, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pincode = models.PositiveIntegerField(default=0)  # or a valid number
    district = models.CharField(max_length=100)
    year_established = models.PositiveIntegerField()
    member_since = models.PositiveIntegerField()
    board = models.CharField(max_length=100)
    no_of_students = models.PositiveIntegerField()
    no_of_boys = models.PositiveIntegerField()
    no_of_girls = models.PositiveIntegerField()
    no_of_gents_staff = models.PositiveIntegerField()
    no_of_ladies_staff = models.PositiveIntegerField()
    no_of_non_teaching_staff = models.PositiveIntegerField()
    avg_salary_teaching = models.DecimalField(max_digits=10, decimal_places=2)
    avg_salary_non_teaching = models.DecimalField(max_digits=10, decimal_places=2)
    recruitment_contact = models.CharField(max_length=100)
    principal_name = models.CharField(max_length=100)
    coordinator_name = models.CharField(max_length=100)
    correspondent_name = models.CharField(max_length=100)
    founder_name = models.CharField(max_length=100)
    is_approved = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ----------------------------
# Custom User Model
# ----------------------------
class User(AbstractUser):
    spouse_name = models.CharField(max_length=100, blank=True)
    dob = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone = models.PositiveBigIntegerField(null=True, blank=True)
    mother_tongue = models.CharField(max_length=50, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    qualification = models.CharField(max_length=200, blank=True, null=True)
    languages_known = models.CharField(max_length=200, blank=True, null=True)
    schooling = models.CharField(max_length=200, blank=True, null=True)
    working_experience_years = models.PositiveIntegerField(null=True, blank=True)
    describing_experience = models.TextField(blank=True, null=True)
    profile_percentage = models.PositiveIntegerField(default=0)
    profile_visibility = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)

    last_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    expected_salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    reference_by_1 = models.CharField(max_length=100, blank=True, null=True)
    reference_by_2 = models.CharField(max_length=100, blank=True, null=True)
    joining_availability = models.CharField(max_length=200, blank=True, null=True)
    aim_of_life = models.TextField(blank=True, null=True)
    about_family = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


# ----------------------------
# Work Experience Model
# ----------------------------
class WorkExperience(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='experiences', on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)  # Name of the Institute
    from_date = models.DateField()
    to_date = models.DateField()
    post_assigned = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} at {self.name}"


# ----------------------------
# Job Model
# ----------------------------
class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('Full-time', 'Full-time'),
        ('Part-time', 'Part-time'),
        ('Contract', 'Contract'),
        ('Internship', 'Internship'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=100)  # e.g., Teaching, Admin
    post = models.CharField(max_length=100)
    job_type = models.CharField(max_length=50, choices=JOB_TYPE_CHOICES)
    experience_needed = models.PositiveIntegerField()
    posted_by = models.ForeignKey(Institution, on_delete=models.CASCADE)
    description = models.TextField()
    location = models.CharField(max_length=200)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2)
    skills_required = models.TextField()
    qualifications = models.TextField()
    subcategory = models.CharField(max_length=100)
    application_deadline = models.DateField()
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ----------------------------
# Job Application Model
# ----------------------------
class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
    ]

    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.username} applied to {self.job.name}"


# ----------------------------
# Job Shortlist Model
# ----------------------------
class JobShortlist(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shortlisted_jobs')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Shortlist for {self.job.name} at {self.institution.name}"


# ----------------------------
# Notification Model
# ----------------------------
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('job_posted', 'Job Posted'),
        ('application_status', 'Application Status Updated'),
        ('shortlisted', 'Shortlisted for Job'),
        ('hired', 'Hired'),
        ('rejected', 'Rejected'),
        ('system', 'System Alert'),
    ]

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='sent_notifications')

    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    url = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"To {self.recipient.username}: {self.message[:50]}"


# ----------------------------
# Omeiat Zones Model
# ----------------------------
class OmeiatZones(models.Model):
    zone_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    from_location = models.CharField(max_length=200, blank=True)
    to_location = models.CharField(max_length=200, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.zone_name
    class Meta:
        verbose_name_plural = "Omeiat Zones"
        ordering = ['zone_name']
        