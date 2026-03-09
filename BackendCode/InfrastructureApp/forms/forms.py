from django import forms
from InfrastructureApp.constants import HTML
from InfrastructureApp.constants.CSS import Bootstrap5

class InfrastructureForm(forms.Form):

    def __init__(self, request=None, *args, **kwargs):
        self.request = request  # makes the request object available to form class.
        super().__init__(*args, **kwargs)


    def clean(self):
        super().clean()
        for inputFieldHTMLName in self.errors.keys():
            if not isinstance(self.fields[inputFieldHTMLName].widget, forms.Select):
                if HTML.ElementAttributes.CLASS in self.fields[inputFieldHTMLName].widget.attrs.keys():
                    self.fields[inputFieldHTMLName].widget.attrs[HTML.ElementAttributes.CLASS] += " is-invalid"
                else:
                    self.fields[inputFieldHTMLName].widget.attrs[HTML.ElementAttributes.CLASS] = "form-control is-invalid"
        return self.cleaned_data

    def render(self, template_name=None, context=None, renderer=None):
        for fieldHTMLName in self.fields.keys():
            widgetObject = self.fields[fieldHTMLName].widget 
            if isinstance(widgetObject, forms.Select):
                widgetObject.attrs
                if HTML.ElementAttributes.CLASS in widgetObject.attrs.keys():
                    widgetObject.attrs[HTML.ElementAttributes.CLASS] += " " + Bootstrap5.Forms.Select.DEFAULT
                else:
                    widgetObject.attrs[HTML.ElementAttributes.CLASS] = Bootstrap5.Forms.Select.DEFAULT
            else:
                if HTML.ElementAttributes.CLASS in widgetObject.attrs.keys():
                    widgetObject.attrs[HTML.ElementAttributes.CLASS] += " form-control"
                else:
                    widgetObject.attrs[HTML.ElementAttributes.CLASS] = "form-control"

        return super().render(template_name, context, renderer)