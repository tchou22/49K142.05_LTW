from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('khach_hang', '0006_alter_hoivien_ma_hoi_vien'),
        ('tich_diem', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VoucherHoiVien',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ma_voucher', models.CharField(max_length=50, unique=True)),
                ('ten_voucher', models.CharField(max_length=255)),
                ('gia_tri_giam', models.DecimalField(decimal_places=0, default=0, max_digits=12)),
                ('diem_da_doi', models.IntegerField(default=0)),
                ('trang_thai', models.CharField(choices=[('chua_su_dung', 'Chưa sử dụng'), ('da_su_dung', 'Đã sử dụng'), ('het_han', 'Hết hạn')], default='chua_su_dung', max_length=20)),
                ('ngay_tao', models.DateTimeField(auto_now_add=True)),
                ('ngay_het_han', models.DateField(blank=True, null=True)),
                ('ngay_su_dung', models.DateTimeField(blank=True, null=True)),
                ('hoi_vien', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voucher_doi_diem', to='khach_hang.hoivien')),
                ('phan_thuong', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='tich_diem.phanthuong')),
            ],
        ),
    ]
