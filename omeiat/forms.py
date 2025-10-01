from django import forms

class EmailAuthenticationForm(form.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
