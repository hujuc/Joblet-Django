import logging
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomUserCreationForm, LoginForm, ProfileForm, ReviewForm, CategoryForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from .models import Profile, Provider, Service, Category
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden


logger = logging.getLogger(__name__)

def pendingservices(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to view this page.")
    services_pending = Service.objects.filter(approval='pending approval')
    return render(request, 'pendingservices.html', {'services_pending': services_pending})

def approve_service(request, service_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to view this page.")
    if request.method == "POST":
        service = get_object_or_404(Service, id=service_id)
        service.approval = 'approved'
        service.save()
        return redirect('pendingservices')

def reject_service(request, service_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to view this page.")
    if request.method == "POST":
        service = get_object_or_404(Service, id=service_id)
        service.approval = 'not approved'
        service.save()
        return redirect('pendingservices')

def users(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to view this page.")
    users = Profile.objects.all()
    return render(request, 'users.html', {'users': users})

def ban_user(request, user_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to view this page.")
    if request.method == "POST":
        user = get_object_or_404(User, id=user_id)
        user.delete()  # Remove o usuário e, por cascade, o Profile e o Provider (se existir)
        return redirect('users')

def myservices(request):
    user_profile = get_object_or_404(Profile, user=request.user)
    provider = get_object_or_404(Provider, profile=user_profile)
    user_services = Service.objects.filter(provider=provider)
    return render(request, 'myservices.html', {'services': user_services})



def categories(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        return HttpResponseForbidden("You are not authorized to view this page.")
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form = CategoryForm()

    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories, 'form': form})

def providers(request):
    providers = Provider.objects.all()
    return render(request, 'providers.html', {'providers': providers})


def edit_service(request, service_id):
    service = Service.objects.get(pk=service_id)
    categories = Category.objects.all()
    if request.method == 'POST':
        service.title = request.POST.get('title')
        service.description = request.POST.get('description')
        service.price = request.POST.get('price')  # Retrieve price from POST data
        service.category_id = request.POST.get('category')
        service.save()
        return redirect('myservices')
    return render(request, 'edit_service.html', {'service': service, 'categories': categories})

from datetime import timedelta


@login_required
def add_service(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        # Retrieve form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        duration_minutes = int(request.POST.get('duration', 0))
        category_id = request.POST.get('category')
        image = request.FILES.get('image')

        # Convert duration to timedelta
        duration = timedelta(minutes=duration_minutes)

        # Get the user’s profile and provider
        profile = Profile.objects.get(user=request.user)
        provider, created = Provider.objects.get_or_create(profile=profile)

        # Create and save new service with the correct provider instance
        service = Service(
            provider=provider,  # Assign Provider instance here
            title=title,
            description=description,
            price=price,
            duration=duration,
            category_id=category_id,
            is_active="Pending Approval",  # Set default status
            image=image
        )
        service.save()

        return redirect('myservices')

    return render(request, 'add_service.html', {'categories': categories})
def delete_service(request, service_id):
    service = Service.objects.get(pk=service_id)
    service.delete()
    return redirect('myservices')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('/')
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

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

def home(request):
    return render(request, 'index.html')

def myorders(request):
    return render(request, 'myorders.html')

def services(request):
    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '0')
    sort_option = request.GET.get('sort', '0')

    # Start with approved services only
    services = Service.objects.filter(approval='approved')

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

def service_detail(request, service_id):
    service = Service.objects.get(pk=service_id)
    return render(request, 'service_detail.html', {'service': service})

def booking(request):
    return render(request, 'booking.html')

def about(request):
    return render(request, 'about.html')

from django.shortcuts import redirect

from decimal import Decimal

def profile(request, user_id):
    # Obter o perfil do usuário pela ID fornecida
    user_profile = get_object_or_404(Profile, user_id=user_id)

    # Tentar obter o provider associado ao perfil
    try:
        provider = Provider.objects.get(profile=user_profile)
        is_provider = True
        avg_rating = provider.reviews.aggregate(Avg('rating'))['rating__avg'] or 0
        reviews = provider.reviews.all().order_by('-created_at')
        services = provider.services.filter(approval='approved')  # Obter apenas serviços aprovados
    except Provider.DoesNotExist:
        is_provider = False
        avg_rating = 0
        reviews = []
        services = []

    # Adicionar balance (somente para o próprio perfil)
    if request.method == 'POST' and "add_balance" in request.POST:
        balance_to_add = request.POST.get("balance_amount", "0")
        try:
            balance_to_add = Decimal(balance_to_add)  # Converter para Decimal
            if request.user.id == user_id:  # Garantir que o usuário está editando seu próprio perfil
                user_profile.wallet += balance_to_add
                user_profile.save()
                return redirect('profile', user_id=user_id)
        except Exception as e:
            # Log ou manipule o erro adequadamente
            print(f"Erro ao adicionar saldo: {e}")
            return redirect('profile', user_id=user_id)

    # Formulário de avaliação
    if request.method == 'POST' and "review" in request.POST:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.provider = provider
            reviewer_profile = Profile.objects.get(user=request.user)
            review.reviewer = reviewer_profile
            review.save()
            return redirect('profile', user_id=user_id)
    else:
        form = ReviewForm()

    # Passar o contexto necessário
    context = {
        'profile': user_profile,
        'is_provider': is_provider,
        'services': services,  # Adicionar serviços no contexto
        'avg_rating': avg_rating,
        'reviews': reviews,
        'form': form,
    }
    return render(request, 'profile.html', context)





def edit_profile(request, user_id):
    profile = get_object_or_404(Profile, user__id=user_id)

    # Ensure only the profile owner can edit
    if request.user != profile.user:
        return redirect('profile', user_id=user_id)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile', user_id=user_id)
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile.html', {'form': form, 'profile': profile})