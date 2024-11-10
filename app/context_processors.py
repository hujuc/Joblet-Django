from .models import Category
from .views import categories


def category_list(request):
    #categories = Category.objects.filter(service__is_active=True).distinct()
    categories = Category.objects.all()
    return {'categories': categories}