import re
from datetime import timedelta
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from goi_tap.models import GoiTap
from lich_tap.models import LichHoc, DangKyLichHoc
from cham_soc_khach_hang.models import QuangCao
from tich_diem.models import LichSuDiem, VoucherHoiVien, cap_nhat_voucher_het_han
from .models import KhachHang, HoiVien, LichSuGiaHanGoi, LichSuTap, LopTap, HuanLuyenVien, PhongTap
from .forms import GiaHanGoiForm, DangKyTuVanGuestForm


def _thu_hom_nay():
    weekday = timezone.localdate().weekday()
    mapping = {0: '2', 1: '3', 2: '4', 3: '5', 4: '6', 5: '7', 6: 'CN'}
    return mapping.get(weekday)

# sinh mã tự động
def _tao_ma_khach_hang_tiep_theo():
    ds_ma = KhachHang.objects.values_list('ma_khach_hang', flat=True)
    so_lon_nhat = 0
    for ma in ds_ma:
        if not ma:
            continue
        match = re.search(r'^KH(\d+)$', str(ma).strip(), re.IGNORECASE)
        if match:
            so_lon_nhat = max(so_lon_nhat, int(match.group(1)))
    return f"KH{so_lon_nhat + 1:03d}"


def _tao_ma_hoi_vien_tiep_theo():
    ds_ma = HoiVien.objects.values_list('ma_hoi_vien', flat=True)
    so_lon_nhat = 0
    for ma in ds_ma:
        if not ma:
            continue
        match = re.search(r'^HV(\d+)$', str(ma).strip(), re.IGNORECASE)
        if match:
            so_lon_nhat = max(so_lon_nhat, int(match.group(1)))
    return f"HV{so_lon_nhat + 1:03d}"


def _du_lieu_khach_hang_mac_dinh(form_data=None):
    return form_data or {'ma_khach_hang': _tao_ma_khach_hang_tiep_theo()}


def _hop_le_so_dien_thoai(so_dien_thoai):
    return bool(re.fullmatch(r'\d{10}', (so_dien_thoai or '').strip()))


def _hop_le_email(email):
    email = (email or '').strip()
    if not email:
        return True
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False

def _goi_tap_con_han(hoi_vien, today=None):
    today = today or timezone.localdate()
    return bool(
        hoi_vien and
        hoi_vien.goi_dang_su_dung_id and
        hoi_vien.ngay_het_han_goi and
        hoi_vien.ngay_het_han_goi >= today
    )


def _xoa_toan_bo_dang_ky_lich(hoi_vien):
    if not hoi_vien:
        return 0
    deleted, _ = DangKyLichHoc.objects.filter(hoi_vien=hoi_vien).delete()
    return deleted


def _dong_bo_dang_ky_lich_theo_trang_thai_goi(hoi_vien, today=None):
    today = today or timezone.localdate()
    if not hoi_vien:
        return 0

    if not hoi_vien.goi_dang_su_dung_id or not hoi_vien.ngay_het_han_goi:
        return _xoa_toan_bo_dang_ky_lich(hoi_vien)

    if hoi_vien.ngay_het_han_goi < today:
        return _xoa_toan_bo_dang_ky_lich(hoi_vien)

    deleted, _ = DangKyLichHoc.objects.filter(hoi_vien=hoi_vien).exclude(
        lich_hoc__goi_tap_id=hoi_vien.goi_dang_su_dung_id
    ).delete()
    return deleted


def _render_trang_khach_hang(request, *, view_mode='list', selected_customer=None, form_data=None, q='', trang_thai=''):
    ds_khach_hang = KhachHang.objects.all().order_by('-id')

    if q:
        ds_khach_hang = ds_khach_hang.filter(ho_ten__icontains=q)

    if trang_thai:
        ds_khach_hang = ds_khach_hang.filter(trang_thai=trang_thai)

    return render(request, 'khach_hang/khach_hang.html', {
        'ds_khach_hang': ds_khach_hang,
        'ds_goi_tap': GoiTap.objects.all(),
        'q': q,
        'trang_thai': trang_thai,
        'view_mode': view_mode,
        'selected_customer': selected_customer,
        'form_data': _du_lieu_khach_hang_mac_dinh(form_data),
        'ma_khach_hang_moi': _tao_ma_khach_hang_tiep_theo(),
    })


def _lay_hoac_tao_lop_tap_tu_lich_hoc(lich_hoc):
    if not lich_hoc:
        return None

    ten_lop = ''
    if getattr(lich_hoc, 'goi_tap', None):
        ten_lop = getattr(lich_hoc.goi_tap, 'ten_goi', '')
    if not ten_lop:
        ten_lop = str(lich_hoc)

    ten_hlv = (getattr(lich_hoc, 'hlv_phu_trach', '') or '').strip()
    ten_phong = (getattr(lich_hoc, 'phong', '') or '').strip()

    huan_luyen_vien = None
    if ten_hlv:
        huan_luyen_vien, _ = HuanLuyenVien.objects.get_or_create(ho_ten=ten_hlv)

    phong_tap = None
    if ten_phong:
        phong_tap, _ = PhongTap.objects.get_or_create(ten_phong=ten_phong)

    lop_tap = LopTap.objects.filter(ten_lop=ten_lop, huan_luyen_vien=huan_luyen_vien, phong_tap=phong_tap).first()
    if lop_tap:
        return lop_tap

    return LopTap.objects.create(ten_lop=ten_lop, huan_luyen_vien=huan_luyen_vien, phong_tap=phong_tap)


