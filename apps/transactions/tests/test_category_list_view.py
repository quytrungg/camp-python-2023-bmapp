from django.db.models import Q
from django.test import Client
from django.urls import reverse

from apps.transactions.models import Category


def test_category_list_view(auth_client: Client, normal_user) -> None:
    """Ensure Category list view page works properly with status code 200."""
    response = auth_client.get(reverse("category-list"))

    assert response.status_code == 200

    response_category = response.context_data["categories"]
    db_category = Category.objects.filter(
        Q(user__isnull=True) | Q(user=normal_user),
    ).order_by("name")[:response.context_data["paginate_by"]]
    assert list(response_category) == list(db_category)
