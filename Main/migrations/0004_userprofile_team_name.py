# Generated by Django 4.1.5 on 2023-03-06 11:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0003_alter_feedback_form_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='team_name',
            field=models.CharField(default='Tech', max_length=50),
            preserve_default=False,
        ),
    ]