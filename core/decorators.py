from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden

def login_required(view_func):
    """
    Redirect to login if no employee session exists.
    Usage:
        @login_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('employee'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def role_required(*allowed_roles):
    """
    Allow access only to users whose role_name is in *allowed_roles.
    Must be used **after** @login_required.
    Usage:
        @login_required
        @role_required('System Admin')
        def admin_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            employee = request.session.get('employee')
            if not employee:
                # Should never happen if login_required is applied first, but be safe
                return redirect('login')
            if employee.get('role_name') not in allowed_roles:
                return HttpResponseForbidden("Access denied: you don't have the required role.")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator