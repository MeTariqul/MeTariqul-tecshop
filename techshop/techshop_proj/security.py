"""
Security middleware for HTTPS enforcement and security headers
"""
from django.http import HttpResponseRedirect
from django.conf import settings
import re


class HTTPSEnforcerMiddleware:
    """
    Middleware to enforce HTTPS in production
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Only enforce HTTPS in production
        if not settings.DEBUG:
            # Check if request is already HTTPS
            if not request.is_secure():
                # Get the full URL with https
                host = request.get_host()
                # Handle port
                if ':' in host:
                    host = host.split(':')[0]
                secure_url = f"https://{host}{request.get_full_path()}"
                return HttpResponseRedirect(secure_url)
        
        return self.get_response(request)


class SecurityHeadersMiddleware:
    """
    Add security headers to all responses
    """
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy - more permissive in DEBUG mode
        if settings.DEBUG:
            response['Content-Security-Policy'] = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' 'unsafe-eval' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com data:; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none';"
            )
        else:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' 'unsafe-eval' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
                "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com data:; "
                "img-src 'self' data: https:; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none';"
            )
        
        # HSTS header (only for HTTPS)
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response
