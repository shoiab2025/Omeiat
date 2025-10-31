# core/admin_sites.py
from django.contrib.admin import AdminSite
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import User, Institution, Job, JobShortlist, InstitutionApproval, OmeiatZone, JobApplication

class SuperAdminSite(AdminSite):
    site_header = "Super Admin Dashboard"
    site_title = "Super Admin Panel"
    index_title = "Welcome, Super Admin"

    def has_permission(self, request):
        # Allow only superusers
        return request.user.is_active and request.user.is_superuser


class AdminSiteForStaff(AdminSite):
    site_header = "Admin Dashboard"
    site_title = "Admin Panel"
    index_title = "Welcome, Admin"

    def has_permission(self, request):
        # Allow staff users but not superusers
        return request.user.is_active and request.user.is_staff and not request.user.is_superuser


# Create admin site objects
super_admin_site = SuperAdminSite(name="super_admin")
staff_admin_site = AdminSiteForStaff(name="staff_admin")


# Register models separately
super_admin_site.register(User)
super_admin_site.register(Institution)
super_admin_site.register(Job)
super_admin_site.register(JobApplication)
super_admin_site.register(JobShortlist)
super_admin_site.register(InstitutionApproval)
super_admin_site.register(OmeiatZone)
