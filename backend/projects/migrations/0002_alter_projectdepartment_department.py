# Generated by Django 4.2.10 on 2025-04-12 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectdepartment',
            name='department',
            field=models.CharField(choices=[('animation', '动画'), ('post', '后期'), ('fx', '解算'), ('producer', '制片'), ('model', '模型'), ('admin', '管理员')], max_length=20, verbose_name='部门'),
        ),
    ]
