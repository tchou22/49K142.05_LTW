from django.db import models
from django.utils import timezone

class KhachHang(models.Model):
    GIOI_TINH_CHOICE = [
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ'),
        ('Khác', 'Khác'),
    ]

    TRANG_THAI_CHOICE = [
        ('moi', 'Khách mới'),
        ('da_chuyen_hoi_vien', 'Đã chuyển thành hội viên'),
    ]

    ma_khach_hang = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Mã khách hàng"
    )
    ho_ten = models.CharField(
        max_length=255,
        verbose_name="Họ và tên"
    )
    ngay_sinh = models.DateField(
        null=True,
        blank=True,
        verbose_name="Ngày sinh"
    )
    gioi_tinh = models.CharField(
        max_length=10,
        choices=GIOI_TINH_CHOICE,
        null=True,
        blank=True,
        verbose_name="Giới tính"
    )
    so_dien_thoai = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Số điện thoại"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email"
    )
    dia_chi = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Địa chỉ"
    )

    tinh_trang_suc_khoe = models.TextField(
        blank=True,
        verbose_name="Tình trạng sức khỏe / Bệnh lý"
    )
    muc_tieu_tap_luyen = models.TextField(
        blank=True,
        verbose_name="Mục tiêu tập luyện"
    )
    ghi_chu_nhan_vien = models.TextField(
        blank=True,
        verbose_name="Ghi chú nội bộ"
    )

    trang_thai = models.CharField(
        max_length=30,
        choices=TRANG_THAI_CHOICE,
        default='moi',
        verbose_name="Trạng thái"
    )

    ngay_tao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )

    def __str__(self):
        return f"{self.ho_ten} ({self.ma_khach_hang})"


class HoiVien(models.Model):
    GIOI_TINH_CHOICE = [
        ('Nam', 'Nam'),
        ('Nữ', 'Nữ'),
        ('Khác', 'Khác')
    ]

    ma_hoi_vien = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        verbose_name="Mã hội viên"
    )
    ho_ten = models.CharField(
        max_length=255,
        verbose_name="Họ và tên"
    )
    ngay_sinh = models.DateField(
        verbose_name="Ngày sinh"
    )
    gioi_tinh = models.CharField(
        max_length=10,
        choices=GIOI_TINH_CHOICE
    )
    so_dien_thoai = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Số điện thoại"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        verbose_name="Email"
    )

    tinh_trang_suc_khoe = models.TextField(
        blank=True,
        verbose_name="Tình trạng sức khỏe / Bệnh lý"
    )
    muc_tieu_tap_luyen = models.TextField(
        blank=True,
        verbose_name="Mục tiêu tập luyện"
    )
    ghi_chu_nhan_vien = models.TextField(
        blank=True,
        verbose_name="Ghi chú nội bộ"
    )

    chieu_cao = models.FloatField(
        help_text="cm",
        null=True,
        blank=True
    )
    can_nang = models.FloatField(
        help_text="kg",
        null=True,
        blank=True
    )
    body_fat = models.FloatField(
        help_text="%",
        null=True,
        blank=True
    )

    goi_dang_su_dung = models.ForeignKey(
        'goi_tap.GoiTap', # ĐÃ SỬA THÀNH CHUỖI
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    ngay_het_han_goi = models.DateField(
        null=True,
        blank=True
    )
    diem_tich_luy = models.IntegerField(
        default=0
    )
    check_in_cuoi = models.DateTimeField(
        null=True,
        blank=True
    )

    ngay_tao = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Ngày tạo"
    )

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new and not self.ma_hoi_vien:
            self.ma_hoi_vien = f"HV{self.pk:03d}"
            super().save(update_fields=['ma_hoi_vien'])

    def __str__(self):
        return f"{self.ho_ten} ({self.ma_hoi_vien})"

class LichSuGiaHanGoi(models.Model):
    hoi_vien = models.ForeignKey(
        HoiVien,
        on_delete=models.CASCADE,
        related_name='lich_su_gia_han'
    )
    goi_cu = models.ForeignKey(
        'goi_tap.GoiTap', # ĐÃ SỬA THÀNH CHUỖI
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gia_han_goi_cu'
    )
    goi_moi = models.ForeignKey(
        'goi_tap.GoiTap', # ĐÃ SỬA THÀNH CHUỖI
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gia_han_goi_moi'
    )
    ngay_bat_dau = models.DateField()
    ngay_het_han_moi = models.DateField()
    gia_goi = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    khuyen_mai = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    tong_thanh_toan = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hoi_vien.ho_ten} - {self.goi_moi}"


class HuanLuyenVien(models.Model):
    ho_ten = models.CharField(max_length=255)

    def __str__(self):
        return self.ho_ten


class PhongTap(models.Model):
    ten_phong = models.CharField(max_length=100)

    def __str__(self):
        return self.ten_phong


class LopTap(models.Model):
    ten_lop = models.CharField(max_length=255)
    huan_luyen_vien = models.ForeignKey(
        HuanLuyenVien,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    phong_tap = models.ForeignKey(
        PhongTap,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.ten_lop


class LichSuTap(models.Model):
    TRANG_THAI_CHOICES = [
        ('checkin', 'Check-in'),
        ('da_tap', 'Đã tập luyện'),
        ('vang', 'Vắng mặt'),
    ]

    hoi_vien = models.ForeignKey(
        HoiVien,
        on_delete=models.CASCADE,
        related_name='lich_su_tap'
    )
    lop_tap = models.ForeignKey(
        LopTap,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    thoi_gian = models.DateTimeField()
    trang_thai = models.CharField(
        max_length=20,
        choices=TRANG_THAI_CHOICES,
        default='checkin'
    )
    diem_cong = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.hoi_vien.ho_ten} - {self.thoi_gian}"