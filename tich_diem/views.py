from datetime import timedelta
from decimal import Decimal
import re

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from khach_hang.models import HoiVien
from .models import LichSuDiem, PhanThuong, VoucherHoiVien, cap_nhat_voucher_het_han


def tinh_hang_hoi_vien(diem):
    if diem >= 1500:
        return 'GOLD'
    elif diem >= 800:
        return 'SILVER'
    return 'BRONZE'


def _phan_thuong_la_voucher(phan_thuong):
    ten = (phan_thuong.ten_qua or '').lower()
    return 'voucher' in ten or 'giảm giá' in ten or 'giam gia' in ten


def _gia_tri_voucher_tu_phan_thuong(phan_thuong):
    ten = (phan_thuong.ten_qua or '').replace('.', '')
    numbers = re.findall(r'(\d+)', ten)
    if numbers:
        value = int(numbers[0])
        if value < 1000:
            value *= 1000
        return Decimal(value)
    return Decimal('0')


def _tao_ma_voucher(hoi_vien):
    prefix = f'VC-{hoi_vien.ma_hoi_vien or hoi_vien.id}'
    count = VoucherHoiVien.objects.filter(hoi_vien=hoi_vien).count() + 1
    return f'{prefix}-{count:03d}'


def quan_ly_diem(request):
    cap_nhat_voucher_het_han()
    q = request.GET.get('q', '')
    hoi_vien_id = request.GET.get('hoi_vien_id')
    tab = request.GET.get('tab', 'xem_diem')

    ds_hoi_vien = HoiVien.objects.all().order_by('ho_ten')
    if q:
        ds_hoi_vien = ds_hoi_vien.filter(ho_ten__icontains=q)

    hoi_vien_duoc_chon = None
    lich_su_diem = []
    ds_phan_thuong = PhanThuong.objects.filter(so_luong_con__gt=0)
    hang_hoi_vien = None
    ds_voucher = VoucherHoiVien.objects.none()

    if hoi_vien_id:
        hoi_vien_duoc_chon = get_object_or_404(HoiVien, id=hoi_vien_id)
    else:
        hoi_vien_duoc_chon = ds_hoi_vien.first()

    if hoi_vien_duoc_chon:
        lich_su_diem = LichSuDiem.objects.filter(hoi_vien=hoi_vien_duoc_chon).order_by('-ngay_thuc_hien')
        hang_hoi_vien = tinh_hang_hoi_vien(hoi_vien_duoc_chon.diem_tich_luy)
        ds_voucher = VoucherHoiVien.objects.filter(hoi_vien=hoi_vien_duoc_chon).order_by('-ngay_tao')

    context = {
        'ds_hoi_vien': ds_hoi_vien,
        'hoi_vien_duoc_chon': hoi_vien_duoc_chon,
        'lich_su_diem': lich_su_diem,
        'ds_phan_thuong': ds_phan_thuong,
        'hang_hoi_vien': hang_hoi_vien,
        'ds_voucher': ds_voucher,
        'q': q,
        'tab': tab,
    }
    return render(request, 'tich_diem/quan_ly_diem.html', context)


def doi_diem(request, hoi_vien_id, phan_thuong_id):
    hoi_vien = get_object_or_404(HoiVien, id=hoi_vien_id)
    phan_thuong = get_object_or_404(PhanThuong, id=phan_thuong_id)

    if request.method != 'POST':
        messages.error(request, 'Yêu cầu không hợp lệ.')
        return redirect(f"{reverse('tich_diem:quan_ly_diem')}?hoi_vien_id={hoi_vien.id}&tab=doi_diem")

    if phan_thuong.so_luong_con <= 0:
        messages.error(request, 'Phần thưởng đã hết số lượng.')
        return redirect(f"{reverse('tich_diem:quan_ly_diem')}?hoi_vien_id={hoi_vien.id}&tab=doi_diem")

    if hoi_vien.diem_tich_luy < phan_thuong.diem_yeu_cau:
        messages.error(request, 'Hội viên không đủ điểm để đổi quà.')
        return redirect(f"{reverse('tich_diem:quan_ly_diem')}?hoi_vien_id={hoi_vien.id}&tab=doi_diem")

    hoi_vien.diem_tich_luy -= phan_thuong.diem_yeu_cau
    hoi_vien.save(update_fields=['diem_tich_luy'])

    phan_thuong.so_luong_con -= 1
    phan_thuong.save(update_fields=['so_luong_con'])

    noi_dung = f'Đổi quà: {phan_thuong.ten_qua}'
    if _phan_thuong_la_voucher(phan_thuong):
        gia_tri_giam = _gia_tri_voucher_tu_phan_thuong(phan_thuong)
        voucher = VoucherHoiVien.objects.create(
            hoi_vien=hoi_vien,
            phan_thuong=phan_thuong,
            ma_voucher=_tao_ma_voucher(hoi_vien),
            ten_voucher=phan_thuong.ten_qua,
            gia_tri_giam=gia_tri_giam,
            diem_da_doi=phan_thuong.diem_yeu_cau,
            ngay_het_han=timezone.localdate() + timedelta(days=30),
        )
        noi_dung = f'Đổi điểm thành voucher: {voucher.ma_voucher}'
        messages.success(request, f'Đổi điểm thành công. Đã tạo voucher {voucher.ma_voucher}.')
    else:
        messages.success(request, f'Đổi điểm thành công: {phan_thuong.ten_qua}')

    LichSuDiem.objects.create(
        hoi_vien=hoi_vien,
        loai_giao_dich='tru',
        so_diem=phan_thuong.diem_yeu_cau,
        noi_dung=noi_dung
    )

    return redirect(f"{reverse('tich_diem:quan_ly_diem')}?hoi_vien_id={hoi_vien.id}&tab=doi_diem")


