from django import forms
from django.db.models import Q
from django.utils import timezone
from .models import HoiVien, LichSuTap
from goi_tap.models import GoiTap
from cham_soc_khach_hang.models import YeuCauTuVan
from tich_diem.models import VoucherHoiVien, cap_nhat_voucher_het_han


class GiaHanGoiForm(forms.Form):
    hoi_vien = forms.ModelChoiceField(
        queryset=HoiVien.objects.all(),
        label="Chọn hội viên"
    )
    goi_moi = forms.ModelChoiceField(
        queryset=GoiTap.objects.all(),
        label="Gói tập mới"
    )
    ngay_bat_dau = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Ngày bắt đầu"
    )
    voucher_doi_diem = forms.ModelChoiceField(
        queryset=VoucherHoiVien.objects.none(),
        required=False,
        empty_label="Không áp voucher đổi điểm",
        label="Voucher đổi điểm"
    )
    voucher_uu_dai = forms.ModelChoiceField(
        queryset=VoucherHoiVien.objects.none(),
        required=False,
        empty_label="Không áp voucher ưu đãi",
        label="Voucher ưu đãi"
    )

    def __init__(self, *args, **kwargs):
        hoi_vien = kwargs.pop('hoi_vien', None)
        super().__init__(*args, **kwargs)
        cap_nhat_voucher_het_han()
        hom_nay = timezone.localdate()
        qs = VoucherHoiVien.objects.filter(
            trang_thai='chua_su_dung'
        ).filter(
            Q(ngay_het_han__isnull=True) | Q(ngay_het_han__gte=hom_nay)
        ).order_by('-ngay_tao')
        if hoi_vien:
            qs = qs.filter(hoi_vien=hoi_vien)
        else:
            qs = VoucherHoiVien.objects.none()
        self.fields['voucher_doi_diem'].queryset = qs.filter(quang_cao__isnull=True)
        self.fields['voucher_uu_dai'].queryset = qs.filter(quang_cao__isnull=False)

    def clean(self):
        cleaned_data = super().clean()
        hoi_vien = cleaned_data.get('hoi_vien')
        voucher_doi_diem = cleaned_data.get('voucher_doi_diem')
        voucher_uu_dai = cleaned_data.get('voucher_uu_dai')

        if voucher_doi_diem and hoi_vien and voucher_doi_diem.hoi_vien_id != hoi_vien.id:
            self.add_error('voucher_doi_diem', 'Voucher đổi điểm không thuộc hội viên đã chọn.')

        if voucher_uu_dai and hoi_vien and voucher_uu_dai.hoi_vien_id != hoi_vien.id:
            self.add_error('voucher_uu_dai', 'Voucher ưu đãi không thuộc hội viên đã chọn.')

        return cleaned_data


class LocLichSuTapForm(forms.Form):
    ten_hoi_vien = forms.CharField(required=False)
    tu_ngay = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    den_ngay = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})

    )


class DangKyTuVanGuestForm(forms.ModelForm):
    ho_ten = forms.CharField(
        max_length=100,
        label="Họ và tên",
        widget=forms.TextInput(attrs={
            'placeholder': 'Ví dụ: Nguyễn Văn A'
        })
    )

    email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Ví dụ: nguyenvana@gmail.com'
        })
    )

    goi_tap_quan_tam = forms.ModelChoiceField(
        queryset=GoiTap.objects.filter(trang_thai='hoat_dong').order_by('ten_goi'),
        required=False,
        empty_label="Chọn dịch vụ bạn muốn tư vấn",
        label="Dịch vụ quan tâm"
    )

    class Meta:
        model = YeuCauTuVan
        fields = ['so_dien_thoai', 'noi_dung']
        labels = {
            'so_dien_thoai': 'Số điện thoại',
            'noi_dung': 'Nội dung cần tư vấn / Mục tiêu',
        }
        widgets = {
            'so_dien_thoai': forms.TextInput(attrs={
                'placeholder': '09xxxxxxxx',
                'inputmode': 'numeric',
                'pattern': r'\d{10}',
                'maxlength': '10',
                'title': 'Số điện thoại phải gồm đúng 10 chữ số'
            }),
            'noi_dung': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Ví dụ: Tôi muốn giảm cân, rảnh vào buổi tối...'
            }),
        }

    def clean_so_dien_thoai(self):
        so_dien_thoai = (self.cleaned_data.get('so_dien_thoai') or '').strip()

        if not so_dien_thoai:
            raise forms.ValidationError('Vui lòng nhập số điện thoại.')

        if not so_dien_thoai.isdigit():
            raise forms.ValidationError('Số điện thoại chỉ được chứa chữ số.')

        if len(so_dien_thoai) != 10:
            raise forms.ValidationError('Số điện thoại phải gồm đúng 10 chữ số.')

        return so_dien_thoai

    def save(self, commit=True):
        instance = super().save(commit=False)

        instance.ho_ten = self.cleaned_data.get('ho_ten')
        instance.email = self.cleaned_data.get('email')

        goi_tap = self.cleaned_data.get('goi_tap_quan_tam')
        instance.dich_vu_quan_tam = goi_tap.ten_goi if goi_tap else ''

        instance.noi_dung = self.cleaned_data.get('noi_dung', '')

        if not instance.trang_thai:
            instance.trang_thai = 'moi'

        if commit:
            instance.save()
        return instance