def _lay_danh_sach_check_in_hom_nay(q=''):
    thu_hom_nay = _thu_hom_nay()
    hom_nay = timezone.localdate()

    dang_ky_hom_nay = DangKyLichHoc.objects.select_related(
        'hoi_vien',
        'hoi_vien__goi_dang_su_dung',
        'lich_hoc',
        'lich_hoc__goi_tap'
    ).filter(lich_hoc__thu=thu_hom_nay).order_by('lich_hoc__gio_bat_dau', 'hoi_vien__ho_ten')

    if q:
        dang_ky_hom_nay = dang_ky_hom_nay.filter(
            Q(hoi_vien__ho_ten__icontains=q) |
            Q(hoi_vien__so_dien_thoai__icontains=q) |
            Q(hoi_vien__ma_hoi_vien__icontains=q)
        )

    ket_qua = []
    da_co = set()

    for dang_ky in dang_ky_hom_nay:
        hoi_vien = dang_ky.hoi_vien
        if not hoi_vien.goi_dang_su_dung:
            continue
        if hoi_vien.ngay_het_han_goi and hoi_vien.ngay_het_han_goi < hom_nay:
            continue

        khoa = (hoi_vien.id, dang_ky.lich_hoc.id)
        if khoa in da_co:
            continue
        da_co.add(khoa)

        da_check_in = LichSuTap.objects.filter(hoi_vien=hoi_vien, thoi_gian__date=hom_nay).exists()
        ket_qua.append({
            'hoi_vien': hoi_vien,
            'lich_hoc': dang_ky.lich_hoc,
            'da_check_in': da_check_in,
        })

    return ket_qua

def danh_sach_khach_hang(request):
    q = request.GET.get('q', '')
    trang_thai = request.GET.get('trang_thai', '')
    view_mode = request.GET.get('view', 'list')
    selected_customer = None

    if view_mode not in ['list', 'add', 'detail', 'edit']:
        view_mode = 'list'

    if view_mode in ['detail', 'edit']:
        customer_id = request.GET.get('id')
        if customer_id:
            selected_customer = KhachHang.objects.filter(id=customer_id).first()

    return _render_trang_khach_hang(
        request,
        view_mode=view_mode,
        selected_customer=selected_customer,
        q=q,
        trang_thai=trang_thai,
    )


def them_khach_hang(request):
    if request.method == 'POST':
        ma_khach_hang = (request.POST.get('ma_khach_hang') or _tao_ma_khach_hang_tiep_theo()).strip()
        ho_ten = (request.POST.get('ho_ten') or '').strip()
        ngay_sinh = request.POST.get('ngay_sinh') or None
        gioi_tinh = request.POST.get('gioi_tinh')
        so_dien_thoai = (request.POST.get('so_dien_thoai') or '').strip()
        email = (request.POST.get('email') or '').strip()
        dia_chi = (request.POST.get('dia_chi') or '').strip()
        tinh_trang_suc_khoe = (request.POST.get('tinh_trang_suc_khoe') or '').strip()
        muc_tieu_tap_luyen = (request.POST.get('muc_tieu_tap_luyen') or '').strip()
        ghi_chu_nhan_vien = (request.POST.get('ghi_chu_nhan_vien') or '').strip()
        trang_thai = request.POST.get('trang_thai', 'moi')

        if not _hop_le_so_dien_thoai(so_dien_thoai):
            messages.error(request, 'Số điện thoại phải gồm đúng 10 chữ số.')
            return _render_trang_khach_hang(request, view_mode='add', form_data=request.POST)

        if not _hop_le_email(email):
            messages.error(request, 'Email không đúng định dạng.')
            return _render_trang_khach_hang(request, view_mode='add', form_data=request.POST)

        if KhachHang.objects.filter(ma_khach_hang=ma_khach_hang).exists():
            messages.error(request, 'Mã khách hàng đã tồn tại.')
            return _render_trang_khach_hang(request, view_mode='add', form_data=request.POST)

        if KhachHang.objects.filter(so_dien_thoai=so_dien_thoai).exists():
            messages.error(request, 'Số điện thoại đã tồn tại.')
            return _render_trang_khach_hang(request, view_mode='add', form_data=request.POST)

        if HoiVien.objects.filter(so_dien_thoai=so_dien_thoai).exists():
            messages.error(request, 'Số điện thoại này đã tồn tại trong danh sách hội viên.')
            return _render_trang_khach_hang(request, view_mode='add', form_data=request.POST)

        KhachHang.objects.create(
            ma_khach_hang=ma_khach_hang,
            ho_ten=ho_ten,
            ngay_sinh=ngay_sinh,
            gioi_tinh=gioi_tinh,
            so_dien_thoai=so_dien_thoai,
            email=email,
            dia_chi=dia_chi,
            tinh_trang_suc_khoe=tinh_trang_suc_khoe,
            muc_tieu_tap_luyen=muc_tieu_tap_luyen,
            ghi_chu_nhan_vien=ghi_chu_nhan_vien,
            trang_thai=trang_thai,
        )

        messages.success(request, 'Thêm khách hàng thành công.')
        return redirect('khach_hang:danh_sach_khach_hang')

    return redirect('khach_hang:danh_sach_khach_hang')


