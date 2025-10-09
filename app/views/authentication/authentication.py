import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from app.models import Institution, InstitutionAddress
from app.utils import institution_required, get_institution_choices
from django.utils.html import strip_tags
import pdb
User = get_user_model()

# ----------------------------
# OTP Helpers
# ----------------------------
def generate_otp():
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    """Send OTP to user's email"""
    subject = "Your OTP Verification Code"
    message = f"Dear User,\n\nYour OTP code is: {otp}\n\nUse this to verify your account."
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email])


# ==========================
# REGISTER FUNCTION
# ==========================

def register_account(request, account_type="user"):
    """
    Register a User or Institution.
    account_type: "user" or "institution"
    """
    choices = get_institution_choices()  # Includes 'categories'

    if request.method == "POST":
        pdb.set_trace()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password1", "")
        confirm_password = request.POST.get("password2", "")
        redirect_url = "register" if account_type == "user" else "institution_register"

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect(redirect_url)

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect(redirect_url)

        # Check if email already exists
        if account_type == "user" and User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect(redirect_url)
        if account_type == "institution" and Institution.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect(redirect_url)

        if account_type == "user":
            username = request.POST.get("username", "")
            phone = request.POST.get("phone", "")
            user = User.objects.create_user(
                username=username,
                email=email,
                phone=phone,
                password=password
            )
            user.is_otp_verified = False
            user.otp = generate_otp()
            user.save()
            send_otp_email(user.email, user.otp)
            request.session["pending_user_email"] = email
            messages.success(request, "Registration successful! Please verify OTP.")
            return redirect("user_verify_otp")

        elif account_type == "institution":
            institution = Institution(
                name=request.POST.get("name", ""),
                email=email,
                phone=request.POST.get("phone", ""),
                website=request.POST.get("website", ""),
                category=request.POST.get("category", ""),
                board=request.POST.get("board", ""),
                about=strip_tags(request.POST.get("about", "")),
                is_otp_verified=False,
                otp=generate_otp(),
                is_omeiat_member=bool(request.POST.get("is_omeiat_member")),
                omeiat_member_since=request.POST.get("omeiat_member_since") or None,
            )

            # Year Established
            try:
                institution.year_established = int(request.POST.get("year_established", 0))
            except ValueError:
                institution.year_established = 0

            # Handle logo upload
            if 'logo' in request.FILES:
                logo_file = request.FILES['logo']
                institution.logo = logo_file  # Make sure your model has an ImageField

            # Password hashing
            institution.password = make_password(password)
            institution.save()

            # Address handling (assuming OneToOne or ForeignKey relationship)
            address_data = {
                "building_no": request.POST.get("building_no", ""),
                "street": request.POST.get("street", ""),
                "area": request.POST.get("area", ""),
                "city": request.POST.get("city", ""),
                "district": request.POST.get("district", ""),
                "state": request.POST.get("state", ""),
                "country": request.POST.get("country", ""),
                "pincode": request.POST.get("pincode", ""),
            }

            address = InstitutionAddress(**address_data)
            address.institution = institution  # Assuming FK to Institution
            address.save()

            # Send OTP
            send_otp_email(institution.email, institution.otp)
            request.session["pending_institution_email"] = email
            messages.success(request, "Institution registered! Please verify OTP.")
            return redirect("institution_verify_otp")

    # GET request
    template = "register.html" if account_type == "user" else "ins_register.html"
    return render(request, template, {
        'categories': choices.get('categories', []),
    })
# ==========================
# LOGIN FUNCTION
# ==========================
def login_account(request, account_type="user"):
    """
    Login a User or Institution.
    account_type: "user" or "institution"
    """
    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        try:
            if account_type == "user":
                account = User.objects.get(email=email)
                if check_password(password, account.password):
                    if not account.is_otp_verified:
                        account.otp = generate_otp()
                        account.save()
                        send_otp_email(account.email, account.otp)
                        request.session["pending_user_email"] = email
                        messages.info(request, "OTP sent to your email. Please verify to login.")
                        return redirect("user_verify_otp")
                    login(request, account)
                    messages.success(request, f"Welcome back, {account.username}!")
                    return redirect("home")

            if account_type == "institution":
                account = Institution.objects.get(email=email)
                if password == account.password:
                    if not account.is_otp_verified:
                        account.otp = generate_otp()
                        account.save()
                        send_otp_email(account.email, account.otp)
                        request.session["pending_institution_email"] = email
                        messages.info(request, "OTP sent to your email. Please verify to login.")
                        return redirect("institution_verify_otp")
                    request.session["institution_id"] = account.id
                    request.session["institution_name"] = account.name
                    messages.success(request, f"Welcome back, {account.name}!")
                    return redirect("dashboard")

            messages.error(request, "Invalid email or password.")
        except (User.DoesNotExist, Institution.DoesNotExist):
            messages.error(request, "Invalid email or password.")

    template = "login.html" if account_type=="user" else "ins_login.html"
    return render(request, template)


# ==========================
# OTP VERIFICATION
# ==========================
def verify_otp(request, account_type="user"):
    """
    Verify OTP for User or Institution.
    account_type: "user" or "institution"
    """
    session_key = "pending_user_email" if account_type=="user" else "pending_institution_email"
    email = request.session.get(session_key)
    if not email:
        messages.error(request, "No pending OTP verification found.")
        return redirect("user_login" if account_type=="user" else "institution_login")

    account_model = User if account_type=="user" else Institution
    account = get_object_or_404(account_model, email=email)

    if request.method == "POST":
        otp_entered = request.POST.get("otp")
        if otp_entered == account.otp:
            account.is_otp_verified = True
            account.otp = None
            account.save()
            if account_type == "user":
                login(request, account)
                messages.success(request, "OTP verified successfully. You are now logged in.")
                return redirect("home")
            else:
                request.session["institution_id"] = account.id
                request.session["institution_name"] = account.name
                messages.success(request, "OTP verified successfully. You are now logged in.")
                return redirect("dashboard")
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect("user_verify_otp" if account_type=="user" else "institution_verify_otp")

    template = "verify_otp.html" if account_type=="user" else "institution_verify_otp.html"
    return render(request, template)


# ==========================
# LOGOUT FUNCTION
# ==========================
def logout_account(request, account_type="user"):
    """
    Logout User or Institution
    """
    if account_type == "user":
        if request.user.is_authenticated:
            logout(request)
            messages.success(request, "You have been logged out successfully.")
        return redirect("user_login")
    else:
        request.session.flush()
        messages.success(request, "You have been logged out successfully.")
        return redirect("institution_login")
