# middleware.py
from .models import Institution

class InstitutionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add institution to request if user has institution role OR institution session exists
        request.institution = None
        
        # Check 1: User with institution role (Django auth)
        if request.user.is_authenticated and hasattr(request.user, 'role') and request.user.role and request.user.role.name == 'institution':
            try:
                request.institution = Institution.objects.get(user=request.user)
            except Institution.DoesNotExist:
                pass
        
        # Check 2: Institution session login (if no institution found via user auth)
        if not request.institution and request.session.get('institution_id'):
            try:
                request.institution = Institution.objects.get(id=request.session['institution_id'])
            except Institution.DoesNotExist:
                # Clear invalid session
                if 'institution_id' in request.session:
                    del request.session['institution_id']
                pass
        
        response = self.get_response(request)
        return response