from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from django.views.generic import ListView

class AutocompleteBaseView(ListView):
    template_name = "widgets/autocomplete_results.html"
    context_object_name = "objects"
    filter_fields = []  # Fields to filter by
    paginate_by = 10
    q = ""

    def get_template_names(self) -> list[str]:
        if "page=" in str(self.request.get_full_path()):
            return ["widgets/htmx_autocomplete_items.html"]
        return super().get_template_names()

    def get_queryset(self):
        queryset = super().get_queryset()
        self.q = self.request.GET.get("q", "")

        for field in self.filter_fields:
            value = self.request.GET.get(field)
            if value:
                queryset = queryset.filter(**{field: value})

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hidden_id"] = self.request.GET.get("hidden_id")
        context["display_id"] = self.request.GET.get("display_id")
        context["search_id"] = self.request.GET.get("search_id")
        context["q"] = self.q

        if context["page_obj"].has_next():
            # Get current URL and query parameters
            current_url = self.request.get_full_path()
            parsed_url = urlparse(current_url)
            query_params = parse_qs(parsed_url.query)

            # Update just the page parameter
            query_params["page"] = [str(context["page_obj"].next_page_number())]

            # Rebuild the URL with updated query
            new_query = urlencode(query_params, doseq=True)
            new_url = urlunparse(
                (
                    parsed_url.scheme,
                    parsed_url.netloc,
                    parsed_url.path,
                    parsed_url.params,
                    new_query,
                    parsed_url.fragment,
                )
            )

            context["next_page_url"] = new_url

        return context
