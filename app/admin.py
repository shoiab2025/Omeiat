from django.contrib import admin
from .models import User, Institution, Job, JobShortlist, InstitutionApproval, OmeiatZone, JobApplication
# Register your models here.
# Register the Job model with the Django admin site to manage job listings through the admin interface.

admin.site.register(Institution)
admin.site.register(InstitutionApproval)
admin.site.register(OmeiatZone)