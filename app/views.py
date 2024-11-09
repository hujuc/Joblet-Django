import logging
from django.db.models import Avg
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import CustomUserCreationForm, LoginForm, ProfileForm, ReviewForm, CategoryForm, AddBalanceForm, \
    ProviderForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import User
from .models import Profile, Provider, Service, Category, Booking, Notification
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden, JsonResponse

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
    categories = Category.objects.all()  # Fetch categories here
    return render(request, 'myservices.html', {'services': user_services, 'categories': categories})


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
    service = get_object_or_404(Service, pk=service_id)
    categories = Category.objects.all()

    if request.method == 'POST':
        # Update fields with POST data
        service.title = request.POST.get('title')
        service.description = request.POST.get('description')
        service.price = request.POST.get('price')
        service.category_id = request.POST.get('category')

        # Check if a new image was uploaded
        if 'image' in request.FILES:
            service.image = request.FILES['image']  # Update image with the new file

        service.save()  # Save the service with updated fields
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
            provider=provider,
            title=title,
            description=description,
            price=price,
            duration=duration,
            category_id=category_id,
            is_active=True,  # Set to True to indicate the service is initially active
            approval='pending approval',  # Set the initial approval status to "Pending Approval"
            image=image
        )
        service.save()

        return redirect('myservices')

    return render(request, 'myservices.html', {'categories': categories})

def delete_service(request, service_id):
    service = Service.objects.get(pk=service_id)
    service.delete()
    return redirect('myservices')

