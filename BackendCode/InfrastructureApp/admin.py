from django.contrib import admin
from django.db.models import Q
from django.core.exceptions import FieldDoesNotExist
from ToolkitAdminApp.models import UserEquivalences
from InfrastructureApp.constants import HTTPMethods
from InfrastructureApp.views import http_method_not_allowed
from InfrastructureApp.db.models import InfrastructureModel
 #from .static.InfrastructureApp.CustomWidgets import WideAutocompleteWidget
#from FinanceDteApp.models import *

# Overriding the defaul AdminSite class to change the website header and title.
class ToolkitAdminSite(admin.AdminSite):
    site_header="Research Toolkit administration"
    site_title="Research Toolkit"

    def index(self, request, extra_context=None):
        """
        This overrides the default index() to ensure that requests bearing any method other than GET and POST aren't serviced.
        """
        # Allowed HTTP methods.
        http_method_names = [HTTPMethods.get, ]

        if request.method.lower() in http_method_names:
            return super().index(request, extra_context)
        else:
            return http_method_not_allowed(request, http_method_names)


# Infrastructure Admin class for models.
class InfrastructureModelAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        infrastructureFieldsToBeAddedToListDisplay = []
        for fieldInInfrastructureModel in InfrastructureModel._meta.get_fields(include_parents=False):
            try:
                modelField = model._meta.get_field(fieldInInfrastructureModel.name)
                infrastructureFieldsToBeAddedToListDisplay.append(modelField.name)
            except FieldDoesNotExist:
                pass
        self.list_display += tuple(infrastructureFieldsToBeAddedToListDisplay)


    # This overrides the default get_queryset() method.
    def get_queryset(self, request):
        qs = super().get_queryset(request)

        # If the user has only view permissions (not add/change/delete permissions), then allow access to the entire queryset.
        # Else (i.e., when the user has write permissions (add/change/delete)), show only partial queryset.
        if request.user.is_superuser or (self.has_view_permission(request) and (not self.has_add_permission(request)) and (not self.has_change_permission(request)) and (not self.has_delete_permission(request))):
            return qs
        else:
            equivalentUsers1 = list(UserEquivalences.objects.filter(referencedOriginalUser_id = request.user.id).values_list("referencedEquivalentUser_id", flat=True))
            equivalentUsers2 = list(UserEquivalences.objects.filter(referencedEquivalentUser_id = request.user.id).values_list("referencedOriginalUser_id", flat=True))
            equivalentUsers = set(equivalentUsers1 + equivalentUsers2)
            return qs.filter(Q(createdBy_id = request.user.id) | Q(modifiedBy_id = request.user.id) | Q(createdBy_id__in = equivalentUsers) | Q(modifiedBy_id__in = equivalentUsers))

        #### -- OLD CODE - NO LONGER USED -- KEPT FOR HOW TO MERGE RESULTS FROM TWO QUERYSETS -- ####
        # TASK-1: Return only those object instances which:
        #   - were created by the current user or an equivalent user, or,
        #   - were modified by the current user or an equivalent user.
        #if (request.user.is_superuser):
        #    return qs
        #else:
        #    equivalentUsers1 = list(UserEquivalences.objects.filter(referencedOriginalUser_id = request.user.id).values_list("referencedEquivalentUser_id", flat=True))
        #    equivalentUsers2 = list(UserEquivalences.objects.filter(referencedEquivalentUser_id = request.user.id).values_list("referencedOriginalUser_id", flat=True))
        #    equivalentUsers = set(equivalentUsers1 + equivalentUsers2)
        #    return qs.filter(Q(createdBy_id = request.user.id) | Q(modifiedBy_id = request.user.id) | Q(createdBy_id__in = equivalentUsers) | Q(modifiedBy_id__in = equivalentUsers))


    # This overrides the default save_model() method.
    def save_model(self, request, obj, form, change):
        #TASK-1: This code sets the createdBy and modifiedBy fields of the model object.
        if (not change):        # Case when a new model object is being added.
            obj.createdBy = request.user
        obj.modifiedBy = request.user
        super().save_model(request, obj, form, change)


    @admin.options.csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        """
        This overrides the default changeform_view() to ensure that requests bearing any method other than GET and POST aren't serviced.
        """
        # Allowed HTTP methods.
        http_method_names = [HTTPMethods.get, HTTPMethods.post]

        if request.method.lower() in http_method_names:
            return super().changeform_view(request, object_id, form_url, extra_context)
        else:
            return http_method_not_allowed(request, http_method_names)


    def _changeform_view(self, request, object_id, form_url, extra_context):
        """
        This overrides the default _changeform_view() to ensure that requests bearing any method other than GET and POST aren't serviced.
        """
        # Allowed HTTP methods.
        http_method_names = [HTTPMethods.get, HTTPMethods.post]

        if request.method.lower() in http_method_names:
            return super()._changeform_view(request, object_id, form_url, extra_context)
        else:
            return http_method_not_allowed(request, http_method_names)
        

    def add_view(self, request, form_url="", extra_context=None):
        """
        This overrides the default add_view() to ensure that requests bearing any method other than GET and POST aren't serviced.
        """
        # Allowed HTTP methods.
        http_method_names = [HTTPMethods.get, HTTPMethods.post]

        if request.method.lower() in http_method_names:
            return super().add_view(request, form_url, extra_context)
        else:
            return http_method_not_allowed(request, http_method_names)
        

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """
        This overrides the default change_view() to ensure that requests bearing any method other than GET and POST aren't serviced.
        """
        # Allowed HTTP methods.
        http_method_names = [HTTPMethods.get, HTTPMethods.post]

        if request.method.lower() in http_method_names:
            return super().change_view(request, object_id, form_url, extra_context)
        else:
            return http_method_not_allowed(request, http_method_names)
        

    @admin.options.csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        """
        This overrides the default changelist_view() to ensure that requests bearing any method other than GET and POST aren't serviced.
        """
        # Allowed HTTP methods.
        http_method_names = [HTTPMethods.get, HTTPMethods.post]

        if request.method.lower() in http_method_names:
            return super().changelist_view(request, extra_context)
        else:
            return http_method_not_allowed(request, http_method_names)
        

    @admin.options.csrf_protect_m
    def delete_view(self, request, object_id, extra_context=None):
        """
        This overrides the default delete_view() to ensure that requests bearing any method other than GET and POST aren't serviced.
        """
        # Allowed HTTP methods.
        http_method_names = [HTTPMethods.get, HTTPMethods.post]

        if request.method.lower() in http_method_names:
            return super().delete_view(request, object_id, extra_context)
        else:
            return http_method_not_allowed(request, http_method_names)
        

    def _delete_view(self, request, object_id, extra_context):
        """
        This overrides the default _delete_view() to ensure that requests bearing any method other than GET and POST aren't serviced.
        """
        # Allowed HTTP methods.
        http_method_names = [HTTPMethods.get, HTTPMethods.post]

        if request.method.lower() in http_method_names:
            return super()._delete_view(request, object_id, extra_context)
        else:
            return http_method_not_allowed(request, http_method_names)
        

    def history_view(self, request, object_id, extra_context=None):
        """
        This overrides the default history_view() to ensure that requests bearing any method other than GET and POST aren't serviced.
        """
        # Allowed HTTP methods.
        http_method_names = [HTTPMethods.get, HTTPMethods.post]

        if request.method.lower() in http_method_names:
            return super().history_view(request, object_id, extra_context)
        else:
            return http_method_not_allowed(request, http_method_names)


    class Meta:
        abstract = True

# Register your models here.
