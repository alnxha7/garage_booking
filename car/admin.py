from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Garage
from django.db import IntegrityError

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
        ('Personal info', {'fields': ('role',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active', 'is_superuser')
    actions = ['delete_users']
    search_fields = ('email', 'username')
    ordering = ('email',)

    def delete_users(self, request, queryset):
        try:
            # Delete the selected garages
            queryset.delete()
            self.message_user(request, "Selected users have been deleted.")
        except IntegrityError as e:
            self.message_error(request, f"An error occurred while deleting users: {e}")

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Remove the 'delete_selected' action
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


class GarageAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'location', 'phone', 'approved')
    actions = ['approve_garages', 'reject_garages', 'delete_garages']

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

    get_username.short_description = 'Username'
    get_email.short_description = 'Email'

    def approve_garages(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected garages have been approved.")

    def reject_garages(self, request, queryset):
        queryset.update(approved=False)
        self.message_user(request, "Selected garages have been rejected.")

    def delete_garages(self, request, queryset):
        try:
            # Delete the selected garages
            queryset.delete()
            self.message_user(request, "Selected garages have been deleted.")
        except IntegrityError as e:
            self.message_error(request, f"An error occurred while deleting garages: {e}")

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Remove the 'delete_selected' action
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions


admin.site.register(User, UserAdmin)
admin.site.register(Garage, GarageAdmin)