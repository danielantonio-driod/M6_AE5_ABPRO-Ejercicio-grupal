from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms

# Vista personalizada para el login
class LoginUsuario(LoginView):
    """Vista personalizada para el inicio de sesión"""
    template_name = 'usuarios/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('eventos:lista')
    
    def form_invalid(self, form):
        messages.error(
            self.request, 
            'Usuario o contraseña incorrectos. Por favor, inténtalo de nuevo.'
        )
        return super().form_invalid(form)

# Vista personalizada para el logout
class LogoutUsuario(LogoutView):
    """Vista personalizada para el cierre de sesión"""
    next_page = reverse_lazy('usuarios:login')
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Has cerrado sesión exitosamente.')
        return super().dispatch(request, *args, **kwargs)

# Formulario personalizado para registro con selección de rol
class FormularioRegistro(UserCreationForm):
    """Formulario personalizado para registro de usuarios"""
    
    TIPO_USUARIO_CHOICES = [
        ('asistente', 'Asistente - Solo puedo ver eventos'),
        ('organizador', 'Organizador - Quiero crear y gestionar eventos'),
    ]
    
    tipo_usuario = forms.ChoiceField(
        choices=TIPO_USUARIO_CHOICES,
        widget=forms.RadioSelect,
        label='¿Cómo quieres usar la plataforma?'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'tipo_usuario')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['username'].help_text = 'Requerido. 150 caracteres o menos. Solo letras, números y @/./+/-/_ permitidos.'
        self.fields['password1'].help_text = 'Tu contraseña debe tener al menos 8 caracteres y no puede ser solo numérica.'

# Vista para registro de usuarios
class RegistroUsuario(CreateView):
    """Vista para registro de nuevos usuarios"""
    form_class = FormularioRegistro
    template_name = 'usuarios/registro.html'
    success_url = reverse_lazy('usuarios:login')
    
    def form_valid(self, form):
        # Crear el usuario
        response = super().form_valid(form)
        
        # Obtener el tipo de usuario seleccionado
        tipo_usuario = form.cleaned_data.get('tipo_usuario')
        
        # Asignar al grupo correspondiente
        if tipo_usuario == 'organizador':
            grupo = Group.objects.get(name='Organizadores')
        else:
            grupo = Group.objects.get(name='Asistentes')
        
        self.object.groups.add(grupo)
        
        # Autenticar y hacer login automático
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        
        if user is not None:
            login(self.request, user)
            messages.success(
                self.request, 
                f'¡Registro exitoso! Bienvenido {username}. Has sido asignado al grupo {grupo.name}.'
            )
        
        return response
    
    def form_invalid(self, form):
        messages.error(
            self.request, 
            'Hubo un error en el registro. Por favor, revisa los datos ingresados.'
        )
        return super().form_invalid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registro de Usuario'
        return context

# Vista para mostrar perfil de usuario
@login_required
def perfil_usuario(request):
    """Vista para mostrar el perfil del usuario autenticado"""
    usuario = request.user
    grupos = usuario.groups.all()
    
    # Obtener estadísticas del usuario
    if grupos.filter(name='Organizadores').exists():
        eventos_organizados = usuario.eventos_organizados.count()
        eventos_activos = usuario.eventos_organizados.filter(estado='publicado').count()
    else:
        eventos_organizados = 0
        eventos_activos = 0
    
    eventos_registrado = usuario.eventos_asistiendo.count()
    
    context = {
        'usuario': usuario,
        'grupos': grupos,
        'eventos_organizados': eventos_organizados,
        'eventos_activos': eventos_activos,
        'eventos_registrado': eventos_registrado,
    }
    
    return render(request, 'usuarios/perfil.html', context)

# Vista para acceso denegado
def acceso_denegado(request):
    """Vista que se muestra cuando un usuario no tiene permisos suficientes"""
    return render(request, 'usuarios/acceso_denegado.html', {
        'titulo': 'Acceso Denegado',
        'mensaje': 'No tienes permisos suficientes para acceder a esta página.'
    })
