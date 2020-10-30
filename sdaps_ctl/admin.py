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

from django.db.models import Q
from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import Survey, UploadedFile


class SurveyAdmin(GuardedModelAdmin):
    list_display = ('name', 'title', 'author')

    @classmethod
    def has_permissions(cls, request, obj=None):
        if request.user.is_superuser or request.user.is_staff:
            return True

        if obj is None:
            return True

        # Is the user the owner?
        if obj.owner == request.user:
            return True

        # if obj.group:
        #     if request.user.groups.filter(pk=obj.group.id).exists():
        #         return True

        return False

    def has_change_permission(self, request, obj=None):
        print("has change permission called")
        if not request.user.has_perms('sdaps_ctl.change_survey'):
            return False

        return self.has_permissions(request, obj)

    def has_review_permission(self, request, obj=None):
        if not request.user.has_perms('sdaps_ctl.review_survey'):
            return False

        return self.has_permissions(request, obj)

    def has_delete_permission(self, request, obj=None):
        if not request.user.has_perms('sdaps_ctl.delete_survey'):
            return False

        return self.has_permissions(request, obj)

    @classmethod
    def filter(cls, request, queryset):
        user = request.user
        if user.is_superuser or user.is_staff:
            return queryset

        # TODO: This should be a nested query instead!
        groups = user.groups.all()

        return queryset.filter(Q(owner=user) | Q(group__in=groups))


admin.site.register(Survey, SurveyAdmin)


class UploadedFileAdmin(GuardedModelAdmin):
    pass


admin.site.register(UploadedFile, UploadedFileAdmin)
