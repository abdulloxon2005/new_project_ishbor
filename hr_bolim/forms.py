from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from .models import User

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ism'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Familiya'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}))
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, initial='candidate', widget=forms.RadioSelect(attrs={'class': 'role-select'}))
    
    consent_privacy = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class': 'checkbox-input'}), label="Maxfiylik siyosatiga roziman")
    consent_data_processing = forms.BooleanField(required=True, widget=forms.CheckboxInput(attrs={'class': 'checkbox-input'}), label="Ma'lumotlarim qayta ishlanishiga roziman")

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'role')
        widgets = {
             'password': forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Parol'}),
             'role': forms.RadioSelect(attrs={'class': 'role-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        if 'password1' in self.fields:
             self.fields['password1'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Parol'})
             self.fields['password1'].label = "Parol"
        if 'password2' in self.fields:
             self.fields['password2'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Parolni tasdiqlash'})
             self.fields['password2'].label = "Parolni tasdiqlash"

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(username=email).exists():
            raise forms.ValidationError("Bu email manzil bilan foydalanuvchi allaqachon mavjud.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Combine consents for the simple boolean field, or just set it true if both are true
        if self.cleaned_data['consent_privacy'] and self.cleaned_data['consent_data_processing']:
            user.consent_given = True
            user.consent_date = timezone.now()
            
        if commit:
            user.save()
            # Here we could log specific consents to ConsentLog if needed
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Email', 'id': 'email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Parol', 'id': 'password'}))

from .models import CandidateProfile

class CandidateProfileForm(forms.ModelForm):
    class Meta:
        model = CandidateProfile
        fields = ['profile_picture', 'profession', 'experience_years', 'resume_file', 'location', 'about_me', 'skills', 'linkedin', 'github', 'portfolio']
        widgets = {
            'profession': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masalan: Dasturchi'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Yil', 'min': 0}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Masalan: Toshkent'}),
            'about_me': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'O\'zingiz haqingizda qisqacha...'}),
            'skills': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Python, Django, SQL...'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://linkedin.com/in/...'}),
            'github': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://github.com/...'}),
            'portfolio': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://portfolio.com'}),
        }

from .models import Experience, Education

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['company', 'position', 'location', 'start_date', 'end_date', 'is_current', 'description']
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Kompaniya nomi'}),
            'position': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Lavozim'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Shahar/Davlat'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'is_current': forms.CheckboxInput(attrs={'class': 'custom-checkbox'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Vazifalaringiz va yutuqlaringiz...'}),
        }

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'description']
        widgets = {
            'institution': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Oliy o\'quv yurti'}),
            'degree': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Daraja (Bakalavr, Magistr...)'}),
            'field_of_study': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Yo\'nalish'}),
            'start_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 3}),
        }

from .models import Resume

class ResumeForm(forms.ModelForm):
    class Meta:
        model = Resume
        fields = ['title', 'file', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'CV nomi (masalan: Python Developer)'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'custom-checkbox'}),
        }

# Employer Forms
from .models import Company, CompanyProfile, EmployerJob, CandidateApplication, Interview

class CompanyRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Parol'}),
        label="Parol"
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Parolni tasdiqlang'}),
        label="Parolni tasdiqlang"
    )
    consent_data_processing = forms.BooleanField(
        required=True, 
        widget=forms.CheckboxInput(attrs={'class': 'custom-checkbox'}),
        label="Ma'lumotlarni qayta ishlash shartlariga roziman"
    )
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Parollar mos kelmadi!")
        return password2
    
    class Meta:
        model = Company
        fields = ['company_name', 'stir', 'email', 'responsible_person', 'phone', 'consent_data_processing']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Kompaniya nomi'}),
            'stir': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'STIR / Ro\'yxat raqami'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'responsible_person': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Mas\'ul shaxs F.I.O'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Telefon'}),
        }

class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = CompanyProfile
        fields = ['logo', 'description', 'address', 'website', 'facebook', 'linkedin', 'instagram', 'telegram']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Kompaniya haqida qisqacha...'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Manzil'}),
            'website': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://example.com'}),
            'facebook': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://facebook.com/...'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://linkedin.com/company/...'}),
            'instagram': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://instagram.com/...'}),
            'telegram': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://t.me/...'}),
        }

class EmployerJobForm(forms.ModelForm):
    class Meta:
        model = EmployerJob
        fields = ['title', 'employment_type', 'salary_min', 'salary_max', 'requirements', 
                  'responsibilities', 'benefits', 'location', 'deadline', 'positions_count']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Lavozim nomi'}),
            'employment_type': forms.Select(attrs={'class': 'form-input'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Minimal maosh', 'min': 0}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Maksimal maosh', 'min': 0}),
            'requirements': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Talablar...'}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Vazifalar...'}),
            'benefits': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Afzalliklar...'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ish joyi'}),
            'deadline': forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
            'positions_count': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'value': 1}),
        }

class CandidateApplicationForm(forms.ModelForm):
    class Meta:
        model = CandidateApplication
        fields = ['status', 'internal_notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-input'}),
            'internal_notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Izohlar...'}),
        }

class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['scheduled_date', 'duration_minutes', 'interview_type', 'location_link', 'notes']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-input', 'min': 15, 'max': 480, 'value': 60}),
            'interview_type': forms.Select(attrs={'class': 'form-input'}),
            'location_link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'Video havola yoki manzil'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Intervyu haqida izohlar...'}),
        }
