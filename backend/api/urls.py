from django.urls import path
from .views import (
    home,
    service_list,
    project_list,
    team_list,
    contact_submit,
    github_webhook,
    AnalyzeReportView,
)

urlpatterns = [
    path('', home, name='home'),
    path('services/', service_list, name='services'),
    path('projects/', project_list, name='projects'),
    path('team/', team_list, name='team'),
    path('contact/', contact_submit, name='contact_submit'),

    # DevSecOps & Reports
    path('github/webhook/', github_webhook, name='github_webhook'),
    path('api/analyze-report/', AnalyzeReportView.as_view(), name='analyze-report'),
]