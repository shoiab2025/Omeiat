from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from app.utils import institution_required
from datetime import date, timedelta
from django.core.paginator import Paginator
from app.models import Job, JobApplication, Institution, User, Skill, Education, JobShortlist
from app.utils import getJobsOpeningsByCategories,getZones
from app.form import JobForm  # Your existing Job form
from app.filters import JobFilter
from django.http import JsonResponse
from django.db.models import Q
from django.db import transaction
import pdb
# ----------------------------
# Utility: Check Role
# ----------------------------
def check_role(user, allowed_roles):
    if not user.role or user.role.name not in allowed_roles:
        raise PermissionDenied("You do not have permission to access this resource.")

# ----------------------------
# Job List (All users)
# ----------------------------

def job_list(request):
    today = timezone.localdate()
    
    # Base queryset - active jobs with valid application deadline
    jobs = Job.objects.filter(is_active=True)
    
    # Get filter parameters from GET request
    search_query = request.GET.get('search')  # Add search parameter
    exact_match = request.GET.get('exact_match')  # Add exact match parameter
    category = request.GET.get('category')
    zone = request.GET.get('zone')
    job_types = request.GET.getlist('job_type')  # Multiple selection
    experiences = request.GET.getlist('experience')
    posted_within_options = request.GET.getlist('posted_within')
    salary_min = request.GET.get('salary_min')
    salary_max = request.GET.get('salary_max')
    
    # Apply search filter
    if search_query:
        if exact_match:
            # Exact match search
            jobs = jobs.filter(
                Q(title__iexact=search_query) |
                Q(posted_by__name__iexact=search_query) |
                Q(location__iexact=search_query) |
                Q(post__iexact=search_query)
            ).distinct()
        else:
            # Broad search across multiple fields
            jobs = jobs.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(posted_by__name__icontains=search_query) |
                Q(location__icontains=search_query) |
                Q(post__icontains=search_query) |
                Q(qualifications_required__icontains=search_query)
            ).distinct()
    
    # Apply filters manually
    if category:
        jobs = jobs.filter(category=category)
    
    if zone:
        jobs = jobs.filter(location__icontains=zone)  # Use icontains for partial matching
    
    # Job Type filter (multiple selection) - FIXED
    if job_types:
        jobs = jobs.filter(job_type__in=job_types)  # Use __in for multiple values
    
    # Experience filter (multiple selection) - FIXED duplicate for loop
    if experiences:
        experience_filters = Q()
        for exp in experiences:
            if exp == '1-2 Years':
                # Jobs requiring 1-2 years experience
                experience_filters |= Q(experience_needed__range=(1, 2))
            elif exp == '2-3 Years':
                experience_filters |= Q(experience_needed__range=(2, 3))
            elif exp == '3-6 Years':
                experience_filters |= Q(experience_needed__range=(3, 6))
            elif exp == '6+ Years':
                experience_filters |= Q(experience_needed__gte=6)
        jobs = jobs.filter(experience_filters)
    
    # Posted Within filter (multiple selection)
    if posted_within_options:
        date_filters = Q()
        for option in posted_within_options:
            if option == 'Today':
                date_filters |= Q(timestamp__date=today)
            elif option == 'Last 2 days':
                date_filters |= Q(timestamp__gte=today - timedelta(days=2))
            elif option == 'Last 5 days':
                date_filters |= Q(timestamp__gte=today - timedelta(days=5))
            elif option == 'Last 10 days':
                date_filters |= Q(timestamp__gte=today - timedelta(days=10))
            elif option == 'Last 15 days':
                date_filters |= Q(timestamp__gte=today - timedelta(days=15))
        jobs = jobs.filter(date_filters)
    
    # Salary filter
    if salary_min:
        try:
            jobs = jobs.filter(max_salary__gte=float(salary_min))
        except (ValueError, TypeError):
            pass
    
    if salary_max:
        try:
            jobs = jobs.filter(min_salary__lte=float(salary_max))
        except (ValueError, TypeError):
            pass
    
    # Apply ordering
    filtered_jobs = jobs.order_by("-timestamp")
    
    # Add time_ago to each job
    for job in filtered_jobs:
        job.time_ago = get_time_ago(job.timestamp)
    
    # Filter options for template - Use actual choices from your model
    job_types_list = [choice[0] for choice in Job.JOB_TYPE_CHOICES]
    experience_levels_list = ['1-2 Years', '2-3 Years', '3-6 Years', '6+ Years']
    posted_options_list = ['Today', 'Last 2 days', 'Last 5 days', 'Last 10 days', 'Last 15 days']
    categories_list = [choice[0] for choice in Job.CATEGORY_CHOICES]
    
    # Pagination
    paginator = Paginator(filtered_jobs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get filter options for template
    zones = getZones()
    categories = getJobsOpeningsByCategories()
    
    context = {
        'jobs': page_obj,
        'categories': categories,
        'zones': zones,
        'job_types': job_types_list,
        'experience_levels': experience_levels_list,
        'posted_options': posted_options_list,
        
        # Pass selected filters back to template to maintain state
        'selected_job_types': job_types,
        'selected_experiences': experiences,
        'selected_posted_within': posted_within_options,
        'selected_category': category,
        'selected_zone': zone,
        'salary_min': salary_min,
        'salary_max': salary_max,
        'search_query': search_query,  # Add search query to context
        'exact_match': exact_match,    # Add exact match to context
    }
    
    return render(request, "job_listing.html", context)
def get_time_ago(timestamp):
    """Calculate human-readable time difference"""
    now = timezone.now()
    diff = now - timestamp
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

def job_list_ins(request):
    today = timezone.localdate()
    
    # Base queryset
    jobs = Job.objects.filter(is_active=True, posted_by = request.institution)
    
    # Apply filters
    job_filter = JobFilter(request.GET, queryset=jobs)
    filtered_jobs = job_filter.qs.order_by("-timestamp")
    
    # Pagination for jobs
    paginator = Paginator(filtered_jobs, 10)  # 10 jobs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Paginate applications for each job
    for job in page_obj:
        applications = job.applications.all().order_by('-applied_at')
        app_page_number = request.GET.get(f'app_page_{job.id}', 1)
        app_paginator = Paginator(applications, 5)  # 5 applications per page
        job.applications_paginated = app_paginator.get_page(app_page_number)
    
    # Filter options for template
    job_types = ['Full Time', 'Part Time', 'Remote', 'Freelance']
    experience_levels = ['1-2 Years', '2-3 Years', '3-6 Years', '6+ Years']
    posted_options = ['Today', 'Last 2 days', 'Last 5 days', 'Last 10 days', 'Last 15 days']
    zones = getZones()
    categories = getJobsOpeningsByCategories()
    
    context = {
        'filter': job_filter,
        'page_obj': page_obj,  # paginated jobs
        'job_types': job_types,
        'experience_levels': experience_levels,
        'categories': categories,
        'zones': zones,
        'posted_options': posted_options,
    }
    
    return render(request, "institution/tables.html", context)

def ins_applications(request):
    # Get all jobs posted by this institution
    jobs = Job.objects.filter(posted_by=request.institution).order_by('-timestamp')
    
    # Create a list to store job data with applications and shortlist info
    job_data = []
    
    for job in jobs:
        # Get applications for this job
        applications = JobApplication.objects.filter(
            job=job
        ).select_related('applicant').order_by('-applied_at')
        
        # Get shortlist info for this job
        try:
            shortlist = JobShortlist.objects.get(
                job=job, 
                institution=request.institution
            )
            shortlisted_count = shortlist.users.count()
            shortlisted_user_ids = list(shortlist.users.values_list('id', flat=True))
            shortlisted_candidates = shortlist.users.all()
        except JobShortlist.DoesNotExist:
            shortlisted_count = 0
            shortlisted_user_ids = []
            shortlisted_candidates = []
        
        # Enhance each application with shortlist status
        enhanced_applications = []
        for application in applications:
            enhanced_applications.append({
                'application': application,
                'is_shortlisted': application.applicant.id in shortlisted_user_ids
            })
        
        job_data.append({
            'job': job,
            'applications': enhanced_applications,
            'applications_count': applications.count(),
            'shortlisted_count': shortlisted_count,
            'shortlisted_user_ids': shortlisted_user_ids,
            'shortlisted_candidates': shortlisted_candidates,
        })
    
    # Get overall status counts
    all_applications = JobApplication.objects.filter(
        job__posted_by=request.institution
    )
    
    status_counts = {
        'pending': all_applications.filter(status='pending').count(),
        'shortlisted': all_applications.filter(status='shortlisted').count(),
        'hired': all_applications.filter(status='hired').count(),
        'rejected': all_applications.filter(status='rejected').count(),
        'total': all_applications.count()
    }

    # Paginate job data
    paginator = Paginator(job_data, 3)  # 3 jobs per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "status_counts": status_counts,
        "status_choices": JobApplication.STATUS_CHOICES,
    }
    
    return render(request, "institution/jobApplicataions.html", context)
