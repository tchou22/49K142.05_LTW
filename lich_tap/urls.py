from django.urls import path
from . import views

app_name = 'lich_tap'

urlpatterns = [
    path('', views.danh_sach_lich_hoc, name='danh_sach_lich_hoc'),
    path('them/', views.them_lich_hoc, name='them_lich_hoc'),
    path('sua/<int:id>/', views.sua_lich_hoc, name='sua_lich_hoc'),
    path('xoa/<int:id>/', views.xoa_lich_hoc, name='xoa_lich_hoc'),
    path('dang-ky/<int:hoi_vien_id>/', views.dang_ky_lich_hoc, name='dang_ky_lich_hoc'),

    path('cua-toi/dang-ky/', views.dang_ky_lich_hoc_cua_toi, name='dang_ky_lich_hoc_cua_toi'),
    path('cua-toi/xac-nhan/', views.xac_nhan_dang_ky_lich, name='xac_nhan_dang_ky_lich'),
    path('cua-toi/luu/', views.luu_dang_ky_lich, name='luu_dang_ky_lich'),
]
