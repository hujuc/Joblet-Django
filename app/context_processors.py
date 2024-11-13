from django.core.exceptions import ObjectDoesNotExist

from .models import Category
from .views import categories
from .models import Notification


def category_list(request):
    #categories = Category.objects.filter(service__is_active=True).distinct()
    categories = Category.objects.all()
    return {'categories': categories}

def unread_notifications_count(request):
    if request.user.is_authenticated:
        try:
            unread_count = Notification.objects.filter(recipient=request.user.profile, read=False).count()
        except ObjectDoesNotExist:
            unread_count = 0
        return {'unread_notifications_count': unread_count}
    return {'unread_notifications_count': 0}