from django.http import JsonResponse
def get_service_data(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    categories = Category.objects.all()

    data = {
        'title': service.title,
        'description': service.description,
        'category': service.category.id,  # Current category ID of the service
        'price': str(service.price),
        'image': service.image.url if service.image else None,
        'categories': [{'id': cat.id, 'name': cat.name} for cat in categories],  # Send all categories
    }
    return JsonResponse(data)


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

from django.db.models import Avg, Q

def services(request):
    # Get filter parameters from request
    search_query = request.GET.get('search', '')
    category_id = request.GET.get('category', '0')
    sort_option = request.GET.get('sort', '0')

    # Start with approved services only
    services = Service.objects.filter(approval='approved').select_related(
        'provider',
        'provider__profile',
        'provider__profile__user',
        'category'
    ).prefetch_related('provider__reviews')

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

    # Annotate each service with the average rating of its provider
    services = services.annotate(avg_rating=Avg('provider__reviews__rating'))

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
    service = get_object_or_404(Service.objects.select_related('provider__profile__user').prefetch_related('provider__reviews'), id=service_id)

    # Calcular a média das avaliações do provedor
    avg_rating = service.provider.reviews.aggregate(avg_rating=Avg('rating'))['avg_rating'] or 0

    context = {
        'service': service,
        'avg_rating': avg_rating,  # Passar o avg_rating para o template
    }
    return render(request, 'service_detail.html', context)

def booking(request):
    return render(request, 'booking.html')

def about(request):
    return render(request, 'about.html')

from django.shortcuts import redirect

from decimal import Decimal

def profile(request, user_id):
    # Get the user's profile
    user_profile = get_object_or_404(Profile, user_id=user_id)

    # Initialize forms
    profile_form = ProfileForm(instance=user_profile)
    provider_form = None
    if hasattr(user_profile, 'provider'):
        provider_form = ProviderForm(instance=user_profile.provider)
    review_form = ReviewForm()
    add_balance_form = AddBalanceForm()

    booking_history = Booking.objects.filter(customer=user_profile).select_related('service').order_by('-date')

    # Get the provider instance if it exists
    provider = user_profile.provider if hasattr(user_profile, 'provider') else None
    is_provider = provider is not None
    approved_services = provider.services.filter(approval='approved') if is_provider else None
    avg_rating = provider.reviews.aggregate(Avg('rating'))['rating__avg'] if is_provider else None
    reviews = provider.reviews.all() if is_provider else None

    # Handle form submissions
    if request.method == 'POST':
        if 'update_profile' in request.POST:  # Profile Form
            profile_form = ProfileForm(request.POST, request.FILES, instance=user_profile)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('profile', user_id=user_id)

        elif 'update_provider' in request.POST and is_provider:  # Pr
            provider_form = ProviderForm(request.POST, request.FILES, instance=user_profile.provider)
            if provider_form.is_valid():
                provider_form.save()
                return redirect('profile', user_id=user_id)

        elif 'add_review' in request.POST and is_provider:  # Review Form
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.provider = provider
                review.reviewer = user_profile
                review.save()
                return redirect('profile', user_id=user_id)

        elif 'add_balance' in request.POST:  # Add Balance Form
            add_balance_form = AddBalanceForm(request.POST)
            if add_balance_form.is_valid():
                amount = add_balance_form.cleaned_data['amount']
                user_profile.wallet += amount
                user_profile.save()
                return redirect('profile', user_id=user_id)

    # Pass context to the template
    context = {
        'profile': user_profile,
        'is_provider': is_provider,
        'services': approved_services,
        'avg_rating': avg_rating,
        'reviews': reviews,
        'profile_form': profile_form,
        'provider_form': provider_form,
        'review_form': review_form,
        'add_balance_form': add_balance_form,
        'booking_history': booking_history if request.user == user_profile.user else None,
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

from django.utils import timezone

@login_required
def book_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    profile = Profile.objects.get(user=request.user)

    if request.method == "POST":
        if profile.wallet < service.price:
            messages.error(request, "Saldo insuficiente para requisitar este serviço.")
            return redirect('service_detail', service_id=service_id)

        profile.wallet -= service.price
        profile.save()

        date_str = request.POST.get("date")
        try:
            date = timezone.datetime.strptime(date_str, "%Y-%m-%dT%H:%M")
            booking = Booking.objects.create(service=service, customer=profile, date=date, status="pending")

            # Cria a notificação para o provedor com ação requerida
            notification_message = f"Novo pedido de reserva para o serviço '{service.title}' por {profile.user.username}."
            Notification.objects.create(
                recipient=service.provider.profile,
                message=notification_message,
                booking=booking,
                action_required=True
            )

            messages.success(request, f"Reserva para {service.title} em {date} criada com sucesso.")
        except ValueError:
            messages.error(request, "Formato de data inválido. Por favor, use o formato correto.")

    return redirect('profile', user_id=request.user.id)


@login_required
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    if request.user.profile != booking.customer:
        messages.error(request, "Você não tem permissão para alterar o status desta reserva.")
        return redirect('profile', user_id=request.user.id)

    if not booking.approved_by_provider:
        messages.warning(request, "Esta reserva ainda não foi aprovada pelo provedor.")
        return redirect('profile', user_id=request.user.id)

    if booking.status != 'completed':
        booking.status = 'completed'
        booking.save()

        provider_profile = booking.service.provider.profile
        provider_profile.wallet += booking.service.price
        provider_profile.save()

        messages.success(request, "Status da reserva atualizado para 'concluído' e valor depositado na carteira.")
    else:
        messages.info(request, "Esta reserva já foi concluída.")

    return redirect('profile', user_id=request.user.id)
@login_required
def notifications(request):
    user_profile = Profile.objects.get(user=request.user)
    notifications = user_profile.notifications.order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user.profile)
    notification.read = True
    notification.save()
    return redirect('notifications')


@login_required
def approve_booking(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user.profile)

    if not notification.booking:
        messages.error(request, "Reserva não encontrada para esta notificação.")
        return redirect('notifications')

    # Aprova a reserva associada
    booking = notification.booking
    booking.approved_by_provider = True
    booking.save()

    # Marca a notificação como lida
    notification.read = True
    notification.action_required = False
    notification.save()

    messages.success(request, "Reserva aprovada com sucesso!")
    return redirect('notifications')

@login_required
def reject_booking(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user.profile)

    if not notification.booking:
        messages.error(request, "Reserva não encontrada para esta notificação.")
        return redirect('notifications')

    # Rejeita a reserva associada
    booking = notification.booking
    booking.status = 'cancelled'
    booking.save()

    # Marca a notificação como lida
    notification.read = True
    notification.action_required = False
    notification.save()

    messages.success(request, "Reserva rejeitada com sucesso!")
    return redirect('notifications')