import logging
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, LoginForm
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

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



