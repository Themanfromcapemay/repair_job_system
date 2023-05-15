# signals.py
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_groups(sender, **kwargs):
    # Check if the migration is related to the 'system_api' app (replace 'system_api' with your app's name)
    if sender.name == 'system_api':
        # Create Admin group
        admin_group, created = Group.objects.get_or_create(name='Admins')
        if created:
            # Assign required permissions
            admin_permissions = [
                Permission.objects.get(codename='add_jobcard'),
                Permission.objects.get(codename='change_jobcard'),
                Permission.objects.get(codename='delete_jobcard'),
                Permission.objects.get(codename='view_jobcard'),
            ]
            admin_group.permissions.set(admin_permissions)
            admin_group.save()

        # Create Technician group
        tech_group, created = Group.objects.get_or_create(name='Technicians')
        if created:
            # Assign required permissions
            tech_permissions = [
                Permission.objects.get(codename='view_jobcard'),
                Permission.objects.get(codename='change_jobcard'),  # Needed to update technician_assessment
            ]
            tech_group.permissions.set(tech_permissions)
            tech_group.save()
