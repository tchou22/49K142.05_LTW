from django.urls import path
from . import views

app_name = 'tich_diem'

urlpatterns = [
    path('', views.quan_ly_diem, name='quan_ly_diem'),
    path('doi-diem/<int:hoi_vien_id>/<int:phan_thuong_id>/', views.doi_diem, name='doi_diem'),

    # Hội viên
    path('hoi-vien/', views.diem_tich_luy_hoi_vien, name='diem_tich_luy_hoi_vien'),
    path('hoi-vien/doi-diem/<int:phan_thuong_id>/', views.doi_diem_hoi_vien, name='doi_diem_hoi_vien'),
]