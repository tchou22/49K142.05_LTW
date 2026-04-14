from django.db import models
from django.utils import timezone
from khach_hang.models import HoiVien
from lich_tap.models import DangKyLichHoc


class ThongBaoNhacNho(models.Model):
    KENH_GUI = [
        ('web', 'Thông báo web'),
        ('email', 'Email'),
    ]

    LOAI_THONG_BAO = [
        ('nhac_lich', 'Nhắc lịch học'),
        ('phan_hoi_khieu_nai', 'Phản hồi góp ý / khiếu nại'),
        ('quang_cao', 'Quảng cáo / ưu đãi'),
        ('he_thong', 'Hệ thống'),
    ]

    hoi_vien = models.ForeignKey(
        HoiVien,
        on_delete=models.CASCADE,
        related_name='thong_bao_nhac_nho'
    )

    dang_ky_lich = models.ForeignKey(
        DangKyLichHoc,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='thong_bao_nhac_nho'
    )

    # Liên kết tới phản hồi/khiếu nại để bấm vào chuông có thể mở đúng nội dung
    # Đổi 'cham_soc_khach_hang' thành tên app thật của bạn nếu khác
    phan_hoi_khieu_nai = models.ForeignKey(
        'cham_soc_khach_hang.KhieuNaiPhanHoi',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='thong_bao_gui_hoi_vien'
    )

    loai_thong_bao = models.CharField(
        max_length=30,
        choices=LOAI_THONG_BAO,
        default='he_thong'
    )

    tieu_de = models.CharField(max_length=255, blank=True)
    noi_dung = models.TextField()
    kenh_gui = models.CharField(
        max_length=20,
        choices=KENH_GUI,
        default='web'
    )
    thoi_gian_gui = models.DateTimeField(default=timezone.now)
    da_doc = models.BooleanField(default=False)

    class Meta:
        ordering = ['-thoi_gian_gui']

    def __str__(self):
        return f"{self.hoi_vien.ho_ten} - {self.get_loai_thong_bao_display()} - {self.thoi_gian_gui:%d/%m/%Y %H:%M}"