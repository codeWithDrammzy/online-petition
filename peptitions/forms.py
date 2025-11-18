from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Petition  # import your Petition model

User = get_user_model()


# === Registration Form ===
class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=255, required= True)
    last_name = forms.CharField(max_length=255, required=True)
    class Meta:
        model = User
        fields = ["first_name", "last_name" ,"email", "password1", "password2"]
        help_texts = {
            'password1': None,
            'password2': None,
        }


# === Login Form (email + password) ===
class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True})
    )

    def confirm_login_allowed(self, user):
        # Optional: restrict inactive users
        if not user.is_active:
            raise forms.ValidationError(
                "This account is inactive.",
                code="inactive",
            )


# === Petition Form ===
class PetitionForm(forms.ModelForm):
    class Meta:
        model = Petition
        fields = ["title", "description", "image", "category", "target_signatures"]
       


# === Petition Form ===
class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__' 
        