from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Department, Job, Application, Contact, ConsentLog, PrivacyPolicy, DataDeletionRequest, AuditLog,
    # Candidate models
    CandidateProfile, Experience, Education, Resume, SavedJob,
    # Employer models  
    Company, CompanyProfile, EmployerJob, CandidateApplication, Interview,
    # Message model
    Message,
)
from django.utils.html import format_html
import json
from django.http import HttpResponse

# User Admin
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'phone', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    actions = ['make_employer', 'make_candidate', 'block_users', 'unblock_users', 'export_users_json']

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('GDPR', {'fields': ('consent_given', 'consent_date', 'data_retention_until')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    @admin.action(description="Tanlanganlarni Ish beruvchi (Employer) qilish")
    def make_employer(self, request, queryset):
        queryset.update(role='employer')
        self.message_user(request, "Tanlangan foydalanuvchilar Ish beruvchi roliga o'tkazildi.")

    @admin.action(description="Tanlanganlarni Ish izlovchi (Candidate) qilish")
    def make_candidate(self, request, queryset):
        queryset.update(role='candidate')
        self.message_user(request, "Tanlangan foydalanuvchilar Ish izlovchi roliga o'tkazildi.")

    @admin.action(description="Foydalanuvchilarni bloklash")
    def block_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, "Foydalanuvchilar bloklandi.")

    @admin.action(description="Foydalanuvchilarni blokdan chiqarish")
    def unblock_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, "Foydalanuvchilar faollashtirildi.")
    
    @admin.action(description="JSON formatida eksport qilish")
    def export_users_json(self, request, queryset):
        data = list(queryset.values('id', 'email', 'first_name', 'last_name', 'role', 'date_joined'))
        response = HttpResponse(json.dumps(data, default=str), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="users.json"'
        return response

# Department Admin
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

# Job Admin
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'posted_by', 'status', 'employment_type', 'posted_at')
    list_filter = ('status', 'department', 'employment_type', 'posted_by')
    search_fields = ('title', 'description')
    actions = ['close_jobs', 'open_jobs']

    @admin.action(description="Ishlarni yopish (Close)")
    def close_jobs(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, "Tanlangan ishlar yopildi.")

    @admin.action(description="Ishlarni ochish (Open)")
    def open_jobs(self, request, queryset):
        queryset.update(status='open')
        self.message_user(request, "Tanlangan ishlar ochildi.")

# GDPR Admin
@admin.register(ConsentLog)
class ConsentLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'consent_type', 'policy_version', 'given_at', 'ip_address')
    list_filter = ('consent_type', 'policy_version', 'given_at')
    search_fields = ('user__email', 'ip_address')
    readonly_fields = ('user', 'consent_type', 'policy_version', 'given_at', 'ip_address', 'notes')

@admin.register(PrivacyPolicy)
class PrivacyPolicyAdmin(admin.ModelAdmin):
    list_display = ('version', 'effective_date', 'is_active', 'updated_at')
    list_filter = ('is_active',)

@admin.register(DataDeletionRequest)
class DataDeletionRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'requested_at', 'status', 'processed_at')
    list_filter = ('status', 'requested_at')
    actions = ['mark_completed', 'mark_rejected']

    @admin.action(description="So'rovni bajarildi deb belgilash")
    def mark_completed(self, request, queryset):
        queryset.update(status='completed', processed_at=timezone.now())
        self.message_user(request, "So'rovlar bajarildi deb belgilandi.")

    @admin.action(description="So'rovni rad etilgan deb belgilash")
    def mark_rejected(self, request, queryset):
        queryset.update(status='rejected', processed_at=timezone.now())
        self.message_user(request, "So'rovlar rad etildi deb belgilandi.")

# Audit Admin
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'ip_address', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('user__email', 'action', 'ip_address')
    readonly_fields = ('user', 'action', 'ip_address', 'created_at')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# Candidate Models
@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profession', 'location', 'experience_years', 'profile_views', 'created_at')
    list_filter = ('experience_years', 'created_at')
    search_fields = ('user__email', 'profession', 'location')

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'position', 'start_date', 'end_date', 'is_current')
    list_filter = ('is_current', 'start_date')
    search_fields = ('user__email', 'company', 'position')

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'degree', 'field_of_study', 'start_date', 'end_date')
    list_filter = ('start_date', 'degree')
    search_fields = ('user__email', 'institution', 'degree')

@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_public', 'created_at')
    list_filter = ('is_public', 'created_at')
    search_fields = ('user__email', 'title')

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ('user', 'job', 'saved_at')
    list_filter = ('saved_at',)
    search_fields = ('user__email', 'job__title')

# Employer Models
@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'stir', 'responsible_person', 'email', 'is_verified', 'created_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('company_name', 'stir', 'email')
    actions = ['verify_companies', 'unverify_companies']

    @admin.action(description="Kompaniyalarni tasdiqlash")
    def verify_companies(self, request, queryset):
        queryset.update(is_verified=True)
        self.message_user(request, "Kompaniyalar tasdiqlandi.")

    @admin.action(description="Kompaniyalarni tasdiqlashdan olish")
    def unverify_companies(self, request, queryset):
        queryset.update(is_verified=False)
        self.message_user(request, "Kompaniyalar tasdiqlashdan olindi.")

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company', 'total_jobs_posted', 'total_applications', 'profile_views', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('company__company_name',)

@admin.register(EmployerJob)
class EmployerJobAdmin(admin.ModelAdmin):
    list_display = ('title', 'company', 'employment_type', 'salary_min', 'salary_max', 'status', 'view_count', 'application_count', 'created_at')
    list_filter = ('status', 'employment_type', 'created_at')
    search_fields = ('title', 'company__company_name')
    actions = ['activate_jobs', 'pause_jobs', 'close_jobs']

    @admin.action(description="Ishlarni faollashtirish")
    def activate_jobs(self, request, queryset):
        queryset.update(status='active')
        self.message_user(request, "Ishlar faollashtirildi.")

    @admin.action(description="Ishlarni pauza qilish")
    def pause_jobs(self, request, queryset):
        queryset.update(status='paused')
        self.message_user(request, "Ishlar pauza qilindi.")

    @admin.action(description="Ishlarni yopish")
    def close_jobs(self, request, queryset):
        queryset.update(status='closed')
        self.message_user(request, "Ishlar yopildi.")

@admin.register(CandidateApplication)
class CandidateApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'candidate', 'status', 'applied_at', 'updated_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('job__title', 'candidate__email')
    actions = ['accept_applications', 'reject_applications']

    @admin.action(description="Arizalarni qabul qilish")
    def accept_applications(self, request, queryset):
        queryset.update(status='accepted')
        self.message_user(request, "Arizalar qabul qilindi.")

    @admin.action(description="Arizalarni rad etish")
    def reject_applications(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request, "Arizalar rad etildi.")

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'scheduled_date', 'duration_minutes', 'interview_type', 'status', 'created_at')
    list_filter = ('status', 'interview_type', 'scheduled_date')
    search_fields = ('application__job__title', 'application__candidate__email')

# Message Model
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'recipient', 'content_preview', 'is_read', 'timestamp')
    list_filter = ('is_read', 'timestamp')
    search_fields = ('sender__email', 'recipient__email', 'content')
    readonly_fields = ('timestamp',)

    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Xabar'

# Contact (Shikoyatlar)
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'sent_at')
    list_filter = ('sent_at',)
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('sent_at',)

