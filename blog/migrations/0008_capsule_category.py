# Generated by Django 2.1.3 on 2019-02-04 22:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_capsule_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='capsule',
            name='category',
            field=models.IntegerField(default=4),
            preserve_default=False,
        ),
    ]
