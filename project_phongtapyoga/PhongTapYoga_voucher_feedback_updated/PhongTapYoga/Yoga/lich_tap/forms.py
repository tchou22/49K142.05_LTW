from django import forms
from .models import LichHoc
from goi_tap.models import GoiTap


class LichHocForm(forms.Form):
    goi_tap = forms.ModelChoiceField(
        queryset=GoiTap.objects.filter(trang_thai='hoat_dong').order_by('ten_goi'),
        empty_label="Chọn gói tập",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    thu = forms.MultipleChoiceField(
        choices=LichHoc.THU_CHOICES,
        required=True,
        widget=forms.CheckboxSelectMultiple
    )

    gio_bat_dau = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )

    gio_ket_thuc = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )

    phong = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    hlv_phu_trach = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    so_cho_toi_da = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )

    def clean(self):
        cleaned_data = super().clean()
        gio_bat_dau = cleaned_data.get('gio_bat_dau')
        gio_ket_thuc = cleaned_data.get('gio_ket_thuc')

        if gio_bat_dau and gio_ket_thuc and gio_bat_dau >= gio_ket_thuc:
            raise forms.ValidationError("Giờ kết thúc phải lớn hơn giờ bắt đầu.")

        return cleaned_data

class DangKyLichHocForm(forms.Form):
    lich_hocs = forms.ModelMultipleChoiceField(
        queryset=LichHoc.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Chọn lịch học'
    )

    def __init__(self, *args, **kwargs):
        lich_queryset = kwargs.pop('lich_queryset', LichHoc.objects.none())
        super().__init__(*args, **kwargs)
        self.fields['lich_hocs'].queryset = lich_queryset