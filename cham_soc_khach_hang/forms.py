from decimal import Decimal

from django import forms
from .models import YeuCauTuVan, KhieuNaiPhanHoi, QuangCao

# bỏ
class YeuCauTuVanForm(forms.ModelForm):
    class Meta:
        model = YeuCauTuVan
        fields = ['ho_ten', 'so_dien_thoai', 'email', 'dich_vu_quan_tam', 'noi_dung']
        widgets = {
            'ho_ten': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập họ và tên'
            }),
            'so_dien_thoai': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập số điện thoại',
                'inputmode': 'numeric',
                'pattern': r'\d{10}',
                'maxlength': '10',
                'title': 'Số điện thoại phải gồm đúng 10 chữ số'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập email'
            }),
            'dich_vu_quan_tam': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: Yoga cơ bản, PT 1-1, Gói 12 tháng...'
            }),
            'noi_dung': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập nội dung cần tư vấn',
                'rows': 5
            }),
        }

    def clean_so_dien_thoai(self):
        sdt = self.cleaned_data.get('so_dien_thoai', '').strip()
        if not sdt.isdigit():
            raise forms.ValidationError("Số điện thoại chỉ được chứa chữ số.")
        if len(sdt) != 10:
            raise forms.ValidationError("Số điện thoại phải gồm đúng 10 chữ số.")
        return sdt
# bỏ

class CapNhatTuVanForm(forms.ModelForm):
    hen_lien_he_lai = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={'class': 'form-control', 'type': 'datetime-local'},
            format='%Y-%m-%dT%H:%M'
        ),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = YeuCauTuVan
        fields = ['trang_thai', 'ghi_chu_tu_van', 'hen_lien_he_lai']
        widgets = {
            'trang_thai': forms.Select(attrs={'class': 'form-control'}),
            'ghi_chu_tu_van': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: Khách quan tâm gói 3 tháng, rảnh buổi chiều...',
                'rows': 4
            }),
        }


class KhieuNaiPhanHoiForm(forms.ModelForm):
    class Meta:
        model = KhieuNaiPhanHoi
        fields = ['chu_de', 'mo_ta_van_de_khac', 'noi_dung_khach']
        widgets = {
            'chu_de': forms.Select(attrs={'class': 'form-control'}),
            'mo_ta_van_de_khac': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập vấn đề khác'
            }),
            'noi_dung_khach': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập nội dung góp ý / khiếu nại',
                'rows': 5
            }),
        }
        labels = {
            'chu_de': 'Bạn muốn viết về điều gì?',
            'mo_ta_van_de_khac': 'Mô tả vấn đề khác',
            'noi_dung_khach': 'Nội dung',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['chu_de'].choices = [('', '--- Chọn vấn đề ---')] + list(KhieuNaiPhanHoi.CHU_DE)
        self.fields['mo_ta_van_de_khac'].required = False

    def clean(self):
        cleaned_data = super().clean()
        chu_de = cleaned_data.get('chu_de')
        mo_ta_van_de_khac = cleaned_data.get('mo_ta_van_de_khac')

        if chu_de == 'van_de_khac' and not (mo_ta_van_de_khac or '').strip():
            self.add_error('mo_ta_van_de_khac', 'Vui lòng nhập mô tả cho mục Vấn đề khác.')

        return cleaned_data

class TraLoiPhanHoiForm(forms.ModelForm):
    class Meta:
        model = KhieuNaiPhanHoi
        fields = ['mo_ta_van_de_khac', 'tra_loi_nhan_vien']
        widgets = {
            'mo_ta_van_de_khac': forms.HiddenInput(),
            'tra_loi_nhan_vien': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Nhập nội dung phản hồi cho hội viên...'
            }),
        }
        labels = {
            'tra_loi_nhan_vien': 'Phản hồi của nhân viên',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mo_ta_van_de_khac'].required = False

        if self.instance and self.instance.pk:
            self.fields['mo_ta_van_de_khac'].initial = self.instance.mo_ta_van_de_khac

    def clean(self):
        cleaned_data = super().clean()

        if self.instance and self.instance.chu_de == 'van_de_khac':
            mo_ta = cleaned_data.get('mo_ta_van_de_khac')
            if not (mo_ta or '').strip():
                cleaned_data['mo_ta_van_de_khac'] = self.instance.mo_ta_van_de_khac or 'Dữ liệu cũ chưa phân loại'

        return cleaned_data

class QuangCaoForm(forms.ModelForm):
    class Meta:
        model = QuangCao
        fields = ['ten_chuong_trinh', 'noi_dung', 'la_voucher', 'ma_uu_dai', 'gia_tri_giam', 'ngay_bat_dau', 'ngay_ket_thuc']
        widgets = {
            'ten_chuong_trinh': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập tên chương trình'
            }),
            'noi_dung': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Nhập nội dung chương trình',
                'rows': 5
            }),
            'la_voucher': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'ma_uu_dai': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: FLY50K'
            }),
            'gia_tri_giam': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ví dụ: 50000',
                'min': '0'
            }),
            'ngay_bat_dau': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'ngay_ket_thuc': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        ngay_bat_dau = cleaned_data.get('ngay_bat_dau')
        ngay_ket_thuc = cleaned_data.get('ngay_ket_thuc')
        la_voucher = cleaned_data.get('la_voucher')
        ma_uu_dai = (cleaned_data.get('ma_uu_dai') or '').strip().upper()
        gia_tri_giam = cleaned_data.get('gia_tri_giam') or Decimal('0')

        if ngay_bat_dau and ngay_ket_thuc and ngay_ket_thuc < ngay_bat_dau:
            raise forms.ValidationError("Ngày kết thúc phải lớn hơn hoặc bằng ngày bắt đầu.")

        if la_voucher:
            if not ma_uu_dai:
                self.add_error('ma_uu_dai', 'Vui lòng nhập mã ưu đãi cho chương trình voucher.')
            if gia_tri_giam <= 0:
                self.add_error('gia_tri_giam', 'Giá trị giảm phải lớn hơn 0.')
            if ma_uu_dai:
                qs = QuangCao.objects.filter(ma_uu_dai__iexact=ma_uu_dai)
                if self.instance.pk:
                    qs = qs.exclude(pk=self.instance.pk)
                if qs.exists():
                    self.add_error('ma_uu_dai', 'Mã ưu đãi này đã tồn tại.')
        else:
            cleaned_data['ma_uu_dai'] = ''
            cleaned_data['gia_tri_giam'] = Decimal('0')

        cleaned_data['ma_uu_dai'] = ma_uu_dai
        return cleaned_data


class YeuCauTuVanHoiVienForm(forms.ModelForm):
    DICH_VU_CHOICES = [
        ('', 'Chọn dịch vụ bạn muốn tư vấn'),
        ('Yoga Bay', 'Yoga Bay'),
        ('Yoga Cơ Bản', 'Yoga Cơ Bản'),
        ('Yoga Trị Liệu', 'Yoga Trị Liệu'),
        ('Yoga Thiền', 'Yoga Thiền'),
    ]

    dich_vu_quan_tam = forms.ChoiceField(
        choices=DICH_VU_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = YeuCauTuVan
        fields = ['ho_ten', 'so_dien_thoai', 'dich_vu_quan_tam', 'noi_dung']
        widgets = {
            'ho_ten': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
            }),
            'so_dien_thoai': forms.TextInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly',
            }),
            'noi_dung': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ví dụ: Tôi muốn giảm cân, rảnh vào buổi tối...'
            }),
        }