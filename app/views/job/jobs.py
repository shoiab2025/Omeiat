import pdb
from django.utils import timezone
from datetime import datetime
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import Job, JobApplication, Institution
from django.core.paginator import Paginator


def job_list(request):
    today = timezone.localdate()
    jobs = Job.objects.filter(is_active=True, application_deadline__gte=today).order_by(
        "-timestamp"
    )
    return render(request, "jobs.html", {"jobs": jobs})

def get_job_detail(request, job_id):
    pdb.set_trace()
    job = get_object_or_404(Job, id=job_id, is_active=True)
    return render(request, "job_detail.html", {"job": job})

@login_required
def apply_job(request, job_id):
    pdb.set_trace()
    job = get_object_or_404(Job, id=job_id, is_active=True)
    if request.method == "POST":

        # Check if the user has already applied for this job
        if JobApplication.objects.filter(applicant=request.user, job=job).exists():
            messages.error(request, "You have already applied for this job.")
            return HttpResponseRedirect(reverse("job_detail", args=[job_id]))

        # Create a new job application
        application = JobApplication(
            applicant=request.user,
            job=job,
            institution=job.posted_by,
            applied_at=datetime.now(),
        )
        application.save()

        messages.success(request, "Your application has been submitted successfully.")
        return HttpResponseRedirect(reverse("job_detail", args=[job_id]))

    return render(request, "applied_jobs.html", {"job": job})

@login_required
def get_applied_jobs(request):
    status_filter = request.GET.get("status", "")
    applications = JobApplication.objects.filter(applicant=request.user).order_by("-applied_at")

    if status_filter:
        applications = applications.filter(status=status_filter)

    paginator = Paginator(applications, 6)  # 6 per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "status_filter": status_filter,
    }
    return render(request, "applied_jobs.html", context)

@login_required
def withdraw_application(request, application_id):
    application = get_object_or_404(
        JobApplication, id=application_id, applicant=request.user
    )
    if request.method == "POST":
        application.delete()
        messages.success(request, "Application withdrawn successfully.")
    return redirect("applied_jobs")
