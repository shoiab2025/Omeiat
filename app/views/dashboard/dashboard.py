from django.db.models import Count
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from app.models import JobApplication, Job
from django.utils import timezone

from django.db.models import Count
from django.shortcuts import render
from app.models import JobApplication

def dashboard_view(request):
    # Default values for anonymous users
    jobs = latest_jobs_views(request)
    status_map = {
        'pending': 0,
        'shortlisted': 0,
        'hired': 0,
        'rejected': 0
    }
    profile_completion = 0

    if request.user.is_authenticated:
        # 1. Application status counts
        status_counts = (
            JobApplication.objects
            .filter(applicant=request.user)
            .values('status')
            .annotate(count=Count('id'))
        )

        for entry in status_counts:
            key = entry['status']
            if key in status_map:
                status_map[key] = entry['count']

        # 2. Profile completion
        profile_completion = calculate_profile_completion(request.user)

        # Update profile_percentage only for authenticated users
        if hasattr(request.user, 'profile_percentage') and request.user.profile_percentage != profile_completion:
            request.user.profile_percentage = profile_completion
            request.user.save(update_fields=['profile_percentage'])
    
    context = {
        'labels': list(map(str.capitalize, status_map.keys())),
        'data': list(status_map.values()),
        'completion': profile_completion,
        'jobs': jobs,
    }
    return render(request, 'dashboard.html', context)



def calculate_profile_completion(user):
    exclude_fields = [
        'id', 'password', 'last_login', 'is_superuser',
        'username', 'email', 'is_staff', 'is_active',
        'date_joined', 'groups', 'user_permissions',
        'profile_percentage', 'profile_visibility',
        'is_deleted', 'timestamp'
    ]

    model_fields = user._meta.get_fields()
    total_fields = 0
    filled_count = 0

    for field in model_fields:
        if hasattr(field, 'attname'):
            field_name = field.attname
            if field_name not in exclude_fields:
                total_fields += 1
                value = getattr(user, field_name, None)
                if value not in [None, '', 0]:
                    filled_count += 1

    return int((filled_count / total_fields) * 100) if total_fields > 0 else 0


def latest_jobs_views(request):
    today = timezone.localdate()
    jobs = Job.objects.filter(is_active=True, application_deadline__gte=today).order_by("-timestamp")
    return jobs
