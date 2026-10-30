from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'so_dien_thoai', 'is_staff']
    list_filter = ['role', 'is_staff', 'is_superuser', 'is_active']

    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin thêm', {'fields': ('role', 'so_dien_thoai')}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin thêm', {'fields': ('role', 'so_dien_thoai')}),
    )