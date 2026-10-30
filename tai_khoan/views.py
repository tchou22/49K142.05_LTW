from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from django.shortcuts import render, redirect
from tai_khoan.models import User


def dieu_huong_sau_dang_nhap(user):
    if user.role == 'hoi_vien':
        return 'khach_hang:gioi_thieu_hoi_vien'
    elif user.role in ['chu', 'nhan_vien', 'hlv']:
        return 'bao_cao:tong_quan'
    return 'khach_hang:gioi_thieu_guest'


def dang_nhap_view(request):
    if request.user.is_authenticated:
        return redirect(dieu_huong_sau_dang_nhap(request.user))

    if request.method == 'POST':
        login_input = request.POST.get('username')
        password = request.POST.get('password')

        username = login_input

        try:
            user_obj = User.objects.get(email=login_input)
            username = user_obj.username
        except User.DoesNotExist:
            pass
        except User.MultipleObjectsReturned:
            messages.error(request, 'Email đang bị trùng trong hệ thống. Vui lòng liên hệ quản trị viên.')
            return render(request, 'tai_khoan/dang_nhap.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect(dieu_huong_sau_dang_nhap(user))
        else:
            messages.error(request, 'Email hoặc mật khẩu không đúng!')

    return render(request, 'tai_khoan/dang_nhap.html')


@login_required
def dang_xuat_view(request):
    logout(request)
    return redirect('khach_hang:gioi_thieu_guest')


@login_required
def doi_mat_khau_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Đổi mật khẩu thành công.')
            return redirect(dieu_huong_sau_dang_nhap(user))
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'tai_khoan/doi_mat_khau.html', {'form': form})