# ----------------------------
# Job Detail
# ----------------------------
def job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    return render(request, "job_details.html", {"job": job})
    
def ins_job_detail(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)
    return render(request, "job_details.html", {"job": job})


# ----------------------------
# Apply Job (Job Seeker only)
# ----------------------------

@login_required
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, is_active=True)

    if JobApplication.objects.filter(applicant=request.user, job=job).exists():
        messages.error(request, "You have already applied for this job.")
        return redirect('job_detail', job_id=job.id)

    if request.method == 'POST':
        # Get form data or use defaults
        cover_letter = request.POST.get('cover_letter', '')
        expire_date = request.POST.get('expire_date') or None
        joining_availability = request.POST.get('joining_availability') or None
        commute_distance_km = request.POST.get('commute_distance_km') or None
        communication = request.POST.get('communication') or None
        technical_skills = request.POST.get('technical_skills') or None
        experience = request.POST.get('experience') or None
        qualification = request.POST.get('qualification') or None
        expire_date = date.today() + timedelta(days=15)
        # Create application
        JobApplication.objects.create(
            applicant=request.user,
            job=job,
            institution=job.posted_by,
            cover_letter=cover_letter,
            communication_skills = communication,
            technical_skills = technical_skills,
            experience = experience,
            qualification = qualification,
            expire_date=expire_date,
            joining_availability=joining_availability,
            commute_distance_km=commute_distance_km,
            applied_at=timezone.now()
        )
        
        messages.success(request, "Application submitted successfully.")
        return redirect('my_applications')

    return render(request, "jobs/apply_job.html", {"job": job})

