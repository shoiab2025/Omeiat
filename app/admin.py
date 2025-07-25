from django.contrib import admin
from .models import JobPost, User, Organization, JobCategory, JobSubCategory
# Register your models here.
# Register the Job model with the Django admin site to manage job listings through the admin interface.
admin.site.register(User)
admin.site.register(Organization)
admin.site.register(JobPost)
admin.site.register(JobCategory)
admin.site.register(JobSubCategory)