def sua_khach_hang(request, id):
    khach = get_object_or_404(KhachHang, id=id)

    if request.method == 'POST':
        ma_khach_hang = (request.POST.get('ma_khach_hang') or '').strip()
        ho_ten = (request.POST.get('ho_ten') or '').strip()
        ngay_sinh = request.POST.get('ngay_sinh') or None
        gioi_tinh = request.POST.get('gioi_tinh')
        so_dien_thoai = (request.POST.get('so_dien_thoai') or '').strip()
        email = (request.POST.get('email') or '').strip()
        dia_chi = (request.POST.get('dia_chi') or '').strip()
        tinh_trang_suc_khoe = (request.POST.get('tinh_trang_suc_khoe') or '').strip()
        muc_tieu_tap_luyen = (request.POST.get('muc_tieu_tap_luyen') or '').strip()
        ghi_chu_nhan_vien = (request.POST.get('ghi_chu_nhan_vien') or '').strip()
        trang_thai = request.POST.get('trang_thai')

        if not _hop_le_so_dien_thoai(so_dien_thoai):
            messages.error(request, 'Số điện thoại phải gồm đúng 10 chữ số.')
            for field, value in {
                'ma_khach_hang': ma_khach_hang,
                'ho_ten': ho_ten,
                'ngay_sinh': ngay_sinh,
                'gioi_tinh': gioi_tinh,
                'so_dien_thoai': so_dien_thoai,
                'email': email,
                'dia_chi': dia_chi,
                'tinh_trang_suc_khoe': tinh_trang_suc_khoe,
                'muc_tieu_tap_luyen': muc_tieu_tap_luyen,
                'ghi_chu_nhan_vien': ghi_chu_nhan_vien,
                'trang_thai': trang_thai,
            }.items():
                setattr(khach, field, value)
            return _render_trang_khach_hang(request, view_mode='edit', selected_customer=khach)

        if not _hop_le_email(email):
            messages.error(request, 'Email không đúng định dạng.')
            for field, value in {
                'ma_khach_hang': ma_khach_hang,
                'ho_ten': ho_ten,
                'ngay_sinh': ngay_sinh,
                'gioi_tinh': gioi_tinh,
                'so_dien_thoai': so_dien_thoai,
                'email': email,
                'dia_chi': dia_chi,
                'tinh_trang_suc_khoe': tinh_trang_suc_khoe,
                'muc_tieu_tap_luyen': muc_tieu_tap_luyen,
                'ghi_chu_nhan_vien': ghi_chu_nhan_vien,
                'trang_thai': trang_thai,
            }.items():
                setattr(khach, field, value)
            return _render_trang_khach_hang(request, view_mode='edit', selected_customer=khach)

        if KhachHang.objects.filter(ma_khach_hang=ma_khach_hang).exclude(id=khach.id).exists():
            messages.error(request, 'Mã khách hàng đã tồn tại.')
            for field, value in {
                'ma_khach_hang': ma_khach_hang,
                'ho_ten': ho_ten,
                'ngay_sinh': ngay_sinh,
                'gioi_tinh': gioi_tinh,
                'so_dien_thoai': so_dien_thoai,
                'email': email,
                'dia_chi': dia_chi,
                'tinh_trang_suc_khoe': tinh_trang_suc_khoe,
                'muc_tieu_tap_luyen': muc_tieu_tap_luyen,
                'ghi_chu_nhan_vien': ghi_chu_nhan_vien,
                'trang_thai': trang_thai,
            }.items():
                setattr(khach, field, value)
            return _render_trang_khach_hang(request, view_mode='edit', selected_customer=khach)

        if KhachHang.objects.filter(so_dien_thoai=so_dien_thoai).exclude(id=khach.id).exists():
            messages.error(request, 'Số điện thoại đã tồn tại.')
            for field, value in {
                'ma_khach_hang': ma_khach_hang,
                'ho_ten': ho_ten,
                'ngay_sinh': ngay_sinh,
                'gioi_tinh': gioi_tinh,
                'so_dien_thoai': so_dien_thoai,
                'email': email,
                'dia_chi': dia_chi,
                'tinh_trang_suc_khoe': tinh_trang_suc_khoe,
                'muc_tieu_tap_luyen': muc_tieu_tap_luyen,
                'ghi_chu_nhan_vien': ghi_chu_nhan_vien,
                'trang_thai': trang_thai,
            }.items():
                setattr(khach, field, value)
            return _render_trang_khach_hang(request, view_mode='edit', selected_customer=khach)

        if HoiVien.objects.filter(so_dien_thoai=so_dien_thoai).exists() and khach.so_dien_thoai != so_dien_thoai:
            messages.error(request, 'Số điện thoại này đã tồn tại trong danh sách hội viên.')
            for field, value in {
                'ma_khach_hang': ma_khach_hang,
                'ho_ten': ho_ten,
                'ngay_sinh': ngay_sinh,
                'gioi_tinh': gioi_tinh,
                'so_dien_thoai': so_dien_thoai,
                'email': email,
                'dia_chi': dia_chi,
                'tinh_trang_suc_khoe': tinh_trang_suc_khoe,
                'muc_tieu_tap_luyen': muc_tieu_tap_luyen,
                'ghi_chu_nhan_vien': ghi_chu_nhan_vien,
                'trang_thai': trang_thai,
            }.items():
                setattr(khach, field, value)
            return _render_trang_khach_hang(request, view_mode='edit', selected_customer=khach)

        khach.ma_khach_hang = ma_khach_hang
        khach.ho_ten = ho_ten
        khach.ngay_sinh = ngay_sinh
        khach.gioi_tinh = gioi_tinh
        khach.so_dien_thoai = so_dien_thoai
        khach.email = email
        khach.dia_chi = dia_chi
        khach.tinh_trang_suc_khoe = tinh_trang_suc_khoe
        khach.muc_tieu_tap_luyen = muc_tieu_tap_luyen
        khach.ghi_chu_nhan_vien = ghi_chu_nhan_vien
        khach.trang_thai = trang_thai
        khach.save()

        messages.success(request, 'Cập nhật khách hàng thành công.')
        return redirect('khach_hang:danh_sach_khach_hang')

    return redirect('khach_hang:danh_sach_khach_hang')


def xoa_khach_hang(request, id):
    khach = get_object_or_404(KhachHang, id=id)

    if request.method == 'POST':
        khach.delete()
        messages.success(request, 'Xóa khách hàng thành công.')
    return redirect('khach_hang:danh_sach_khach_hang')

def danh_sach_hoi_vien(request):
    q = request.GET.get('q', '')
    ds_hoi_vien = HoiVien.objects.select_related('goi_dang_su_dung').all().order_by('-id')

    if q:
        ds_hoi_vien = ds_hoi_vien.filter(ho_ten__icontains=q)

    return render(request, 'khach_hang/hoi_vien.html', {
        'ds_hoi_vien': ds_hoi_vien,
        'q': q,
    })


