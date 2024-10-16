# Generated by Django 4.2.16 on 2024-10-11 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('video_analysis', '0005_remove_footballvideo_uploaded_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='footballvideo',
            name='player_name',
        ),
        migrations.AlterField(
            model_name='footballvideo',
            name='shooting_accuracy',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
        migrations.AlterField(
            model_name='footballvideo',
            name='shooting_angle',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=5),
        ),
    ]
