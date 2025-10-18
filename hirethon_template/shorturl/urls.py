from django.urls import path
from hirethon_template.shorturl import views

app_name = "shorturl"
urlpatterns = [
    # Organization API URLs
    path("organizations/", views.OrganizationListCreateAPIView.as_view(), name="organization_list_create"),
    path("organizations/<int:pk>/", views.OrganizationDetailAPIView.as_view(), name="organization_detail"),
    path("organizations/<int:pk>/members/", views.organization_members, name="organization_members"),
    path("organizations/<int:pk>/namespaces/", views.organization_namespaces, name="organization_namespaces"),
    
    # Namespace API URLs
    path("namespaces/", views.NamespaceCreateAPIView.as_view(), name="namespace_create"),
]
