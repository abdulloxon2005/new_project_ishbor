from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Job, Department, CandidateProfile, Application, SavedJob, Experience, Education, Resume, PrivacyPolicy, DataDeletionRequest, Message, Company, CompanyProfile, EmployerJob, CandidateApplication, Interview, Contact, ConsentLog
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm, CustomAuthenticationForm, CompanyRegistrationForm, CompanyProfileForm, EmployerJobForm, CandidateApplicationForm, InterviewForm
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count, Avg
from types import SimpleNamespace
from django.utils import timezone
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings

from functools import wraps


def candidate_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if getattr(request.user, 'role', None) != 'candidate':
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped


def employer_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        if getattr(request.user, 'role', None) != 'employer':
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped

def home_view(request):
    # So‘nggi 5 ta ochiq ishlarni olish
    latest_jobs = Job.objects.filter(status='open').order_by('-posted_at')[:5]
    return render(request, 'hr_bolim/home.html', {'latest_jobs': latest_jobs})

def submit_complaint(request):
    """Submit a complaint form"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        consent = request.POST.get('consent')
        
        if not all([name, email, subject, message, consent]):
            messages.error(request, "Barcha maydonlarni to'ldiring.")
            return redirect('submit_complaint')
        
        # Create contact/complaint
        contact = Contact.objects.create(
            name=name,
            email=email,
            subject=subject,
            message=message,
            consent_given=True if consent else False,
            consent_date=timezone.now() if consent else None
        )
        
        messages.success(request, "Shikoyatingiz muvaffaqiyatli yuborildi. Tez orada sizga javob beramiz!")
        return redirect('home')
    
    return render(request, 'hr_bolim/complaint_form.html')

def jobs_list_view(request):
    # Legacy jobs
    legacy_jobs = Job.objects.filter(status='open').order_by('-posted_at')
    
    # Employer jobs
    employer_jobs = EmployerJob.objects.filter(status='active').order_by('-created_at')

    # Filters
    query = request.GET.get('q')
    location = request.GET.get('location')
    department_id = request.GET.get('department')
    emp_type = request.GET.get('type')
    salary_min = request.GET.get('salary_min')
    salary_max = request.GET.get('salary_max')
    experience = request.GET.get('experience')

    # Apply filters to legacy jobs
    if query:
        legacy_jobs = legacy_jobs.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(department__name__icontains=query))

    if location:
        legacy_jobs = legacy_jobs.filter(loaction__icontains=location)

    if department_id:
        legacy_jobs = legacy_jobs.filter(department_id=department_id)

    if emp_type:
        jobs = jobs.filter(employment_type=emp_type)
        
    if salary_min:
        legacy_jobs = legacy_jobs.filter(salary_max__gte=salary_min)

    if salary_max:
        legacy_jobs = legacy_jobs.filter(salary_min__lte=salary_max)

    if experience and experience != 'all':
        if experience == '0':
            legacy_jobs = legacy_jobs.filter(experience_required='0')
        elif experience == '1-3':
            legacy_jobs = legacy_jobs.filter(experience_required='1-3')
        elif experience == '3-5':
            legacy_jobs = legacy_jobs.filter(experience_required='3-5')
        elif experience == '5+':
            legacy_jobs = legacy_jobs.filter(experience_required='5+')

    # Apply filters to employer jobs
    if query:
        employer_jobs = employer_jobs.filter(Q(title__icontains=query) | Q(requirements__icontains=query) | Q(responsibilities__icontains=query))

    if location:
        employer_jobs = employer_jobs.filter(location__icontains=location)

    if emp_type:
        employer_jobs = employer_jobs.filter(employment_type=emp_type)

    if salary_min:
        employer_jobs = employer_jobs.filter(salary_max__gte=salary_min)

    if salary_max:
        employer_jobs = employer_jobs.filter(salary_min__lte=salary_max)

    # Combine and sort
    combined_jobs = list(legacy_jobs) + list(employer_jobs)
    # Simple sort by date-like attribute; for production, use a more sophisticated approach
    combined_jobs.sort(key=lambda x: getattr(x, 'posted_at', None) or getattr(x, 'created_at', None) or timezone.now(), reverse=True)

    departments = Department.objects.all()

    context = {
        'jobs': combined_jobs,
        'departments': departments,
    }
    return render(request, 'hr_bolim/jobs_list.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.role == 'candidate':
                return redirect('candidate_dashboard')
            elif user.role == 'employer':
                return redirect('employer_dashboard')
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'hr_bolim/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'hr_bolim/login.html'
    authentication_form = CustomAuthenticationForm

    def get_success_url(self):
        return '/dashboard/'

def privacy_policy_view(request):
    return render(request, 'candidate/privacy.html')

@login_required
def dashboard_view(request):
    """Unified dashboard for both candidate and employer"""
    # Route to appropriate dashboard based on user role
    if request.user.role == 'candidate':
        return candidate_dashboard(request)
    elif request.user.role == 'employer':
        return employer_dashboard(request)
    elif request.user.role == 'admin' or request.user.is_superuser:
        return admin_dashboard(request)
    else:
        return redirect('home')

@candidate_required
def candidate_dashboard(request):
    
    profile, created = CandidateProfile.objects.get_or_create(user=request.user)
    applied_count = Application.objects.filter(user=request.user).count()
    saved_count = SavedJob.objects.filter(user=request.user).count()
    interview_count = Application.objects.filter(user=request.user, status='interview').count()
    unread_messages = Message.objects.filter(recipient=request.user, is_read=False).count()
    
    context = {
        'profile': profile,
        'applied_count': applied_count,
        'saved_count': saved_count,
        'interview_count': interview_count,
        'unread_messages': unread_messages,
    }
    return render(request, 'hr_bolim/candidate/dashboard.html', context)

from .forms import CandidateProfileForm
from django.contrib import messages

@candidate_required
def candidate_profile(request):
    
    profile, created = CandidateProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = CandidateProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil muvaffaqiyatli yangilandi!")
            return redirect('candidate_profile')
    else:
        form = CandidateProfileForm(instance=profile)
    
    resumes = request.user.resumes.all().order_by('-created_at')
    
    context = {
        'form': form,
        'profile': profile,
        'resumes': resumes
    }
    return render(request, 'hr_bolim/candidate/profile.html', context)

from .forms import ExperienceForm, EducationForm
from .models import Experience, Education
from django.shortcuts import get_object_or_404

@candidate_required
def candidate_cv(request):
    
    experiences = Experience.objects.filter(user=request.user).order_by('-start_date')
    educations = Education.objects.filter(user=request.user).order_by('-start_date')
    resumes = request.user.resumes.all().order_by('-created_at')
    
    context = {
        'experiences': experiences,
        'educations': educations,
        'resumes': resumes
    }
    return render(request, 'hr_bolim/candidate/cv_list.html', context)

from .forms import ExperienceForm, EducationForm, ResumeForm
from .models import Experience, Education, Resume

@candidate_required
def add_resume(request):
    
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            messages.success(request, "CV muvaffaqiyatli yuklandi!")
            return redirect('candidate_cv')
    else:
        form = ResumeForm()
    
    return render(request, 'hr_bolim/candidate/form_generic.html', {'form': form, 'title': 'CV yuklash'})

@candidate_required
def add_experience(request):
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST)
        if form.is_valid():
            exp = form.save(commit=False)
            exp.user = request.user
            exp.save()
            messages.success(request, "Ish tajribasi qo'shildi!")
            return redirect('candidate_cv')
    else:
        form = ExperienceForm()
    
    return render(request, 'hr_bolim/candidate/form_generic.html', {'form': form, 'title': 'Ish tajribasi qo\'shish'})

@candidate_required
def add_education(request):
    
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            edu = form.save(commit=False)
            edu.user = request.user
            edu.save()
            messages.success(request, "Ta'lim ma'lumoti qo'shildi!")
            return redirect('candidate_cv')
    else:
        form = EducationForm()
    
    return render(request, 'hr_bolim/candidate/form_generic.html', {'form': form, 'title': 'Ta\'lim qo\'shish'})

@candidate_required
def edit_resume(request, id):
    
    resume = get_object_or_404(Resume, id=id, user=request.user)
    
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES, instance=resume)
        if form.is_valid():
            form.save()
            messages.success(request, "CV ma'lumotlari yangilandi!")
            return redirect('candidate_cv')
    else:
        form = ResumeForm(instance=resume)
    
    return render(request, 'hr_bolim/candidate/form_generic.html', {'form': form, 'title': 'CV tahrirlash'})

@candidate_required
def edit_experience(request, id):
    
    experience = get_object_or_404(Experience, id=id, user=request.user)
    
    if request.method == 'POST':
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            messages.success(request, "Ish tajribasi yangilandi!")
            return redirect('candidate_cv')
    else:
        form = ExperienceForm(instance=experience)
    
    return render(request, 'hr_bolim/candidate/form_generic.html', {'form': form, 'title': 'Ish tajribasini tahrirlash'})

@candidate_required
def edit_education(request, id):
    
    education = get_object_or_404(Education, id=id, user=request.user)
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            messages.success(request, "Ta'lim ma'lumotlari yangilandi!")
            return redirect('candidate_cv')
    else:
        form = EducationForm(instance=education)
    
    return render(request, 'hr_bolim/candidate/form_generic.html', {'form': form, 'title': 'Ta\'lim ma\'lumotlarini tahrirlash'})

@candidate_required
def delete_item(request, model_name, id):
    
    if model_name == 'experience':
        item = get_object_or_404(Experience, id=id, user=request.user)
    elif model_name == 'education':
        item = get_object_or_404(Education, id=id, user=request.user)
    elif model_name == 'resume':
        item = get_object_or_404(Resume, id=id, user=request.user)
    else:
        return redirect('candidate_cv')
    
    item.delete()
    messages.warning(request, "Ma'lumot o'chirildi.")
    return redirect('candidate_cv')

# GDPR view

from django.http import HttpResponse, JsonResponse
from django.core import serializers
from .models import PrivacyPolicy, DataDeletionRequest
import json
from django.shortcuts import render

@candidate_required
def apply_job(request, job_id):
    
    job = get_object_or_404(Job, id=job_id)
    
    # Check if already applied
    if Application.objects.filter(user=request.user, job=job).exists():
        messages.warning(request, "Siz bu ishga allaqachon topshirgansiz.")
        return redirect('candidate_dashboard') # Or job detail

    if request.method == 'POST':
        # 1-Click with Profile CV or Selected Resume
        resume_id = request.POST.get('resume_id')
        cover_letter = request.POST.get('cover_letter', '')
        
        application = Application(user=request.user, job=job, cover_letter=cover_letter)
        
        if resume_id:
            # Use existing Resume
            resume = get_object_or_404(Resume, id=resume_id, user=request.user)
            application.resume_file = resume.file
        elif request.user.candidate_profile.resume_file:
            # Use Profile Default
            application.resume_file = request.user.candidate_profile.resume_file
        elif 'resume_file' in request.FILES:
             # Upload new (maybe save as Resume too? For now just Application)
            application.resume_file = request.FILES['resume_file']
        else:
            messages.error(request, "Rezyume yuklang yoki tanlang.")
            return redirect('jobs_list') # Should handle this better UI wise

        application.consent_given = True
        application.consent_date = timezone.now()
        application.save()
        messages.success(request, "Arizangiz muvaffaqiyatli yuborildi!")
        return redirect('my_applications')
    
    return redirect('jobs_list')


@login_required
def apply_employer_job(request, job_id):
    """Apply to an EmployerJob (posted by companies). Creates CandidateApplication."""
    if request.user.role != 'candidate':
        return redirect('home')

    try:
        emp_job = EmployerJob.objects.get(id=job_id, status='active')
    except EmployerJob.DoesNotExist:
        messages.error(request, "Vakansiya topilmadi.")
        return redirect('jobs_list')

    # Check duplicate
    if CandidateApplication.objects.filter(job=emp_job, candidate=request.user).exists():
        messages.warning(request, "Siz bu vakansiyaga allaqachon topshirgansiz.")
        return redirect('jobs_list')

    if request.method == 'POST':
        # Similar resume selection logic as apply_job
        resume_id = request.POST.get('resume_id')
        if resume_id:
            try:
                resume = Resume.objects.get(id=resume_id, user=request.user)
                resume_file = resume.file
            except Resume.DoesNotExist:
                resume_file = None
        elif hasattr(request.user, 'candidate_profile') and request.user.candidate_profile.resume_file:
            resume_file = request.user.candidate_profile.resume_file
        elif 'resume_file' in request.FILES:
            resume_file = request.FILES['resume_file']
        else:
            messages.error(request, "Rezyume yuklang yoki tanlang.")
            return redirect('jobs_list')

        ca = CandidateApplication.objects.create(
            job=emp_job,
            candidate=request.user,
            resume_file=resume_file,
            cover_letter=request.POST.get('cover_letter', ''),
            consent_given=True,
            consent_date=timezone.now()
        )

        # Update counts
        emp_job.application_count = emp_job.application_count + 1
        emp_job.save()

        messages.success(request, "Arizangiz muvaffaqiyatli yuborildi!")
        return redirect('my_applications')

    return redirect('jobs_list')

@candidate_required
def my_applications(request):
    legacy_apps = Application.objects.filter(user=request.user).order_by('-applied_at')
    employer_apps = CandidateApplication.objects.filter(candidate=request.user).order_by('-applied_at')

    combined = []
    # Legacy applications
    for app in legacy_apps:
        combined.append(SimpleNamespace(
            job=SimpleNamespace(title=app.job.title, department=SimpleNamespace(name=getattr(app.job.department, 'name', ''))),
            applied_at=app.applied_at,
            status=app.status,
        ))

    # Employer posted job applications
    for app in employer_apps:
        dept_like = SimpleNamespace(name=app.job.company.company_name)
        # Map employer status 'new' -> 'pending' for template consistency
        status_map = {'new': 'pending'}
        status = status_map.get(app.status, app.status)
        combined.append(SimpleNamespace(
            job=SimpleNamespace(title=app.job.title, department=dept_like),
            applied_at=app.applied_at,
            status=status,
        ))

    # Sort unified list by applied_at desc
    combined.sort(key=lambda x: x.applied_at or timezone.now(), reverse=True)

    return render(request, 'hr_bolim/candidate/my_applications.html', {'applications': combined})

@candidate_required
def candidate_interviews(request):
    """Show all interviews scheduled for the candidate"""
    # Get all interviews for this candidate's applications
    interviews = Interview.objects.filter(
        application__candidate=request.user
    ).order_by('-scheduled_date')
    
    context = {
        'interviews': interviews
    }
    return render(request, 'hr_bolim/candidate/interviews.html', context)

@login_required
def inbox(request):
    # Get all users who have exchanged messages with current user
    # This is a simple approach, distinct() might be needed database-wise or python-wise
    sent_to = Message.objects.filter(sender=request.user).values_list('recipient', flat=True)
    received_from = Message.objects.filter(recipient=request.user).values_list('sender', flat=True)
    
    user_ids = set(list(sent_to) + list(received_from))
    
    conversations = []
    for user_id in user_ids:
        other_user = User.objects.get(id=user_id)
        last_msg = Message.objects.filter(
            Q(sender=request.user, recipient=other_user) | 
            Q(sender=other_user, recipient=request.user)
        ).order_by('-timestamp').first()
        
        conversations.append({
            'user': other_user,
            'last_message': last_msg
        })
    
    # Sort by last message timestamp
    conversations.sort(key=lambda x: x['last_message'].timestamp, reverse=True)
    
    return render(request, 'hr_bolim/candidate/inbox.html', {'conversations': conversations})

@login_required
def chat_detail(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, recipient=other_user, content=content)
            return redirect('chat_detail', user_id=user_id)
    
    messages_qs = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) | 
        Q(sender=other_user, recipient=request.user)
    ).order_by('timestamp')
    
    # Mark received as read
    Message.objects.filter(sender=other_user, recipient=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'hr_bolim/candidate/chat.html', {
        'other_user': other_user,
        'messages': messages_qs
    })

@login_required
def candidate_gdpr(request):
    if request.user.role != 'candidate':
        return redirect('home')
    
    policy = PrivacyPolicy.objects.filter(is_active=True).order_by('-effective_date').first()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'export_data':
            # Collect data
            user_data = serializers.serialize('json', [request.user])
            try:
                prof_qs = [request.user.candidate_profile]
            except:
                prof_qs = []
            profile_data = serializers.serialize('json', prof_qs)
            exp_data = serializers.serialize('json', request.user.experiences.all())
            edu_data = serializers.serialize('json', request.user.educations.all())
            
            full_data = {
                "user": json.loads(user_data),
                "profile": json.loads(profile_data),
                "experiences": json.loads(exp_data),
                "educations": json.loads(edu_data),
            }
            
            resp = HttpResponse(json.dumps(full_data, indent=4), content_type='application/json')
            resp['Content-Disposition'] = 'attachment; filename="my_data_export.json"'
            return resp
        
        elif action == 'delete_account':
            DataDeletionRequest.objects.get_or_create(user=request.user, status="pending")
            messages.warning(request, "Hisobingiz 30 kun ichida o'chiriladi.")
            return redirect('candidate_gdpr')

        elif action == 'restrict_processing':
            profile = request.user.candidate_profile
            # Toggle
            profile.is_processing_restricted = not profile.is_processing_restricted
            profile.save()
            status = "cheklandi" if profile.is_processing_restricted else "faollashtirildi"
            messages.info(request, f"Ma'lumotlarni qayta ishlash {status}.")
            return redirect('candidate_gdpr')

    del_req = DataDeletionRequest.objects.filter(user=request.user, status='pending').first()
    
    # Consent History
    consent_history = []
    # Registration
    if request.user.consent_given:
         consent_history.append({
             'action': "Ro'yxatdan o'tish",
             'date': request.user.consent_date or request.user.date_joined,
             'details': "Maxfiylik siyosati va shartlarga rozilik"
         })
    
    # Applications
    apps = Application.objects.filter(user=request.user, consent_given=True)
    for app in apps:
        consent_history.append({
            'action': f"Ariza: {app.job.title}",
            'date': app.consent_date or app.applied_at,
            'details': f"{app.job.department.name} uchun ma'lumotlarni uzatish"
        })
        
    consent_history.sort(key=lambda x: x['date'], reverse=True)

    return render(request, 'hr_bolim/candidate/gdpr.html', {
        'policy': policy,
        'deletion_request': del_req,
        'consent_history': consent_history,
        'profile': request.user.candidate_profile
    })

# ----------------------------------------------------------------
# Employer Views
# ----------------------------------------------------------------

@employer_required
def employer_dashboard(request):
    
    try:
        company = Company.objects.get(user=request.user)
        profile, created = CompanyProfile.objects.get_or_create(company=company)
    except Company.DoesNotExist:
        return redirect('employer_register')
    
    # Statistics
    total_jobs = EmployerJob.objects.filter(company=company).count()
    active_jobs = EmployerJob.objects.filter(company=company, status='active').count()
    total_applications = CandidateApplication.objects.filter(job__company=company).count()
    new_applications = CandidateApplication.objects.filter(job__company=company, status='new').count()
    profile_views = profile.profile_views if profile else 0
    
    # Recent applications
    recent_applications = CandidateApplication.objects.filter(
        job__company=company
    ).order_by('-applied_at')[:5]
    
    # Popular jobs
    popular_jobs = EmployerJob.objects.filter(
        company=company
    ).order_by('-view_count')[:5]
    
    context = {
        'company': company,
        'profile': profile,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'new_applications': new_applications,
        'profile_views': profile_views,
        'recent_applications': recent_applications,
        'popular_jobs': popular_jobs,
    }
    return render(request, 'hr_bolim/employer/dashboard.html', context)

def employer_register_public(request):
    """Public employer registration for new users"""
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            # First create user account
            user = User.objects.create_user(
                username=form.cleaned_data['email'],
                email=form.cleaned_data['email'],
                password=form.cleaned_data['password1'],
                role='employer'
            )
            
            # Then create company
            company = form.save(commit=False)
            company.user = user
            company.data_processing_consent = True
            company.consent_date = timezone.now()
            company.save()
            
            # Create profile
            CompanyProfile.objects.create(company=company)
            
            messages.success(request, "Kompaniya muvaffaqiyatli ro'yxatdan o'tkazildi!")
            return redirect('login')
    else:
        form = CompanyRegistrationForm()
    
    return render(request, 'hr_bolim/employer/register.html', {'form': form})

@login_required
def employer_register(request):
    """For existing employers to complete company registration"""
    if request.user.role != 'employer':
        return redirect('home')
    
    # Check if already registered
    try:
        company = Company.objects.get(user=request.user)
        # Company already exists, redirect to dashboard
        return redirect('employer_dashboard')
    except Company.DoesNotExist:
        # No company yet, show registration form
        pass
    
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user
            company.data_processing_consent = True
            company.consent_date = timezone.now()
            company.save()
            
            # Create profile if it doesn't exist
            CompanyProfile.objects.get_or_create(company=company)
            
            messages.success(request, "Kompaniya muvaffaqiyatli ro'yxatdan o'tkazildi!")
            return redirect('employer_dashboard')
    else:
        form = CompanyRegistrationForm()
    
    return render(request, 'hr_bolim/employer/register.html', {'form': form})

@login_required
@employer_required
def employer_profile(request):
    
    try:
        company = Company.objects.get(user=request.user)
        profile = CompanyProfile.objects.get(company=company)
    except Company.DoesNotExist:
        return redirect('employer_register')
    except CompanyProfile.DoesNotExist:
        profile = CompanyProfile.objects.create(company=company)
    
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil muvaffaqiyatli yangilandi!")
            return redirect('employer_profile')
    else:
        form = CompanyProfileForm(instance=profile)
    
    context = {
        'company': company,
        'profile': profile,
        'form': form,
    }
    return render(request, 'hr_bolim/employer/profile.html', context)

@login_required
@employer_required
def employer_jobs(request):
    try:
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        return redirect('employer_register')

    jobs = EmployerJob.objects.filter(company=company).order_by('-created_at')

    context = {
        'company': company,
        'jobs': jobs,
    }
    return render(request, 'hr_bolim/employer/jobs.html', context)

@login_required
def create_job(request):
    if request.user.role != 'employer':
        return redirect('home')
    
    try:
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        return redirect('employer_register')
    
    if request.method == 'POST':
        form = EmployerJobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company
            job.status = 'active'
            job.save()
            
            # Update profile stats
            try:
                profile = CompanyProfile.objects.get(company=company)
                profile.total_jobs_posted += 1
                profile.save()
            except CompanyProfile.DoesNotExist:
                pass
            
            messages.success(request, "Vakansiya muvaffaqiyatli joylandi!")
            return redirect('employer_jobs')
    else:
        form = EmployerJobForm()
    
    return render(request, 'hr_bolim/employer/create_job.html', {'form': form})

@login_required
def edit_job(request, job_id):
    if request.user.role != 'employer':
        return redirect('home')
    
    try:
        company = Company.objects.get(user=request.user)
        job = EmployerJob.objects.get(id=job_id, company=company)
    except (Company.DoesNotExist, EmployerJob.DoesNotExist):
        return redirect('employer_jobs')
    
    if request.method == 'POST':
        form = EmployerJobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Vakansiya muvaffaqiyatli yangilandi!")
            return redirect('employer_jobs')
    else:
        form = EmployerJobForm(instance=job)
    
    return render(request, 'hr_bolim/employer/edit_job.html', {'form': form, 'job': job})

@login_required
def delete_job(request, job_id):
    if request.user.role != 'employer':
        return redirect('home')
    
    try:
        company = Company.objects.get(user=request.user)
        job = EmployerJob.objects.get(id=job_id, company=company)
        job.delete()
        messages.warning(request, "Vakansiya o'chirildi.")
    except (Company.DoesNotExist, EmployerJob.DoesNotExist):
        pass
    
    return redirect('employer_jobs')

@login_required
def employer_applications(request):
    if request.user.role != 'employer':
        return redirect('home')
    
    try:
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        return redirect('employer_register')
    
    applications = CandidateApplication.objects.filter(
        job__company=company
    ).order_by('-applied_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Filter by job
    job_filter = request.GET.get('job')
    if job_filter:
        applications = applications.filter(job_id=job_filter)
    
    jobs = EmployerJob.objects.filter(company=company)
    
    context = {
        'company': company,
        'applications': applications,
        'jobs': jobs,
        'status_filter': status_filter,
        'job_filter': job_filter,
    }
    return render(request, 'hr_bolim/employer/applications.html', context)

@login_required
def application_detail(request, application_id):
    if request.user.role != 'employer':
        return redirect('home')
    
    try:
        company = Company.objects.get(user=request.user)
        application = CandidateApplication.objects.get(
            id=application_id, 
            job__company=company
        )
    except (Company.DoesNotExist, CandidateApplication.DoesNotExist):
        return redirect('employer_applications')
    
    if request.method == 'POST':
        form = CandidateApplicationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Ariza holati yangilandi!")
            return redirect('application_detail', application_id=application_id)
    else:
        form = CandidateApplicationForm(instance=application)
    
    # Get candidate profile if exists
    try:
        candidate_profile = application.candidate.candidate_profile
    except:
        candidate_profile = None
    
    context = {
        'company': company,
        'application': application,
        'form': form,
        'candidate_profile': candidate_profile,
    }
    return render(request, 'hr_bolim/employer/application_detail.html', context)

@login_required
def schedule_interview(request, application_id):
    if request.user.role != 'employer':
        return redirect('home')
    
    try:
        company = Company.objects.get(user=request.user)
        application = CandidateApplication.objects.get(
            id=application_id, 
            job__company=company
        )
    except (Company.DoesNotExist, CandidateApplication.DoesNotExist):
        return redirect('employer_applications')
    
    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.application = application
            interview.save()
            
            # Update application status
            application.status = 'interview'
            application.save()
            
            # Send notification to candidate (you can implement email sending here)
            messages.success(request, "Intervyu muvaffaqiyatli rejalashtirildi!")
            return redirect('application_detail', application_id=application_id)
    else:
        form = InterviewForm()
    
    return render(request, 'hr_bolim/employer/schedule_interview.html', {
        'form': form, 
        'application': application
    })

@login_required
def employer_statistics(request):
    if request.user.role != 'employer':
        return redirect('home')
    
    try:
        company = Company.objects.get(user=request.user)
        profile = CompanyProfile.objects.get(company=company)
    except Company.DoesNotExist:
        return redirect('employer_register')
    except CompanyProfile.DoesNotExist:
        profile = CompanyProfile.objects.create(company=company)
    
    # Basic stats
    total_jobs = EmployerJob.objects.filter(company=company).count()
    active_jobs = EmployerJob.objects.filter(company=company, status='active').count()
    total_applications = CandidateApplication.objects.filter(job__company=company).count()
    
    # Application stats by status
    application_stats = CandidateApplication.objects.filter(
        job__company=company
    ).values('status').annotate(count=Count('id'))
    
    # Most viewed jobs
    most_viewed = EmployerJob.objects.filter(
        company=company
    ).order_by('-view_count')[:10]
    
    # Jobs with most applications
    most_applied = EmployerJob.objects.filter(
        company=company
    ).annotate(app_count=Count('applications')).order_by('-app_count')[:10]
    
    # Recent activity
    recent_applications = CandidateApplication.objects.filter(
        job__company=company
    ).order_by('-applied_at')[:10]
    
    context = {
        'company': company,
        'profile': profile,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'application_stats': application_stats,
        'most_viewed': most_viewed,
        'most_applied': most_applied,
        'recent_applications': recent_applications,
    }
    return render(request, 'hr_bolim/employer/statistics.html', context)

@login_required
def employer_messages(request):
    if request.user.role != 'employer':
        return redirect('home')
    
    try:
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        return redirect('employer_register')
    
    # Get all conversations
    sent_to = Message.objects.filter(sender=request.user).values_list('recipient', flat=True)
    received_from = Message.objects.filter(recipient=request.user).values_list('sender', flat=True)
    
    user_ids = set(list(sent_to) + list(received_from))
    
    conversations = []
    for user_id in user_ids:
        other_user = User.objects.get(id=user_id)
        last_msg = Message.objects.filter(
            Q(sender=request.user, recipient=other_user) | 
            Q(sender=other_user, recipient=request.user)
        ).order_by('-timestamp').first()
        
        conversations.append({
            'user': other_user,
            'last_message': last_msg
        })
    
    # Sort by last message timestamp
    conversations.sort(key=lambda x: x['last_message'].timestamp, reverse=True)
    
    return render(request, 'hr_bolim/employer/messages.html', {'conversations': conversations})

@login_required
def employer_chat_detail(request, user_id):
    if request.user.role != 'employer':
        return redirect('home')
    
    try:
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        return redirect('employer_register')
    
    other_user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, recipient=other_user, content=content)
            return redirect('employer_chat_detail', user_id=user_id)
    
    messages_qs = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) | 
        Q(sender=other_user, recipient=request.user)
    ).order_by('timestamp')
    
    # Mark received as read
    Message.objects.filter(sender=other_user, recipient=request.user, is_read=False).update(is_read=True)
    
    return render(request, 'hr_bolim/employer/chat.html', {
        'company': company,
        'other_user': other_user,
        'messages': messages_qs
    })

@login_required
def job_detail(request, job_id):
    """Show detailed information about a specific job"""
    try:
        job = EmployerJob.objects.get(id=job_id)
    except EmployerJob.DoesNotExist:
        messages.error(request, "Vakansiya topilmadi.")
        return redirect('jobs_list')
    
    # Increment view count
    job.view_count += 1
    job.save(update_fields=['view_count'])
    
    # Check if user has already applied
    has_applied = False
    if request.user.is_authenticated and request.user.role == 'candidate':
        has_applied = CandidateApplication.objects.filter(
            job=job, 
            candidate=request.user
        ).exists()
    
    context = {
        'job': job,
        'has_applied': has_applied,
    }
    return render(request, 'hr_bolim/job_detail.html', context)

@employer_required
def employer_interviews(request):
    """Show all interviews for employer's applications"""
    try:
        company = Company.objects.get(user=request.user)
    except Company.DoesNotExist:
        return redirect('employer_register')
    
    # Get all interviews for this company's job applications
    interviews = Interview.objects.filter(
        application__job__company=company
    ).order_by('-scheduled_date')
    
    context = {
        'interviews': interviews,
        'company': company,
    }
    return render(request, 'hr_bolim/employer/interviews.html', context)