def them_hoi_vien(request):
    ds_goi_tap = GoiTap.objects.all()

    if request.method == 'POST':
        ma_hoi_vien = (request.POST.get('ma_hoi_vien') or _tao_ma_hoi_vien_tiep_theo()).strip()
        ho_ten = (request.POST.get('ho_ten') or '').strip()
        ngay_sinh = (request.POST.get('ngay_sinh') or '').strip()
        gioi_tinh = (request.POST.get('gioi_tinh') or 'Khác').strip()
        so_dien_thoai = (request.POST.get('so_dien_thoai') or '').strip()
        email = (request.POST.get('email') or '').strip()
        tinh_trang_suc_khoe = (request.POST.get('tinh_trang_suc_khoe') or '').strip()
        muc_tieu_tap_luyen = (request.POST.get('muc_tieu_tap_luyen') or '').strip()
        ghi_chu_nhan_vien = (request.POST.get('ghi_chu_nhan_vien') or '').strip()
        goi_id = request.POST.get('goi_dang_su_dung')
        ngay_het_han_goi = request.POST.get('ngay_het_han_goi') or None
        diem_tich_luy = request.POST.get('diem_tich_luy') or 0

        if not ngay_sinh:
            messages.error(request, 'Vui lòng nhập ngày sinh.')
            return render(request, 'khach_hang/hoi_vien_form.html', {
                'title': 'Thêm hội viên',
                'action_url': 'khach_hang:them_hoi_vien',
                'hv': None,
                'form_data': request.POST,
                'ds_goi_tap': ds_goi_tap,
                'ma_hoi_vien_moi': ma_hoi_vien,
            })

        if not _hop_le_so_dien_thoai(so_dien_thoai):
            messages.error(request, 'Số điện thoại phải gồm đúng 10 chữ số.')
            return render(request, 'khach_hang/hoi_vien_form.html', {
                'title': 'Thêm hội viên',
                'action_url': 'khach_hang:them_hoi_vien',
                'hv': None,
                'form_data': request.POST,
                'ds_goi_tap': ds_goi_tap,
                'ma_hoi_vien_moi': ma_hoi_vien,
            })

        if not _hop_le_email(email):
            messages.error(request, 'Email không đúng định dạng.')
            return render(request, 'khach_hang/hoi_vien_form.html', {
                'title': 'Thêm hội viên',
                'action_url': 'khach_hang:them_hoi_vien',
                'hv': None,
                'form_data': request.POST,
                'ds_goi_tap': ds_goi_tap,
                'ma_hoi_vien_moi': ma_hoi_vien,
            })

        if HoiVien.objects.filter(ma_hoi_vien=ma_hoi_vien).exists():
            messages.error(request, 'Mã hội viên đã tồn tại.')
            return render(request, 'khach_hang/hoi_vien_form.html', {
                'title': 'Thêm hội viên',
                'action_url': 'khach_hang:them_hoi_vien',
                'hv': None,
                'form_data': request.POST,
                'ds_goi_tap': ds_goi_tap,
                'ma_hoi_vien_moi': ma_hoi_vien,
            })

        if HoiVien.objects.filter(so_dien_thoai=so_dien_thoai).exists():
            messages.error(request, 'Số điện thoại đã tồn tại.')
            return render(request, 'khach_hang/hoi_vien_form.html', {
                'title': 'Thêm hội viên',
                'action_url': 'khach_hang:them_hoi_vien',
                'hv': None,
                'form_data': request.POST,
                'ds_goi_tap': ds_goi_tap,
                'ma_hoi_vien_moi': ma_hoi_vien,
            })

        goi_tap = GoiTap.objects.filter(id=goi_id).first() if goi_id else None

        HoiVien.objects.create(
            ma_hoi_vien=ma_hoi_vien,
            ho_ten=ho_ten,
            ngay_sinh=ngay_sinh,
            gioi_tinh=gioi_tinh,
            so_dien_thoai=so_dien_thoai,
            email=email,
            tinh_trang_suc_khoe=tinh_trang_suc_khoe,
            muc_tieu_tap_luyen=muc_tieu_tap_luyen,
            ghi_chu_nhan_vien=ghi_chu_nhan_vien,
            goi_dang_su_dung=goi_tap,
            ngay_het_han_goi=ngay_het_han_goi,
            diem_tich_luy=diem_tich_luy,
        )

        messages.success(request, 'Thêm hội viên thành công.')
        return redirect('khach_hang:danh_sach_hoi_vien')

    return render(request, 'khach_hang/hoi_vien_form.html', {
        'title': 'Thêm hội viên',
        'action_url': 'khach_hang:them_hoi_vien',
        'hv': None,
        'form_data': {},
        'ds_goi_tap': ds_goi_tap,
        'ma_hoi_vien_moi': _tao_ma_hoi_vien_tiep_theo(),
    })

def chi_tiet_hoi_vien(request, id):
    hv = get_object_or_404(HoiVien.objects.select_related('goi_dang_su_dung'), id=id)
    return render(request, 'khach_hang/chi_tiet_hoi_vien.html', {
        'hv': hv
    })


