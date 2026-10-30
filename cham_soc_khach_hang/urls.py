from django.urls import path
from . import views

app_name = 'cham_soc_khach_hang'

urlpatterns = [
    path('gui-yeu-cau-tu-van/', views.gui_yeu_cau_tu_van, name='gui_yeu_cau_tu_van'),
    path('yeu-cau-tu-van/', views.danh_sach_yeu_cau_tu_van, name='danh_sach_yeu_cau_tu_van'),
    path('yeu-cau-tu-van/cap-nhat/<int:id>/', views.cap_nhat_tu_van, name='cap_nhat_tu_van'),

    # Hội viên gửi đánh giá / khiếu nại
    path('danh-gia-khieu-nai/', views.tao_phan_hoi_khieu_nai, name='danh_gia_khieu_nai'),

    # Nhân viên quản lý / xử lý
    path('phan-hoi-khieu-nai/tao/', views.tao_phan_hoi_khieu_nai, name='tao_phan_hoi_khieu_nai'),
    path('phan-hoi-khieu-nai/', views.danh_sach_phan_hoi_khieu_nai, name='danh_sach_phan_hoi_khieu_nai'),
    path('phan-hoi-khieu-nai/cap-nhat/<int:id>/', views.cap_nhat_phan_hoi_khieu_nai, name='cap_nhat_phan_hoi_khieu_nai'),
    path('phan-hoi-khieu-nai/gui-tin-nhan/<int:id>/', views.gui_tin_nhan_nhan_vien, name='gui_tin_nhan_nhan_vien'),

    path('', views.danh_sach_quang_cao, name='danh_sach_quang_cao'),
    path('them/', views.them_quang_cao, name='them_quang_cao'),
    path('xem/<int:id>/', views.xem_quang_cao, name='xem_quang_cao'),
    path('xoa/<int:id>/', views.xoa_quang_cao, name='xoa_quang_cao'),
    path('gui/<int:id>/', views.gui_quang_cao, name='gui_quang_cao'),

    path('uu-dai/', views.danh_sach_uu_dai_hoi_vien, name='danh_sach_uu_dai_hoi_vien'),
    path('uu-dai/luu/<int:id>/', views.luu_ma_uu_dai, name='luu_ma_uu_dai'),
    path('dang-ky-tu-van/', views.dang_ky_tu_van_hoi_vien, name='dang_ky_tu_van_hoi_vien'),

    # Hội viên xem và trao đổi tiếp
    path('hoi-vien/phan-hoi/<int:id>/', views.xem_phan_hoi_hoi_vien, name='xem_phan_hoi_hoi_vien'),
]