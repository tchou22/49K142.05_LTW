from datetime import date, timedelta
from calendar import monthrange

from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum, Count, Max

from khach_hang.models import HoiVien, LichSuGiaHanGoi, LichSuTap


def tong_quan(request):
    hom_nay = timezone.localdate()

    # ===== LẤY THÁNG / NĂM TỪ BỘ LỌC =====
    thang_raw = request.GET.get('thang')
    nam_raw = request.GET.get('nam')

    co_loc = bool(thang_raw or nam_raw)

    thang = None
    nam = None
    dau_thang = None
    cuoi_thang = None

    if co_loc:
        try:
            thang = int(thang_raw) if thang_raw else hom_nay.month
            nam = int(nam_raw) if nam_raw else hom_nay.year

            if not 1 <= thang <= 12:
                thang = hom_nay.month

            dau_thang = date(nam, thang, 1)
            ngay_cuoi_thang = monthrange(nam, thang)[1]
            cuoi_thang = date(nam, thang, ngay_cuoi_thang)
        except ValueError:
            co_loc = False
            thang = None
            nam = None

    moc_14_ngay = hom_nay - timedelta(days=14)
    moc_7_ngay = hom_nay + timedelta(days=7)

    # ===== HỘI VIÊN =====
    ds_hv = HoiVien.objects.all().order_by('-id')
    total_hoi_vien = ds_hv.count()
    goi_con_han = ds_hv.filter(ngay_het_han_goi__gte=hom_nay).count()

    if co_loc:
        ds_hoi_vien_loc = ds_hv.filter(
            ngay_tao__date__gte=dau_thang,
            ngay_tao__date__lte=cuoi_thang
        )
        hoi_vien_moi = ds_hoi_vien_loc.count()
    else:
        ds_hoi_vien_loc = ds_hv
        hoi_vien_moi = 0

    # ===== DOANH THU =====
    ds_giao_dich = LichSuGiaHanGoi.objects.all().order_by('-ngay_tao')

    if co_loc:
        ds_doanh_thu_loc = ds_giao_dich.filter(
            ngay_tao__date__gte=dau_thang,
            ngay_tao__date__lte=cuoi_thang
        )
        tong_doanh_thu = ds_doanh_thu_loc.aggregate(
            t=Sum('tong_thanh_toan')
        )['t'] or 0
        doanh_thu_moi = tong_doanh_thu
    else:
        ds_doanh_thu_loc = ds_giao_dich
        tong_doanh_thu = ds_giao_dich.aggregate(
            t=Sum('tong_thanh_toan')
        )['t'] or 0
        doanh_thu_moi = tong_doanh_thu

    doanh_thu_gia_han = doanh_thu_moi

    # ===== TẦN SUẤT TẬP =====
    ds_tap = LichSuTap.objects.all()

    if co_loc:
        ds_tap_loc = ds_tap.filter(
            thoi_gian__date__gte=dau_thang,
            thoi_gian__date__lte=cuoi_thang
        )
    else:
        ds_tap_loc = ds_tap

    tong_checkin = ds_tap_loc.count()
    trung_binh_checkin = round(tong_checkin / total_hoi_vien, 1) if total_hoi_vien else 0

    so_hv_da_tap = ds_tap_loc.values('hoi_vien').distinct().count()
    ty_le_tham_gia = round((so_hv_da_tap / total_hoi_vien) * 100, 1) if total_hoi_vien else 0

    ds_tan_suat = (
        ds_tap_loc.values('hoi_vien', 'hoi_vien__ho_ten')
        .annotate(
            so_buoi=Count('id'),
            lan_cuoi=Max('thoi_gian')
        )
        .order_by('-so_buoi')[:10]
    )

    # ===== NGUY CƠ BỎ TẬP =====
    ds_nguy_co = []
    for hv in ds_hv:
        muc_do = 'Bình thường'

        lan_cuoi = hv.check_in_cuoi.date() if hv.check_in_cuoi else None
        han_goi = hv.ngay_het_han_goi

        if lan_cuoi and lan_cuoi <= moc_14_ngay:
            muc_do = 'Rất cao'
        elif han_goi and han_goi <= moc_7_ngay:
            muc_do = 'Sắp hết hạn'
        elif lan_cuoi and lan_cuoi <= hom_nay - timedelta(days=7):
            muc_do = 'Trung bình'

        if muc_do != 'Bình thường':
            ds_nguy_co.append({
                'ho_ten': hv.ho_ten,
                'so_dien_thoai': hv.so_dien_thoai,
                'lan_cuoi': hv.check_in_cuoi,
                'han_goi': hv.ngay_het_han_goi,
                'muc_do': muc_do,
            })

    nguy_co_cao = len([x for x in ds_nguy_co if x['muc_do'] == 'Rất cao'])
    vang_hon_14_ngay = len([x for x in ds_nguy_co if x['muc_do'] == 'Rất cao'])
    sap_het_han_7_ngay = len([x for x in ds_nguy_co if x['muc_do'] == 'Sắp hết hạn'])

    context = {
        'thang': thang,
        'nam': nam,
        'co_loc': co_loc,
        'ds_thang': range(1, 13),
        'ds_nam': range(hom_nay.year - 5, hom_nay.year + 2),

        'total_hoi_vien': total_hoi_vien,
        'hoi_vien_moi': hoi_vien_moi,
        'goi_con_han': goi_con_han,

        'tong_doanh_thu': tong_doanh_thu,
        'doanh_thu_moi': doanh_thu_moi,
        'doanh_thu_gia_han': doanh_thu_gia_han,

        'tong_checkin': tong_checkin,
        'trung_binh_checkin': trung_binh_checkin,
        'ty_le_tham_gia': ty_le_tham_gia,

        'nguy_co_cao': nguy_co_cao,
        'vang_hon_14_ngay': vang_hon_14_ngay,
        'sap_het_han_7_ngay': sap_het_han_7_ngay,

        'ds_hoi_vien': ds_hoi_vien_loc[:10],
        'ds_doanh_thu': ds_doanh_thu_loc[:10],
        'ds_tan_suat': ds_tan_suat,
        'ds_nguy_co': ds_nguy_co[:10],
    }
    return render(request, 'bao_cao/tong_quan.html', context)