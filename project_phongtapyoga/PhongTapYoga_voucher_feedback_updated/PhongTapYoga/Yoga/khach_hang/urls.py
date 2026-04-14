from django.urls import path
from . import views

app_name = 'khach_hang'

urlpatterns = [
    # KHÁCH HÀNG
    path('', views.danh_sach_khach_hang, name='danh_sach_khach_hang'),
    path('them/', views.them_khach_hang, name='them_khach_hang'),
    path('sua/<int:id>/', views.sua_khach_hang, name='sua_khach_hang'),
    path('xoa/<int:id>/', views.xoa_khach_hang, name='xoa_khach_hang'),

    # HỘI VIÊN (CHỈ GIỮ 1 DÒNG NÀY)
    path('hoi-vien/', views.quan_ly_hoi_vien, name='danh_sach_hoi_vien'),

    path('hoi-vien/them/', views.them_hoi_vien, name='them_hoi_vien'),
    path('hoi-vien/chi-tiet/<int:id>/', views.chi_tiet_hoi_vien, name='chi_tiet_hoi_vien'),
    path('hoi-vien/sua/<int:id>/', views.sua_hoi_vien, name='sua_hoi_vien'),
    path('hoi-vien/xoa/<int:id>/', views.xoa_hoi_vien, name='xoa_hoi_vien'),
    path('hoi-vien/check-in/<int:id>/', views.check_in_hoi_vien, name='check_in_hoi_vien'),

    # CHUYỂN KHÁCH HÀNG -> HỘI VIÊN
    path('chuyen-thanh-hoi-vien/<int:id>/', views.chuyen_thanh_hoi_vien, name='chuyen_thanh_hoi_vien'),

    # Cho khách hàng trang tổng quan của khách hàng
    path('gioi-thieu/', views.gioi_thieu_guest, name='gioi_thieu_guest'),
    path('goi-tap/', views.goi_tap_guest, name='goi_tap_guest'),
    path('lich-tap/', views.lich_tap_guest, name='lich_tap_guest'),
    path('uu-dai/', views.uu_dai_guest, name='uu_dai_guest'),
    path('dang-ky-tu-van/', views.dang_ky_tu_van_guest, name='dang_ky_tu_van_guest'),

    # Cho hội viên
    path('hoi-vien/gioi-thieu/', views.gioi_thieu_hoi_vien, name='gioi_thieu_hoi_vien'),
    path('hoi-vien/goi-tap/', views.goi_tap_hoi_vien, name='goi_tap_hoi_vien'),
    path('hoi-vien/goi-tap/dang-ky/<int:goi_id>/', views.dang_ky_goi_tap, name='dang_ky_goi_tap'),

]