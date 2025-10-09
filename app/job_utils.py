from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def format_salary_range(min_salary, max_salary):
    """Format salary range with proper formatting"""
    if min_salary and max_salary:
        return f"₹{min_salary:,.0f} - ₹{max_salary:,.0f}"
    elif min_salary:
        return f"₹{min_salary:,.0f}+"
    elif max_salary:
        return f"Up to ₹{max_salary:,.0f}"
    return "Negotiable"

@register.filter
def days_until_deadline(deadline):
    """Calculate days until application deadline"""
    if deadline:
        today = timezone.now().date()
        delta = deadline - today
        return max(0, delta.days)
    return 0

@register.filter
def is_deadline_urgent(deadline):
    """Check if deadline is within 3 days"""
    return days_until_deadline(deadline) <= 3

@register.filter
def get_status_badge_class(status):
    """Return Bootstrap badge class for status"""
    status_classes = {
        'Open': 'bg-success',
        'Closed': 'bg-secondary',
        'Pending': 'bg-warning',
        'Cancelled': 'bg-danger',
        'pending': 'bg-secondary',
        'shortlisted': 'bg-warning',
        'hired': 'bg-success',
        'rejected': 'bg-danger',
    }
    return status_classes.get(status, 'bg-secondary')

@register.simple_tag
def get_shortlisted_count(job, institution):
    """Get count of shortlisted candidates for a job"""
    from app.models import JobShortlist
    try:
        shortlist = JobShortlist.objects.get(job=job, institution=institution)
        return shortlist.users.count()
    except JobShortlist.DoesNotExist:
        return 0

@register.simple_tag
def get_shortlisted_users(job, institution):
    """Get shortlisted users for a job"""
    from app.models import JobShortlist
    try:
        shortlist = JobShortlist.objects.get(job=job, institution=institution)
        return shortlist.users.all()
    except JobShortlist.DoesNotExist:
        return []

@register.filter
def is_user_shortlisted(job, user_id):
    """Check if user is shortlisted for a job"""
    from app.models import JobShortlist
    try:
        shortlist = JobShortlist.objects.get(job=job)
        return shortlist.users.filter(id=user_id).exists()
    except JobShortlist.DoesNotExist:
        return False

@register.filter
def get_experience_display(experience):
    """Format experience for display"""
    if experience == 0:
        return "Fresher"
    elif experience == 1:
        return "1 year"
    else:
        return f"{experience} years"

@register.simple_tag
def get_application_stats(job):
    """Get application statistics for a job"""
    applications = job.applications.all()
    total = applications.count()
    shortlisted = applications.filter(status='shortlisted').count()
    hired = applications.filter(status='hired').count()
    rejected = applications.filter(status='rejected').count()
    
    return {
        'total': total,
        'shortlisted': shortlisted,
        'hired': hired,
        'rejected': rejected
    }