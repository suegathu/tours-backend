from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.db import models

class User(AbstractUser, PermissionsMixin):
    email = models.EmailField(unique=True)

    # Resolve conflicts by specifying related_name
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="custom_user_permissions_set",
        blank=True
    )

    def __str__(self):
        return self.username
