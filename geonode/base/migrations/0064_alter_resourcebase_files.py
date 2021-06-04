# Generated by Django 3.2 on 2021-06-04 07:42

from django.db import migrations, models
from geonode.base.models import ResourceBase

def change_value(apps, schema_editor):
    resource = ResourceBase.objects.all()
    for r in resource:
        if isinstance(r.files, dict):
            f = list(r.files.values())
            r.files = f
            r.save()


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0063_alter_resourcebase_files'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resourcebase',
            name='files',
            field=models.JSONField(blank=True, default=list, null=True),
        ),
        migrations.RunPython(change_value),

    ]