# ----------------------------
# My Applications (Job Seeker only)
# ----------------------------
@login_required
def my_applications(request):
    applications = JobApplication.objects.filter(applicant=request.user).select_related('job', 'job__posted_by').order_by('-applied_at')

    # Get status counts for statistics
    status_counts = {
        'pending': applications.filter(status='pending').count(),
        'shortlisted': applications.filter(status='shortlisted').count(),
        'hired': applications.filter(status='hired').count(),
        'rejected': applications.filter(status='rejected').count(),
        'total': applications.count()
    }

    paginator = Paginator(applications, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "status_counts": status_counts,
        "status_choices": JobApplication.STATUS_CHOICES,
    }
    
    return render(request, "applied_jobs.html", context)

# ----------------------------
# Withdraw Application (Job Seeker only)
# ----------------------------
@login_required
def withdraw_application(request, application_id):
    check_role(request.user, ['job_seeker'])
    application = get_object_or_404(JobApplication, id=application_id, applicant=request.user)

    if request.method == 'POST':
        application.delete()
        messages.success(request, "Application withdrawn successfully.")
        return redirect('my_applications')

    return render(request, "jobs/confirm_withdraw.html", {"application": application})

# ----------------------------
# Institution: List My Jobs
# ----------------------------
@login_required
def my_jobs(request):
    check_role(request.user, ['institution'])
    jobs = Job.objects.filter(posted_by=request.user.institution).order_by('-timestamp')

    paginator = Paginator(jobs, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "jobs/my_jobs.html", {"page_obj": page_obj})

