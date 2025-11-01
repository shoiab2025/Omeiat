# utils.py
import random
from django.core.mail import send_mail
from django.utils import timezone
from app.models import Job, OmeiatZone, Institution,InstitutionContact
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.shortcuts import render
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp, user_name="User"):
    """Send a styled HTML OTP email to the user."""
    subject = "Your OTP Verification Code"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER)
    to = [email]

    # Context for the HTML template
    context = {
        "user_name": user_name,
        "otp_code": otp,
        "expiry_minutes": 10,
        "site_name": "My Django App",
        "year": timezone.now().year,
    }

    # Render email templates
    html_content = render_to_string("emails/otp_email.html", context)
    text_content = (
        f"Hello {user_name},\n\n"
        f"Your OTP code is {otp}. It will expire in 10 minutes.\n\n"
        f"Thank you,\nMy Django App Team"
    )

    # Create and send the email
    email_message = EmailMultiAlternatives(subject, text_content, from_email, to)
    email_message.attach_alternative(html_content, "text/html")

    try:
        email_message.send()
        print(f"✅ OTP email sent successfully to {email}")
    except Exception as e:
        print(f"❌ Failed to send OTP email to {email}: {e}")

def getJobsOpeningsByCategories():
    category_choices = Job.CATEGORY_CHOICES

    # Annotate job counts per category
    job_counts = Job.objects.values('category').annotate(total=Count('id'))

    # Convert to a dictionary for easy lookup
    job_count_map = {item['category']: item['total'] for item in job_counts}

    # Build a structured list combining category + display name + job count
    icons = {
        'teaching': 'fa-chalkboard-teacher',
        'non-teaching': 'fa-user-tie',
        'admin': 'fa-users-cog',
        'technical': 'fa-laptop-code',
        'support': 'fa-headset',
        'medical': 'fa-user-md',
    }
    categories = [
        {
            'key': key,
            'name': value,
            'icon': icons.get(key, 'fa-briefcase'),  # default icon            
            'count': job_count_map.get(key, 0)
        }
        for key, value in category_choices
    ]

    return categories

def getZones():
    zones = OmeiatZone.objects.all().order_by('name')
    return [{"id": zone.id, "name": zone.name} for zone in zones]

def getRecentJobs():
    now = timezone.now()
    fifteen_days_ago = now - timedelta(days=15)
    jobs = Job.objects.filter(timestamp__gte=fifteen_days_ago).order_by('-timestamp')    
    return jobs

def getJobsByPosting(days = 0):
    now = timezone.now()
    fifteen_days_ago = now - timedelta(days)
    jobs = Job.objects.filter(timestamp__gte=fifteen_days_ago).order_by('-timestamp')    
    return jobs
    

def time_since(dt):
    """
    Returns a human-readable "time ago" string.
    dt: datetime field (timezone-aware)
    """
    now = timezone.now()
    diff = now - dt

    seconds = diff.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} seconds ago"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 2419200:
        weeks = int(seconds // 604800)
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"
    else:
        months = int(seconds // 2419200)
        return f"{months} month{'s' if months != 1 else ''} ago"

def calculate_profile_completion(user):
    from django.db.models import Field, FileField, ManyToManyField

    # Fields to exclude from calculation
    exclude_fields = {
        'id', 'password', 'last_login', 'is_superuser',
        'username', 'email', 'is_staff', 'is_active',
        'date_joined', 'groups', 'user_permissions',
        'profile_percentage', 'profile_visibility',
        'is_deleted', 'timestamp'
    }

    total_fields = 0
    filled_fields = 0

    for field in user._meta.get_fields():
        # Skip reverse relations and ManyToMany fields
        if isinstance(field, ManyToManyField) or field.auto_created:
            continue

        # Get actual field name
        field_name = getattr(field, 'attname', None) or getattr(field, 'name', None)
        if not field_name or field_name in exclude_fields:
            continue

        try:
            value = getattr(user, field_name)
        except AttributeError:
            continue

        # Increment total
        total_fields += 1

        # Determine if field is filled
        if isinstance(field, FileField):
            if value and hasattr(value, 'url'):
                filled_fields += 1
        elif isinstance(value, bool):
            # Accept both True and False as valid
            filled_fields += 1
        elif value not in [None, '', []]:
            filled_fields += 1

    return int((filled_fields / total_fields) * 100) if total_fields > 0 else 0


def toast_message(request):
    # Add a success message to display in the template
    messages.success(request, "This is a success message!")
    messages.error(request, "This is an error message!")

    # Render the template
    return render(request, 'base_layout.html')

def institution_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if institution is available via middleware
        if not request.institution:
            return redirect('institution_login')  # Redirect to institution login page
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def get_institution_choices():
    categories = [cat[0] for cat in Institution.CATEGORY_CHOICES]
    contacts = [contact[0] for contact in InstitutionContact.CONTACT_TYPE_CHOICES]
    
    return {
        "categories": categories,
        "contact_types": contacts
    }