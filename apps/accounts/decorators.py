# RBAC: require login and optional role/permission
from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*role_names: str):
    """Decorator: require user to be logged in and have one of the given roles."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            profile = getattr(request.user, "profile", None)
            if not profile or not profile.role:
                messages.error(request, "You do not have a role assigned.")
                return redirect("home")
            if profile.role.name not in role_names:
                messages.error(request, "You do not have permission to access this page.")
                return redirect("home")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator


def permission_required(perm_name: str):
    """Decorator: require user to be logged in and have the given permission."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            profile = getattr(request.user, "profile", None)
            if not profile or not profile.has_perm(perm_name):
                messages.error(request, "You do not have permission to access this page.")
                return redirect("home")
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
