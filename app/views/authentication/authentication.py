from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from app.models import Institution
User = get_user_model()


# ----------------------------
# USER LOGIN
# ----------------------------
def user_login(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in.")
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if not getattr(user, "is_deleted", False):
                login(request, user)
                messages.success(request, "Logged in successfully.")
                return redirect("home")
            else:
                messages.error(request, "Your account has been deactivated.")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")

    return render(request, "login.html")


# ----------------------------
# USER LOGOUT
# ----------------------------
def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have been logged out successfully.")
    return redirect("login")


# ----------------------------
# USER REGISTRATION
# ----------------------------
def register_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password1")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("register")

        # ✅ create_user handles hashing
        user = User.objects.create_user(username=username, password=password, email=email, phone=phone)
        login(request, user)
        messages.success(request, "User registered successfully.")
        return redirect("home")

    return render(request, "register.html")


# ----------------------------
# UPDATE USER PROFILE
# ----------------------------
@login_required
def update_user(request):
    if request.method == "POST":
        user = request.user

        editable_fields = [
            "username", "spouse_name", "dob", "mother_tongue", "address",
            "qualification", "schooling", "languages_known", "working_experience_years",
            "describing_experience", "last_salary", "expected_salary",
            "reference_by_1", "reference_by_2", "joining_availability",
            "aim_of_life", "about_family"
        ]

        for field in editable_fields:
            if field in request.POST:
                value = request.POST.get(field)
                setattr(user, field, value if value != "" else None)

        if "profile_picture" in request.FILES:
            user.profile_picture = request.FILES["profile_picture"]

        # Profile completion %
        exclude_fields = [
            "id", "password", "last_login", "is_superuser", "is_staff", "is_active",
            "date_joined", "groups", "user_permissions",
            "profile_percentage", "profile_visibility", "is_deleted", "timestamp", "email"
        ]
        model_fields = [f.name for f in user._meta.get_fields() if hasattr(f, "attname")]
        total_fields, filled_fields = 0, 0

        for field_name in model_fields:
            if field_name not in exclude_fields:
                total_fields += 1
                value = getattr(user, field_name, None)
                if value not in [None, "", 0]:
                    filled_fields += 1

        user.profile_percentage = int((filled_fields / total_fields) * 100) if total_fields > 0 else 0
        user.save()

        messages.success(request, f"Profile updated successfully! ({user.profile_percentage}% complete)")
        return redirect("profile")

    return redirect("profile")


# ----------------------------
# INSTITUTION REGISTRATION
# ----------------------------
def institution_register(request):
    if request.method == "POST":
        email = request.POST.get("email").lower()
        if Institution.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect("institution_register")

        institution = Institution(
            name=request.POST.get("name"),
            email=email,
            phone=request.POST.get("phone"),
            website=request.POST.get("website"),
            category=request.POST.get("category"),
            address=request.POST.get("address"),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            district=request.POST.get("district"),
            country=request.POST.get("country"),
            pincode=request.POST.get("pincode") or 0,
            year_established=request.POST.get("year_established") or 0,
            omeiat_member_since=request.POST.get("member_since") or 0,
            board=request.POST.get("board"),
            no_of_students=request.POST.get("no_of_students") or 0,
            no_of_boys=request.POST.get("no_of_boys") or 0,
            no_of_girls=request.POST.get("no_of_girls") or 0,
            no_of_gents_staff=request.POST.get("no_of_gents_staff") or 0,
            no_of_ladies_staff=request.POST.get("no_of_ladies_staff") or 0,
            no_of_non_teaching_staff=request.POST.get("no_of_non_teaching_staff") or 0,
            recruitment_contact=request.POST.get("recruitment_contact"),
            principal_name=request.POST.get("principal_name"),
            coordinator_name=request.POST.get("coordinator_name"),
            correspondent_name=request.POST.get("correspondent_name"),
            founder_name=request.POST.get("founder_name"),
        )
        password = request.POST.get("password")
        institution.password = make_password(password)
        institution.save()

        messages.success(request, "Institution registered successfully! Please login.")
        return redirect("institution_login")

    return render(request, "institution_register_form.html")


# ----------------------------
# INSTITUTION LOGIN
# ----------------------------
def institution_login(request):
    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")

        try:
            institution = Institution.objects.get(email=email)
            if check_password(password, institution.password):
                # Save institution info in session
                request.session["institution_id"] = institution.id
                request.session["institution_name"] = institution.name
                messages.success(request, f"Welcome back, {institution.name}!")
                return redirect("institution_dashboard")
            else:
                messages.error(request, "Invalid email or password.")
        except Institution.DoesNotExist:
            messages.error(request, "Invalid email or password.")

    return render(request, "institution_login_form.html")


# ----------------------------
# INSTITUTION LOGOUT
# ----------------------------
def institution_logout(request):
    request.session.flush()
    messages.success(request, "You have been logged out successfully.")
    return redirect("home")
