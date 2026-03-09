from django.utils.cache import add_never_cache_headers
from django.middleware.security import SecurityMiddleware
from django.conf import settings


class NeverCacheMiddleware:
    """
    This middleware shall set the Cache-Control header to 'no-cache' and 'no-store' for all responses.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        add_never_cache_headers(response)

        return response
    

class ToolkitSecurityMiddleware(SecurityMiddleware):
    """
    We override the SecurityMiddleware class to add the additional security-related headers X-XSS-Protection header to responses.
    (https://docs.djangoproject.com/en/4.2/releases/4.0/#securitymiddleware-no-longer-sets-the-x-xss-protection-header)
        - Most modern browsers don’t honor the X-XSS-Protection HTTP header. 
        - You can use Content-Security-Policy without allowing 'unsafe-inline' scripts instead.
        - If you want to support legacy browsers and set the header, use this line in a custom middleware:
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
    """
    def process_response(self, request, response):
        # 1. Process the response object as per the default implementation in django.middleware.security.SecurityMiddleware
        response = super().process_response(request, response)

        # 2. Add the X-XSS-Protection header to response.
        """
        X-XSS-Protection header to responses.
        (https://docs.djangoproject.com/en/4.2/releases/4.0/#securitymiddleware-no-longer-sets-the-x-xss-protection-header)
        - Most modern browsers don’t honor the X-XSS-Protection HTTP header. 
        - You can use Content-Security-Policy without allowing 'unsafe-inline' scripts instead.
        - If you want to support legacy browsers and set the header, use this line in a custom middleware:
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")
        """
        response.headers.setdefault("X-XSS-Protection", "1; mode=block")

        # 3. Add the Content-Security-Policy (CSP) header to response. 
        """
        https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy
        [SYNTAX:]
        Content-Security-Policy: <policy-directive>; <policy-directive>

        Although Django docs suggest against the use of 'unsafe-inline' in CSP (https://docs.djangoproject.com/en/4.2/releases/4.0/#securitymiddleware-no-longer-sets-the-x-xss-protection-header),
        but without it, the styles weren't being rendered properly on the site.
        I checked that Facebook also allows 'unsafe-inline' in its CSP.
        """
        defaultSources = ""
        if len(settings.CONTENT_SECURITY_POLICY_DEFAULT_SOURCES) > 0:
            defaultSources = " ".join(settings.CONTENT_SECURITY_POLICY_DEFAULT_SOURCES) + " "
        response.headers["Content-Security-Policy"] = "default-src 'self' " + defaultSources + "'unsafe-inline' 'unsafe-eval'; "


        return response