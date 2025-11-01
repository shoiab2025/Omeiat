import random
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from app.models import Institution, InstitutionAddress, InstitutionApproval
from app.utils import institution_required, get_institution_choices
from django.utils.html import strip_tags
import pdb
User = get_user_model()
from django.utils import timezone
# ----------------------------
# OTP Helpers
# ----------------------------
def generate_otp():
    """Generate a 6-digit numeric OTP as a string."""
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
        "site_name": "Careers in Omeiat Institutions",
        "year": timezone.now().year,
    }

    # Render email templates
    html_content = render_to_string("email/otp_email.html", context)
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

def send_institution_pending_approval_email(email, institution_name):
    """
    Send a styled HTML email to the institution when registration is complete
    and waiting for admin approval.
    """
    subject = "Your Institution Registration is Pending Approval"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER)
    to = [email]

    # Context for the HTML email
    context = {
        "institution_name": institution_name,
        "site_name": "Careers in Omeiat Institutions",
        "year": timezone.now().year,
    }

    # Render HTML template (create templates/email/institution_pending_approval.html)
    html_content = render_to_string("email/approval_email.html", context)
    
    # Fallback plain-text version
    text_content = (
        f"Hello {institution_name},\n\n"
        "Thank you for registering with OMEIAT EMPLOYMENT PORTAL.\n\n"
        "Your institution registration has been received and is currently pending "
        "approval by our admin team. You’ll receive an email once it has been reviewed and approved.\n\n"
        "Warm regards,\n"
        "Omeiat Team"
    )

    # Send email
    email_message = EmailMultiAlternatives(subject, text_content, from_email, to)
    email_message.attach_alternative(html_content, "text/html")

    try:
        email_message.send()
        print(f"✅ Approval pending email sent successfully to {email}")
    except Exception as e:
        print(f"❌ Failed to send approval pending email to {email}: {e}")

def send_admin_institution_approval_notification(institution_name):
    """
    Send an email notification to the admin when a new institution
    registration is pending approval.
    Automatically uses the email(s) from settings.ADMINS.
    """
    subject = "New Institution Awaiting Approval"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", settings.EMAIL_HOST_USER)

    # Get admin emails from settings.ADMINS
    admin_emails = [email for _, email in getattr(settings, "ADMINS", [])]
    if not admin_emails:
        admin_emails = [from_email]  # fallback to default if ADMINS not set

    # Email context
    context = {
        "institution_name": institution_name,
        "approval_link": getattr(settings, "ADMIN_APPROVAL_URL", "#"),
        "year": timezone.now().year,
    }

    # Render HTML email template
    html_content = render_to_string("email/request_approval.html", context)

    # Plain text fallback
    text_content = (
        f"A new institution, '{institution_name}', has registered on the "
        "OMEIAT EMPLOYMENT PORTAL and is awaiting your approval.\n\n"
        "Please review and approve the registration in the admin dashboard.\n\n"
        "Regards,\nOMEIAT Team"
    )

    # Compose and send email
    email_message = EmailMultiAlternatives(subject, text_content, from_email, admin_emails)
    email_message.attach_alternative(html_content, "text/html")

    try:
        email_message.send()
        print(f"✅ Admin approval notification sent to: {', '.join(admin_emails)}")
    except Exception as e:
        print(f"❌ Failed to send admin approval email: {e}")

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
            send_otp_email(user.email, user.otp, user.username)
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
            approval = InstitutionApproval.objects.create(
                institution=institution,
                is_approved=False
            )
            approval.save()

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
            send_otp_email(institution.email, institution.otp, institution.name)
            send_admin_institution_approval_notification(institution.name)
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
                        send_otp_email(account.email, account.otp, account.username)
                        request.session["pending_user_email"] = email
                        messages.info(request, "OTP sent to your email. Please verify to login.")
                        return redirect("user_verify_otp")
                    login(request, account)
                    messages.success(request, f"Welcome back, {account.username}!")
                    return redirect("home")

            if account_type == "institution":
                account = Institution.objects.get(email=email)
                if check_password(password, account.password):
                    if not account.is_otp_verified:
                        account.otp = generate_otp()
                        account.save()
                        send_otp_email(account.email, account.otp, account.name)
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
                request.session["institution_email"] = account.email
                messages.success(request, "OTP verified successfully. You are now logged in.")
                # After institution.save()
                send_institution_pending_approval_email(request.session["institution_email"], request.session["institution_name"])
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
