from django.urls import path

from ..views import (
    CategoryCreateView,
    CategoryDetailView,
    CategoryListView,
    CategoryUpdateView,
)

urlpatterns = [
    path("", CategoryListView.as_view(), name="category-list"),
    path("create/", CategoryCreateView.as_view(), name="category-create"),
    path("<int:pk>/", CategoryDetailView.as_view(), name="category-detail"),
    path(
        "update/<int:pk>/",
        CategoryUpdateView.as_view(),
        name="category-update",
    ),
]
