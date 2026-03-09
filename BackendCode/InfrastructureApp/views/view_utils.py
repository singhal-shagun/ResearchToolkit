from django.shortcuts import render
import logging
from django.http import HttpResponseNotAllowed


logger = logging.getLogger("django.request")

# Create your views here.
def http_method_not_allowed(request, allowed_http_methods, ayncBoolean=False):
    """
    This code is adapted from django.views.View class' http_method_not_allowed() method.
    It will be called in function-based views for invalid HTTP request.method values.
    A sample call to this function would look like this:
        http_method_not_allowed(request, allowed_http_methods)
        where:
            request: HttpRequest instance
            allowed_http_methods: list of allowed strings of allowed HTTP methods
    When calling from an asynchronous function-based view, you would call this function as follows:
        http_method_not_allowed(request, allowed_http_methods, ayncBoolean=True)
    """
    logger.warning(
        "Method Not Allowed (%s): %s",
        request.method,
        request.path,
        extra={"status_code": 405, "request": request},
    )
    response = HttpResponseNotAllowed(allowed_http_methods)
    if ayncBoolean:
        async def func():
            return response
        return func()
    else:
        return response