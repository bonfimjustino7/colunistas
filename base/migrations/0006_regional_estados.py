# Generated by Django 2.1.7 on 2019-04-02 00:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_uf'),
    ]

    operations = [
        migrations.AddField(
            model_name='regional',
            name='estados',
            field=models.CharField(help_text='Separe os estados com vírgula', max_length=100, null=True),
        ),
    ]
