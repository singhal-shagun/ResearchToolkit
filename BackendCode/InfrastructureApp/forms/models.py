from django import forms


class InfrastructureModelForm(forms.ModelForm):

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)


    def clean(self):
        super().clean()
        for inputFieldHTMLName in self.errors.keys():
            if "class" in self.fields[inputFieldHTMLName].widget.attrs.keys():
                self.fields[inputFieldHTMLName].widget.attrs["class"] += " is-invalid"
            else:
                self.fields[inputFieldHTMLName].widget.attrs["class"] = "form-control is-invalid"

    def render(self, template_name=None, context=None, renderer=None):
        for fieldHTMLName in self.fields.keys():
            if "class" in self.fields[fieldHTMLName].widget.attrs.keys():
                self.fields[fieldHTMLName].widget.attrs["class"] += " form-control"
            else:
                self.fields[fieldHTMLName].widget.attrs["class"] = "form-control"

        return super().render(template_name, context, renderer)