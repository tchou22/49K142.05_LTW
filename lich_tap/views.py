from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import LichHocForm
from .models import LichHoc, DangKyLichHoc
from .forms import DangKyLichHocForm
from khach_hang.models import HoiVien
from goi_tap.models import DangKyGoiTap
from django.db import transaction
from khach_hang.views import lay_hoi_vien_tu_user, _goi_tap_con_han, _xoa_toan_bo_dang_ky_lich, _dong_bo_dang_ky_lich_theo_trang_thai_goi

def tao_ma_lich_tu_dong():
    lich_cuoi = LichHoc.objects.order_by('-id').first()
    if not lich_cuoi:
        return 'LT001'
    try:
        so = int(lich_cuoi.ma_lich.replace('LT', '')) + 1
    except:
        so = 1
    return f'LT{so:03d}'

def danh_sach_lich_hoc(request):
    q = request.GET.get('q', '')
    thu = request.GET.get('thu', '')
    trang_thai = request.GET.get('trang_thai', '')
    thu_choices = [
        ('2', 'Thứ 2'),
        ('3', 'Thứ 3'),
        ('4', 'Thứ 4'),
        ('5', 'Thứ 5'),
        ('6', 'Thứ 6'),
        ('7', 'Thứ 7'),
        ('CN', 'Chủ nhật'),
    ]

    ds_lich = LichHoc.objects.all()

    if q:
        ds_lich = ds_lich.filter(ma_lich__icontains=q)

    if thu:
        ds_lich = ds_lich.filter(thu=thu)

    if trang_thai:
        if trang_thai == 'True':
            ds_lich = ds_lich.filter(trang_thai=True)
        elif trang_thai == 'False':
            ds_lich = ds_lich.filter(trang_thai=False)

    ds_lich = ds_lich.order_by('hlv_phu_trach', 'gio_bat_dau')
    lich_gom = {}

    for lich in ds_lich:
        key = (
            lich.goi_tap_id if lich.goi_tap else None,
            lich.hlv_phu_trach,
            lich.gio_bat_dau,
            lich.gio_ket_thuc,
            lich.phong,
            lich.so_cho_toi_da,
            lich.trang_thai,
        )

        if key not in lich_gom:
            lich_gom[key] = {
                'id': lich.id,
                'ma_lich': lich.ma_lich,
                'goi_tap': lich.goi_tap,
                'ds_thu': [lich.get_thu_display() if hasattr(lich, 'get_thu_display') else lich.thu],
                'gio_bat_dau': lich.gio_bat_dau,
                'gio_ket_thuc': lich.gio_ket_thuc,
                'phong': lich.phong,
                'hlv_phu_trach': lich.hlv_phu_trach,
                'so_cho_toi_da': lich.so_cho_toi_da,
                'trang_thai': lich.trang_thai,
            }
        else:
            ten_thu = lich.get_thu_display() if hasattr(lich, 'get_thu_display') else lich.thu
            if ten_thu not in lich_gom[key]['ds_thu']:
                lich_gom[key]['ds_thu'].append(ten_thu)

    lich_hoc_list = list(lich_gom.values())

    return render(request, 'lich_tap/danh_sach_lich_hoc.html', {
        'lich_hoc_list': lich_hoc_list,
        'q': q,
        'thu': thu,
        'trang_thai': trang_thai,
        'thu_choices': thu_choices,
    })

def them_lich_hoc(request):
    if request.method == 'POST':
        form = LichHocForm(request.POST)
        if form.is_valid():
            goi_tap = form.cleaned_data['goi_tap']
            thu_list = form.cleaned_data['thu']
            gio_bat_dau = form.cleaned_data['gio_bat_dau']
            gio_ket_thuc = form.cleaned_data['gio_ket_thuc']
            phong = form.cleaned_data['phong']
            hlv_phu_trach = form.cleaned_data['hlv_phu_trach']
            so_cho_toi_da = form.cleaned_data['so_cho_toi_da']
            for thu in thu_list:
                LichHoc.objects.create(
                    ma_lich=tao_ma_lich_tu_dong(),
                    goi_tap=goi_tap,
                    thu=thu,
                    gio_bat_dau=gio_bat_dau,
                    gio_ket_thuc=gio_ket_thuc,
                    phong=phong,
                    hlv_phu_trach=hlv_phu_trach,
                    so_cho_toi_da=so_cho_toi_da,
                    trang_thai=True
                )

            messages.success(request, 'Thêm lịch tập theo tuần thành công.')
            return redirect('lich_tap:danh_sach_lich_hoc')
        else:
            print(form.errors)
    else:
        form = LichHocForm()

    return render(request, 'lich_tap/them_lich_hoc.html', {
        'form': form
    })


