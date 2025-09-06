from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
import pdb

User = get_user_model()

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 1️⃣ Try normal Django authentication first
        user = authenticate(request, username=username, password=password)

        if user is None:
            # 2️⃣ If that fails, manually check password hash
            try:
                db_user = User.objects.get(username=username)
            except User.DoesNotExist:
                messages.error(request, 'Invalid username or password.')
                return redirect('login')

            if check_password(password, db_user.password):
                user = db_user  # password matches, assign to user object
            else:
                messages.error(request, 'Invalid username or password.')
                return redirect('login')

        # 3️⃣ If we have a valid user object, log them in
        if user:
            if not getattr(user, 'is_deleted', False):
                login(request, user)
                messages.success(request, 'Logged in successfully.')
                pdb.set_trace()
                return redirect('home')
            else:
                messages.error(request, 'Your account has been deactivated.')

    return render(request, 'login.html')

def user_logout(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
    return redirect('login')  # Redirect to login page after logout


@login_required
def update_user(request):
    if request.method == 'POST':
        user = request.user

        # Update all editable fields from request.POST
        editable_fields = [
            'username', 'spouse_name', 'dob', 'mother_tongue', 'address',
            'qualification', 'schooling', 'languages_known', 'working_experience_years',
            'describing_experience', 'last_salary', 'expected_salary',
            'reference_by_1', 'reference_by_2', 'joining_availability',
            'aim_of_life', 'about_family'
        ]

        for field in editable_fields:
            if field in request.POST:
                value = request.POST.get(field)
                setattr(user, field, value if value != '' else None)

        # Handle file upload
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']

        # Calculate profile completion dynamically
        exclude_fields = [
            'id', 'password', 'last_login', 'is_superuser', 'is_staff', 'is_active',
            'date_joined', 'groups', 'user_permissions',
            'profile_percentage', 'profile_visibility', 'is_deleted', 'timestamp', 'email'
        ]
        model_fields = [f.name for f in user._meta.get_fields() if hasattr(f, 'attname')]
        total_fields = 0
        filled_fields = 0

        for field_name in model_fields:
            if field_name not in exclude_fields:
                total_fields += 1
                value = getattr(user, field_name, None)
                if value not in [None, '', 0]:
                    filled_fields += 1

        user.profile_percentage = int((filled_fields / total_fields) * 100) if total_fields > 0 else 0

        # Save changes
        user.save()

        # Success message
        messages.success(request, f'Profile updated successfully! ({user.profile_percentage}% complete)')
        return redirect('profile')  # Change 'profile' to your profile view name

    # If not POST, just redirect back
    return redirect('profile')


def register_user(request):
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password1')
        hashed_password = make_password(password)
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('register')
        pdb.set_trace()
        user = User.objects.create_user(username=username, password=hashed_password, email=email, phone=phone)
        user.save()
        login(request, user)  # Automatically log in the user after registration
        messages.success(request, 'User registered successfully. Please log in.')
        return redirect('home')

    return render(request, 'register.html')  # Render registration form