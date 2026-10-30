from django.db import models


class TuVan(models.Model):
    sdt = models.CharField(max_length=11, blank=True, default="unknown")
    noi_dung = models.TextField()
    trang_thai = models.CharField(max_length=50, default="Mới")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tư vấn - {self.sdt} - {self.trang_thai}"


class KhieuNai(models.Model):
    noi_dung = models.TextField()
    trang_thai = models.CharField(max_length=50, default="Mới")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Khiếu nại - {self.trang_thai}"