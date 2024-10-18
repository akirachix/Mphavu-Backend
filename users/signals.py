from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import User

@receiver(post_save, sender=User)
def assign_user_permissions(sender, instance, created, **kwargs):
    if created:
        user_content_type = ContentType.objects.get_for_model(User)

        if instance.role == "admin":
            admin_group, _ = Group.objects.get_or_create(name="Admin")
            instance.groups.add(admin_group)
            # Assign admin-specific permissions
            admin_permissions = Permission.objects.filter(
                codename__in=['view_dashboard', 'send_invite']
            )
            instance.user_permissions.add(*admin_permissions)
        
        elif instance.role == "coach":
            coach_group, _ = Group.objects.get_or_create(name="Coach")
            instance.groups.add(coach_group)
            # Assign coach-specific permissions
            coach_permissions = Permission.objects.filter(
                codename__in ['add_team', 'add_player', 'upload_statistics', 'upload_video', 'view_performance']
            )
            instance.user_permissions.add(*coach_permissions)
        
        elif instance.role == "agent":
            agent_group, _ = Group.objects.get_or_create(name="Agent")
            instance.groups.add(agent_group)
            # Assign agent-specific permissions (view-only)
            agent_permissions = Permission.objects.filter(
                codename__in ['view_team', 'view_player', 'view_performance', 'view_video']
            )
            instance.user_permissions.add(*agent_permissions)
        
        instance.save()







