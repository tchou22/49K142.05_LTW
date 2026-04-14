from django.db import models
from django.utils import timezone

class GoiTap(models.Model):
    LOAI_CHOICE = [
        ('buoi', 'Theo buổi'),
        ('thang', 'Theo tháng'),
    ]
    TRANG_THAI_CHOICE = [
        ('hoat_dong', 'Hoạt động'),
        ('ngung', 'Ngưng'),
    ]

    ma_goi = models.CharField(max_length=10, unique=True)
    ten_goi = models.CharField(max_length=100)
    loai_goi = models.CharField(max_length=10, choices=LOAI_CHOICE)
    thoi_han_so_buoi = models.IntegerField()
    gia_goi = models.DecimalField(max_digits=12, decimal_places=0)
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICE, default='hoat_dong')
    ghi_chu = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.ten_goi

class DangKyGoiTap(models.Model):
    TRANG_THAI_CHOICES = [
        ('cho_xac_nhan', 'Chờ xác nhận'),
        ('hoat_dong', 'Hoạt động'),
        ('het_han', 'Hết hạn'),
        ('huy', 'Hủy'),
    ]

    hoi_vien = models.ForeignKey('khach_hang.HoiVien', on_delete=models.CASCADE, related_name='ds_dang_ky_goi')
    goi_tap = models.ForeignKey('goi_tap.GoiTap', on_delete=models.CASCADE, related_name='ds_dang_ky')
    ngay_dang_ky = models.DateField(default=timezone.now)
    ngay_bat_dau = models.DateField(default=timezone.now)
    ngay_ket_thuc = models.DateField(null=True, blank=True)
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI_CHOICES, default='hoat_dong')

    def __str__(self):
        return f"{self.hoi_vien.ho_ten} - {self.goi_tap.ten_goi}"

    @property
    def con_hieu_luc(self):
        today = timezone.localdate()
        return self.trang_thai == 'hoat_dong' and (self.ngay_ket_thuc is None or self.ngay_ket_thuc >= today)
