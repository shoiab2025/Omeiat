from django import forms

class EmailAuthenticationForm(form.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(UserCreationForm):
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password1', 'password2',
            'dob', 'age', 'phone', 'father_name', 'spouse_name',
            'profile_picture'
        ]