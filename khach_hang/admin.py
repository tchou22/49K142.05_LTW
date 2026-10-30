from django.contrib import admin
from .models import HoiVien

@admin.register(HoiVien)
class HoiVienAdmin(admin.ModelAdmin):
    list_display = ['ma_hoi_vien', 'ho_ten', 'so_dien_thoai', 'goi_dang_su_dung', 'ngay_het_han_goi', 'diem_tich_luy']
    search_fields = ['ma_hoi_vien', 'ho_ten', 'so_dien_thoai', 'email']
    list_filter = ['gioi_tinh', 'goi_dang_su_dung']