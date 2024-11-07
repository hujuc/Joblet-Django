from .models import Provider

def is_provider(request):
    if request.user.is_authenticated:
        return {'is_provider': hasattr(request.user, 'profile') and hasattr(request.user.profile, 'provider')}
    return {'is_provider': False}