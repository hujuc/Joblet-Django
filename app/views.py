import logging

from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, LoginForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from .models import Service, Profile

from .models import Service, Category

logger = logging.getLogger(__name__)

def myservices(request):
    # Obtenha o perfil do usuário autenticado
    user_profile = Profile.objects.get(user=request.user)
    # Filtre os serviços usando o perfil do usuário como provedor
    user_services = Service.objects.filter(provider=user_profile)
    return render(request, 'myservices.html', {'services': user_services})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'GET':
        form = LoginForm()
        return render(request, 'login.html', {'form': form})

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'index')
                return redirect(next_url)
            else:
                messages.error(request, 'Nome de usuário ou senha inválidos.')

        return render(request, 'login.html', {'form': form})

def home(request):
    return render(request, 'index.html')

def services(request):
    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '0')
    sort_option = request.GET.get('sort', '0')

    # Start with all services
    services = Service.objects.all()

    # Filter by search query
    if search_query:
        services = services.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )

    # Filter by category if selected
    if category_id and category_id != '0':
        services = services.filter(category_id=category_id)

    # Apply sorting
    if sort_option == '1':  # Most Popular
        services = services.order_by('-popularity')  # Ensure you have a popularity field or adjust accordingly
    elif sort_option == '2':  # Price: Low to High
        services = services.order_by('price')
    elif sort_option == '3':  # Price: High to Low
        services = services.order_by('-price')
    else:  # Most Recent
        services = services.order_by('-created_at')  # Ensure you have a created_at field or adjust accordingly

    # Pass categories and filtered services to template
    categories = Category.objects.all()
    context = {
        'title': 'Services',
        'services': services,
        'categories': categories,
        'search_query': search_query,
        'category_id': category_id,
        'sort_option': sort_option,
    }
    return render(request, 'services.html', context)


def booking(request):
    return render(request, 'booking.html')


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Conta criada com sucesso para {user.username}!")
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Erro ao criar conta. Por favor, verifique os dados.")
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    messages.success(request, "Você foi desconectado com sucesso!")
    return redirect('login')

def about(request):
    return render(request, 'about.html')

def profile(request):
    return render(request, 'profile.html')



