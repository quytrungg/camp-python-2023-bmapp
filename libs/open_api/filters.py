from rest_framework import filters

from drf_spectacular import drainage


class OrderingFilterBackend(filters.OrderingFilter):
    """Custom OrderingFilter for better support of openapi."""

    def get_schema_operation_parameters(self, view):
        """Extend description."""
        operation_parameters = super().get_schema_operation_parameters(
            view=view,
        )
        # Not using get_valid_fields since it is requires additional params
        if not hasattr(view, "ordering_fields"):
            drainage.warn(
                "`ordering_fields` are not set up for "
                f"{view.__class__}",
            )
            return operation_parameters
        formatted_fields = ", ".join(
            f"`{field}`" for field in view.ordering_fields
        )
        operation_parameters[0]["description"] = (
            "Which fields to use when ordering the results. А list "
            "fields separated by `,`. Example: `field1,field2`\n\n"
            f"Supported fields: {formatted_fields}.\n\n"
            "To reverse order just add `-` to field. Example:"
            "`field` -> `-field`"
        )
        return operation_parameters


class SearchFilterBackend(filters.SearchFilter):
    """Custom SearchFilter for better support of openapi."""

    def get_schema_operation_parameters(self, view):
        """Extend description."""
        operation_parameters = super().get_schema_operation_parameters(
            view=view,
        )
        # Not using get_search_fields since it is requires additional params
        if not hasattr(view, "search_fields"):
            drainage.warn(
                "`search_fields` are not set up for "
                f"{view.__class__}",
            )
            return operation_parameters
        formatted_fields = ", ".join(
            f"`{field}`" for field in view.search_fields
        )
        operation_parameters[0]["description"] = (
            "A search term.\n\n"
            f"Performed on this fields: {formatted_fields}."
        )
        return operation_parameters