def sua_hoi_vien(request, id):
    hv = get_object_or_404(HoiVien, id=id)
    ds_goi_tap = GoiTap.objects.all()

    if request.method == 'POST':
        ma_hoi_vien = (request.POST.get('ma_hoi_vien') or '').strip()
        ho_ten = (request.POST.get('ho_ten') or '').strip()
        ngay_sinh = request.POST.get('ngay_sinh') or None
        gioi_tinh = request.POST.get('gioi_tinh') or 'Khác'
        so_dien_thoai = (request.POST.get('so_dien_thoai') or '').strip()
        email = (request.POST.get('email') or '').strip()
        tinh_trang_suc_khoe = (request.POST.get('tinh_trang_suc_khoe') or '').strip()
        muc_tieu_tap_luyen = (request.POST.get('muc_tieu_tap_luyen') or '').strip()
        ghi_chu_nhan_vien = (request.POST.get('ghi_chu_nhan_vien') or '').strip()
        goi_id = request.POST.get('goi_dang_su_dung')
        ngay_het_han_goi = request.POST.get('ngay_het_han_goi') or None
        diem_tich_luy = request.POST.get('diem_tich_luy') or 0

        if not _hop_le_so_dien_thoai(so_dien_thoai):
            messages.error(request, 'Số điện thoại phải gồm đúng 10 chữ số.')
            return render(request, 'khach_hang/hoi_vien_form.html', {
                'title': 'Sửa hội viên',
                'action_url': 'khach_hang:sua_hoi_vien',
                'hv': hv,
                'ds_goi_tap': ds_goi_tap,
                'form_data': request.POST,
            })

        if not _hop_le_email(email):
            messages.error(request, 'Email không đúng định dạng.')
            return render(request, 'khach_hang/hoi_vien_form.html', {
                'title': 'Sửa hội viên',
                'action_url': 'khach_hang:sua_hoi_vien',
                'hv': hv,
                'ds_goi_tap': ds_goi_tap,
                'form_data': request.POST,
            })

        if HoiVien.objects.filter(ma_hoi_vien=ma_hoi_vien).exclude(id=hv.id).exists():
            messages.error(request, 'Mã hội viên đã tồn tại.')
            return render(request, 'khach_hang/hoi_vien_form.html', {
                'title': 'Sửa hội viên',
                'action_url': 'khach_hang:sua_hoi_vien',
                'hv': hv,
                'ds_goi_tap': ds_goi_tap,
                'form_data': request.POST,
            })

        if HoiVien.objects.filter(so_dien_thoai=so_dien_thoai).exclude(id=hv.id).exists():
            messages.error(request, 'Số điện thoại đã tồn tại trong danh sách hội viên.')
            return render(request, 'khach_hang/hoi_vien_form.html', {
                'title': 'Sửa hội viên',
                'action_url': 'khach_hang:sua_hoi_vien',
                'hv': hv,
                'ds_goi_tap': ds_goi_tap,
                'form_data': request.POST,
            })

        goi_tap = GoiTap.objects.filter(id=goi_id).first() if goi_id else None

        hv.ma_hoi_vien = ma_hoi_vien
        hv.ho_ten = ho_ten
        hv.ngay_sinh = ngay_sinh
        hv.gioi_tinh = gioi_tinh
        hv.so_dien_thoai = so_dien_thoai
        hv.email = email
        hv.tinh_trang_suc_khoe = tinh_trang_suc_khoe
        hv.muc_tieu_tap_luyen = muc_tieu_tap_luyen
        hv.ghi_chu_nhan_vien = ghi_chu_nhan_vien
        hv.goi_dang_su_dung = goi_tap
        hv.ngay_het_han_goi = ngay_het_han_goi
        hv.diem_tich_luy = diem_tich_luy
        hv.save()

        messages.success(request, 'Cập nhật hội viên thành công.')
        return redirect('khach_hang:danh_sach_hoi_vien')

    return render(request, 'khach_hang/hoi_vien_form.html', {
        'title': 'Sửa hội viên',
        'action_url': 'khach_hang:sua_hoi_vien',
        'hv': hv,
        'ds_goi_tap': ds_goi_tap,
    })


def xoa_hoi_vien(request, id):
    hv = get_object_or_404(HoiVien, id=id)

    if request.method == 'POST':
        hv.delete()
        messages.success(request, 'Xóa hội viên thành công.')
    else:
        messages.error(request, 'Yêu cầu không hợp lệ.')

    return redirect('khach_hang:danh_sach_hoi_vien')


def chuyen_thanh_hoi_vien(request, id):
    khach = get_object_or_404(KhachHang, id=id)
    if request.method == 'POST':
        goi_id = request.POST.get('goi_dang_su_dung')
        ngay_het_han_goi = request.POST.get('ngay_het_han_goi') or None

        if HoiVien.objects.filter(so_dien_thoai=khach.so_dien_thoai).exists():
            messages.warning(request, 'Khách hàng này đã tồn tại trong danh sách hội viên.')
            return redirect('khach_hang:danh_sach_hoi_vien')

        goi_tap = GoiTap.objects.filter(id=goi_id).first() if goi_id else None
        ma_moi = _tao_ma_hoi_vien_tiep_theo()

        HoiVien.objects.create(
            ma_hoi_vien=ma_moi,
            ho_ten=khach.ho_ten,
            ngay_sinh=khach.ngay_sinh,
            gioi_tinh=khach.gioi_tinh or 'Khác',
            so_dien_thoai=khach.so_dien_thoai,
            email=khach.email,
            tinh_trang_suc_khoe=khach.tinh_trang_suc_khoe,
            muc_tieu_tap_luyen=khach.muc_tieu_tap_luyen,
            ghi_chu_nhan_vien=khach.ghi_chu_nhan_vien,
            goi_dang_su_dung=goi_tap,
            ngay_het_han_goi=ngay_het_han_goi,
            diem_tich_luy=0,
        )
        khach.trang_thai = 'da_chuyen_hoi_vien'
        khach.save(update_fields=['trang_thai'])

        messages.success(request, 'Chuyển khách hàng thành hội viên thành công.')
        return redirect('khach_hang:danh_sach_hoi_vien')

    return redirect('khach_hang:danh_sach_khach_hang')


