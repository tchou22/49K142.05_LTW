from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from khach_hang.models import HoiVien
from thong_bao.models import ThongBaoNhacNho

from .models import (
    YeuCauTuVan,
    KhieuNaiPhanHoi,
    TinNhanKhieuNai,
    QuangCao,
    MaUuDaiHoiVien
)
from .forms import (
    YeuCauTuVanForm,
    CapNhatTuVanForm,
    KhieuNaiPhanHoiForm,
    TraLoiPhanHoiForm,
    QuangCaoForm,
    YeuCauTuVanHoiVienForm,
)


def gui_yeu_cau_tu_van(request):
    if request.method == 'POST':
        form = YeuCauTuVanForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gửi yêu cầu tư vấn thành công!')
            return redirect('cham_soc_khach_hang:gui_yeu_cau_tu_van')
    else:
        form = YeuCauTuVanForm()

    return render(request, 'cham_soc_khach_hang/gui_yeu_cau_tu_van.html', {
        'form': form
    })


def danh_sach_yeu_cau_tu_van(request):
    ds_yeu_cau = YeuCauTuVan.objects.all().order_by('-ngay_gui')

    q = request.GET.get('q', '').strip()
    trang_thai = request.GET.get('trang_thai', '').strip()

    if q:
        ds_yeu_cau = ds_yeu_cau.filter(
            Q(ma_yeu_cau__icontains=q) |
            Q(ho_ten__icontains=q) |
            Q(so_dien_thoai__icontains=q) |
            Q(dich_vu_quan_tam__icontains=q)
        )

    if trang_thai:
        ds_yeu_cau = ds_yeu_cau.filter(trang_thai=trang_thai)

    tong_moi = YeuCauTuVan.objects.filter(trang_thai='moi').count()
    tong_dang = YeuCauTuVan.objects.filter(trang_thai='dang').count()
    tong_xong = YeuCauTuVan.objects.filter(trang_thai='xong').count()

    return render(request, 'cham_soc_khach_hang/danh_sach_yeu_cau_tu_van.html', {
        'ds_yeu_cau': ds_yeu_cau,
        'q': q,
        'trang_thai': trang_thai,
        'tong_moi': tong_moi,
        'tong_dang': tong_dang,
        'tong_xong': tong_xong,
    })


def cap_nhat_tu_van(request, id):
    yeu_cau = get_object_or_404(YeuCauTuVan, id=id)

    if request.method == 'POST':
        form = CapNhatTuVanForm(request.POST, instance=yeu_cau)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.trang_thai = 'xong'
            obj.save()
            messages.success(request, 'Cập nhật tư vấn thành công!')
            return redirect('cham_soc_khach_hang:danh_sach_yeu_cau_tu_van')
    else:
        form = CapNhatTuVanForm(instance=yeu_cau)

    return render(request, 'cham_soc_khach_hang/cap_nhat_tu_van.html', {
        'form': form,
        'yeu_cau': yeu_cau
    })


@login_required
def tao_phan_hoi_khieu_nai(request):
    hoi_vien = get_object_or_404(HoiVien, ma_hoi_vien=request.user.username)

    if request.method == 'POST':
        form = KhieuNaiPhanHoiForm(request.POST)
        if form.is_valid():
            phan_hoi = form.save(commit=False)
            phan_hoi.hoi_vien = hoi_vien
            phan_hoi.trang_thai = 'moi_tiep_nhan'
            phan_hoi.save()

            messages.success(request, 'Gửi góp ý / khiếu nại thành công!')
            return redirect('cham_soc_khach_hang:xem_phan_hoi_hoi_vien', id=phan_hoi.id)
    else:
        form = KhieuNaiPhanHoiForm()

    return render(request, 'cham_soc_khach_hang/hoi_vien/tao_phan_hoi_khieu_nai.html', {
        'form': form,
        'hoi_vien': hoi_vien,
    })

