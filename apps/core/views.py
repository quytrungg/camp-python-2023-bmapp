import platform
from collections import namedtuple
from typing import Any

import django
from django.conf import settings
from django.db.models import QuerySet
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView

from libs.utils import get_changelog_html, get_latest_version

Changelog = namedtuple("Changelog", ["name", "text", "version", "open_api_ui"])

ARGO_CD_URL_MAPPING = {
    "development": "https://deploy.saritasa.rocks/",
    "prod": "TODO",
}
ARGO_CD_MAPPING = {
    "development": "camp-python-2023-bmapp-dev",
    "prod": "camp-python-2023-bmapp-prod",
}


class AppStatsMixin:
    """Add information about app to context."""

    def get_context_data(self, **kwargs):
        """Load changelog data from files."""
        context = super().get_context_data(**kwargs)
        context.update(
            debug_setting=settings.DEBUG,
            env=settings.ENVIRONMENT,
            version=get_latest_version("CHANGELOG.md"),
            python_version=platform.python_version(),
            django_version=django.get_version(),
            app_url=settings.FRONTEND_URL,
            app_label=settings.APP_LABEL,
            argo_cd_url=ARGO_CD_URL_MAPPING.get(
                settings.ENVIRONMENT, ARGO_CD_URL_MAPPING["development"],
            ),
            argo_cd_app=ARGO_CD_MAPPING.get(
                settings.ENVIRONMENT, ARGO_CD_MAPPING["development"],
            ),
        )
        return context


class IndexView(AppStatsMixin, TemplateView):
    """Class-based view for that shows version of open_api file on main page.

    Displays the current version of the open_api specification and changelog.

    """

    template_name = "index.html"

    def get_context_data(self, **kwargs):
        """Load changelog data from files."""
        context = super().get_context_data(**kwargs)
        context["changelog"] = Changelog(
            name=settings.SPECTACULAR_SETTINGS.get("TITLE"),
            text=get_changelog_html("CHANGELOG.md"),
            version=settings.SPECTACULAR_SETTINGS.get("VERSION"),
            open_api_ui=reverse_lazy("open_api:ui"),
        )
        return context


class BaseListView(ListView):
    """Provide base class inherited from ListView for all models.

    Allow pagination and filtering in a list view page. All models will be
    inherited from this BaseListView class.

    """

    paginate_by = 10
    paginate_by_options = [5, 10, 15, 20, 25, 50, 100]
    filter_class = None
    filtering = None

    def get_paginate_by(self, queryset) -> int:
        """Return the number of items to paginate by."""
        paginate_by = self.request.GET.get("paginate-by")
        if paginate_by and int(paginate_by) in self.paginate_by_options:
            return int(paginate_by)
        return self.paginate_by

    def get_queryset(self) -> QuerySet:
        """Get object queryset and add django_filter instance."""
        qs = super().get_queryset()
        self.filtering = self.filter_class(  # pylint: disable=E1102
            self.request.GET,
            queryset=qs,
            request=self.request,
        )

        return self.filtering.qs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Get context data, including pagination and filtering."""
        context = super().get_context_data(**kwargs)
        data_to_update = {}

        data_to_update["filter"] = self.filtering
        data_to_update["paginate_by_options"] = self.paginate_by_options
        data_to_update["paginate_by"] = self.get_paginate_by(
            context["object_list"],
        )

        context.update(data_to_update)
        return context
