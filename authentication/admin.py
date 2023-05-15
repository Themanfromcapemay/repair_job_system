from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'service_center', 'get_groups')
    list_filter = ('service_center','is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = UserAdmin.fieldsets + (('Service Center', {'fields': ('service_center',)}),)

    def get_groups(self, obj):
        return ", ".join([str(group.name) for group in obj.groups.all()])

    get_groups.short_description = 'Groups'


admin.site.unregister(Group)
admin.site.register(CustomUser, CustomUserAdmin)
