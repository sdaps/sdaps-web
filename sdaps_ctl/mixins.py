from django.conf import settings
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponseNotFound
from guardian.mixins import PermissionRequiredMixin 
from guardian.conf import settings as guardian_settings
from django.shortcuts import render

# This mixin is mostly a copy of PermissionRequiredMixin
# https://github.com/django-guardian/django-guardian/issues/665


def get_any_40x_or_None(request, perms, obj=None, login_url=None,
                    redirect_field_name=None, return_403=False,
                    return_404=False, accept_global_perms=False):
    login_url = login_url or settings.LOGIN_URL
    redirect_field_name = redirect_field_name or REDIRECT_FIELD_NAME

    # Handles both original and with object provided permission check
    # as ``obj`` defaults to None

    has_permissions = False
    # global perms check first (if accept_global_perms)
    if accept_global_perms:
        has_permissions = any(request.user.has_perm(perm) for perm in perms)
    # if still no permission granted, try obj perms
    if not has_permissions:
        has_permissions = any(request.user.has_perm(perm, obj)
                              for perm in perms)

    if not has_permissions:
        if return_403:
            if guardian_settings.RENDER_403:
                response = render(request, guardian_settings.TEMPLATE_403)
                response.status_code = 403
                return response
            elif guardian_settings.RAISE_403:
                raise PermissionDenied
            return HttpResponseForbidden()
        if return_404:
            if guardian_settings.RENDER_404:
                response = render(request, guardian_settings.TEMPLATE_404)
                response.status_code = 404
                return response
            elif guardian_settings.RAISE_404:
                raise ObjectDoesNotExist
            return HttpResponseNotFound()
        else:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path(),
                                     login_url,
                                     redirect_field_name)


class AnyPermissionRequiredMixin(PermissionRequiredMixin):
    def check_permissions(self, request):
        """
        Checks if *request.user* has any permissions returned by
        *get_required_permissions* method.
        :param request: Original request.
        """
        obj = self.get_permission_object()

        forbidden = get_any_40x_or_None(request,
                                    perms=self.get_required_permissions(
                                        request),
                                    obj=obj,
                                    login_url=self.login_url,
                                    redirect_field_name=self.redirect_field_name,
                                    return_403=self.return_403,
                                    return_404=self.return_404,
                                    accept_global_perms=self.accept_global_perms
                                    )
        if forbidden:
            self.on_permission_check_fail(request, forbidden, obj=obj)
        if forbidden and self.raise_exception:
            raise PermissionDenied()
        return forbidden
