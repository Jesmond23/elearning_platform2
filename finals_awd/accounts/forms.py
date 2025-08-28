from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class RegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]

    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta:
        model = CustomUser
        fields= ['username','email','first_name','last_name','password1','password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        user.is_student = (role == 'student')
        user.is_teacher = (role == 'teacher')
        if commit:
            user.save()
        return user


#Edit Profle Form
class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields=['username', 'first_name', 'last_name', 'profile_picture']

