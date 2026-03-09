from django.views.generic.base import RedirectView, View, TemplateView
from InfrastructureApp.constants import HTTPMethods

class InfrastructureTemplateView(TemplateView):
    # Allowed HTTP methods.
    http_method_names = [HTTPMethods.get, ]

class InfrastructureRedirectView(RedirectView):
    # Allowed HTTP methods.
    http_method_names = [HTTPMethods.get, ]


class InfrastructureView(View):
    # Allowed HTTP methods.
    http_method_names = [HTTPMethods.get, HTTPMethods.post, ]