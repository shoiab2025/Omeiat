from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from app.views.job import jobs as job_views

# from .views import UserViewSet, JobPostViewSet, OrganizationViewSet, JobCategoryViewSet, JobSubCategoryViewSet

# Create a router and register our viewsets with it
# router = DefaultRouter()
# router.register(r'users', UserViewSet)
# router.register(r'jobposts', JobPostViewSet)
# router.register(r'organizations', OrganizationViewSet)
# router.register(r'jobcategories', JobCategoryViewSet)
# router.register(r'jobsubcategories', JobSubCategoryViewSet)

urlpatterns = [
    path("", TemplateView.as_view(template_name="dashboard.html"), name="home"),
    path(
        "jobs/",
        job_views.job_list,
        name="jobs",
    ),
    path(
        "jobs_detail/<int:job_id>",
        job_views.get_job_detail,
        name="job_detail",
    ),
    path(
        "applied_jobs",
        TemplateView.as_view(template_name="applied_jobs.html"),
        name="applied_jobs",
    ),
    path(
        "profile",
        TemplateView.as_view(template_name="profile.html"),
        name="profile",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="login.html"),
        name="login",
    ),
    path(
        "logout",
        auth_views.LogoutView.as_view(template_name="logout.html"),
        name="logout",
    ),
    path(
        "register",
        TemplateView.as_view(template_name="register.html"),
        name="register",
    ),
]