# ADMIN VIEWS


@login_required
def admin_dashboard(request):
    """Admin dashboard"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        return redirect('home')
    
    # Statistics
    total_users = User.objects.count()
    total_candidates = User.objects.filter(role='candidate').count()
    total_employers = User.objects.filter(role='employer').count()
    total_jobs = EmployerJob.objects.count()
    total_applications = CandidateApplication.objects.count()
    
    context = {
        'total_users': total_users,
        'total_candidates': total_candidates,
        'total_employers': total_employers,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
    }
    return render(request, 'hr_bolim/admin/dashboard.html', context)

@login_required
def admin_companies(request):
    """Admin companies management"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        return redirect('home')
    
    companies = Company.objects.all().order_by('-created_at')
    
    context = {
        'companies': companies,
    }
    return render(request, 'hr_bolim/admin/companies.html', context)

@login_required
def admin_gdpr_logs(request):
    """Admin GDPR logs view"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        return redirect('home')
    
    logs = ConsentLog.objects.all().order_by('-given_at')
    
    context = {
        'logs': logs,
    }
    return render(request, 'hr_bolim/admin/gdpr_logs.html', context)

@login_required
def admin_data_requests(request):
    """Admin data deletion requests"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        return redirect('home')
    
    requests_list = DataDeletionRequest.objects.all().order_by('-requested_at')
    
    context = {
        'requests': requests_list,
    }
    return render(request, 'hr_bolim/admin/data_requests.html', context)

@login_required
def admin_complaints(request):
    """Admin complaints management"""
    if request.user.role != 'admin' and not request.user.is_superuser:
        return redirect('home')
    
    complaints = Contact.objects.all().order_by('-sent_at')
    
    context = {
        'complaints': complaints,
    }
    return render(request, 'hr_bolim/admin/complaints.html', context)


def custom_logout(request):
    """Custom logout view that accepts both GET and POST requests"""
    if request.method == 'POST' or request.method == 'GET':
        logout(request)
        messages.success(request, "Siz tizimdan muvaffaqiyatli chiqdingiz.")
        return redirect('home')
    return redirect('home')
