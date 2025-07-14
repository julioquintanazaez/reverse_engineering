# decorators.py
from django.conf import settings
from functools import wraps
from rest_framework.response import Response
from rest_framework import status

def development_only(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not settings.DEBUG:
            return Response(
                {"error": "Este endpoint solo está disponible en modo desarrollo"},
                status=status.HTTP_403_FORBIDDEN
            )
        return view_func(request, *args, **kwargs)
    return _wrapped_view