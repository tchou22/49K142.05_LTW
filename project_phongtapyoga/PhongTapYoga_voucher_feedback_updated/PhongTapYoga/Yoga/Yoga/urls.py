from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('khach_hang:gioi_thieu_guest')),
    path('admin/', admin.site.urls),
    path('tai-khoan/', include('tai_khoan.urls')),
    path('bao-cao/', include('bao_cao.urls')),
    path('khach-hang/', include('khach_hang.urls')),
    path('goi-tap/', include('goi_tap.urls')),
    path('lich-tap/', include('lich_tap.urls')),
    path('tich-diem/', include('tich_diem.urls')),
    path('cham-soc-khach-hang/', include('cham_soc_khach_hang.urls')),
    path('thong-bao/', include('thong_bao.urls')),
    path("chatbot/", include("chatbot.urls")),
]