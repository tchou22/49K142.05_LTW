from django.urls import path
from . import views

app_name = 'goi_tap'

urlpatterns = [
    path('', views.goi_tap, name='goi_tap'),
    path('them/', views.them_goi_tap, name='them_goi_tap'),
    path('sua/<int:id>/', views.sua_goi_tap, name='sua_goi_tap'),
    path('xoa/<int:id>/', views.xoa_goi_tap, name='xoa_goi_tap'),

]