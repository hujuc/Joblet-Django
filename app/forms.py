from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from app.models import Profile


class CustomUserCreationForm(UserCreationForm):
    is_provider = forms.BooleanField(required=False, label="Are you a provider?")
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este email já está em uso.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                provider=self.cleaned_data['is_provider']
            )
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control input w-full', 'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control input w-full', 'placeholder': 'Enter your password'})
    )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar', 'about', 'contact_email', 'linkedin', 'twitter', 'facebook']
        widgets = {
            'about': forms.Textarea(attrs={'placeholder': 'Tell us about yourself', 'rows': 4}),
            'contact_email': forms.EmailInput(attrs={'placeholder': 'Enter your email'}),
            'linkedin': forms.URLInput(attrs={'placeholder': 'https://linkedin.com/in/username'}),
            'twitter': forms.URLInput(attrs={'placeholder': 'https://twitter.com/username'}),
            'facebook': forms.URLInput(attrs={'placeholder': 'https://facebook.com/username'}),
        }