def quan_ly_hoi_vien(request):
    # DS HV
    tab = request.GET.get('tab', 'danh_sach')
    q = request.GET.get('q', '').strip()
    trang_thai = request.GET.get('trang_thai', '').strip()
    ds_hoi_vien = HoiVien.objects.select_related('goi_dang_su_dung').all().order_by('-id')
    if q:
        ds_hoi_vien = ds_hoi_vien.filter(
            Q(ho_ten__icontains=q) |
            Q(so_dien_thoai__icontains=q) |
            Q(ma_hoi_vien__icontains=q)
        )

    today = timezone.now().date()
    ds_hoi_vien = list(ds_hoi_vien)
    for hv in ds_hoi_vien:
        _dong_bo_dang_ky_lich_theo_trang_thai_goi(hv, today)
        lich_su_moi_nhat = hv.lich_su_tap.order_by('-thoi_gian').first()
        hv.check_in_cuoi = lich_su_moi_nhat.thoi_gian if lich_su_moi_nhat else None
        if not hv.goi_dang_su_dung or not hv.ngay_het_han_goi:
            hv.trang_thai_goi = 'chua_co_goi'
        else:
            so_ngay_con_lai = (hv.ngay_het_han_goi - today).days
            if so_ngay_con_lai < 0:
                hv.trang_thai_goi = 'het_han'
            elif so_ngay_con_lai <= 7:
                hv.trang_thai_goi = 'sap_het_han'
            else:
                hv.trang_thai_goi = 'hoat_dong'

    if trang_thai:
        ds_hoi_vien = [hv for hv in ds_hoi_vien if hv.trang_thai_goi == trang_thai]

    selected_member_id = request.GET.get('hoi_vien_id') or request.POST.get('hoi_vien')
    selected_member = None

    if selected_member_id:
        try:
            selected_member = HoiVien.objects.select_related('goi_dang_su_dung').get(id=selected_member_id)
        except HoiVien.DoesNotExist:
            selected_member = None
    # GIA HẠN GÓI
    cap_nhat_voucher_het_han()

    if request.method == 'POST' and request.POST.get('action') == 'gia_han_goi':
        form_gia_han = GiaHanGoiForm(request.POST, hoi_vien=selected_member)

        if form_gia_han.is_valid():
            hoi_vien = form_gia_han.cleaned_data['hoi_vien']
            goi_moi = form_gia_han.cleaned_data['goi_moi']
            ngay_bat_dau = form_gia_han.cleaned_data['ngay_bat_dau']
            voucher_doi_diem = form_gia_han.cleaned_data.get('voucher_doi_diem')
            voucher_uu_dai = form_gia_han.cleaned_data.get('voucher_uu_dai')
            danh_sach_voucher = [voucher for voucher in [voucher_doi_diem, voucher_uu_dai] if voucher]

            khuyen_mai = sum((Decimal(voucher.gia_tri_giam or 0) for voucher in danh_sach_voucher), Decimal('0'))

            gia_goi = goi_moi.gia_goi or Decimal('0')
            tong_thanh_toan = gia_goi - khuyen_mai
            if tong_thanh_toan < 0:
                tong_thanh_toan = Decimal('0')

            ngay_het_han_moi = ngay_bat_dau + timedelta(days=goi_moi.thoi_han_so_buoi)
            goi_cu = hoi_vien.goi_dang_su_dung

            LichSuGiaHanGoi.objects.create(
                hoi_vien=hoi_vien,
                goi_cu=goi_cu,
                goi_moi=goi_moi,
                ngay_bat_dau=ngay_bat_dau,
                ngay_het_han_moi=ngay_het_han_moi,
                gia_goi=gia_goi,
                khuyen_mai=khuyen_mai,
                tong_thanh_toan=tong_thanh_toan
            )

            can_xoa_lich_cu = (
                not _goi_tap_con_han(hoi_vien, timezone.localdate()) or
                not goi_cu or
                goi_cu.id != goi_moi.id
            )

            hoi_vien.goi_dang_su_dung = goi_moi
            hoi_vien.ngay_het_han_goi = ngay_het_han_moi
            hoi_vien.save()

            if can_xoa_lich_cu:
                _xoa_toan_bo_dang_ky_lich(hoi_vien)

            if danh_sach_voucher:
                for voucher in danh_sach_voucher:
                    voucher.trang_thai = 'da_su_dung'
                    voucher.ngay_su_dung = timezone.now()
                    voucher.save(update_fields=['trang_thai', 'ngay_su_dung'])

                    if voucher.quang_cao_id:
                        from cham_soc_khach_hang.models import MaUuDaiHoiVien
                        MaUuDaiHoiVien.objects.filter(hoi_vien=hoi_vien, quang_cao_id=voucher.quang_cao_id).update(trang_thai='da_su_dung')

            messages.success(request, 'Gia hạn/đổi gói thành công.')
            return redirect('khach_hang:danh_sach_hoi_vien')

        hoi_vien_id_post = request.POST.get('hoi_vien')
        if hoi_vien_id_post:
            try:
                selected_member = HoiVien.objects.select_related('goi_dang_su_dung').get(id=hoi_vien_id_post)
            except HoiVien.DoesNotExist:
                selected_member = None
    else:
        initial_data = {}
        if selected_member:
            initial_data['hoi_vien'] = selected_member
        form_gia_han = GiaHanGoiForm(initial=initial_data, hoi_vien=selected_member)
    # LỊCH SỬ TẬP
    ds_lich_su_tap = LichSuTap.objects.select_related(
        'hoi_vien',
        'lop_tap'
    ).all().order_by('-thoi_gian')

    ds_check_in_hom_nay = _lay_danh_sach_check_in_hom_nay(q if tab == 'check_in' else '')

    context = {
        'tab': tab,
        'q': q,
        'trang_thai': trang_thai,
        'ds_hoi_vien': ds_hoi_vien,
        'form_gia_han': form_gia_han,
        'ds_lich_su_tap': ds_lich_su_tap,
        'selected_member': selected_member,
        'ds_goi_tap': GoiTap.objects.all().order_by('id'),
        'ds_check_in_hom_nay': ds_check_in_hom_nay,
        'thu_hom_nay': _thu_hom_nay(),
        'hom_nay': timezone.localdate(),
        'ds_voucher_doi_diem_hop_le': VoucherHoiVien.objects.filter(
            hoi_vien=selected_member,
            trang_thai='chua_su_dung',
            quang_cao__isnull=True
        ).filter(
            Q(ngay_het_han__isnull=True) | Q(ngay_het_han__gte=timezone.localdate())
        ).order_by('-ngay_tao') if selected_member else VoucherHoiVien.objects.none(),
        'ds_voucher_uu_dai_hop_le': VoucherHoiVien.objects.filter(
            hoi_vien=selected_member,
            trang_thai='chua_su_dung',
            quang_cao__isnull=False
        ).filter(
            Q(ngay_het_han__isnull=True) | Q(ngay_het_han__gte=timezone.localdate())
        ).order_by('-ngay_tao') if selected_member else VoucherHoiVien.objects.none(),
    }
    return render(request, 'khach_hang/hoi_vien.html', context)

