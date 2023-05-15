# Generated by Django 4.1.7 on 2023-05-02 19:53

from django.db import migrations, models
import system_api.models


class Migration(migrations.Migration):

    dependencies = [
        ('system_api', '0006_alter_jobcard_job_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jobcard',
            name='additional_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='jobcard',
            name='image_after_assessment',
            field=models.ImageField(blank=True, null=True, upload_to='job_cards/after_assessment/%Y/%m/%d/%s/'),
        ),
        migrations.AlterField(
            model_name='jobcard',
            name='image_before_assessment',
            field=models.ImageField(blank=True, null=True, upload_to='job_cards/before_assessment/%Y/%m/%d/%s/'),
        ),
        migrations.AlterField(
            model_name='jobcard',
            name='job_number',
            field=system_api.models.JobNumberField(max_length=13, unique=True),
        ),
        migrations.AlterField(
            model_name='jobcard',
            name='purchase_slip_image',
            field=models.ImageField(blank=True, null=True, upload_to='job_cards/purchase_slips/%Y/%m/%d/%s/'),
        ),
        migrations.AlterField(
            model_name='jobcard',
            name='work_environment_image',
            field=models.ImageField(blank=True, null=True, upload_to='job_cards/work_environment/%Y/%m/%d/%s/'),
        ),
    ]