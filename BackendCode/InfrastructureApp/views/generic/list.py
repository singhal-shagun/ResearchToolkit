from django.views.generic import ListView
from InfrastructureApp.constants import HTTPMethods

class InfrastructureListView(ListView):
        http_method_names = [HTTPMethods.get, ]
        paginate_by = 100       # overrides the default 'None' value for the number of pages to be displayed by the ListView Paginator.
        fields = []           # Define the list of fields to be displayed in the ListView.

        def get_context_data(self, object_list=None, **kwargs):
                context = super().get_context_data(**kwargs)
                paginator = context["paginator"]
                page_obj = context["page_obj"]

                context["page_range"] = paginator.get_elided_page_range(page_obj.number)
                context["pagination_required"] = paginator.count > self.paginate_by

                if hasattr(self, "model") and (len(self.fields)>0):
                        context["modelFields"] = [self.model._meta.get_field(field) for field in self.fields]

                if hasattr(self, "title"):
                        context["title"] = self.title

                #-- Convert queryset to list --#
                # queryset = object_list if object_list is not None else self.object_list
                # context_object_name = self.get_context_object_name(queryset)
                # if (context_object_name is not None):
                #         context[context_object_name] = queryset.values(self.fields)

                return context

