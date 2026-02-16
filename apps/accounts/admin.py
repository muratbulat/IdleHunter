from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

from .models import Role, UserProfile

User = get_user_model()


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"


class UserAdminWithProfile(BaseUserAdmin):
    inlines = (UserProfileInline,)


# Re-register User with inline profile
admin.site.unregister(User)
admin.site.register(User, UserAdminWithProfile)
