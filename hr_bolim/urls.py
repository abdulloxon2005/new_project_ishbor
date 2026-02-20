from django.urls import path
from .views import (
    home_view, submit_complaint, jobs_list_view, register_view, CustomLoginView, dashboard_view, candidate_dashboard, candidate_profile, candidate_cv, 
    add_experience, add_education, delete_item, candidate_gdpr, add_resume, apply_job, my_applications, inbox, chat_detail, candidate_interviews,
    edit_resume, edit_experience, edit_education, apply_employer_job, job_detail,
    # Employer views
    employer_dashboard, employer_register, employer_register_public, employer_profile, employer_jobs, create_job, edit_job, delete_job,
    employer_applications, application_detail, schedule_interview, employer_statistics, employer_messages, employer_chat_detail, employer_interviews,
    # Admin views
    admin_dashboard, admin_companies, admin_gdpr_logs, admin_data_requests, admin_complaints,
    custom_logout,
)

urlpatterns = [
    path('', home_view, name='home'),
    path('jobs/', jobs_list_view, name='jobs_list'),
    path('complaint/', submit_complaint, name='submit_complaint'),
    
    # Auth Pages
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', register_view, name='register'),
    path('logout/', custom_logout, name='logout'),

    # Unified Dashboard
    path('dashboard/', dashboard_view, name='dashboard'),

    # Candidate Dashboard
    path('candidate/dashboard/', candidate_dashboard, name='candidate_dashboard'),
    path('candidate/profile/', candidate_profile, name='candidate_profile'),
    
    # CV System
    path('candidate/cv/', candidate_cv, name='candidate_cv'),
    path('candidate/cv/add/experience/', add_experience, name='add_experience'),
    path('candidate/cv/add/education/', add_education, name='add_education'),
    path('candidate/cv/add/resume/', add_resume, name='add_resume'),
    path('candidate/cv/edit/resume/<int:id>/', edit_resume, name='edit_resume'),
    path('candidate/cv/edit/experience/<int:id>/', edit_experience, name='edit_experience'),
    path('candidate/cv/edit/education/<int:id>/', edit_education, name='edit_education'),
    path('candidate/cv/delete/<str:model_name>/<int:id>/', delete_item, name='delete_item'),
    
    # Job Application
    path('candidate/apply/<int:job_id>/', apply_job, name='apply_job'),
    path('candidate/apply_employer/<int:job_id>/', apply_employer_job, name='apply_employer_job'),
    path('candidate/my-applications/', my_applications, name='my_applications'),
    path('candidate/interviews/', candidate_interviews, name='candidate_interviews'),

    # Messaging
    path('candidate/inbox/', inbox, name='inbox'),
    path('candidate/chat/<int:user_id>/', chat_detail, name='chat_detail'),

    # GDPR
    path('candidate/gdpr/', candidate_gdpr, name='candidate_gdpr'),

    # Employer Dashboard
    path('employer/dashboard/', employer_dashboard, name='employer_dashboard'),
    path('employer/register/', employer_register_public, name='employer_register'),
    path('employer/profile/', employer_profile, name='employer_profile'),
    
    # Employer Jobs
    path('employer/jobs/', employer_jobs, name='employer_jobs'),
    path('employer/jobs/create/', create_job, name='create_job'),
    path('employer/jobs/edit/<int:job_id>/', edit_job, name='edit_job'),
    path('employer/jobs/delete/<int:job_id>/', delete_job, name='delete_job'),
    
    # Employer Applications
    path('employer/applications/', employer_applications, name='employer_applications'),
    path('employer/applications/<int:application_id>/', application_detail, name='application_detail'),
    path('employer/applications/<int:application_id>/interview/', schedule_interview, name='schedule_interview'),
    
    # Employer Statistics
    path('employer/statistics/', employer_statistics, name='employer_statistics'),
    
    # Employer Messaging
    path('employer/messages/', employer_messages, name='employer_messages'),
    path('employer/chat/<int:user_id>/', employer_chat_detail, name='employer_chat_detail'),
    
    # Employer Interviews
    path('employer/interviews/', employer_interviews, name='employer_interviews'),
    
    # Job Detail
    path('job/<int:job_id>/', job_detail, name='job_detail'),
    
    # Admin Views (use different prefix to avoid conflict with Django admin site)
    path('admin-panel/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin-panel/companies/', admin_companies, name='admin_companies'),
    path('admin-panel/gdpr-logs/', admin_gdpr_logs, name='admin_gdpr_logs'),
    path('admin-panel/data-requests/', admin_data_requests, name='admin_data_requests'),
    path('admin-panel/complaints/', admin_complaints, name='admin_complaints'),
]
