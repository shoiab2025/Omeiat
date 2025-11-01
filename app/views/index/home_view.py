from django.shortcuts import render, redirect, get_object_or_404
from app.utils import getJobsOpeningsByCategories, getZones, getRecentJobs,calculate_profile_completion
from app.utils import time_since
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from app.utils import institution_required, get_institution_choices
from app.models import Institution, InstitutionAddress,InstitutionStrength, InstitutionContact, User, UserAddress, Education, WorkExperience, Skill, Language, Job, JobApplication, JobShortlist
import pdb
def home(request):
    profile_percentage = 0
    categories = getJobsOpeningsByCategories()
    zones = getZones()
    recent_jobs = getRecentJobs()
    for job in recent_jobs:
        job.time_ago = time_since(job.timestamp)
    if request.user.is_authenticated:
         profile_percentage = calculate_profile_completion(request.user)
        
    return render(request, "index.html", {"categories": categories, "zones" : zones, "recent_jobs": recent_jobs,"profile_percentage": profile_percentage })


def about(request):
    return render(request, "about.html")
    
@institution_required
def institution_dashboard(request):
    # Ensure only logged-in institution users access this
    user = request.institution

    # Assuming institution user posts jobs using 'posted_by'
    job_count = Job.objects.filter(posted_by=user).count()

    # Count job applications related to this user's jobs
    application_count = JobApplication.objects.filter(job__posted_by=user).count()

    # Count shortlisted candidates related to this user's jobs
    shortlisted_count = JobShortlist.objects.filter(job__posted_by=user).count()

    context = {
        'job_count': job_count,
        'application_count': application_count,
        'shortlisted_count': shortlisted_count,
    }

    return render(request, 'institution/dashboard.html', context)


@institution_required
def institution_profile(request):
    choices = get_institution_choices()

    # Check if institution is new (register) or existing (update)
    is_new = not hasattr(request, 'institution') or request.institution is None

    if not is_new:
        institution = get_object_or_404(Institution, id=request.institution.id)
    else:
        institution = None

    if request.method == "POST":
        # --- Common Fields ---
        name = request.POST.get('name')
        category = request.POST.get('category')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        website = request.POST.get('website')
        about = request.POST.get('about')
        year_established = request.POST.get('year_established')
        board = request.POST.get('board')
        is_omeiat_member = bool(request.POST.get('is_omeiat_member'))
        omeiat_member_since = request.POST.get('omeiat_member_since')
        logo = request.FILES.get('logo')

        if is_new:
            # --- Password Validation for Registration ---
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            if not password or password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return render(request, 'ins_register.html', {
                    'categories': choices['categories'],
                })

            # --- Create Institution ---
            institution = Institution.objects.create(
                name=name,
                category=category,
                email=email,
                phone=phone,
                website=website,
                about=about,
                password=make_password(password),
                year_established=year_established,
                board=board,
                is_omeiat_member=is_omeiat_member,
                omeiat_member_since=omeiat_member_since,
                logo=logo
            )

            messages.success(request, "Institution registered successfully.")
        else:
            # --- Update Existing Institution ---
            institution.name = name
            institution.category = category
            institution.email = email
            institution.phone = phone
            institution.website = website
            institution.about = about
            institution.year_established = year_established
            institution.board = board
            institution.is_omeiat_member = is_omeiat_member
            institution.omeiat_member_since = omeiat_member_since
            if logo:
                institution.logo = logo
            institution.save()

            messages.success(request, "Institution profile updated successfully.")

        # --- Save Address (Create or Update) ---
        address, _ = InstitutionAddress.objects.get_or_create(institution=institution)
        address.building_no = request.POST.get('building_no')
        address.street = request.POST.get('street')
        address.area = request.POST.get('area')
        address.city = request.POST.get('city')
        address.district = request.POST.get('district')
        address.state = request.POST.get('state')
        address.country = request.POST.get('country')
        address.pincode = request.POST.get('pincode')
        address.save()

        # --- Save Strength (optional) ---
        strength, _ = InstitutionStrength.objects.get_or_create(institution=institution)
        strength.students_male = request.POST.get('students_male') or 0
        strength.students_female = request.POST.get('students_female') or 0
        strength.teachers_male = request.POST.get('teachers_male') or 0
        strength.teachers_female = request.POST.get('teachers_female') or 0
        strength.non_teaching_staff = request.POST.get('non_teaching_staff') or 0
        strength.save()

        # --- Save Contacts ---
        institution.contacts.all().delete()
        contact_types = request.POST.getlist('contact_type[]')
        contact_names = request.POST.getlist('contact_name[]')
        contact_phones = request.POST.getlist('contact_phone[]')
        contact_emails = request.POST.getlist('contact_email[]')

        for c_type, c_name, c_phone, c_email in zip(contact_types, contact_names, contact_phones, contact_emails):
            if c_name or c_phone or c_email:
                InstitutionContact.objects.create(
                    institution=institution,
                    contact_type=c_type,
                    name=c_name,
                    phone=c_phone,
                    email=c_email
                )

        return redirect('dashboard')

    # GET Request
    return render(request, 'institution/register.html' if is_new else 'institution/profile.html', {
        'institution': institution,
        'categories': choices['categories'],
        'contact_types': choices['contact_types'],
    })
