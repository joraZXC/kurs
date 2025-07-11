# Generated by Django 4.2.16 on 2025-06-01 23:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('review_id', models.AutoField(primary_key=True, serialize=False)),
                ('zone_id', models.IntegerField()),
                ('event_id', models.IntegerField()),
                ('review_text', models.TextField()),
                ('rating', models.SmallIntegerField(null=True)),
                ('created_at', models.DateField()),
            ],
            options={
                'verbose_name': 'Отзыв',
                'verbose_name_plural': 'Отзывы',
                'db_table': 'review',
                'managed': False,
            },
        ),
    ]
