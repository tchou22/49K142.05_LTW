from django.urls import path
from . import views

app_name = 'tai_khoan'
urlpatterns = [
    path('dang-nhap/', views.dang_nhap_view, name='dang_nhap'),
    path('dang-xuat/', views.dang_xuat_view, name='dang_xuat'),
    path('doi-mat-khau/', views.doi_mat_khau_view, name='doi_mat_khau'),
]