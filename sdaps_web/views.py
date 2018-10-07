from django.conf.urls import url
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^accounts/login/$', auth_views.LoginView.as_view(), name="login"),
    url(r'^accounts/logout/$', auth_views.LogoutView.as_view(), name="logout"),
#    url(r'^accounts/profile$', auth_views.profile),
    url(r'^accounts/password_change/$', auth_views.PasswordChangeView.as_view(), name="password_change"),
    url(r'^accounts/password_change_done/$', auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),

# TODO: Password reset
# password_reset, password_reset_done, password_reset_confirm, password_reset_complete
]

