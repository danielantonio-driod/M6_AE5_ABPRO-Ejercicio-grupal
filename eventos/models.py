from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# Modelo para diferentes tipos de eventos
class TipoEvento(models.Model):
    """Modelo para definir los tipos de eventos (Conferencia, Concierto, Seminario, etc.)"""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del tipo")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    
    class Meta:
        verbose_name = "Tipo de Evento"
        verbose_name_plural = "Tipos de Eventos"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre

# Modelo principal para los eventos
class Evento(models.Model):
    """Modelo principal para gestionar eventos"""
    
    ESTADO_CHOICES = [
        ('borrador', 'Borrador'),
        ('publicado', 'Publicado'),
        ('cancelado', 'Cancelado'),
        ('finalizado', 'Finalizado'),
    ]
    
    PRIVACIDAD_CHOICES = [
        ('publico', 'Público'),
        ('privado', 'Privado'),
    ]
    
    titulo = models.CharField(max_length=200, verbose_name="Título del evento")
    descripcion = models.TextField(verbose_name="Descripción del evento")
    tipo_evento = models.ForeignKey(
        TipoEvento, 
        on_delete=models.CASCADE, 
        verbose_name="Tipo de evento"
    )
    
    # Información de fechas y ubicación
    fecha_inicio = models.DateTimeField(verbose_name="Fecha y hora de inicio")
    fecha_fin = models.DateTimeField(verbose_name="Fecha y hora de fin")
    ubicacion = models.CharField(max_length=300, verbose_name="Ubicación")
    capacidad_maxima = models.PositiveIntegerField(
        default=100, 
        verbose_name="Capacidad máxima"
    )
    
    # Configuraciones del evento
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='borrador',
        verbose_name="Estado del evento"
    )
    privacidad = models.CharField(
        max_length=20, 
        choices=PRIVACIDAD_CHOICES, 
        default='publico',
        verbose_name="Tipo de privacidad"
    )
    
    # Relaciones con usuarios
    organizador = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='eventos_organizados',
        verbose_name="Organizador"
    )
    asistentes = models.ManyToManyField(
        User, 
        through='RegistroEvento', 
        related_name='eventos_asistiendo',
        blank=True,
        verbose_name="Asistentes"
    )
    
    # Campos de imagen y metadata
    imagen = models.ImageField(
        upload_to='eventos/', 
        blank=True, 
        null=True,
        verbose_name="Imagen del evento"
    )
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        verbose_name="Precio de entrada"
    )
    
    # Campos de auditoría
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"
        ordering = ['-fecha_inicio']
        permissions = [
            ('can_view_private_events', 'Puede ver eventos privados'),
            ('can_manage_all_events', 'Puede gestionar todos los eventos'),
        ]
    
    def __str__(self):
        return f"{self.titulo} - {self.fecha_inicio.strftime('%d/%m/%Y')}"
    
    def get_absolute_url(self):
        return reverse('eventos:detalle', kwargs={'pk': self.pk})
    
    @property
    def esta_activo(self):
        """Verifica si el evento está activo (no ha finalizado)"""
        return timezone.now() < self.fecha_fin
    
    @property
    def plazas_disponibles(self):
        """Calcula las plazas disponibles"""
        registros_confirmados = self.registros.filter(estado='confirmado').count()
        return self.capacidad_maxima - registros_confirmados
    
    def puede_ver_evento(self, usuario):
        """Verifica si un usuario puede ver este evento"""
        if self.privacidad == 'publico':
            return True
        
        if not usuario.is_authenticated:
            return False
        
        # El organizador siempre puede ver su evento
        if self.organizador == usuario:
            return True
        
        # Usuarios con permisos especiales
        if usuario.has_perm('eventos.can_view_private_events'):
            return True
        
        # Asistentes registrados pueden ver eventos privados
        return self.asistentes.filter(id=usuario.id).exists()

# Modelo para el registro de asistentes a eventos
class RegistroEvento(models.Model):
    """Modelo intermedio para gestionar registros de usuarios a eventos"""
    
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('cancelado', 'Cancelado'),
    ]
    
    usuario = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Usuario"
    )
    evento = models.ForeignKey(
        Evento, 
        on_delete=models.CASCADE, 
        related_name='registros',
        verbose_name="Evento"
    )
    
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='pendiente',
        verbose_name="Estado del registro"
    )
    
    fecha_registro = models.DateTimeField(auto_now_add=True)
    comentarios = models.TextField(
        blank=True, 
        verbose_name="Comentarios adicionales"
    )
    
    class Meta:
        verbose_name = "Registro de Evento"
        verbose_name_plural = "Registros de Eventos"
        unique_together = ['usuario', 'evento']
        ordering = ['-fecha_registro']
    
    def __str__(self):
        return f"{self.usuario.username} - {self.evento.titulo}"