def sua_lich_hoc(request, id):
    lich_hoc = get_object_or_404(LichHoc, id=id)
    if request.method == 'POST':
        form = LichHocForm(request.POST)
        if form.is_valid():
            lich_hoc.goi_tap = form.cleaned_data['goi_tap']

            thu_list = form.cleaned_data['thu']
            if thu_list:
                lich_hoc.thu = thu_list[0]

            lich_hoc.gio_bat_dau = form.cleaned_data['gio_bat_dau']
            lich_hoc.gio_ket_thuc = form.cleaned_data['gio_ket_thuc']
            lich_hoc.phong = form.cleaned_data['phong']
            lich_hoc.hlv_phu_trach = form.cleaned_data['hlv_phu_trach']
            lich_hoc.so_cho_toi_da = form.cleaned_data['so_cho_toi_da']
            lich_hoc.save()

            messages.success(request, 'Cập nhật lịch học thành công.')
            return redirect('lich_tap:danh_sach_lich_hoc')
    else:
        form = LichHocForm(initial={
            'goi_tap': lich_hoc.goi_tap,
            'thu': [lich_hoc.thu],
            'gio_bat_dau': lich_hoc.gio_bat_dau,
            'gio_ket_thuc': lich_hoc.gio_ket_thuc,
            'phong': lich_hoc.phong,
            'hlv_phu_trach': lich_hoc.hlv_phu_trach,
            'so_cho_toi_da': lich_hoc.so_cho_toi_da,
        })

    return render(request, 'lich_tap/them_lich_hoc.html', {
        'form': form
    })

def xoa_lich_hoc(request, id):
    lich_hoc = get_object_or_404(LichHoc, id=id)
    if request.method == 'POST':
        lich_hoc.delete()
        messages.success(request, 'Xóa lịch học thành công.')
    else:
        messages.error(request, 'Yêu cầu không hợp lệ.')

    return redirect('lich_tap:danh_sach_lich_hoc')

def dang_ky_lich_hoc(request, hoi_vien_id):
    hoi_vien = get_object_or_404(HoiVien, id=hoi_vien_id)
    _dong_bo_dang_ky_lich_theo_trang_thai_goi(hoi_vien)

    goi_tap = getattr(hoi_vien, 'goi_dang_su_dung', None)
    if not goi_tap:
        messages.error(request, 'Hội viên chưa có gói tập nên chưa thể đăng ký lịch.')
        return redirect('khach_hang:danh_sach_hoi_vien')

    if not _goi_tap_con_han(hoi_vien):
        _xoa_toan_bo_dang_ky_lich(hoi_vien)
        messages.error(request, 'Gói tập của hội viên đã hết hạn. Hệ thống đã xóa lịch cũ, vui lòng gia hạn hoặc đăng ký gói mới rồi chọn lịch lại.')
        return redirect('khach_hang:danh_sach_hoi_vien')

    lich_queryset = LichHoc.objects.filter(
        goi_tap=goi_tap,
        trang_thai=True
    ).order_by('id')

    ds_da_dang_ky = DangKyLichHoc.objects.filter(
        hoi_vien=hoi_vien
    ).select_related('lich_hoc')
    da_dang_ky_ids = set(ds_da_dang_ky.values_list('lich_hoc_id', flat=True))

    if request.method == 'POST':
        form = DangKyLichHocForm(request.POST, lich_queryset=lich_queryset)
        if form.is_valid():
            lich_hocs = form.cleaned_data['lich_hocs']
            lich_moi = [lich for lich in lich_hocs if lich.id not in da_dang_ky_ids]
            if ds_da_dang_ky.count() + len(lich_moi) > 3:
                messages.error(request, 'Hội viên chỉ được chọn tối đa 3 buổi/tuần.')
                return redirect('lich_tap:dang_ky_lich_hoc', hoi_vien_id=hoi_vien.id)

            for lich in lich_moi:
                so_nguoi_da_dang_ky = DangKyLichHoc.objects.filter(lich_hoc=lich).count()
                if so_nguoi_da_dang_ky >= lich.so_cho_toi_da:
                    messages.error(
                        request,
                        f'Khung giờ {lich.gio_bat_dau.strftime("%H:%M")} - {lich.gio_ket_thuc.strftime("%H:%M")} ngày {lich.get_thu_display()} đã đủ học viên.'
                    )
                    return redirect('lich_tap:dang_ky_lich_hoc', hoi_vien_id=hoi_vien.id)

            so_luong_them = 0
            for lich in lich_moi:
                DangKyLichHoc.objects.create(
                    hoi_vien=hoi_vien,
                    lich_hoc=lich
                )
                so_luong_them += 1

            if so_luong_them > 0:
                messages.success(request, f'Đăng ký thành công {so_luong_them} lịch học.')
            else:
                messages.warning(request, 'Các lịch này đã được đăng ký trước đó.')

            return redirect('lich_tap:dang_ky_lich_hoc', hoi_vien_id=hoi_vien.id)
    else:
        form = DangKyLichHocForm(lich_queryset=lich_queryset)

    return render(request, 'lich_tap/dang_ky_lich_hoc.html', {
        'hoi_vien': hoi_vien,
        'goi_tap': goi_tap,
        'form': form,
        'ds_da_dang_ky': ds_da_dang_ky,
        'so_luong_da_dang_ky': ds_da_dang_ky.count(),
    })


