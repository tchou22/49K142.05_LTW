from django.db import models
from khach_hang.models import HoiVien
from django.utils import timezone


class LichSuDiem(models.Model):
    LOAI_GD = [('cong', 'Tích điểm'), ('tru', 'Đổi điểm')]
    hoi_vien = models.ForeignKey(HoiVien, on_delete=models.CASCADE)
    loai_giao_dich = models.CharField(max_length=10, choices=LOAI_GD)
    so_diem = models.IntegerField()
    noi_dung = models.CharField(max_length=255)
    ngay_thuc_hien = models.DateTimeField(auto_now_add=True)


class PhanThuong(models.Model):
    ten_qua = models.CharField(max_length=100)
    diem_yeu_cau = models.IntegerField()
    so_luong_con = models.IntegerField(default=0)

    def __str__(self):
        return self.ten_qua


class VoucherHoiVien(models.Model):
    TRANG_THAI = [
        ('chua_su_dung', 'Chưa sử dụng'),
        ('da_su_dung', 'Đã sử dụng'),
        ('het_han', 'Hết hạn'),
    ]

    hoi_vien = models.ForeignKey(
        HoiVien,
        on_delete=models.CASCADE,
        related_name='voucher_doi_diem'
    )
    phan_thuong = models.ForeignKey(
        PhanThuong,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ma_voucher = models.CharField(max_length=50, unique=True)
    ten_voucher = models.CharField(max_length=255)
    gia_tri_giam = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    diem_da_doi = models.IntegerField(default=0)
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI, default='chua_su_dung')
    ngay_tao = models.DateTimeField(auto_now_add=True)
    ngay_het_han = models.DateField(null=True, blank=True)
    ngay_su_dung = models.DateTimeField(null=True, blank=True)

    def het_han_thuc_te(self):
        return self.ngay_het_han and self.ngay_het_han < timezone.localdate()

    def __str__(self):
        return f"{self.ma_voucher} - {self.ten_voucher}"
