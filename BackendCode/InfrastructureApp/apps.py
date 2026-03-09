from django.apps import AppConfig
from django.contrib.admin.apps import AdminConfig


class InfrastructureAppConfig(AppConfig):
    name = 'InfrastructureApp'

class ToolkitAdminConfig(AdminConfig):
    default_site = 'InfrastructureApp.admin.ToolkitAdminSite'