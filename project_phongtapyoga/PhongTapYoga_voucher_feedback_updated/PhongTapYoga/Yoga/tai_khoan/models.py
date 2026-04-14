from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('chu', 'Chủ trung tâm'),
        ('nhan_vien', 'Nhân viên'),
        ('hoi_vien', 'Hội viên'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='hoi_vien')
    so_dien_thoai = models.CharField(max_length=10, unique=True, null=True, blank=True)

    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="tai_khoan_user_groups",
        related_query_name="user",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="tai_khoan_user_permissions",
        related_query_name="user",
    )
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"