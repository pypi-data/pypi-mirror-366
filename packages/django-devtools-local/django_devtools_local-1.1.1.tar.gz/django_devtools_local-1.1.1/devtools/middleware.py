from django.conf import settings
from django.http import Http404
from .utils import is_debug_mode, is_authorized_ip


class DevToolsMiddleware:
    """
    Middleware to restrict access to DevTools
    Optional - can be enabled in settings.MIDDLEWARE
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Check for DevTools URLs
        if request.path.startswith('/devtools/'):
            # DEBUG mode required
            if not is_debug_mode():
                raise Http404("DevTools not available in production")
            
            # Authorized IP required
            if not is_authorized_ip(request):
                raise Http404("IP not authorized")
        
        response = self.get_response(request)
        return response


class DevToolsSecurityMiddleware:
    """
    Enhanced security middleware for DevTools
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.path.startswith('/devtools/'):
            # Strict security checks
            if not is_debug_mode():
                raise Http404("DevTools disabled")
            
            # Authenticated user and superuser required
            if not request.user.is_authenticated or not request.user.is_superuser:
                raise Http404("Access denied")
            
            # IP whitelisting
            if not is_authorized_ip(request):
                raise Http404("Unauthorized IP")
            
            # Security headers
            response = self.get_response(request)
            response['X-Frame-Options'] = 'DENY'
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-XSS-Protection'] = '1; mode=block'
            return response
        
        return self.get_response(request) 