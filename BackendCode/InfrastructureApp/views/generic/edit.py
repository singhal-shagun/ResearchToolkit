from django.views.generic.edit import FormView
from InfrastructureApp.constants import HTTPMethods
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

class InfrastructureFormView (FormView):

    # Allowed HTTP methods.
    http_method_names = [HTTPMethods.get, HTTPMethods.post, ]

    # Attributes not in django, but introduced in our software. These are expected to be overridden in the child FormView class.
    model = None
    add_url = None

    def get_form_kwargs(self):
        """
        The following code makes the request object available to the form.
        Use 
        """
        kwargs = super().get_form_kwargs()
        if not isinstance(self, InfrastructureFormSetView):
            kwargs["request"] = self.request    # makes the request object available to InfrastructureFormView object but not a InfrastructureForSetView object.
        return kwargs
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, "title"):
            context["title"] = self.title
        if self.model is not None:
            context["opts"] = {}
            context["opts"]["verbose_name"] = self.model._meta.verbose_name
            context["opts"]["verbose_name_plural"] = self.model._meta.verbose_name_plural
            context["opts"]["label"] = self.model._meta.label
            context["opts"]["label_lower"] = self.model._meta.label_lower

        if self.add_url is not None:
            context["add_url"] = self.add_url

        # When model is specified for the view, add model-specific permissions available to the user.
        # Examples when model may not be specified: ToolkitAdminApp.views.PasswordResetView
        if self.model is not None:
            contentType = ContentType.objects.get_for_model(self.model)
            permissionsQueryset = Permission.objects.filter(content_type = contentType)
            addPermissionObject = permissionsQueryset.get(codename__startswith = 'add_')
            changePermissionObject = permissionsQueryset.get(codename__startswith = 'change_')
            deletePermissionObject = permissionsQueryset.get(codename__startswith = 'delete_')
            viewPermissionObject = permissionsQueryset.get(codename__startswith = 'view_')
            context["userPermissions"] = {}
            if self.request.user.has_perm(".".join([contentType.app_label, addPermissionObject.codename])):
                context["userPermissions"]["addPermission"] = True
            else:
                context["userPermissions"]["addPermission"] = False
            if self.request.user.has_perm(".".join([contentType.app_label, changePermissionObject.codename])):
                context["userPermissions"]["changePermission"] = True
            else:
                context["userPermissions"]["changePermission"] = False
            if self.request.user.has_perm(".".join([contentType.app_label, deletePermissionObject.codename])):
                context["userPermissions"]["deletePermission"] = True
            else:
                context["userPermissions"]["deletePermission"] = False
            if self.request.user.has_perm(".".join([contentType.app_label, viewPermissionObject.codename])):
                context["userPermissions"]["viewPermission"] = True
            else:
                context["userPermissions"]["viewPermission"] = False
        """
        [DEBATE:] 
        When model isn't specified, should I set the default value for addPermission, changePermission, deletePermission, and viewPermission to `False`?
        Because otherwise, the "userPermissions" dictionary won't be available in the context.
        """
                

        return context
    

class InfrastructureFormSetView (InfrastructureFormView):
    # Attributes not in django, but introduced in our software. These are expected to be overridden in the child FormView class.
    queryset = None         # This is expected to be overridden in the child class so instantiate the formset when this View is used in edit cases.
    formset_class = None    # This is expected to be overridden in the child class using return value from formset_factory() or modelformset_factory() method.


    def get_formset_class(self):
        """Return the formset class to use."""
        return self.formset_class
    

    def get_formset_kwargs(self):
        """
        Return the keyword arguments for instantiating the formset.
        Necessary arguments (such as queryset) should be added to this kwargs dictionary by child classes.
        """
        kwargs = self.get_form_kwargs()
        kwargs["form_kwargs"]= {"request": self.request}    # Formset's form_kwargs dictionary makes objects available to the contained forms' kwargs dictionary, allowing the passing of view's request object to the forms contained in this formset.
        return kwargs

        
    def get_formset(self, formset_class=None):
        """Return an instance of the formset to be used in this view."""
        if formset_class is None:
            formset_class = self.get_formset_class()
        formset_kwargs = self.get_formset_kwargs()
        return formset_class(
            **formset_kwargs,
            # **self.get_formset_kwargs(),
            )
    
    def formset_valid(self, formset):
        return super().form_valid(form=None)
    
    def formset_invalid(self, formset):
        return super().form_invalid(form=None)


    def post(self, request, *args, **kwargs):
        """
        [OVERRIDEN METHOD}
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        formset = self.get_formset()
        if formset.is_valid():
            return self.formset_valid(formset)
        else:
            return self.formset_invalid(formset)
        

    def get_context_data(self, **kwargs):
        """
        [OVERRIDEN METHOD}
        Insert the formset into the context dict.
        """
        if "formset" not in kwargs:
            kwargs["formset"] = self.get_formset()
        return super().get_context_data(**kwargs)