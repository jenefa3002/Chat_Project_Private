# Generated by Django 5.1.5 on 2025-01-31 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_privatemessage_is_deleted_privatemessage_is_read'),
    ]

    operations = [
        migrations.AlterField(
            model_name='privatemessage',
            name='file',
            field=models.FileField(
                blank=True, null=True,
                upload_to='upload_file/'),
        ),
    ]