# ----------------------------
# Institution: Create Job
# ----------------------------
@institution_required
def create_or_update_job(request):
    job_id = request.POST.get('job_id')
    job = None

    # Handle GET request - display job listing and form
    if request.method == 'GET':
        jobs = Job.objects.filter(posted_by=request.institution).order_by('-timestamp')
        job_types = [choice[0] for choice in Job.JOB_TYPE_CHOICES]
        categories_list = [{'key': key, 'name': name} for key, name in Job.CATEGORY_CHOICES]
        skills = Skill.objects.all()
        certifications = Education.objects.all()

        context = {
            'jobs': jobs,
            'job_types': job_types,
            'categories': categories_list,
            'skills': skills,
            'certifications': certifications,
            'job': job,
            'JOB_TYPE_CHOICES': Job.JOB_TYPE_CHOICES,
            'STATUS_CHOICES': Job.STATUS_CHOICES,
            'GENDER_CHOICES': Job.GENDER_CHOICES,
            'CATEGORY_CHOICES': Job.CATEGORY_CHOICES,
        }
        return render(request, "institution/tables.html", context)

    # Handle POST request - create or update job
    if request.method == 'POST':
        # Form data
        title = request.POST.get('title', '').strip()
        location = request.POST.get('location', '').strip()
        job_type = request.POST.get('job_type', '')
        category = request.POST.get('category', '')
        description = request.POST.get('description', '')
        min_salary = request.POST.get('min_salary')
        max_salary = request.POST.get('max_salary')
        candidate_gender = request.POST.get('candidate_gender')
        degree_required = request.POST.get('degree_required')
        skills_required = request.POST.getlist('skills_required')  # Expecting multiple
        certifications_required = request.POST.getlist('certifications_required')  # Expecting multiple
        qualifications_required = request.POST.get('qualifications_required')
        interview_date = request.POST.get('interview_date')
        job_timing = request.POST.get('job_timing')
        experience_needed = request.POST.get('experience_needed')
        application_deadline = request.POST.get('application_deadline')
        no_of_openings = request.POST.get('no_of_openings')
        location_range_km = request.POST.get('location_range_km')
        status = request.POST.get('status', 'open')  # default to 'open'
        is_active = request.POST.get('is_active', 'true') == 'true'  # Convert to boolean

        # Basic validation
        if not title or not location:
            messages.error(request, "Title and location are required.")
            return redirect('job_create_or_update')

        try:
            if job_id:
                # Update existing job
                job = get_object_or_404(Job, id=job_id, posted_by=request.institution)
                job.title = title
                job.location = location
                job.job_type = job_type
                job.category = category
                job.description = description
                job.min_salary = min_salary or None
                job.max_salary = max_salary or None
                job.experience_needed = experience_needed or None
                job.application_deadline = application_deadline if application_deadline else None
                job.qualifications_required = qualifications_required
                job.degree_required = degree_required
                job.candidate_gender = candidate_gender
                job.job_timing = job_timing
                job.no_of_openings = int(no_of_openings) if no_of_openings else 1
                job.location_range_km = int(location_range_km) if location_range_km else 0
                job.status = status
                job.is_active = is_active
                job.save()

                messages.success(request, "Job updated successfully.")
            else:
                # Create new job
                job = Job.objects.create(
                    title=title,
                    location=location,
                    job_type=job_type,
                    category=category,
                    description=description,
                    min_salary=min_salary or None,
                    max_salary=max_salary or None,
                    experience_needed=experience_needed or None,
                    application_deadline=application_deadline if application_deadline else None,
                    no_of_openings=int(no_of_openings) if no_of_openings else 1,
                    qualifications_required=qualifications_required,
                    degree_required=degree_required,
                    candidate_gender=candidate_gender,
                    location_range_km=int(location_range_km) if location_range_km else 0,
                    job_timing=job_timing,
                    status=status,
                    is_active=is_active,
                    posted_by=request.institution,
                    timestamp=timezone.now()
                )
                job.save()
                messages.success(request, "Job created successfully.")

            # Set ManyToMany fields
            if skills_required:
                job.skills_required.set(Skill.objects.filter(id__in=skills_required))
            if certifications_required:
                job.certifications_required.set(Education.objects.filter(id__in=certifications_required))

            return redirect('job_create_or_update')

        except Exception as e:
            messages.error(request, f"Error saving job: {str(e)}")
            return redirect('job_create_or_update')

# Institution: Update Job
# ----------------------------