def danh_sach_phan_hoi_khieu_nai(request):
    ds_phan_hoi = KhieuNaiPhanHoi.objects.select_related('hoi_vien').all().order_by('-ngay_gui')

    q = request.GET.get('q', '').strip()
    chu_de = request.GET.get('chu_de', '').strip()
    trang_thai = request.GET.get('trang_thai', '').strip()

    if q:
        ds_phan_hoi = ds_phan_hoi.filter(
            Q(hoi_vien__ho_ten__icontains=q) |
            Q(hoi_vien__so_dien_thoai__icontains=q) |
            Q(noi_dung_khach__icontains=q) |
            Q(mo_ta_van_de_khac__icontains=q)
        )

    if chu_de:
        ds_phan_hoi = ds_phan_hoi.filter(chu_de=chu_de)

    if trang_thai:
        ds_phan_hoi = ds_phan_hoi.filter(trang_thai=trang_thai)

    tong_tat_ca = KhieuNaiPhanHoi.objects.count()
    tong_moi_tiep_nhan = KhieuNaiPhanHoi.objects.filter(trang_thai='moi_tiep_nhan').count()
    tong_dang_trao_doi = KhieuNaiPhanHoi.objects.filter(trang_thai='dang_trao_doi').count()
    tong_da_xu_ly = KhieuNaiPhanHoi.objects.filter(trang_thai='da_xu_ly').count()
    tong_da_dong = KhieuNaiPhanHoi.objects.filter(trang_thai='da_dong').count()

    return render(request, 'cham_soc_khach_hang/danh_sach_phan_hoi_khieu_nai.html', {
        'ds_phan_hoi': ds_phan_hoi,
        'q': q,
        'chu_de': chu_de,
        'trang_thai': trang_thai,
        'chu_de_choices': KhieuNaiPhanHoi.CHU_DE,
        'trang_thai_choices': KhieuNaiPhanHoi.TRANG_THAI,
        'tong_tat_ca': tong_tat_ca,
        'tong_moi_tiep_nhan': tong_moi_tiep_nhan,
        'tong_dang_trao_doi': tong_dang_trao_doi,
        'tong_da_xu_ly': tong_da_xu_ly,
        'tong_da_dong': tong_da_dong,
    })


def cap_nhat_phan_hoi_khieu_nai(request, id):
    phan_hoi = get_object_or_404(KhieuNaiPhanHoi, id=id)

    tra_loi_cu = (phan_hoi.tra_loi_nhan_vien or '').strip()

    if request.method == 'POST':
        form = TraLoiPhanHoiForm(request.POST, instance=phan_hoi)

        if form.is_valid():
            phan_hoi = form.save(commit=False)
            tra_loi_moi = (phan_hoi.tra_loi_nhan_vien or '').strip()

            co_noi_dung_tra_loi_moi = bool(tra_loi_moi and tra_loi_moi != tra_loi_cu)

            if tra_loi_moi:
                phan_hoi.trang_thai = 'da_xu_ly'
                phan_hoi.ngay_phan_hoi = timezone.now()

            phan_hoi.save()

            if co_noi_dung_tra_loi_moi:
                ThongBaoNhacNho.objects.create(
                    hoi_vien=phan_hoi.hoi_vien,
                    tieu_de='Bạn đã nhận được phản hồi mới',
                    noi_dung=f"Flying Yoga đã phản hồi nội dung thuộc chủ đề '{phan_hoi.get_chu_de_display()}'.",
                    kenh_gui='web',
                    loai_thong_bao='phan_hoi_khieu_nai',
                    phan_hoi_khieu_nai=phan_hoi
                )

            messages.success(request, 'Cập nhật phản hồi thành công!')
            return redirect('cham_soc_khach_hang:danh_sach_phan_hoi_khieu_nai')
        else:
            messages.error(request, form.errors)

    else:
        form = TraLoiPhanHoiForm(instance=phan_hoi)

    tin_nhan = phan_hoi.ds_tin_nhan.all().order_by('thoi_gian_gui')

    return render(request, 'cham_soc_khach_hang/cap_nhat_phan_hoi_khieu_nai.html', {
        'form': form,
        'phan_hoi': phan_hoi,
        'tin_nhan': tin_nhan,
    })

