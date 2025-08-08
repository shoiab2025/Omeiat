from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

# from .views import UserViewSet, JobPostViewSet, OrganizationViewSet, JobCategoryViewSet, JobSubCategoryViewSet

# Create a router and register our viewsets with it
# router = DefaultRouter()
# router.register(r'users', UserViewSet)
# router.register(r'jobposts', JobPostViewSet)
# router.register(r'organizations', OrganizationViewSet)
# router.register(r'jobcategories', JobCategoryViewSet)
# router.register(r'jobsubcategories', JobSubCategoryViewSet)

urlpatterns = [
    path('', TemplateView.as_view(template_name='dashboard.html'), name='home'),
     path(
        "jobs",
        TemplateView.as_view(template_name="user_jobs.html"),
        name="jobs",
    ),
    
    path(
        "jobs_details/<int:job_id>",
        TemplateView.as_view(template_name="job_details.html"),
        name="job_details",
    ),
    
    path(
        "applied_jobs",
        TemplateView.as_view(template_name="applied_details.html"),
        name="applied_jobs",
    ),
    
    path(
        "profile",
        TemplateView.as_view(template_name="profile.html"),
        name="profile",
    ),
]


