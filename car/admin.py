from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Garage

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
    search_fields = ('email', 'username')
    ordering = ('email',)

class GarageAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'location', 'phone', 'approved')
    actions = ['approve_garages', 'reject_garages']

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

    get_username.short_description = 'Username'
    get_email.short_description = 'Email'

    def approve_garages(self, request, queryset):
        queryset.update(approved=True)
        self.message_user(request, "Selected auditoriums have been approved.")

    approve_garages.short_description = 'Approve selected auditoriums'

    def reject_garages(self, request, queryset):
        queryset.update(approved=False)
        self.message_user(request, "Selected garages have been rejected.")

    reject_garages.short_description = 'Reject selected auditoriums'

admin.site.register(User, UserAdmin)
admin.site.register(Garage, GarageAdmin)