@login_required
def diem_tich_luy_hoi_vien(request):
    cap_nhat_voucher_het_han()
    hoi_vien = get_object_or_404(HoiVien, ma_hoi_vien=request.user.username)

    lich_su_diem = LichSuDiem.objects.filter(hoi_vien=hoi_vien).order_by('-ngay_thuc_hien')
    ds_phan_thuong = PhanThuong.objects.filter(so_luong_con__gt=0).order_by('diem_yeu_cau')
    hang_hoi_vien = tinh_hang_hoi_vien(hoi_vien.diem_tich_luy)
    ds_voucher = VoucherHoiVien.objects.filter(hoi_vien=hoi_vien).order_by('-ngay_tao')

    context = {
        'hoi_vien': hoi_vien,
        'lich_su_diem': lich_su_diem,
        'ds_phan_thuong': ds_phan_thuong,
        'ds_voucher': ds_voucher,
        'hang_hoi_vien': hang_hoi_vien,
        'tab': request.GET.get('tab', 'doi_diem'),
    }
    return render(request, 'tich_diem/hoi_vien/diem_tich_luy.html', context)


@login_required
def doi_diem_hoi_vien(request, phan_thuong_id):
    hoi_vien = get_object_or_404(HoiVien, ma_hoi_vien=request.user.username)
    phan_thuong = get_object_or_404(PhanThuong, id=phan_thuong_id)

    if request.method != 'POST':
        messages.error(request, 'Yêu cầu không hợp lệ.')
        return redirect('tich_diem:diem_tich_luy_hoi_vien')

    if phan_thuong.so_luong_con <= 0:
        messages.error(request, 'Phần thưởng đã hết số lượng.')
        return redirect('tich_diem:diem_tich_luy_hoi_vien')

    if hoi_vien.diem_tich_luy < phan_thuong.diem_yeu_cau:
        messages.error(request, 'Bạn không đủ điểm để đổi ưu đãi này.')
        return redirect('tich_diem:diem_tich_luy_hoi_vien')

    hoi_vien.diem_tich_luy -= phan_thuong.diem_yeu_cau
    hoi_vien.save(update_fields=['diem_tich_luy'])

    phan_thuong.so_luong_con -= 1
    phan_thuong.save(update_fields=['so_luong_con'])

    noi_dung = f'Đổi quà: {phan_thuong.ten_qua}'
    if _phan_thuong_la_voucher(phan_thuong):
        gia_tri_giam = _gia_tri_voucher_tu_phan_thuong(phan_thuong)
        voucher = VoucherHoiVien.objects.create(
            hoi_vien=hoi_vien,
            phan_thuong=phan_thuong,
            ma_voucher=_tao_ma_voucher(hoi_vien),
            ten_voucher=phan_thuong.ten_qua,
            gia_tri_giam=gia_tri_giam,
            diem_da_doi=phan_thuong.diem_yeu_cau,
            ngay_het_han=timezone.localdate() + timedelta(days=30),
        )
        noi_dung = f'Đổi điểm thành voucher: {voucher.ma_voucher}'
        messages.success(request, f'Đổi điểm thành công. Bạn đã nhận voucher {voucher.ma_voucher}.')
    else:
        messages.success(request, f'Đổi điểm thành công: {phan_thuong.ten_qua}')

    LichSuDiem.objects.create(
        hoi_vien=hoi_vien,
        loai_giao_dich='tru',
        so_diem=phan_thuong.diem_yeu_cau,
        noi_dung=noi_dung
    )

    return redirect('tich_diem:diem_tich_luy_hoi_vien')