@login_required
def profile_view(request):
    user = request.user

    # Ensure address exists
    address, created = UserAddress.objects.get_or_create(user=user)

    if request.method == "POST":
        # ---- USER BASIC INFO ----
        user.username = request.POST.get("username", user.username)
        user.email = request.POST.get("email", user.email)
        user.phone = request.POST.get("phone")
        user.dob = request.POST.get("dob") or None
        user.father_name = request.POST.get("father_name")
        user.spouse_name = request.POST.get("spouse_name")

        if request.FILES.get("profile_picture"):
            user.profile_picture = request.FILES["profile_picture"]

        user.save()

        # ---- ADDRESS ----
        address.building_no = request.POST.get("building_no")
        address.street = request.POST.get("street")
        address.area = request.POST.get("area")
        address.district = request.POST.get("district")
        address.state = request.POST.get("state")
        address.pincode = request.POST.get("pincode")
        address.save()

        # ---- EDUCATION ----
        Education.objects.filter(user=user).delete()
        edu_levels = request.POST.getlist("edu_level[]")
        edu_institutions = request.POST.getlist("edu_institution[]")
        edu_degrees = request.POST.getlist("edu_degree[]")
        edu_percentages = request.POST.getlist("edu_percentage[]")

        for i in range(len(edu_levels)):
            if edu_institutions[i].strip():
                Education.objects.create(
                    user=user,
                    level=edu_levels[i],
                    institution=edu_institutions[i],
                    degree=edu_degrees[i] or "",
                    percentage=edu_percentages[i] or None,
                )

        # ---- EXPERIENCE ----
        WorkExperience.objects.filter(user=user).delete()
        exp_companies = request.POST.getlist("exp_company[]")
        exp_roles = request.POST.getlist("exp_role[]")
        exp_start_dates = request.POST.getlist("exp_start_date[]")
        exp_end_dates = request.POST.getlist("exp_end_date[]")
        exp_descriptions = request.POST.getlist("exp_description[]")

        for i in range(len(exp_roles)):
            if exp_roles[i].strip():
                WorkExperience.objects.create(
                    user=user,
                    company=exp_companies[i],
                    role=exp_roles[i],
                    start_date=exp_start_dates[i] or None,
                    end_date=exp_end_dates[i] or None,
                    description=exp_descriptions[i],
                )

        # ---- SKILLS ----
        Skill.objects.filter(user=user).delete()
        skill_names = request.POST.getlist("skill_name[]")
        skill_levels = request.POST.getlist("skill_level[]")

        for i in range(len(skill_names)):
            if skill_names[i].strip():
                Skill.objects.create(
                    user=user,
                    name=skill_names[i],
                    level=skill_levels[i],
                )

        # ---- LANGUAGES ----
        Language.objects.filter(user=user).delete()
        lang_names = request.POST.getlist("lang_name[]")
        lang_proficiencies = request.POST.getlist("lang_proficiency[]")

        for i in range(len(lang_names)):
            if lang_names[i].strip():
                Language.objects.create(
                    user=user,
                    name=lang_names[i],
                    proficiency=lang_proficiencies[i],
                )

        return redirect("profile")  # Redirect after save

    # ---- GET ----
    context = {"user": user}
    return render(request, "profile.html", context)