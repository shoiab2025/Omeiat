import pdb
from django.utils import timezone
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.models import Job

def job_list(request):
    today = timezone.localdate()
    jobs = Job.objects.filter(
        is_active=True,
        application_deadline__gte=today
    ).order_by('-timestamp')
    return render(request, 'jobs.html', {'jobs': jobs})

def get_job_detail(request, job_id):
    pdb.set_trace()
    job = get_object_or_404(Job,id=job_id, is_active=True)
    return render(request, 'job_detail.html', {'job': job})


