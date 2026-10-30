from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from khach_hang.models import HoiVien
from lich_tap.models import DangKyLichHoc
from .models import ThongBaoNhacNho


@login_required
def quan_ly_thong_bao(request):
    q = request.GET.get('q', '').strip()
    hoi_vien_id = request.GET.get('hoi_vien_id')
    ds_hoi_vien = HoiVien.objects.all().order_by('ho_ten')
    if q:
        ds_hoi_vien = ds_hoi_vien.filter(ho_ten__icontains=q)

    hoi_vien_duoc_chon = None
    dang_ky_gan_nhat = None
    noi_dung_mac_dinh = ''
    lich_su_gui = ThongBaoNhacNho.objects.none()

    if hoi_vien_id:
        hoi_vien_duoc_chon = get_object_or_404(HoiVien, id=hoi_vien_id)

        dang_ky_gan_nhat = (
            DangKyLichHoc.objects
            .select_related('lich_hoc')
            .filter(hoi_vien=hoi_vien_duoc_chon)
            .order_by('-id')
            .first()
        )

        if dang_ky_gan_nhat and dang_ky_gan_nhat.lich_hoc:
            lich = dang_ky_gan_nhat.lich_hoc
            ten_lop = getattr(lich, 'khoa_hoc', 'Lớp học')
            gio_bat_dau = lich.gio_bat_dau.strftime('%H:%M') if lich.gio_bat_dau else ''
            ngay_hoc = getattr(dang_ky_gan_nhat, 'ngay_hoc', None)

            if ngay_hoc:
                ngay_text = ngay_hoc.strftime('%d/%m/%Y')
                noi_dung_mac_dinh = (
                    f"Namaste {hoi_vien_duoc_chon.ho_ten}! "
                    f"Đừng quên bạn có lịch tập lớp {ten_lop} vào lúc {gio_bat_dau} "
                    f"ngày {ngay_text} tại Flying Yoga. Hẹn gặp lại bạn!"
                )
            else:
                thu = getattr(lich, 'thu', '')
                noi_dung_mac_dinh = (
                    f"Namaste {hoi_vien_duoc_chon.ho_ten}! "
                    f"Đừng quên bạn có lịch tập lớp {ten_lop} vào lúc {gio_bat_dau} "
                    f"{('thứ ' + str(thu)) if thu else ''} tại Flying Yoga. Hẹn gặp lại bạn!"
                )
        else:
            noi_dung_mac_dinh = (
                f"Namaste {hoi_vien_duoc_chon.ho_ten}! "
                f"Bạn có thông báo mới từ Flying Yoga. Vui lòng kiểm tra lịch tập của mình nhé!"
            )

        lich_su_gui = (
            ThongBaoNhacNho.objects
            .filter(hoi_vien=hoi_vien_duoc_chon)
            .order_by('-thoi_gian_gui')
        )

    if request.method == 'POST':
        hoi_vien_id_post = request.POST.get('hoi_vien_id')
        noi_dung = request.POST.get('noi_dung', '').strip()
        tieu_de = request.POST.get('tieu_de', '').strip()
        kenh_gui = request.POST.get('kenh_gui', 'web')

        hoi_vien = get_object_or_404(HoiVien, id=hoi_vien_id_post)

        dang_ky_gan_nhat = (
            DangKyLichHoc.objects
            .select_related('lich_hoc')
            .filter(hoi_vien=hoi_vien)
            .order_by('-id')
            .first()
        )

        if not noi_dung:
            messages.error(request, 'Nội dung thông báo không được để trống.')
            return redirect(f"{request.path}?hoi_vien_id={hoi_vien.id}")

        ThongBaoNhacNho.objects.create(
            hoi_vien=hoi_vien,
            dang_ky_lich=dang_ky_gan_nhat,
            tieu_de=tieu_de,
            noi_dung=noi_dung,
            kenh_gui=kenh_gui,
            thoi_gian_gui=timezone.now()
        )

        messages.success(request, 'Gửi thông báo thành công!')
        return redirect(f"{request.path}?hoi_vien_id={hoi_vien.id}")

    context = {
        'q': q,
        'ds_hoi_vien': ds_hoi_vien,
        'hoi_vien_duoc_chon': hoi_vien_duoc_chon,
        'dang_ky_gan_nhat': dang_ky_gan_nhat,
        'noi_dung_mac_dinh': noi_dung_mac_dinh,
        'lich_su_gui': lich_su_gui,
    }
    return render(request, 'thong_bao/quan_ly_thong_bao.html', context)


@login_required
def danh_sach_thong_bao(request):
    hoi_vien = HoiVien.objects.filter(ma_hoi_vien=request.user.username).first()
    ds_thong_bao = ThongBaoNhacNho.objects.none()

    if hoi_vien:
        loc = request.GET.get('loc', 'tat_ca')
        ds_thong_bao = ThongBaoNhacNho.objects.filter(
            hoi_vien=hoi_vien,
            kenh_gui='web'
        ).order_by('-thoi_gian_gui')

        if loc == 'chua_doc':
            ds_thong_bao = ds_thong_bao.filter(da_doc=False)
    else:
        loc = 'tat_ca'

    return render(request, 'thong_bao/hoi_vien/danh_sach_thong_bao.html', {
        'ds_thong_bao': ds_thong_bao,
        'loc_hien_tai': loc,
    })


@login_required
def danh_dau_da_doc(request, thong_bao_id):
    hoi_vien = HoiVien.objects.filter(ma_hoi_vien=request.user.username).first()

    if not hoi_vien:
        return JsonResponse({'success': False, 'message': 'Không tìm thấy hội viên'}, status=403)

    thong_bao = get_object_or_404(
        ThongBaoNhacNho,
        id=thong_bao_id,
        hoi_vien=hoi_vien
    )

    thong_bao.da_doc = True
    thong_bao.save(update_fields=['da_doc'])

    return JsonResponse({'success': True})

@login_required
def mo_thong_bao(request, id):
    hoi_vien = get_object_or_404(HoiVien, ma_hoi_vien=request.user.username)
    thong_bao = get_object_or_404(ThongBaoNhacNho, id=id, hoi_vien=hoi_vien)

    thong_bao.da_doc = True
    thong_bao.save()

    if thong_bao.loai_thong_bao == 'phan_hoi_khieu_nai' and thong_bao.phan_hoi_khieu_nai:
        return redirect('cham_soc_khach_hang:xem_phan_hoi_hoi_vien', id=thong_bao.phan_hoi_khieu_nai.id)

    return redirect('thong_bao:danh_sach_thong_bao')