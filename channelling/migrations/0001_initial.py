# Generated by Django 3.0.2 on 2020-01-25 13:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('twitting', '0002_auto_20200125_1311'),
        ('accounting', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Channel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField(verbose_name='توضیحات')),
                ('admins', models.ManyToManyField(related_name='authors', to='accounting.Account')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounting.Account')),
                ('tweets', models.ManyToManyField(related_name='posts', to='twitting.Tweet')),
            ],
        ),
    ]