def update_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        try:
            job.title = request.POST.get('title', '').strip()
            job.post = request.POST.get('post', '').strip()
            job.category = request.POST.get('category', '')
            job.subcategory = request.POST.get('subcategory') or ''
            job.job_type = request.POST.get('job_type', '')
            job.no_of_openings = int(request.POST.get('no_of_openings') or 1)
            job.description = request.POST.get('description', '')
            job.min_salary = request.POST.get('min_salary') or None
            job.max_salary = request.POST.get('max_salary') or None
            job.experience_needed = request.POST.get('experience_needed') or None
            job.candidate_gender = request.POST.get('candidate_gender', 'Any')
            job.qualifications_required = request.POST.get('qualifications_required', '')
            job.degree_required = request.POST.get('degree_required', '')
            job.location = request.POST.get('location', '')
            job.location_range_km = int(request.POST.get('location_range_km') or 0)
            job.application_deadline = parse_date(request.POST.get('application_deadline')) or timezone.now().date()
            job.interview_date = parse_date(request.POST.get('interview_date')) if request.POST.get('interview_date') else None
            job.job_timing = request.POST.get('job_timing') or ''
            job.status = request.POST.get('status', 'Open')
            job.is_verified = 'is_verified' in request.POST
            job.is_active = 'is_active' in request.POST

            job.save()

            # ManyToMany fields
            skill_ids = request.POST.getlist('skills_required')
            cert_ids = request.POST.getlist('certifications_required')
            job.skills_required.set(Skill.objects.filter(id__in=skill_ids))
            job.certifications_required.set(Education.objects.filter(id__in=cert_ids))

            messages.success(request, "Job updated successfully.")
            return redirect('my_jobs')

        except Exception as e:
            messages.error(request, f"Error updating job: {e}")

    context = {
        'job': job,
        'skills': Skill.objects.all(),
        'certifications': Education.objects.all(),
        'JOB_TYPE_CHOICES': Job.JOB_TYPE_CHOICES,
        'STATUS_CHOICES': Job.STATUS_CHOICES,
        'GENDER_CHOICES': Job.GENDER_CHOICES,
        'CATEGORY_CHOICES': Job.CATEGORY_CHOICES,
    }

    return render(request, 'institution/job_form.html', context)

# ----------------------------
# Institution: Delete Job
# ----------------------------
@institution_required
def delete_job(request, job_id):
    check_role(request.user, ['institution'])
    job = get_object_or_404(Job, id=job_id, posted_by=request.user.institution)

    if request.method == 'POST':
        job.delete()
        messages.success(request, "Job deleted successfully.")
        return redirect('my_jobs')

    return render(request, "jobs/delete_job.html", {"job": job})

@institution_required
def job_applications_view(request, job_id):
    """
    Display all applications for a specific job.
    Accessible to the job poster (institution/employer).
    """
    job = get_object_or_404(Job, id=job_id)
    
    # ✅ Fetch all applications for this job
    applications = JobApplication.objects.filter(
        job=job
    ).select_related('applicant').order_by('-applied_at')
    
    return render(request, 'institution/application_details.html', {
        'job': job,
        'applications': applications
    })
# ----------------------------
# Admin: List All Applications
# ----------------------------
@institution_required
def all_applications(request):
    check_role(request.user, ['admin'])
    applications = JobApplication.objects.all().order_by('-applied_at')

    paginator = Paginator(applications, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "jobs/all_applications.html", {"page_obj": page_obj})