def gui_tin_nhan_nhan_vien(request, id):
    phan_hoi = get_object_or_404(KhieuNaiPhanHoi, id=id)

    if request.method == 'POST':
        noi_dung = request.POST.get('noi_dung', '').strip()

        if noi_dung:
            TinNhanKhieuNai.objects.create(
                khieu_nai=phan_hoi,
                nguoi_gui='nhan_vien',
                noi_dung=noi_dung
            )

            phan_hoi.tra_loi_nhan_vien = noi_dung
            phan_hoi.ngay_phan_hoi = timezone.now()
            phan_hoi.trang_thai = 'dang_trao_doi'
            phan_hoi.save()

            ThongBaoNhacNho.objects.create(
                hoi_vien=phan_hoi.hoi_vien,
                tieu_de='Bạn đã nhận được phản hồi mới',
                noi_dung=f"Flying Yoga đã phản hồi nội dung thuộc chủ đề '{phan_hoi.get_chu_de_display()}'.",
                kenh_gui='web',
                loai_thong_bao='phan_hoi_khieu_nai',
                phan_hoi_khieu_nai=phan_hoi
            )

            messages.success(request, 'Đã gửi phản hồi tiếp cho hội viên.')
        else:
            messages.error(request, 'Vui lòng nhập nội dung phản hồi.')

    return redirect('cham_soc_khach_hang:cap_nhat_phan_hoi_khieu_nai', id=phan_hoi.id)


def danh_sach_quang_cao(request):
    q = request.GET.get('q', '').strip()
    trang_thai = request.GET.get('trang_thai', '').strip()

    danh_sach = QuangCao.objects.all().order_by('-ngay_tao')

    if q:
        danh_sach = danh_sach.filter(ten_chuong_trinh__icontains=q)

    if trang_thai:
        danh_sach = danh_sach.filter(trang_thai=trang_thai)

    return render(request, 'quang_cao/danh_sach_quang_cao.html', {
        'danh_sach': danh_sach,
        'q': q,
        'trang_thai': trang_thai,
    })


def them_quang_cao(request):
    if request.method == 'POST':
        form = QuangCaoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thêm chương trình quảng cáo thành công!')
            return redirect('cham_soc_khach_hang:danh_sach_quang_cao')
    else:
        form = QuangCaoForm()

    return render(request, 'quang_cao/them_quang_cao.html', {'form': form})


def xem_quang_cao(request, id):
    quang_cao = get_object_or_404(QuangCao, id=id)
    quang_cao.cap_nhat_trang_thai()
    quang_cao.save()
    return render(request, 'quang_cao/xem_quang_cao.html', {'quang_cao': quang_cao})


def xoa_quang_cao(request, id):
    quang_cao = get_object_or_404(QuangCao, id=id)
    quang_cao.delete()
    messages.success(request, 'Xóa chương trình quảng cáo thành công!')
    return redirect('cham_soc_khach_hang:danh_sach_quang_cao')


def gui_quang_cao(request, id):
    quang_cao = get_object_or_404(QuangCao, id=id)
    quang_cao.da_gui = True
    quang_cao.save()
    messages.success(request, f'Đã gửi chương trình "{quang_cao.ten_chuong_trinh}" thành công!')
    return redirect('cham_soc_khach_hang:danh_sach_quang_cao')


@login_required
def danh_sach_uu_dai_hoi_vien(request):
    today = timezone.localdate()
    hoi_vien = get_object_or_404(HoiVien, ma_hoi_vien=request.user.username)

    danh_sach = QuangCao.objects.filter(
        da_gui=True,
        ngay_bat_dau__lte=today,
        ngay_ket_thuc__gte=today
    ).order_by('-ngay_tao')

    uu_dai_da_luu_ids = set(
        MaUuDaiHoiVien.objects.filter(
            hoi_vien=hoi_vien
        ).values_list('quang_cao_id', flat=True)
    )

    return render(request, 'quang_cao/hoivien/uu_dai.html', {
        'danh_sach': danh_sach,
        'uu_dai_da_luu_ids': uu_dai_da_luu_ids,
    })


