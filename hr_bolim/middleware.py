from django.shortcuts import redirect


class RoleRestrictionMiddleware:
    """Prevent users from accessing other-role protected URL prefixes.

    - URLs starting with /employer/ require user.role == 'employer'
    - URLs starting with /candidate/ require user.role == 'candidate'

    Redirects unauthorized users to 'home'.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path_info or ''

        # Only enforce on our app prefixes
        try:
            user_role = getattr(request.user, 'role', None)
        except Exception:
            user_role = None

        if path.startswith('/employer/'):
            if not request.user.is_authenticated or user_role != 'employer':
                return redirect('home')

        if path.startswith('/candidate/'):
            if not request.user.is_authenticated or user_role != 'candidate':
                return redirect('home')

        return self.get_response(request)