@institution_required
@institution_required
def add_to_shortlist(request, job_id, user_id):
    """
    Add a candidate to job shortlist
    """
    try:
        with transaction.atomic():
            # Get job and verify ownership
            job = get_object_or_404(Job, id=job_id, posted_by=request.institution)
            candidate = get_object_or_404(User, id=user_id)
            
            # Get or create shortlist for this job
            shortlist, created = JobShortlist.objects.get_or_create(
                job=job,
                institution=request.institution
            )
            
            # Check if user is already in shortlist
            if shortlist.users.filter(id=user_id).exists():
                # If already exists, remove it (toggle behavior)
                shortlist.users.remove(candidate)
                action = 'removed'
                message = f'{candidate.get_full_name()} removed from shortlist'
            else:
                # Add user to shortlist
                shortlist.users.add(candidate)
                action = 'added'
                message = f'{candidate.get_full_name()} added to shortlist'
            
            shortlist.save()
            
            # Get updated count
            shortlisted_count = shortlist.users.count()
            
            response_data = {
                'status': 'success',
                'message': message,
                'action': action,
                'shortlisted_count': shortlisted_count,
                'candidate_name': candidate.get_full_name(),
                'job_title': job.title
            }
            
            # For AJAX requests, return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)
            else:
                # For regular form submissions, redirect back to jobs page
                messages.success(request, response_data['message'])
                return redirect('ins_applications')  # Redirect to institution jobs list
                
    except Job.DoesNotExist:
        error_msg = 'Job not found or you do not have permission'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': error_msg}, status=404)
        else:
            messages.error(request, error_msg)
            return redirect('ins_applications')
    except User.DoesNotExist:
        error_msg = 'Candidate not found'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': error_msg}, status=404)
        else:
            messages.error(request, error_msg)
            return redirect('ins_applications')
    except Exception as e:
        error_msg = f'Error updating shortlist: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': error_msg}, status=500)
        else:
            messages.error(request, error_msg)
            return redirect('ins_applications')

@institution_required
def remove_from_shortlist(request, job_id, user_id):
    """
    Remove a candidate from job shortlist
    """
    try:
        with transaction.atomic():
            # Get job and verify ownership
            job = get_object_or_404(Job, id=job_id, posted_by=request.institution)
            candidate = get_object_or_404(User, id=user_id)
            
            # Get shortlist
            shortlist = get_object_or_404(
                JobShortlist, 
                job=job, 
                institution=request.institution
            )
            
            # Check if user is in shortlist
            if not shortlist.users.filter(id=user_id).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Candidate is not in shortlist',
                    'action': 'not_found'
                }, status=400)
            
            # Remove user from shortlist
            shortlist.users.remove(candidate)
            
            # Get updated count
            shortlisted_count = shortlist.users.count()
            
            response_data = {
                'status': 'success',
                'message': f'{candidate.get_full_name()} removed from shortlist',
                'action': 'removed',
                'shortlisted_count': shortlisted_count,
                'candidate_name': candidate.get_full_name()
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)
            else:
                messages.success(request, response_data['message'])
                return redirect('job_shortlist', job_id=job_id)
                
    except JobShortlist.DoesNotExist:
        error_msg = 'Shortlist not found for this job'
        return handle_error(request, error_msg, job_id, 404)
    except Job.DoesNotExist:
        error_msg = 'Job not found or you do not have permission'
        return handle_error(request, error_msg, job_id, 404)
    except User.DoesNotExist:
        error_msg = 'Candidate not found'
        return handle_error(request, error_msg, job_id, 404)
    except Exception as e:
        error_msg = f'Error removing from shortlist: {str(e)}'
        return handle_error(request, error_msg, job_id, 500)

@institution_required
def toggle_shortlist(request, job_id, user_id):
    """
    Toggle candidate shortlist status (add if not exists, remove if exists)
    """
    try:
        with transaction.atomic():
            # Get job and verify ownership
            job = get_object_or_404(Job, id=job_id, posted_by=request.user.institution)
            candidate = get_object_or_404(User, id=user_id)
            
            # Get or create shortlist
            shortlist, created = JobShortlist.objects.get_or_create(
                job=job,
                institution=request.institution
            )
            
            # Toggle user in shortlist
            if shortlist.users.filter(id=user_id).exists():
                shortlist.users.remove(candidate)
                action = 'removed'
                message = f'{candidate.get_full_name()} removed from shortlist'
            else:
                shortlist.users.add(candidate)
                action = 'added'
                message = f'{candidate.get_full_name()} added to shortlist'
            
            # Get updated count
            shortlisted_count = shortlist.users.count()
            
            response_data = {
                'status': 'success',
                'action': action,
                'message': message,
                'shortlisted_count': shortlisted_count,
                'is_shortlisted': action == 'added',
                'candidate_name': candidate.get_full_name()
            }
            
            return JsonResponse(response_data)
                
    except Job.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Job not found or you do not have permission'
        }, status=404)
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Candidate not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error toggling shortlist: {str(e)}'
        }, status=500)

