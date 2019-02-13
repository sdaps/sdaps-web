#!/usr/bin/env python3
# sdaps_web - Webinterface for SDAPS
# Copyright(C) 2019, Benjamin Berg <benjamin@sipsolutions.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from django.conf.urls import url
from django.contrib.auth import views as auth_views
from sdaps_web.settings import LOGIN_TEXT

urlpatterns = [
    url(r'^accounts/login/$', auth_views.LoginView.as_view(extra_context={'login_text': LOGIN_TEXT}), {'template_name': 'login.html'}, name="login"),
    url(r'^accounts/logout/$', auth_views.LogoutView.as_view(), name="logout"),
#    url(r'^accounts/profile$', auth_views.profile),
    url(r'^accounts/password_change/$', auth_views.PasswordChangeView.as_view(), name="password_change"),
    url(r'^accounts/password_change_done/$', auth_views.PasswordChangeDoneView.as_view(), name="password_change_done"),

# TODO: Password reset
# password_reset, password_reset_done, password_reset_confirm, password_reset_complete
]

