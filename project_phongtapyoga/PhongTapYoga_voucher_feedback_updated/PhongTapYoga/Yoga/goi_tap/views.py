from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from khach_hang.models import HoiVien
from lich_tap.models import LichHoc, DangKyLichHoc
from .models import GoiTap, DangKyGoiTap

def goi_tap(request):
    q = request.GET.get('q', '').strip()
    trang_thai = request.GET.get('trang_thai', '').strip()
    view_mode = request.GET.get('view', 'list')
    selected_id = request.GET.get('id')
    ds_goi = GoiTap.objects.all().order_by('-id')
    if q:
        ds_goi = ds_goi.filter(ten_goi__icontains=q)

    if trang_thai:
        ds_goi = ds_goi.filter(trang_thai=trang_thai)
    selected_goi = None
    if selected_id:
        selected_goi = get_object_or_404(GoiTap, id=selected_id)

    context = {
        'ds_goi': ds_goi,
        'q': q,
        'trang_thai': trang_thai,
        'view_mode': view_mode,
        'selected_goi': selected_goi,
    }
    return render(request, 'goi_tap.html', context)

def them_goi_tap(request):
    if request.method == 'POST':
        ma_goi = request.POST.get('ma_goi', '').strip()
        ten_goi = request.POST.get('ten_goi', '').strip()
        loai_goi = request.POST.get('loai_goi', '').strip()
        thoi_han_so_buoi = request.POST.get('thoi_han_so_buoi', '').strip()
        gia_goi = request.POST.get('gia_goi', '').strip()
        trang_thai = request.POST.get('trang_thai', '').strip()
        ghi_chu = request.POST.get('ghi_chu', '').strip()

        if not ma_goi or not ten_goi or not loai_goi or not thoi_han_so_buoi or not gia_goi or not trang_thai:
            messages.error(request, 'Vui lòng nhập đầy đủ các trường bắt buộc.')
            return redirect('/goi-tap/?view=add')

        if GoiTap.objects.filter(ma_goi=ma_goi).exists():
            messages.error(request, 'Mã gói đã tồn tại.')
            return redirect('/goi-tap/?view=add')

        GoiTap.objects.create(
            ma_goi=ma_goi,
            ten_goi=ten_goi,
            loai_goi=loai_goi,
            thoi_han_so_buoi=thoi_han_so_buoi,
            gia_goi=gia_goi,
            trang_thai=trang_thai,
            ghi_chu=ghi_chu,
        )

        messages.success(request, 'Thêm gói tập thành công.')
        return redirect('goi_tap:goi_tap')

    return redirect('goi_tap:goi_tap')


def sua_goi_tap(request, id):
    goi = get_object_or_404(GoiTap, id=id)

    if request.method == 'POST':
        ten_goi = request.POST.get('ten_goi', '').strip()
        loai_goi = request.POST.get('loai_goi', '').strip()
        thoi_han_so_buoi = request.POST.get('thoi_han_so_buoi', '').strip()
        gia_goi = request.POST.get('gia_goi', '').strip()
        trang_thai = request.POST.get('trang_thai', '').strip()
        ghi_chu = request.POST.get('ghi_chu', '').strip()

        if not ten_goi or not loai_goi or not thoi_han_so_buoi or not gia_goi or not trang_thai:
            messages.error(request, 'Vui lòng nhập đầy đủ các trường bắt buộc.')
            return redirect(f'/goi-tap/?view=edit&id={goi.id}')

        goi.ten_goi = ten_goi
        goi.loai_goi = loai_goi
        goi.thoi_han_so_buoi = thoi_han_so_buoi
        goi.gia_goi = gia_goi
        goi.trang_thai = trang_thai
        goi.ghi_chu = ghi_chu
        goi.save()

        messages.success(request, 'Cập nhật gói tập thành công.')
        return redirect('goi_tap:goi_tap')

    return redirect('goi_tap:goi_tap')


def xoa_goi_tap(request, id):
    goi = get_object_or_404(GoiTap, id=id)

    if request.method == 'POST':
        goi.delete()
        messages.success(request, 'Xóa gói tập thành công.')

    return redirect('goi_tap:goi_tap')

# Dành cho hội viên
def dang_ky_goi_tap_hoi_vien(request, goi_id):
    hoi_vien = get_object_or_404(HoiVien, user=request.user)
    goi_tap = get_object_or_404(GoiTap, id=goi_id, trang_thai='hoat_dong')
    dang_ky_hien_tai = DangKyGoiTap.objects.filter(
        hoi_vien=hoi_vien,
        trang_thai='hoat_dong'
    ).first()
    if dang_ky_hien_tai:
        messages.warning(request, 'Bạn đã có gói tập đang hoạt động.')
        return redirect('goi_tap:danh_sach_goi_tap_hoi_vien')
    ngay_bat_dau = timezone.localdate()
    if goi_tap.loai_goi == 'thang':
        ngay_ket_thuc = ngay_bat_dau + timedelta(days=30 * goi_tap.thoi_han_so_buoi)
    else:
        ngay_ket_thuc = None
    DangKyGoiTap.objects.create(
        hoi_vien=hoi_vien,
        goi_tap=goi_tap,
        ngay_dang_ky=ngay_bat_dau,
        ngay_bat_dau=ngay_bat_dau,
        ngay_ket_thuc=ngay_ket_thuc,
        trang_thai='hoat_dong'
    )
    messages.success(request, 'Đăng ký gói tập thành công. Bạn có thể tiếp tục đăng ký lịch học.')
    return redirect('lich_tap:lich_tap_cua_toi')