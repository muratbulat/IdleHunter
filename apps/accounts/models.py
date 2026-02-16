# Accounts: roles and user profiles for RBAC
from django.conf import settings
from django.db import models


class Role(models.Model):
    """Role for RBAC. Permissions are checked by role name in decorators."""

    class RoleName(models.TextChoices):
        VIEWER = "viewer", "Viewer"
        OPERATOR = "operator", "Operator"
        ADMIN = "admin", "Admin"

    name = models.CharField(
        max_length=20, choices=RoleName.choices, unique=True, db_index=True
    )
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.get_name_display()

    def has_perm(self, perm_name: str) -> bool:
        """Check if this role has the given permission (by name)."""
        return perm_name in self._permission_map().get(self.name, [])

    @classmethod
    def _permission_map(cls):
        """Map role name -> list of permission codenames."""
        return {
            cls.RoleName.VIEWER: ["view_dashboard", "view_datasource", "view_vm", "view_scanrun"],
            cls.RoleName.OPERATOR: [
                "view_dashboard", "view_datasource", "view_vm", "view_scanrun",
                "run_scan", "view_idle_score",
            ],
            cls.RoleName.ADMIN: [
                "view_dashboard", "view_datasource", "view_vm", "view_scanrun",
                "run_scan", "view_idle_score",
                "manage_datasource", "manage_users",
            ],
        }


class UserProfile(models.Model):
    """Extended profile for User: links to Role for RBAC."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, related_name="profiles", null=True, blank=True
    )

    class Meta:
        verbose_name = "User profile"
        verbose_name_plural = "User profiles"

    def __str__(self):
        return f"{self.user.username} ({self.role.name if self.role else 'no role'})"

    def has_perm(self, perm_name: str) -> bool:
        if self.role:
            return self.role.has_perm(perm_name)
        return False