def check_in_hoi_vien(request, id):
    hoi_vien = get_object_or_404(HoiVien, id=id)
    next_url = request.POST.get('next') or request.GET.get('next') or 'khach_hang:danh_sach_hoi_vien'

    if request.method != 'POST':
        messages.error(request, 'Yêu cầu không hợp lệ.')
        return redirect(next_url)

    today = timezone.localdate()
    thu_hom_nay = _thu_hom_nay()

    if not hoi_vien.goi_dang_su_dung:
        messages.error(request, 'Hội viên chưa có gói tập, không thể check-in.')
        return redirect(next_url)

    if hoi_vien.ngay_het_han_goi and hoi_vien.ngay_het_han_goi < today:
        _xoa_toan_bo_dang_ky_lich(hoi_vien)
        messages.error(request, 'Gói tập đã hết hạn. Hệ thống đã xóa lịch cũ, vui lòng gia hạn hoặc đăng ký gói mới rồi chọn lịch lại.')
        return redirect(next_url)

    da_check_in = LichSuTap.objects.filter(hoi_vien=hoi_vien, thoi_gian__date=today).exists()
    if da_check_in:
        messages.warning(request, f'Hội viên {hoi_vien.ho_ten} đã check-in hôm nay.')
        return redirect(next_url)

    dang_ky_hom_nay = DangKyLichHoc.objects.select_related('lich_hoc', 'lich_hoc__goi_tap').filter(hoi_vien=hoi_vien, lich_hoc__thu=thu_hom_nay).order_by('lich_hoc__gio_bat_dau').first()
    if not dang_ky_hom_nay or not dang_ky_hom_nay.lich_hoc:
        messages.error(request, f'Hội viên {hoi_vien.ho_ten} không có lịch học hôm nay nên không thể check-in.')
        return redirect(next_url)

    lop_tap = _lay_hoac_tao_lop_tap_tu_lich_hoc(dang_ky_hom_nay.lich_hoc)

    LichSuTap.objects.create(
        hoi_vien=hoi_vien,
        lop_tap=lop_tap,
        thoi_gian=timezone.now(),
        trang_thai='checkin',
        diem_cong=50
    )

    hoi_vien.diem_tich_luy += 50
    hoi_vien.check_in_cuoi = timezone.now()
    hoi_vien.save(update_fields=['diem_tich_luy', 'check_in_cuoi'])

    noi_dung_checkin = f'Check-in {lop_tap.ten_lop}' if lop_tap else 'Check-in buổi tập'
    LichSuDiem.objects.create(hoi_vien=hoi_vien, loai_giao_dich='cong', so_diem=50, noi_dung=noi_dung_checkin)

    messages.success(request, f'Check-in thành công cho {hoi_vien.ho_ten}. +50 điểm.')
    return redirect(next_url)

# CÁC HÀM DÀNH CHO KHÁCH HÀNG SỬ DỤNG

# Cho khách hàng vẵng lai

def gioi_thieu_guest(request):
    return render(request, 'khach_hang/guest/gioi_thieu.html')

def goi_tap_guest(request):
    ds_goi_tap = GoiTap.objects.filter(trang_thai='hoat_dong').order_by('ma_goi')
    context = {
        'ds_goi_tap': ds_goi_tap,
    }
    return render(request, 'khach_hang/guest/goi_tap.html', context)

def lich_tap_guest(request):
    goi_tap_id = request.GET.get('goi_tap')
    ds_goi_tap = GoiTap.objects.filter(trang_thai='hoat_dong').order_by('ma_goi')
    ds_lich = LichHoc.objects.select_related('goi_tap').filter(trang_thai=True)
    if goi_tap_id:
        ds_lich = ds_lich.filter(goi_tap_id=goi_tap_id)

    thu_data = [
        ('2', 'Thứ 2'),
        ('3', 'Thứ 3'),
        ('4', 'Thứ 4'),
        ('5', 'Thứ 5'),
        ('6', 'Thứ 6'),
        ('7', 'Thứ 7'),
        ('CN', 'Chủ nhật'),
    ]

    grouped_data = {}
    for lich in ds_lich.order_by('goi_tap__ma_goi', 'thu', 'gio_bat_dau'):
        goi = lich.goi_tap

        if goi.id not in grouped_data:
            grouped_data[goi.id] = {
                'goi': goi,
                'columns': [{'key': thu, 'label': label, 'items': []} for thu, label in thu_data]
            }

        for col in grouped_data[goi.id]['columns']:
            if col['key'] == lich.thu:
                col['items'].append(lich)
                break

    context = {
        'ds_goi_tap': ds_goi_tap,
        'grouped_data': grouped_data.values(),
        'goi_tap_id': goi_tap_id,
    }
    return render(request, 'khach_hang/guest/lich_tap.html', context)

def uu_dai_guest(request):
    hom_nay = timezone.now().date()

    ds_uu_dai = QuangCao.objects.filter(
        ngay_bat_dau__lte=hom_nay,
        ngay_ket_thuc__gte=hom_nay
    ).order_by('-ngay_bat_dau', 'ngay_ket_thuc')

    return render(request, 'khach_hang/guest/uu_dai.html', {
        'ds_uu_dai': ds_uu_dai
    })
