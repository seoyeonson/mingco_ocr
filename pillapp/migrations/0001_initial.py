# Generated by Django 3.2.5 on 2022-07-07 06:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('user_name', models.CharField(max_length=30, unique=True)),
                ('user_pw', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('p_id', models.AutoField(primary_key=True, serialize=False)),
                ('p_imgpath', models.ImageField(upload_to='UploadedFiles')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pillapp.user')),
            ],
        ),
        migrations.CreateModel(
            name='medicine',
            fields=[
                ('m_id', models.AutoField(primary_key=True, serialize=False)),
                ('m_name', models.CharField(max_length=50)),
                ('p_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pillapp.prescription')),
            ],
        ),
    ]