@login_required
def luu_ma_uu_dai(request, id):
    today = timezone.localdate()
    hoi_vien = get_object_or_404(HoiVien, ma_hoi_vien=request.user.username)
    quang_cao = get_object_or_404(QuangCao, id=id)

    if not quang_cao.da_gui:
        messages.error(request, 'Ưu đãi này chưa được phát hành.')
        return redirect('cham_soc_khach_hang:danh_sach_uu_dai_hoi_vien')

    if quang_cao.ngay_bat_dau > today or quang_cao.ngay_ket_thuc < today:
        messages.error(request, 'Ưu đãi này đã hết hạn hoặc chưa tới thời gian áp dụng.')
        return redirect('cham_soc_khach_hang:danh_sach_uu_dai_hoi_vien')

    da_luu = MaUuDaiHoiVien.objects.filter(
        hoi_vien=hoi_vien,
        quang_cao=quang_cao
    ).exists()

    if da_luu:
        messages.warning(request, 'Bạn đã lưu mã ưu đãi này rồi.')
        return redirect('cham_soc_khach_hang:danh_sach_uu_dai_hoi_vien')

    MaUuDaiHoiVien.objects.create(
        hoi_vien=hoi_vien,
        quang_cao=quang_cao,
        trang_thai='da_luu'
    )

    messages.success(request, 'Lưu mã ưu đãi thành công!')
    return redirect('cham_soc_khach_hang:danh_sach_uu_dai_hoi_vien')


@login_required
def dang_ky_tu_van_hoi_vien(request):
    hoi_vien = get_object_or_404(HoiVien, ma_hoi_vien=request.user.username)

    if request.method == 'POST':
        form = YeuCauTuVanHoiVienForm(request.POST)
        if form.is_valid():
            yeu_cau = form.save(commit=False)
            yeu_cau.ho_ten = hoi_vien.ho_ten
            yeu_cau.so_dien_thoai = hoi_vien.so_dien_thoai
            yeu_cau.save()

            messages.success(request, 'Đăng ký tư vấn thành công! Chúng tôi sẽ liên hệ lại trong vòng 30 phút.')
            return redirect('cham_soc_khach_hang:dang_ky_tu_van_hoi_vien')
    else:
        form = YeuCauTuVanHoiVienForm(initial={
            'ho_ten': hoi_vien.ho_ten,
            'so_dien_thoai': hoi_vien.so_dien_thoai,
        })

    return render(request, 'quang_cao/hoivien/dang_ky_tu_van.html', {
        'form': form,
        'hoi_vien': hoi_vien,
    })


@login_required
def xem_phan_hoi_hoi_vien(request, id):
    hoi_vien = get_object_or_404(HoiVien, ma_hoi_vien=request.user.username)
    phan_hoi = get_object_or_404(KhieuNaiPhanHoi, id=id, hoi_vien=hoi_vien)

    if request.method == 'POST':
        noi_dung = request.POST.get('noi_dung', '').strip()

        if noi_dung:
            TinNhanKhieuNai.objects.create(
                khieu_nai=phan_hoi,
                nguoi_gui='hoi_vien',
                noi_dung=noi_dung
            )

            phan_hoi.trang_thai = 'dang_trao_doi'
            phan_hoi.save()

            messages.success(request, 'Đã gửi nội dung trao đổi tiếp cho nhân viên.')
            return redirect('cham_soc_khach_hang:xem_phan_hoi_hoi_vien', id=phan_hoi.id)
        else:
            messages.error(request, 'Vui lòng nhập nội dung trước khi gửi.')

    tin_nhan = phan_hoi.ds_tin_nhan.all().order_by('thoi_gian_gui')

    return render(request, 'cham_soc_khach_hang/hoi_vien/xem_phan_hoi_hoi_vien.html', {
        'phan_hoi': phan_hoi,
        'tin_nhan': tin_nhan
    })