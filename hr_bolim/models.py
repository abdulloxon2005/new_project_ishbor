from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

#Users modeli

class User(AbstractUser):
    ROLE_CHOICES = (
        ("candidate","Ish izlovchi"),
        ("employer","Ish beruvchi"),
        ("admin","Admin")
    )
    role = models.CharField(max_length=20,choices=ROLE_CHOICES, default='candidate')
    phone = models.CharField(max_length=20,blank=True,null=True)
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(blank=True,null=True)
    consent_policy_version = models.CharField(max_length=10,blank=True,null=True)
    data_retention_until = models.DateTimeField(blank=True,null=True)
    is_delete = models .BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    # Django admin uchun kerakli maydonlar
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    def __str__(self):
        return self.email
#User information modeli
class UserInformation(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    date_of_birth = models.DateField(blank=True,null=True)
    address = models.CharField(max_length=200,blank=True,null=True)
    work_experience = models.TextField()
    education = models.TextField()
    skills = models.TextField()
    additional_info = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} Info"
    
class Department(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Job(models.Model):
    STATUS_CHOICES = (
        ("open","Open"),
        ("closed","Closed")

    )

    EMPLOYMENT_TYPE = (
        ("full-time", "Full time"),
        ("part-time", "Part time"),
        ("remote", "Remote"),
        ("internship", "Internship"),
    )
    title = models.CharField(max_length=200)
    department = models.ForeignKey(Department,on_delete=models.CASCADE)
    employment_type = models.CharField(max_length=50,choices=EMPLOYMENT_TYPE)
    loaction = models.CharField(max_length=150)
    description = models.TextField()
    requirements = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={"role": "employer"})
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="open")
    
    # Filter fields
    salary_min = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    experience_required = models.CharField(max_length=20, choices=(
        ("0", "Tajriba talab qilinmaydi"),
        ("1-3", "1-3 yil"),
        ("3-5", "3-5 yil"),
        ("5+", "5 yildan ortiq")
    ), default="0")

    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deadline = models.DateTimeField(blank=True,null=True)

    def __str__(self):
        return self.title
    
class Application(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("reviewed", "Reviewed"),
        ("interview", "Interview"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    )
    user = models.ForeignKey(User,on_delete=models.CASCADE,limit_choices_to={"role":"candidate"})
    job = models.ForeignKey(Job,on_delete=models.CASCADE)
    resume_file = models.FileField(upload_to="resumes/")
    cover_letter = models.TextField(blank=True,null=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default="pending")

    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(blank=True,null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ("user","job")

    def __str__(self):
        return f"{self.user.email} - {self.job.title}"

class Contact(models.Model):
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()

    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(blank=True, null=True)

    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    
class ConsentLog(models.Model):

    CONSENT_TYPES = (
        ("privacy", "Privacy Policy"),
        ("marketing", "Marketing"),
        ("job_application", "Job Application"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    consent_type = models.CharField(max_length=50, choices=CONSENT_TYPES)
    policy_version = models.CharField(max_length=10)

    given_at = models.DateTimeField(default=timezone.now)
    revoked_at = models.DateTimeField(blank=True, null=True)

    ip_address = models.GenericIPAddressField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.consent_type}"


class PrivacyPolicy(models.Model):
    version = models.CharField(max_length=10)
    content = models.TextField()
    effective_date = models.DateField()
    is_active = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Version {self.version}"


class DataDeletionRequest(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("rejected", "Rejected"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    def __str__(self):
        return f"{self.user.email} - {self.status}"


class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.action

# ----------------------------------------------------------------
# Candidate (Job Seeker) Models
# ----------------------------------------------------------------

class CandidateProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='candidate_profile')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    profession = models.CharField(max_length=150, blank=True, null=True, help_text="Ex: Software Engineer")
    location = models.CharField(max_length=150, blank=True, null=True)
    about_me = models.TextField(blank=True, null=True)
    skills = models.TextField(blank=True, null=True, help_text="Comma separated skills")
    
    # Stats
    profile_views = models.PositiveIntegerField(default=0)
    is_processing_restricted = models.BooleanField(default=False, help_text="User restricted data processing")
    
    # New fields
    experience_years = models.PositiveIntegerField(default=0, help_text="Total years of experience")
    resume_file = models.FileField(upload_to='resumes/default/', blank=True, null=True, help_text="Default CV for 1-click apply")

    # Links
    linkedin = models.URLField(blank=True, null=True)
    github = models.URLField(blank=True, null=True)
    portfolio = models.URLField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} Profile"

class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='experiences')
    company = models.CharField(max_length=150)
    position = models.CharField(max_length=150)
    location = models.CharField(max_length=150, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)

    @property
    def duration(self):
        end = self.end_date
        if self.is_current or not end:
            end = timezone.now().date()
            
        if not self.start_date:
            return ""

        # Calculate difference in years and months
        diff = end.year - self.start_date.year
        months = end.month - self.start_date.month
        
        if months < 0:
            diff -= 1
            months += 12
            
        parts = []
        if diff > 0:
            parts.append(f"{diff} yil")
        if months > 0:
            parts.append(f"{months} oy")
            
        if not parts:
            return "1 oydan kam"
            
        return " ".join(parts)

    def __str__(self):
        return f"{self.position} at {self.company}"

class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=150)
    degree = models.CharField(max_length=150)
    field_of_study = models.CharField(max_length=150, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.degree} at {self.institution}"

class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'job')

    def __str__(self):
        return f"{self.user.email} saved {self.job.title}"

