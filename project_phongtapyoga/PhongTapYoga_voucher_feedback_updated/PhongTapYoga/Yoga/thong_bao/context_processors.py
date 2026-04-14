from khach_hang.models import HoiVien
from .models import ThongBaoNhacNho


def thong_bao_context(request):
    so_thong_bao_chua_doc = 0
    ds_thong_bao_dropdown = ThongBaoNhacNho.objects.none()

    if request.user.is_authenticated:
        hoi_vien = HoiVien.objects.filter(
            ma_hoi_vien=request.user.username
        ).first()

        if hoi_vien:
            qs_thong_bao = (
                ThongBaoNhacNho.objects
                .filter(
                    hoi_vien=hoi_vien,
                    kenh_gui='web'
                )
                .select_related('phan_hoi_khieu_nai')
                .order_by('-thoi_gian_gui')
            )

            so_thong_bao_chua_doc = qs_thong_bao.filter(da_doc=False).count()
            ds_thong_bao_dropdown = qs_thong_bao[:10]

    return {
        'so_thong_bao_chua_doc': so_thong_bao_chua_doc,
        'ds_thong_bao_dropdown': ds_thong_bao_dropdown,
    }