# Đăng ký lịch học của hội viên
@login_required
def dang_ky_lich_hoc_cua_toi(request):
    hoi_vien = lay_hoi_vien_tu_user(request.user)
    _dong_bo_dang_ky_lich_theo_trang_thai_goi(hoi_vien)

    goi_tap = getattr(hoi_vien, 'goi_dang_su_dung', None)

    if not goi_tap:
        messages.error(request, 'Bạn chưa có gói tập nên chưa thể đăng ký lịch.')
        return redirect('khach_hang:goi_tap_hoi_vien')

    if not _goi_tap_con_han(hoi_vien):
        _xoa_toan_bo_dang_ky_lich(hoi_vien)
        messages.error(request, 'Gói tập của bạn đã hết hạn. Hệ thống đã xóa lịch cũ, vui lòng đăng ký hoặc gia hạn gói rồi chọn lịch lại.')
        return redirect('khach_hang:goi_tap_hoi_vien')

    lich_queryset = LichHoc.objects.filter(
        goi_tap=goi_tap,
        trang_thai=True
    ).order_by('thu', 'gio_bat_dau')

    ds_da_dang_ky = DangKyLichHoc.objects.filter(
        hoi_vien=hoi_vien
    ).select_related('lich_hoc')

    da_dang_ky_ids = set(ds_da_dang_ky.values_list('lich_hoc_id', flat=True))

    if request.method == 'POST':
        form = DangKyLichHocForm(request.POST, lich_queryset=lich_queryset)
        if form.is_valid():
            lich_hocs = form.cleaned_data['lich_hocs']
            if not lich_hocs:
                messages.error(request, 'Vui lòng chọn ít nhất 1 buổi tập để tiếp tục.')
                return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')

            # chỉ tính những buổi chưa đăng ký trước đó
            lich_moi = [lich for lich in lich_hocs if lich.id not in da_dang_ky_ids]

            tong_sau_khi_dang_ky = ds_da_dang_ky.count() + len(lich_moi)
            if tong_sau_khi_dang_ky > 3:
                messages.error(request, 'Bạn chỉ được chọn tối đa 3 buổi/tuần cho gói tập này.')
                return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')

            so_luong_them = 0

            for lich in lich_moi:
                # kiểm tra số chỗ
                so_nguoi_da_dang_ky = DangKyLichHoc.objects.filter(
                    lich_hoc=lich
                ).count()

                if so_nguoi_da_dang_ky >= lich.so_cho_toi_da:
                    messages.error(
                        request,
                        f'Khung giờ {lich.gio_bat_dau.strftime("%H:%M")} - {lich.gio_ket_thuc.strftime("%H:%M")} ngày {lich.get_thu_display()} đã đủ học viên.'
                    )
                    return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')

            for lich in lich_moi:
                DangKyLichHoc.objects.create(
                    hoi_vien=hoi_vien,
                    lich_hoc=lich
                )
                so_luong_them += 1

            if so_luong_them > 0:
                messages.success(request, f'Đăng ký thành công {so_luong_them} lịch học.')
            else:
                messages.warning(request, 'Các lịch này đã được đăng ký trước đó.')

            return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')
    else:
        form = DangKyLichHocForm(lich_queryset=lich_queryset)

    return render(request, 'lich_tap/hoi_vien/dang_ky_lich_tap.html', {
        'hoi_vien': hoi_vien,
        'goi_tap': goi_tap,
        'form': form,
        'ds_da_dang_ky': ds_da_dang_ky,
    })

