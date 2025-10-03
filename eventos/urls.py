from django.urls import path
from . import views

app_name = 'eventos'

urlpatterns = [
    # URLs principales
    path('', views.ListaEventosView.as_view(), name='lista'),
    path('crear/', views.CrearEventoView.as_view(), name='crear'),
    path('mis-eventos/', views.MisEventosView.as_view(), name='mis_eventos'),
    
    # URLs específicas de eventos
    path('<int:pk>/', views.DetalleEventoView.as_view(), name='detalle'),
    path('<int:pk>/editar/', views.EditarEventoView.as_view(), name='editar'),
    path('<int:pk>/eliminar/', views.EliminarEventoView.as_view(), name='eliminar'),
    
    # URLs para registro de asistentes
    path('<int:pk>/registrarse/', views.registrarse_evento, name='registrarse'),
    path('<int:pk>/cancelar-registro/', views.cancelar_registro, name='cancelar_registro'),
]