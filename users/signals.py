from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import User
@receiver(post_save, sender=User)
def assign_user_permissions(sender, instance, created, **kwargs):
    print("*****************************************")
    if created:
        print("########################")
        # Get the content type for the User model
        user_content_type = ContentType.objects.get_for_model(User)
        if instance.role=="Admin":
            # Add the superuser to the admin group
            admin_group, _ = Group.objects.get_or_create(name="Admin")
            instance.groups.add(admin_group)
            # Assign admin permissions
            admin_permissions = Permission.objects.filter(
                codename__in=['view_dashboard', 'edit_questions', 'view_users', 'view_children', 'delete_children', 'restrict_users']
            )
            instance.user_permissions.add(*admin_permissions)
            print(f"Admin permissions assigned: {admin_permissions}")
        elif instance.role == "parent":
            # Assign parent group and permissions
            parent_group, _ = Group.objects.get_or_create(name="Parent")
            instance.groups.add(parent_group)
            parent_permissions = Permission.objects.filter(
                codename__in=[
                    'can_add_child', 'can_view_resources', 'can_view_milestones',
                    'can_view_assessment', 'can_view_results', 'can_logout',
                    'can_create_account', 'can_login', 'view_children'
                ]
            )
            print(f"!!!!!!!!!!!!!!!!!!!{parent_permissions}!!!!!!!!!!!!!!!!!!!111")
            instance.user_permissions.add(*parent_permissions)
            print(f"Parent permissions assigned: {parent_permissions}")
        else:
            # Default group for regular users
            default_group, _ = Group.objects.get_or_create(name="Default User")
            instance.groups.add(default_group)
            default_permissions = Permission.objects.filter(
                content_type=user_content_type,
                codename="view_dashboard"
            )
            instance.user_permissions.add(*default_permissions)
            print(f"Default permissions assigned: {default_permissions}")
        instance.save()
        print(f"User: {instance}")
        print(f"Role: {instance.role}")
        print(f"Groups: {instance.groups.all()}")
        print(f"Permissions: {instance.user_permissions.all()}")