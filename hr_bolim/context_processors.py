from .models import CompanyProfile

def company_profile_context(request):
    """
    Context processor to make company profile data available to all templates
    for employer users to display company logo in sidebar
    """
    company_profile = None
    
    if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role == 'employer':
        try:
            # Try to get the company and profile
            company = request.user.company
            company_profile = CompanyProfile.objects.get(company=company)
        except (AttributeError, Company.DoesNotExist, CompanyProfile.DoesNotExist):
            # If company or profile doesn't exist, keep company_profile as None
            pass
    
    return {
        'company_profile': company_profile
    }
