from .models import ApiKey
from django.http import JsonResponse
def api_auth(required=True):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # Get API key from request headers or query params
            api_key = request.headers.get('X-API-AUTH') or request.GET.get('api_key')
            if api_key:
                try:
                    api_key_obj = ApiKey.objects.get(key=api_key)
                except ApiKey.DoesNotExist:
                    return JsonResponse({'error': 'Unauthorized. Invalid or missing API key.'}, status=401)
                request.user = api_key_obj.user
                return view_func(request, *args, **kwargs)
            else:
                if required:
                    return JsonResponse({'error': 'Unauthorized. Missing API key.'}, status=401)
                return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator