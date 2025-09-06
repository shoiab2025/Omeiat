from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from app.views.job import jobs as job_views
from app.views.dashboard.dashboard import dashboard_view, latest_jobs_views
from app.views.authentication.authentication import user_login, user_logout, update_user, register_user

# from .views import UserViewSet, JobPostViewSet, OrganizationViewSet, JobCategoryViewSet, JobSubCategoryViewSet

# Create a router and register our viewsets with it
# router = DefaultRouter()
# router.register(r'users', UserViewSet)
# router.register(r'jobposts', JobPostViewSet)
# router.register(r'organizations', OrganizationViewSet)
# router.register(r'jobcategories', JobCategoryViewSet)
# router.register(r'jobsubcategories', JobSubCategoryViewSet)

urlpatterns = [
    path("",
         dashboard_view,                  
         name="home"),

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
        "apply_job/<int:job_id>",
        job_views.apply_job,
        name="apply_job",
    ),
    path(
        "applied_jobs",
        job_views.get_applied_jobs,
        name="applied_jobs",
    ),
    
    path(
        'withdraw/<int:application_id>/', 
        job_views.withdraw_application, 
        name='withdraw_application'),
    
    path(
        "profile",
        TemplateView.as_view(template_name="profile.html"),
        name="profile",
    ),
    
    path (
        "update_profile",
        update_user,
        name="update_profile",
    ),
    
    path("login/", user_login, name="login"),
    path(
        "logout",
        user_logout,
        name="logout",
    ),
    path(
        "register",
        register_user,
        name="register",
    ),
]
