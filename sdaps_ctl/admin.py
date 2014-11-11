
from django.contrib.auth.models import User, Group

from django.db.models import Q
from django import forms
from django.contrib import admin
from .models import Survey

class SurveyAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'author')

    @classmethod
    def has_permissions(cls, request, obj=None):
        if request.user.is_superuser or request.user.is_staff:
            return True;

        if obj is None:
            return True

        # Is the user the owner?
        if obj.owner == request.user:
            return True

        if obj.group:
            if request.user.groups.filter(pk=obj.group.id).exists():
                return True

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

