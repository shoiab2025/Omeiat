from django.urls import path, include
from django.contrib.auth import views as auth_views
from rest_framework.routers import DefaultRouter
from . import views
from .views import UserViewSet, JobPostViewSet, OrganizationViewSet, JobCategoryViewSet, JobSubCategoryViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'jobposts', JobPostViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'jobcategories', JobCategoryViewSet)
router.register(r'jobsubcategories', JobSubCategoryViewSet)

urlpatterns = [
    path('', views.home, name='list'),
    path('job-detail/<int:id>/', views.job_view, name='job_detail'),
    path('login/', auth_views.LoginView.as_view(template_name='authentication/login.html'), name='login'),
    path('register/', auth_views.LoginView.as_view(template_name='authentication/register.html'), name='register'),
    path('register_user/', views.register_user, name='register_user'),
    path('login_user/', views.login_user, name='login_user'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('api/', include(router.urls)),
]
