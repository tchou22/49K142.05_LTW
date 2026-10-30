from django.urls import path
from . import views

app_name = 'thong_bao'

urlpatterns = [
    path('thong-bao/', views.quan_ly_thong_bao, name='quan_ly_thong_bao'),
# hội viên
    path('danh-sach/', views.danh_sach_thong_bao, name='danh_sach_thong_bao'),
    path('danh-dau-da-doc/<int:thong_bao_id>/', views.danh_dau_da_doc, name='danh_dau_da_doc'),
    path('mo/<int:id>/', views.mo_thong_bao, name='mo_thong_bao'),
    path('mo/<int:id>/', views.mo_thong_bao, name='mo_thong_bao'),
]