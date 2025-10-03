from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from .models import TipoEvento, Evento, RegistroEvento

# Configuración para TipoEvento
@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'descripcion']
    search_fields = ['nombre']
    ordering = ['nombre']

# Inline para mostrar registros en el admin de eventos
class RegistroEventoInline(admin.TabularInline):
    model = RegistroEvento
    extra = 0
    readonly_fields = ['fecha_registro']
    fields = ['usuario', 'estado', 'fecha_registro', 'comentarios']

# Configuración para Evento
@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 
        'tipo_evento', 
        'organizador', 
        'fecha_inicio', 
        'estado', 
        'privacidad',
        'plazas_disponibles'
    ]
    list_filter = [
        'estado', 
        'privacidad', 
        'tipo_evento', 
        'fecha_inicio'
    ]
    search_fields = ['titulo', 'descripcion', 'organizador__username']
    ordering = ['-fecha_inicio']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'tipo_evento', 'imagen')
        }),
        ('Fecha y Ubicación', {
            'fields': ('fecha_inicio', 'fecha_fin', 'ubicacion', 'capacidad_maxima')
        }),
        ('Configuración', {
            'fields': ('organizador', 'estado', 'privacidad', 'precio')
        }),
        ('Información de Sistema', {
            'fields': ('fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['fecha_creacion', 'fecha_actualizacion']
    inlines = [RegistroEventoInline]
    
    def plazas_disponibles(self, obj):
        return obj.plazas_disponibles
    plazas_disponibles.short_description = 'Plazas Disponibles'

# Configuración para RegistroEvento
@admin.register(RegistroEvento)
class RegistroEventoAdmin(admin.ModelAdmin):
    list_display = [
        'usuario', 
        'evento', 
        'estado', 
        'fecha_registro'
    ]
    list_filter = ['estado', 'fecha_registro', 'evento__tipo_evento']
    search_fields = [
        'usuario__username', 
        'usuario__email', 
        'evento__titulo'
    ]
    ordering = ['-fecha_registro']
    
    fieldsets = (
        ('Información del Registro', {
            'fields': ('usuario', 'evento', 'estado')
        }),
        ('Detalles Adicionales', {
            'fields': ('comentarios', 'fecha_registro'),
        }),
    )
    
    readonly_fields = ['fecha_registro']
