import logging

from django.db.models import Q, Avg
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, LoginForm, ProfileForm, ReviewForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from .models import Service, Profile
from django.shortcuts import get_object_or_404

from .models import Service, Category

logger = logging.getLogger(__name__)

def myservices(request):
    # Obtenha o perfil do usuário autenticado
    user_profile = Profile.objects.get(user=request.user)
    # Filtre os serviços usando o perfil do usuário como provedor
    user_services = Service.objects.filter(provider=user_profile)
    return render(request, 'myservices.html', {'services': user_services})

def categories(request):
    categories = Category.objects.all()
    return render(request, 'categories.html', {'categories': categories})

def providers(request):
    providers = Profile.objects.all()
    return render(request, 'providers.html', {'providers': providers})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')  # Redirect to home page or another page after login
            else:
                # Display an error message if authentication fails
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

def service_detail(request, service_id):
    service = Service.objects.get(pk=service_id)
    return render(request, 'service_detail.html', {'service': service})

def booking(request):
    return render(request, 'booking.html')

def about(request):
    return render(request, 'about.html')


def profile(request, user_id):
    user_profile = get_object_or_404(Profile, user_id=user_id)

    # Calculate average rating
    avg_rating = user_profile.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    # Fetch reviews
    reviews = user_profile.reviews.all().order_by('-created_at')

    # Handle review form submission
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.profile = user_profile
            review.reviewer = request.user
            review.save()
            return redirect('profile', user_id=user_id)
    else:
        form = ReviewForm()

    context = {
        'profile': user_profile,
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