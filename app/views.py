import pdb
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework import viewsets

from .models import (
    User,
    JobPost,
    Organization,
    JobCategory,
    JobSubCategory,
    JobApplication,  # ✅ Make sure this model is created
)

from .serializers import (
    UserSerializer,
    JobPostSerializer,
    OrganizationSerializer,
    JobCategorySerializer,
    JobSubCategorySerializer,
)


def home(request):
    job_posts = JobPost.objects.all()
    organizations = Organization.objects.all()

    context = {
        "job_posts": job_posts,
        "organizations": organizations,
    }
    return render(request, "jobs/list.html", context)


def job_view(request, id):
    job_post = get_object_or_404(JobPost, id=id)
    context = {
        "job_post": job_post,
    }
    return render(request, "jobs/job_detail.html", context)


def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        phone = request.POST.get("phone")
        dob = request.POST.get("dob")
        email = request.POST.get("email")
        experience = request.POST.get("experience")
        skills = request.POST.get("skills")
        edlevel = request.POST.get("edlevel")
        profile_visibility = request.POST.get("profile_visibility")
        password = request.POST.get("password")

        user = User(
            username=username,
            email=email,
            phone_number=phone,
            education_level=edlevel,
            experience=experience,
            skills=skills,
            role="job_seeker",
        )
        user.set_password(password)
        user.save()

        return JsonResponse(
            {"status": "success", "message": "User registered successfully"}
        )

    return JsonResponse({"status": "error", "message": "Invalid request method"})


def login_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # set user as authenticated
            messages.success(request, f"Welcome, {user.username}!")
            return redirect("list")  # redirect to homepage or dashboard
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "login.html")


def apply_job(request, job_id):
    if request.method == "POST":
        user = request.user

        if not user.is_authenticated:
            return JsonResponse(
                {"message": "You must be logged in to apply"}, status=403
            )

        job_post = get_object_or_404(JobPost, id=job_id)

        pdb.set_trace()

        application, created = JobApplication.objects.get_or_create(
            applicant=user, job_post=job_post
        )

        if created:
            return JsonResponse({"message": "Application submitted successfully"})
        else:
            return JsonResponse({"message": "You have already applied for this job"})

    return JsonResponse({"message": "Invalid request method"}, status=405)


# ViewSets for API
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class JobPostViewSet(viewsets.ModelViewSet):
    queryset = JobPost.objects.all()
    serializer_class = JobPostSerializer


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class JobCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer


class JobSubCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobSubCategory.objects.all()
    serializer_class = JobSubCategorySerializer
