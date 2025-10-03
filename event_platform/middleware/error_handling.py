from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.contrib import messages
from django.shortcuts import redirect

class ErrorHandlingMiddleware:
    """Middleware para manejar errores de permisos y otros errores comunes"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        """Maneja excepciones específicas"""
        
        if isinstance(exception, PermissionDenied):
            # Error de permisos insuficientes
            messages.error(
                request, 
                'No tienes permisos suficientes para realizar esta acción.'
            )
            
            # Si no está autenticado, redirigir al login
            if not request.user.is_authenticated:
                return redirect('usuarios:login')
            
            # Si está autenticado pero sin permisos, mostrar página de acceso denegado
            return render(request, 'usuarios/acceso_denegado.html', {
                'titulo': 'Acceso Denegado',
                'mensaje': 'No tienes permisos suficientes para acceder a esta página.',
                'detalle': str(exception) if str(exception) else None
            }, status=403)
        
        # Para otros errores, dejar que Django los maneje normalmente
        return None