class Resume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resumes')
    title = models.CharField(max_length=150, help_text="CV nomi (masalan: Python Developer CV)")
    file = models.FileField(upload_to='resumes/user_uploads/')
    is_public = models.BooleanField(default=True, help_text="Boshqa ish beruvchilar ko'ra oladimi?")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.title}"

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to='messages/', blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From {self.sender} to {self.recipient}"

# ----------------------------------------------------------------
# Employer Models
# ----------------------------------------------------------------

class Company(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    company_name = models.CharField(max_length=200)
    stir = models.CharField(max_length=50, unique=True, help_text="STIR / Ro'yxat raqami")
    email = models.EmailField()
    responsible_person = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    
    # GDPR consent
    data_processing_consent = models.BooleanField(default=False)
    consent_date = models.DateTimeField(blank=True, null=True)
    
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.company_name

class CompanyProfile(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='profile')
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    description = models.TextField()
    address = models.TextField()
    website = models.URLField(blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    telegram = models.URLField(blank=True, null=True)
    
    # Statistics
    total_jobs_posted = models.PositiveIntegerField(default=0)
    total_applications = models.PositiveIntegerField(default=0)
    profile_views = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company.company_name} Profile"

class EmployerJob(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("active", "Active"),
        ("closed", "Closed"),
        ("paused", "Paused"),
    )
    
    EMPLOYMENT_TYPE = (
        ("full-time", "To'liq stavka"),
        ("part-time", "Qisman stavka"),
        ("remote", "Masofaviy"),
        ("hybrid", "Gibrid"),
        ("internship", "Stajirovka"),
    )
    
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPE)
    salary_min = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=0, blank=True, null=True)
    requirements = models.TextField()
    responsibilities = models.TextField()
    benefits = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=200)
    deadline = models.DateTimeField()
    positions_count = models.PositiveIntegerField(default=1)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    
    # Statistics
    view_count = models.PositiveIntegerField(default=0)
    application_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} at {self.company.company_name}"

class CandidateApplication(models.Model):
    STATUS_CHOICES = (
        ("new", "Yangi"),
        ("reviewed", "Ko'rilgan"),
        ("interview", "Intervyu"),
        ("rejected", "Rad etilgan"),
        ("accepted", "Qabul qilingan"),
    )
    
    job = models.ForeignKey(EmployerJob, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={"role": "candidate"})
    resume_file = models.FileField(upload_to="applications/resumes/")
    cover_letter = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    internal_notes = models.TextField(blank=True, null=True)
    
    # GDPR
    consent_given = models.BooleanField(default=False)
    consent_date = models.DateTimeField(blank=True, null=True)
    
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'candidate')

    def __str__(self):
        return f"{self.candidate.email} - {self.job.title}"

class Interview(models.Model):
    STATUS_CHOICES = (
        ("scheduled", "Rejalashtirilgan"),
        ("completed", "Yakunlangan"),
        ("cancelled", "Bekor qilingan"),
    )
    
    application = models.OneToOneField(CandidateApplication, on_delete=models.CASCADE, related_name='interview')
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    interview_type = models.CharField(max_length=50, choices=(
        ("phone", "Telefon"),
        ("video", "Video"),
        ("offline", "Ofisda"),
    ), default="video")
    
    location_link = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Interview for {self.application.job.title}"

