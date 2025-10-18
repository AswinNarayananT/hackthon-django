from django.urls import path

from hirethon_template.users.views import (
    CustomLoginView,
    CustomLogoutView,
    CustomRefreshTokenView,
    CustomRegisterView,
    user_detail_view,
    user_redirect_view,
    user_update_view,
)

app_name = "users"
urlpatterns = [
    path('custom-login/', CustomLoginView.as_view(), name='custom-login'),
    path('custom-register/', CustomRegisterView.as_view(), name='custom-register'),
    path('custom-logout/', CustomLogoutView.as_view(), name='custom-logout'),
    path('token-refresh/', CustomRefreshTokenView.as_view(), name='token-refresh'),
    path("~redirect/", view=user_redirect_view, name="redirect"),
    path("~update/", view=user_update_view, name="update"),
    path("<int:pk>/", view=user_detail_view, name="detail"),
]