@login_required
@transaction.atomic
def xac_nhan_dang_ky_lich(request):
    hoi_vien = lay_hoi_vien_tu_user(request.user)
    if not hoi_vien:
        messages.error(request, 'Không tìm thấy thông tin hội viên của bạn.')
        return redirect('khach_hang:gioi_thieu_guest')

    _dong_bo_dang_ky_lich_theo_trang_thai_goi(hoi_vien)

    goi_tap = getattr(hoi_vien, 'goi_dang_su_dung', None)

    if not goi_tap:
        messages.error(request, 'Bạn chưa có gói tập nên chưa thể đăng ký lịch.')
        return redirect('khach_hang:goi_tap_hoi_vien')

    if not _goi_tap_con_han(hoi_vien):
        _xoa_toan_bo_dang_ky_lich(hoi_vien)
        messages.error(request, 'Gói tập của bạn đã hết hạn. Hệ thống đã xóa lịch cũ, vui lòng đăng ký hoặc gia hạn gói rồi chọn lịch lại.')
        return redirect('khach_hang:goi_tap_hoi_vien')

    if request.method != 'POST':
        return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')

    lich_ids = request.POST.getlist('lich_hocs')
    if not lich_ids:
        messages.error(request, 'Vui lòng chọn ít nhất 1 buổi tập để tiếp tục.')
        return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')

    lich_da_chon = list(
        LichHoc.objects.filter(
            id__in=lich_ids,
            goi_tap=goi_tap,
            trang_thai=True
        ).order_by('thu', 'gio_bat_dau')
    )

    if len(lich_da_chon) != len(lich_ids):
        messages.error(request, 'Có buổi tập không hợp lệ.')
        return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')

    so_buoi_da_dang_ky = DangKyLichHoc.objects.filter(hoi_vien=hoi_vien).count()
    if so_buoi_da_dang_ky + len(lich_da_chon) > 3:
        messages.error(request, 'Bạn chỉ được chọn tối đa 3 buổi/tuần cho gói tập này.')
        return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')

    return render(request, 'lich_tap/hoi_vien/xac_nhan_dang_ky_lich.html', {
        'hoi_vien': hoi_vien,
        'goi_tap': goi_tap,
        'lich_da_chon': lich_da_chon,
        'lich_ids': lich_ids,
    })


@login_required
def luu_dang_ky_lich(request):
    hoi_vien = lay_hoi_vien_tu_user(request.user)
    if not hoi_vien:
        messages.error(request, 'Không tìm thấy thông tin hội viên của bạn.')
        return redirect('khach_hang:gioi_thieu_guest')
    _dong_bo_dang_ky_lich_theo_trang_thai_goi(hoi_vien)
    goi_tap = getattr(hoi_vien, 'goi_dang_su_dung', None)
    if not goi_tap:
        messages.error(request, 'Bạn chưa có gói tập nên chưa thể đăng ký lịch.')
        return redirect('khach_hang:goi_tap_hoi_vien')

    if not _goi_tap_con_han(hoi_vien):
        _xoa_toan_bo_dang_ky_lich(hoi_vien)
        messages.error(request, 'Gói tập của bạn đã hết hạn. Hệ thống đã xóa lịch cũ, vui lòng đăng ký hoặc gia hạn gói rồi chọn lịch lại.')
        return redirect('khach_hang:goi_tap_hoi_vien')

    if request.method != 'POST':
        return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')

    lich_ids = request.POST.getlist('lich_hocs')

    if not lich_ids:
        messages.error(request, 'Vui lòng chọn ít nhất 1 buổi tập để tiếp tục.')
        return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')

    lich_list = list(
        LichHoc.objects.filter(
            id__in=lich_ids,
            goi_tap=goi_tap,
            trang_thai=True
        )
    )

    if len(lich_list) != len(lich_ids):
        messages.error(request, 'Có buổi tập không hợp lệ.')
        return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')

    ds_da_dang_ky = DangKyLichHoc.objects.filter(hoi_vien=hoi_vien)
    da_dang_ky_ids = set(ds_da_dang_ky.values_list('lich_hoc_id', flat=True))

    lich_moi = [lich for lich in lich_list if lich.id not in da_dang_ky_ids]

    if ds_da_dang_ky.count() + len(lich_moi) > 3:
        messages.error(request, 'Bạn chỉ được chọn tối đa 3 buổi/tuần cho gói tập này.')
        return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')

    for lich in lich_moi:
        so_nguoi_da_dang_ky = DangKyLichHoc.objects.filter(lich_hoc=lich).count()
        if so_nguoi_da_dang_ky >= lich.so_cho_toi_da:
            messages.error(
                request,
                f'Khung giờ {lich.gio_bat_dau.strftime("%H:%M")} - {lich.gio_ket_thuc.strftime("%H:%M")} ngày {lich.get_thu_display()} đã đủ học viên.'
            )
            return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')

    for lich in lich_moi:
        DangKyLichHoc.objects.create(
            hoi_vien=hoi_vien,
            lich_hoc=lich
        )

    messages.success(request, 'Đăng ký lịch tập thành công.')
    return redirect('lich_tap:dang_ky_lich_hoc_cua_toi')
