from django.urls import path
from . import views

app_name = 'usuarios'

urlpatterns = [
    # URLs para autenticación
    path('login/', views.LoginUsuario.as_view(), name='login'),
    path('logout/', views.LogoutUsuario.as_view(), name='logout'),
    path('registro/', views.RegistroUsuario.as_view(), name='registro'),
    
    # URLs para gestión de perfil
    path('perfil/', views.perfil_usuario, name='perfil'),
    
    # URL para acceso denegado
    path('acceso-denegado/', views.acceso_denegado, name='acceso_denegado'),
]