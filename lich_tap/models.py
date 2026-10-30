from django.db import models
from khach_hang.models import HoiVien
from goi_tap.models import GoiTap
from khach_hang.models import HoiVien


class LichHoc(models.Model):
    THU_CHOICES = [
        ('2', 'Thứ 2'),
        ('3', 'Thứ 3'),
        ('4', 'Thứ 4'),
        ('5', 'Thứ 5'),
        ('6', 'Thứ 6'),
        ('7', 'Thứ 7'),
        ('CN', 'Chủ Nhật'),
    ]

    ma_lich = models.CharField(max_length=10, unique=True)
    goi_tap = models.ForeignKey(
        GoiTap,
        on_delete=models.CASCADE,
        related_name='lich_hoc'
    )
    thu = models.CharField(max_length=2, choices=THU_CHOICES)
    gio_bat_dau = models.TimeField()
    gio_ket_thuc = models.TimeField()
    phong = models.CharField(max_length=50)
    hlv_phu_trach = models.CharField(max_length=100)
    so_cho_toi_da = models.IntegerField()
    trang_thai = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.ma_lich} - {self.goi_tap.ten_goi} - {self.get_thu_display()}"


class CheckIn(models.Model):
    hoi_vien = models.ForeignKey(HoiVien, on_delete=models.CASCADE)
    lich_hoc = models.ForeignKey(LichHoc, on_delete=models.SET_NULL, null=True)
    ngay_tap = models.DateField(auto_now_add=True)
    thoi_gian_checkin = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hoi_vien} - {self.lich_hoc}"


class DangKyLichHoc(models.Model):
    hoi_vien = models.ForeignKey(HoiVien, on_delete=models.CASCADE, related_name='dang_ky_lichs')
    lich_hoc = models.ForeignKey(LichHoc, on_delete=models.CASCADE, related_name='hoi_vien_dang_ky')
    ngay_dang_ky = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('hoi_vien', 'lich_hoc')
        verbose_name = 'Đăng ký lịch học'
        verbose_name_plural = 'Đăng ký lịch học'

    def __str__(self):
        return f"{self.hoi_vien} - {self.lich_hoc}"