#nhận request từ trình duyệt và trả về giao diện (HTML)
def dang_ky_tu_van_guest(request):
    #Nếu người dùng bấm nút gửi form. Dữ liệu sẽ được gửi bằng phương thức POST
    if request.method == 'POST':
        #Lấy dữ liệu người dùng nhập và đổ vào form Django
        form = DangKyTuVanGuestForm(request.POST)
        #Django sẽ kiểm tra:Có thiếu dữ liệu không, Email/SĐT có đúng định dạng không, Các rule validate trong forms.py
        if form.is_valid():
            #Nếu hợp lệ: Tạo 1 bản ghi mới trong database. Lưu thông tin khách đăng ký tư vấn
            form.save()
            messages.success(request, 'Đăng ký tư vấn thành công! Chúng tôi sẽ liên hệ với bạn trong thời gian sớm nhất.')
            #Sau khi lưu xong, chuyển hướng về trang đăng ký tư vấn để tránh việc người dùng bấm
            return redirect('khach_hang:dang_ky_tu_van_guest')
    #Nếu người dùng mới truy cập vào trang đăng ký tư vấn, hoặc có lỗi khi gửi form. Hệ thống sẽ hiển thị form để người dùng điền thông tin
    else:
        form = DangKyTuVanGuestForm()
    #Gửi dữ liệu form về template để hiển thị cho người dùng điền thông tin đăng ký tư vấn
    return render(request, 'khach_hang/guest/dang_ky_tu_van.html', {
        'form': form
    })

# Dành cho hội viên
from django.contrib.auth.decorators import login_required

def lay_hoi_vien_tu_user(user):
    if not user.is_authenticated or user.role != 'hoi_vien':
        return None

    hoi_vien = HoiVien.objects.filter(ma_hoi_vien__iexact=user.username).first()
    if hoi_vien:
        return hoi_vien

    username = (user.username or '').strip()
    match = re.match(r'^hv(\d+)$', username, re.IGNORECASE)
    if match:
        so = int(match.group(1))
        ma_chuan = f'HV{so:03d}'
        hoi_vien = HoiVien.objects.filter(ma_hoi_vien__iexact=ma_chuan).first()
        if hoi_vien:
            return hoi_vien
    if user.email:
        hoi_vien = HoiVien.objects.filter(email__iexact=user.email).first()
        if hoi_vien:
            return hoi_vien

    return None

@login_required
def gioi_thieu_hoi_vien(request):
    if request.user.role != 'hoi_vien':
        return redirect('bao_cao:tong_quan')
    return render(request, 'khach_hang/hoivien/gioi_thieu.html')

def goi_tap_hoi_vien(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn chưa đăng nhập.')
        return redirect('tai_khoan:dang_nhap')

    hoi_vien = lay_hoi_vien_tu_user(request.user)
    if not hoi_vien:
        messages.error(request, 'Không tìm thấy thông tin hội viên.')
        return redirect('khach_hang:gioi_thieu_hoi_vien')

    ds_goi = GoiTap.objects.filter(trang_thai='hoat_dong').order_by('id')
    hom_nay = timezone.now().date()
    _dong_bo_dang_ky_lich_theo_trang_thai_goi(hoi_vien, hom_nay)

    co_goi_con_han = (
        hoi_vien.goi_dang_su_dung is not None and
        hoi_vien.ngay_het_han_goi is not None and
        hoi_vien.ngay_het_han_goi >= hom_nay
    )

    return render(request, 'khach_hang/hoivien/goi_tap.html', {
        'hoi_vien': hoi_vien,
        'ds_goi': ds_goi,
        'co_goi_con_han': co_goi_con_han,
        'hom_nay': hom_nay,
    })


def dang_ky_goi_tap(request, goi_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Bạn chưa đăng nhập.')
        return redirect('tai_khoan:dang_nhap')

    hoi_vien = lay_hoi_vien_tu_user(request.user)
    if not hoi_vien:
        messages.error(request, 'Không tìm thấy thông tin hội viên.')
        return redirect('khach_hang:gioi_thieu_hoi_vien')

    goi_tap = get_object_or_404(GoiTap, id=goi_id, trang_thai='hoat_dong')
    hom_nay = timezone.now().date()
    if (
        hoi_vien.goi_dang_su_dung is not None and
        hoi_vien.ngay_het_han_goi is not None and
        hoi_vien.ngay_het_han_goi >= hom_nay
    ):
        messages.error(request, 'Bạn đang có gói tập còn hiệu lực, không thể đăng ký thêm.')
        return redirect('khach_hang:goi_tap_hoi_vien')

    if request.method == 'POST':
        ngay_bat_dau_str = request.POST.get('ngay_bat_dau')
        if not ngay_bat_dau_str:
            messages.error(request, 'Vui lòng chọn ngày bắt đầu hiệu lực.')
            return redirect('khach_hang:dang_ky_goi_tap', goi_id=goi_id)

        ngay_bat_dau = timezone.datetime.strptime(ngay_bat_dau_str, '%Y-%m-%d').date()

        if goi_tap.loai_goi == 'thang':
            ngay_het_han = ngay_bat_dau + timedelta(days=30 * goi_tap.thoi_han_so_buoi)
        else:
            ngay_het_han = ngay_bat_dau

        goi_cu = hoi_vien.goi_dang_su_dung
        can_xoa_lich_cu = (
            not _goi_tap_con_han(hoi_vien, hom_nay) or
            not goi_cu or
            goi_cu.id != goi_tap.id
        )

        hoi_vien.goi_dang_su_dung = goi_tap
        hoi_vien.ngay_het_han_goi = ngay_het_han
        hoi_vien.save()

        if can_xoa_lich_cu:
            _xoa_toan_bo_dang_ky_lich(hoi_vien)

        LichSuGiaHanGoi.objects.create(
            hoi_vien=hoi_vien,
            goi_cu=goi_cu,
            goi_moi=goi_tap,
            ngay_bat_dau=ngay_bat_dau,
            ngay_het_han_moi=ngay_het_han,
            gia_goi=goi_tap.gia_goi,
            khuyen_mai=0,
            tong_thanh_toan=goi_tap.gia_goi
        )

        messages.success(request, 'Đăng ký gói tập thành công!')
        return redirect('khach_hang:goi_tap_hoi_vien')
    return render(request, 'khach_hang/hoivien/xac_nhan_dang_ky_goi.html', {
        'hoi_vien': hoi_vien,
        'goi_tap': goi_tap,
        'hom_nay': hom_nay,
    })