@institution_required
def bulk_add_to_shortlist(request, job_id):
    """
    Add multiple candidates to shortlist at once
    """
    try:
        data = json.loads(request.body)
        user_ids = data.get('user_ids', [])
        
        if not user_ids:
            return JsonResponse({
                'status': 'error',
                'message': 'No candidates selected'
            }, status=400)
        
        with transaction.atomic():
            job = get_object_or_404(Job, id=job_id, posted_by=request.institution)
            
            # Get or create shortlist
            shortlist, created = JobShortlist.objects.get_or_create(
                job=job,
                institution=request.user.institution
            )
            
            added_count = 0
            already_exists_count = 0
            
            for user_id in user_ids:
                try:
                    candidate = User.objects.get(id=user_id)
                    if not shortlist.users.filter(id=user_id).exists():
                        shortlist.users.add(candidate)
                        added_count += 1
                    else:
                        already_exists_count += 1
                except User.DoesNotExist:
                    continue
            
            shortlisted_count = shortlist.users.count()
            
            response_data = {
                'status': 'success',
                'message': f'Added {added_count} candidates to shortlist',
                'added_count': added_count,
                'already_exists_count': already_exists_count,
                'shortlisted_count': shortlisted_count
            }
            
            return JsonResponse(response_data)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Job.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Job not found or you do not have permission'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error in bulk add: {str(e)}'
        }, status=500)

@institution_required
def clear_shortlist(request, job_id):
    """
    Clear all candidates from job shortlist
    """
    try:
        with transaction.atomic():
            job = get_object_or_404(Job, id=job_id, posted_by=request.institution)
            
            shortlist = get_object_or_404(
                JobShortlist, 
                job=job, 
                institution=request.user.institution
            )
            
            # Get count before clearing
            count_before = shortlist.users.count()
            
            # Clear all users
            shortlist.users.clear()
            
            response_data = {
                'status': 'success',
                'message': f'Cleared {count_before} candidates from shortlist',
                'cleared_count': count_before,
                'shortlisted_count': 0
            }
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(response_data)
            else:
                messages.success(request, response_data['message'])
                return redirect('job_shortlist', job_id=job_id)
                
    except JobShortlist.DoesNotExist:
        error_msg = 'Shortlist not found for this job'
        return handle_error(request, error_msg, job_id, 404)
    except Job.DoesNotExist:
        error_msg = 'Job not found or you do not have permission'
        return handle_error(request, error_msg, job_id, 404)
    except Exception as e:
        error_msg = f'Error clearing shortlist: {str(e)}'
        return handle_error(request, error_msg, job_id, 500)

@institution_required
def get_shortlist_status(request, job_id, user_id):
    """
    Check if a candidate is shortlisted for a job
    """
    try:
        job = get_object_or_404(Job, id=job_id, posted_by=request.institution)
        candidate = get_object_or_404(User, id=user_id)
        
        is_shortlisted = JobShortlist.objects.filter(
            job=job,
            institution=request.user.institution,
            users=user_id
        ).exists()
        
        return JsonResponse({
            'status': 'success',
            'is_shortlisted': is_shortlisted,
            'candidate_name': candidate.get_full_name(),
            'job_title': job.title
        })
        
    except Job.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Job not found'
        }, status=404)
    except User.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Candidate not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error checking shortlist status: {str(e)}'
        }, status=500)

def handle_error(request, error_message, job_id, status_code):
    """
    Helper function to handle errors consistently
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'error',
            'message': error_message
        }, status=status_code)
    else:
        messages.error(request, error_message)
        return redirect('institution/jobApplications.html', job_id=job_id)

# Utility view to get shortlist count for a job
@institution_required
def get_shortlist_count(request, job_id):
    """
    Get the count of shortlisted candidates for a job
    """
    try:
        job = get_object_or_404(Job, id=job_id, posted_by=request.institution)
        
        shortlist_count = JobShortlist.objects.filter(
            job=job,
            institution=request.user.institution
        ).values_list('users', flat=True).count()
        
        return JsonResponse({
            'status': 'success',
            'shortlisted_count': shortlist_count,
            'job_title': job.title
        })
        
    except Job.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Job not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error getting shortlist count: {str(e)}'
        }, status=500)