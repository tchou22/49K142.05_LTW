from django.db import models
from khach_hang.models import HoiVien
from django.utils import timezone

from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from khach_hang.models import HoiVien


class KhieuNaiPhanHoi(models.Model):
    CHU_DE = [
        ('chat_luong_dich_vu', 'Chất lượng dịch vụ'),
        ('thai_do_nhan_vien', 'Thái độ nhân viên'),
        ('co_so_vat_chat', 'Cơ sở vật chất'),
        ('van_de_khac', 'Vấn đề khác'),
    ]

    TRANG_THAI = [
        ('moi_tiep_nhan', 'Mới tiếp nhận'),
        ('dang_trao_doi', 'Đang trao đổi'),
        ('da_xu_ly', 'Đã xử lý'),
        ('da_dong', 'Đã đóng'),
    ]

    hoi_vien = models.ForeignKey(
        HoiVien,
        on_delete=models.CASCADE,
        related_name='danh_sach_phan_hoi_khieu_nai'
    )

    chu_de = models.CharField(max_length=30, choices=CHU_DE)

    mo_ta_van_de_khac = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    noi_dung_khach = models.TextField()
    tra_loi_nhan_vien = models.TextField(blank=True, null=True)

    ngay_gui = models.DateTimeField(auto_now_add=True)
    ngay_phan_hoi = models.DateTimeField(blank=True, null=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    trang_thai = models.CharField(
        max_length=20,
        choices=TRANG_THAI,
        default='moi_tiep_nhan'
    )

    def clean(self):
        if self.chu_de == 'van_de_khac' and not (self.mo_ta_van_de_khac or '').strip():
            raise ValidationError({
                'mo_ta_van_de_khac': 'Vui lòng nhập mô tả cho mục Vấn đề khác.'
            })

    def __str__(self):
        return f"{self.hoi_vien.ho_ten} - {self.get_chu_de_display()}"

class TinNhanKhieuNai(models.Model):
    NGUOI_GUI = [
        ('hoi_vien', 'Hội viên'),
        ('nhan_vien', 'Nhân viên'),
    ]

    khieu_nai = models.ForeignKey(
        KhieuNaiPhanHoi,
        on_delete=models.CASCADE,
        related_name='ds_tin_nhan'
    )

    nguoi_gui = models.CharField(max_length=20, choices=NGUOI_GUI)
    noi_dung = models.TextField()
    thoi_gian_gui = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.khieu_nai.id} - {self.nguoi_gui} - {self.thoi_gian_gui:%d/%m/%Y %H:%M}"


class YeuCauTuVan(models.Model):
    TRANG_THAI = [
        ('moi', 'Mới tiếp nhận'),
        ('dang', 'Đang tư vấn'),
        ('hen', 'Hẹn tập thử'),
        ('xong', 'Thành công'),
    ]

    ma_yeu_cau = models.CharField(max_length=20, unique=True, blank=True)
    ho_ten = models.CharField(max_length=100)
    so_dien_thoai = models.CharField(max_length=11)
    email = models.EmailField(blank=True, null=True)
    dich_vu_quan_tam = models.CharField(max_length=100, blank=True, null=True)
    noi_dung = models.TextField()
    ngay_gui = models.DateTimeField(auto_now_add=True)
    ngay_cap_nhat = models.DateTimeField(auto_now=True)

    trang_thai = models.CharField(max_length=10, choices=TRANG_THAI, default='moi')
    ghi_chu_tu_van = models.TextField(blank=True, null=True)
    hen_lien_he_lai = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.ma_yeu_cau:
            last_record = YeuCauTuVan.objects.order_by('-id').first()
            next_id = 1 if not last_record else last_record.id + 1
            self.ma_yeu_cau = f"YC{next_id:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ma_yeu_cau} - {self.ho_ten}"

class QuangCao(models.Model):
    TRANG_THAI = [
        ('dang_ap_dung', 'Đang áp dụng'),
        ('sap_dien_ra', 'Sắp diễn ra'),
        ('da_het_han', 'Đã hết hạn'),
    ]

    ten_chuong_trinh = models.CharField(max_length=200)
    noi_dung = models.TextField()
    la_voucher = models.BooleanField(default=False)
    ma_uu_dai = models.CharField(max_length=50, blank=True, null=True)
    gia_tri_giam = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    ngay_bat_dau = models.DateField()
    ngay_ket_thuc = models.DateField()
    trang_thai = models.CharField(
        max_length=20,
        choices=TRANG_THAI,
        default='sap_dien_ra'
    )
    da_gui = models.BooleanField(default=False)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def cap_nhat_trang_thai(self):
        today = timezone.localdate()
        if self.ngay_ket_thuc < today:
            self.trang_thai = 'da_het_han'
        elif self.ngay_bat_dau > today:
            self.trang_thai = 'sap_dien_ra'
        else:
            self.trang_thai = 'dang_ap_dung'

    def save(self, *args, **kwargs):
        self.cap_nhat_trang_thai()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.ten_chuong_trinh

# ƯU đãi cho hội viên

class MaUuDaiHoiVien(models.Model):
    TRANG_THAI = [
        ('da_luu', 'Đã lưu'),
        ('da_su_dung', 'Đã sử dụng'),
        ('het_han', 'Hết hạn'),
    ]

    hoi_vien = models.ForeignKey(HoiVien, on_delete=models.CASCADE, related_name='ma_uu_dai_da_luu')
    quang_cao = models.ForeignKey(QuangCao, on_delete=models.CASCADE, related_name='hoi_vien_da_luu')
    ngay_luu = models.DateTimeField(auto_now_add=True)
    trang_thai = models.CharField(max_length=20, choices=TRANG_THAI, default='da_luu')

    class Meta:
        unique_together = ('hoi_vien', 'quang_cao')

    def __str__(self):
        return f"{self.hoi_vien} - {self.quang_cao.ten_chuong_trinh}"