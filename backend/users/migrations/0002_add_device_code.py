# Generated manually

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),  # 请根据实际情况修改这里的依赖
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='device_code',
            field=models.CharField(blank=True, help_text='用户设备代号，格式如：FTDHDH05', max_length=10, null=True, verbose_name='设备代号'),
        ),
    ] 