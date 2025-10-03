from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from eventos.models import Evento, RegistroEvento, TipoEvento

class Command(BaseCommand):
    help = 'Crear grupos de usuarios y asignar permisos para la gestión de eventos'

    def handle(self, *args, **options):
        # Crear tipos de eventos básicos
        tipos_eventos = [
            ('Conferencia', 'Eventos académicos y profesionales'),
            ('Concierto', 'Eventos musicales y artísticos'),
            ('Seminario', 'Eventos educativos y de capacitación'),
            ('Taller', 'Eventos prácticos y de aprendizaje'),
            ('Reunión', 'Eventos corporativos y de trabajo'),
        ]
        
        for nombre, descripcion in tipos_eventos:
            tipo, created = TipoEvento.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': descripcion}
            )
            if created:
                self.stdout.write(f'Tipo de evento creado: {nombre}')

        # Obtener content types
        evento_ct = ContentType.objects.get_for_model(Evento)
        registro_ct = ContentType.objects.get_for_model(RegistroEvento)
        
        # Crear grupo de Administradores
        admin_group, created = Group.objects.get_or_create(name='Administradores')
        if created:
            self.stdout.write('Grupo "Administradores" creado')
            
            # Permisos para administradores (todos los permisos)
            admin_permissions = Permission.objects.filter(
                content_type__in=[evento_ct, registro_ct]
            )
            admin_group.permissions.set(admin_permissions)
            
            # Permisos adicionales
            custom_perms = Permission.objects.filter(
                codename__in=['can_view_private_events', 'can_manage_all_events']
            )
            admin_group.permissions.add(*custom_perms)
            
            self.stdout.write('Permisos asignados a Administradores')

        # Crear grupo de Organizadores de Eventos
        organizer_group, created = Group.objects.get_or_create(name='Organizadores')
        if created:
            self.stdout.write('Grupo "Organizadores" creado')
            
            # Permisos para organizadores
            organizer_permissions = Permission.objects.filter(
                content_type=evento_ct,
                codename__in=['add_evento', 'change_evento', 'view_evento']
            )
            organizer_group.permissions.set(organizer_permissions)
            
            # Permisos para gestionar registros
            registro_permissions = Permission.objects.filter(
                content_type=registro_ct,
                codename__in=['view_registroevento', 'change_registroevento']
            )
            organizer_group.permissions.add(*registro_permissions)
            
            # Permiso para ver eventos privados
            private_perm = Permission.objects.get(
                codename='can_view_private_events'
            )
            organizer_group.permissions.add(private_perm)
            
            self.stdout.write('Permisos asignados a Organizadores')

        # Crear grupo de Asistentes
        attendee_group, created = Group.objects.get_or_create(name='Asistentes')
        if created:
            self.stdout.write('Grupo "Asistentes" creado')
            
            # Permisos para asistentes (solo visualización)
            attendee_permissions = Permission.objects.filter(
                content_type=evento_ct,
                codename='view_evento'
            )
            attendee_group.permissions.set(attendee_permissions)
            
            # Permiso para ver sus propios registros
            registro_view_perm = Permission.objects.get(
                content_type=registro_ct,
                codename='view_registroevento'
            )
            attendee_group.permissions.add(registro_view_perm)
            
            self.stdout.write('Permisos asignados a Asistentes')

        self.stdout.write(
            self.style.SUCCESS('Grupos y permisos configurados exitosamente')
        )
        
        # Mostrar información sobre los permisos creados
        self.stdout.write('\n--- RESUMEN DE GRUPOS Y PERMISOS ---')
        
        for group in Group.objects.all():
            self.stdout.write(f'\nGrupo: {group.name}')
            perms = group.permissions.all()
            for perm in perms:
                self.stdout.write(f'  - {perm.codename}: {perm.name}')