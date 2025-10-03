from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import (
    ListView, DetailView, CreateView, 
    UpdateView, DeleteView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.http import Http404
from django.core.exceptions import PermissionDenied
from .models import Evento, TipoEvento, RegistroEvento
from django import forms

# Formulario para crear/editar eventos
class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = [
            'titulo', 'descripcion', 'tipo_evento', 
            'fecha_inicio', 'fecha_fin', 'ubicacion', 
            'capacidad_maxima', 'estado', 'privacidad', 
            'imagen', 'precio'
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'fecha_inicio': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'fecha_fin': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personalizar labels en español
        self.fields['titulo'].label = 'Título del Evento'
        self.fields['descripcion'].label = 'Descripción'
        self.fields['tipo_evento'].label = 'Tipo de Evento'
        self.fields['fecha_inicio'].label = 'Fecha y Hora de Inicio'
        self.fields['fecha_fin'].label = 'Fecha y Hora de Finalización'
        self.fields['ubicacion'].label = 'Ubicación'
        self.fields['capacidad_maxima'].label = 'Capacidad Máxima'
        self.fields['estado'].label = 'Estado del Evento'
        self.fields['privacidad'].label = 'Privacidad'
        self.fields['imagen'].label = 'Imagen del Evento'
        self.fields['precio'].label = 'Precio de Entrada'

# Vista para listar eventos
class ListaEventosView(ListView):
    """Vista para mostrar la lista de eventos públicos y permitidos"""
    model = Evento
    template_name = 'eventos/lista.html'
    context_object_name = 'eventos'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Evento.objects.all()
        
        # Si el usuario no está autenticado, solo eventos públicos
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(privacidad='publico', estado='publicado')
        else:
            # Si está autenticado, mostrar eventos públicos y privados permitidos
            user = self.request.user
            
            # Administradores ven todo
            if user.has_perm('eventos.can_manage_all_events'):
                pass  # No filtrar nada
            # Organizadores ven eventos públicos + sus eventos + eventos privados permitidos
            elif user.has_perm('eventos.can_view_private_events'):
                queryset = queryset.filter(
                    Q(privacidad='publico') |
                    Q(organizador=user) |
                    Q(privacidad='privado', asistentes=user)
                ).distinct()
            # Asistentes ven solo eventos públicos + eventos privados donde están registrados
            else:
                queryset = queryset.filter(
                    Q(privacidad='publico', estado='publicado') |
                    Q(privacidad='privado', asistentes=user)
                ).distinct()
        
        # Filtro por búsqueda
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(titulo__icontains=search) |
                Q(descripcion__icontains=search) |
                Q(ubicacion__icontains=search)
            )
        
        # Filtro por tipo
        tipo = self.request.GET.get('tipo')
        if tipo:
            queryset = queryset.filter(tipo_evento__id=tipo)
        
        return queryset.order_by('-fecha_inicio')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tipos_eventos'] = TipoEvento.objects.all()
        context['search'] = self.request.GET.get('search', '')
        context['tipo_seleccionado'] = self.request.GET.get('tipo', '')
        return context

# Vista temporal usando función (será reemplazada por la clase)
def lista_eventos(request):
    view = ListaEventosView.as_view()
    return view(request)

# Vista para ver detalle de un evento
class DetalleEventoView(DetailView):
    """Vista para mostrar el detalle de un evento"""
    model = Evento
    template_name = 'eventos/detalle.html'
    context_object_name = 'evento'
    
    def get_object(self, queryset=None):
        evento = super().get_object(queryset)
        
        # Verificar si el usuario puede ver este evento
        if not evento.puede_ver_evento(self.request.user):
            raise Http404("El evento no existe o no tienes permisos para verlo")
        
        return evento
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            # Verificar si el usuario ya está registrado
            context['esta_registrado'] = RegistroEvento.objects.filter(
                evento=self.object,
                usuario=self.request.user,
                estado='confirmado'
            ).exists()
            
            # Verificar si puede editar el evento
            context['puede_editar'] = (
                self.request.user == self.object.organizador or
                self.request.user.has_perm('eventos.can_manage_all_events')
            )
        
        return context

# Vista para crear eventos
class CrearEventoView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    """Vista para crear nuevos eventos"""
    model = Evento
    form_class = EventoForm
    template_name = 'eventos/crear.html'
    permission_required = 'eventos.add_evento'
    login_url = '/usuarios/login/'
    
    def form_valid(self, form):
        # Asignar el usuario actual como organizador
        form.instance.organizador = self.request.user
        messages.success(
            self.request, 
            f'El evento "{form.instance.titulo}" ha sido creado exitosamente.'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(
            self.request, 
            'Hubo errores en el formulario. Por favor, revisa los datos ingresados.'
        )
        return super().form_invalid(form)

# Vista para editar eventos
class EditarEventoView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    """Vista para editar eventos existentes"""
    model = Evento
    form_class = EventoForm
    template_name = 'eventos/editar.html'
    permission_required = 'eventos.change_evento'
    login_url = '/usuarios/login/'
    
    def get_object(self, queryset=None):
        evento = super().get_object(queryset)
        
        # Solo el organizador o administradores pueden editar
        if not (self.request.user == evento.organizador or 
                self.request.user.has_perm('eventos.can_manage_all_events')):
            raise PermissionDenied("No tienes permisos para editar este evento")
        
        return evento
    
    def form_valid(self, form):
        messages.success(
            self.request, 
            f'El evento "{form.instance.titulo}" ha sido actualizado exitosamente.'
        )
        return super().form_valid(form)

# Vista para eliminar eventos
class EliminarEventoView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Vista para eliminar eventos"""
    model = Evento
    template_name = 'eventos/eliminar.html'
    permission_required = 'eventos.delete_evento'
    success_url = reverse_lazy('eventos:lista')
    login_url = '/usuarios/login/'
    
    def get_object(self, queryset=None):
        evento = super().get_object(queryset)
        
        # Solo administradores pueden eliminar eventos
        if not self.request.user.has_perm('eventos.can_manage_all_events'):
            raise PermissionDenied("Solo los administradores pueden eliminar eventos")
        
        return evento
    
    def delete(self, request, *args, **kwargs):
        evento = self.get_object()
        titulo = evento.titulo
        messages.success(
            request, 
            f'El evento "{titulo}" ha sido eliminado exitosamente.'
        )
        return super().delete(request, *args, **kwargs)

# Vista para registrarse a un evento
@login_required
def registrarse_evento(request, pk):
    """Vista para que un usuario se registre a un evento"""
    evento = get_object_or_404(Evento, pk=pk)
    
    # Verificar si puede ver el evento
    if not evento.puede_ver_evento(request.user):
        messages.error(request, 'No tienes permisos para acceder a este evento.')
        return redirect('eventos:lista')
    
    # Verificar si ya está registrado
    registro_existente = RegistroEvento.objects.filter(
        evento=evento,
        usuario=request.user
    ).first()
    
    if registro_existente:
        if registro_existente.estado == 'confirmado':
            messages.warning(request, 'Ya estás registrado en este evento.')
        elif registro_existente.estado == 'cancelado':
            # Reactivar registro
            registro_existente.estado = 'confirmado'
            registro_existente.save()
            messages.success(request, 'Te has registrado exitosamente al evento.')
        else:
            messages.info(request, 'Tu registro está pendiente de confirmación.')
    else:
        # Verificar capacidad
        if evento.plazas_disponibles <= 0:
            messages.error(request, 'Este evento ha alcanzado su capacidad máxima.')
            return redirect('eventos:detalle', pk=pk)
        
        # Crear nuevo registro
        RegistroEvento.objects.create(
            evento=evento,
            usuario=request.user,
            estado='confirmado'
        )
        messages.success(request, 'Te has registrado exitosamente al evento.')
    
    return redirect('eventos:detalle', pk=pk)

# Vista para cancelar registro a un evento
@login_required
def cancelar_registro(request, pk):
    """Vista para cancelar el registro a un evento"""
    evento = get_object_or_404(Evento, pk=pk)
    
    registro = get_object_or_404(
        RegistroEvento,
        evento=evento,
        usuario=request.user,
        estado='confirmado'
    )
    
    registro.estado = 'cancelado'
    registro.save()
    
    messages.success(request, f'Has cancelado tu registro al evento "{evento.titulo}".')
    return redirect('eventos:detalle', pk=pk)

# Vista para listar mis eventos (como organizador)
class MisEventosView(LoginRequiredMixin, ListView):
    """Vista para que los organizadores vean sus eventos"""
    model = Evento
    template_name = 'eventos/mis_eventos.html'
    context_object_name = 'eventos'
    login_url = '/usuarios/login/'
    
    def get_queryset(self):
        return Evento.objects.filter(organizador=self.request.user).order_by('-fecha_creacion')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['puede_crear'] = self.request.user.has_perm('eventos.add_evento')
        return context
