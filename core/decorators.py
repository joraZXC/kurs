from django.http import HttpResponseForbidden
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_staff:
            return HttpResponseForbidden("Только администраторы могут получить доступ.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view