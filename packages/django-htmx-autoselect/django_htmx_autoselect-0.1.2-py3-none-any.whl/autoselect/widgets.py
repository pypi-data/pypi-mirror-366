import json
import secrets
import string

from django import forms
from django.urls import reverse_lazy


class HTMXAutocompleteWidget(forms.MultiWidget):
    template_name = "widgets/htmx_autocomplete.html"
    results_template_name = "widgets/autocomplete_results.html"
    unique_prefix_id = ""

    def __init__(
        self, autocomplete_class, attrs=None, forwarded_fields=None, view_name=None
    ):
        self.forwarded_fields = forwarded_fields or []
        self.view_name = view_name
        self.autocomplete_class = autocomplete_class
        self.unique_prefix_id = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(15)
        )

        widgets = [
            forms.HiddenInput(
                attrs={"class": "htmx-autocomplete-value", "required": "required"}
            ),
            forms.TextInput(
                attrs={
                    "class": "htmx-autocomplete-display",
                    "readonly": True,
                    "tabindex": "-1",
                    "required": "required",
                }
            ),
            forms.TextInput(
                attrs={
                    "class": "input is-medium htmx-autocomplete-input",
                    "placeholder": "Search...",
                    "autocomplete": "off",
                    "required": False,  # Explicitly not required
                }
            ),
        ]

        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value, self.get_display_value(value), ""]
        return [None, "", ""]

    def value_from_datadict(self, data, files, name):
        """Only return the value from the hidden input"""
        return data.get(f"{name}_hidden")

    def get_display_value(self, value):
        if value and hasattr(self, "autocomplete_class"):
            try:
                return str(self.autocomplete_class.objects.get(pk=value))
            except (AttributeError, self.autocomplete_class.DoesNotExist):
                pass
        return ""

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)

        if not self.view_name:
            raise ValueError("view_name is required for HTMXAutocompleteWidget")

        search_attrs = {
            "hx-get": reverse_lazy(self.view_name),
            "hx-trigger": "keyup changed delay:300ms, click",
            "hx-target": "next .htmx-autocomplete-results",
            "hx-vals": json.dumps(
                {
                    "search_id": f"{attrs['id']}_{self.unique_prefix_id}_search",
                    "hidden_id": f"{attrs['id']}_{self.unique_prefix_id}_hidden",
                    "display_id": f"{attrs['id']}_{self.unique_prefix_id}_display",
                }
            ),
            "name": "q",  # Send the input value as `q` in the request
            "autocomplete": "off",  # Disable browser autocomplete
        }

        if self.forwarded_fields:
            forwarded_names = [f"*[name='{field}']" for field in self.forwarded_fields]
            search_attrs["hx-include"] = ", ".join(forwarded_names)

        self.widgets[2].attrs.update(search_attrs)
        # print(self.widgets[2].attrs)
        return attrs

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context.update(
            {
                "hidden_widget": self.widgets[0].get_context(
                    f"{name}_hidden",
                    value,
                    {"id": f"{attrs['id']}_{self.unique_prefix_id}_hidden"},
                )["widget"],
                "display_widget": self.widgets[1].get_context(
                    f"{name}_display",
                    self.get_display_value(value),
                    {"id": f"{attrs['id']}_{self.unique_prefix_id}_display"},
                )["widget"],
                "search_widget": self.widgets[2].get_context(
                    f"q", "", {"id": f"{attrs['id']}_{self.unique_prefix_id}_search"}
                )["widget"],
                "view_name": self.view_name,
                "forwarded_fields": self.forwarded_fields,
            }
        )
        return context
