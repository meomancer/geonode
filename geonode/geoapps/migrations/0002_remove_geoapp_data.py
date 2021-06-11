# Generated by Django 3.2 on 2021-06-11 13:26

from django.db import migrations
from geonode.base.models import ResourceBase


def move_data_blob(apps, schema_editor):
    MyModel = apps.get_model('gepapps', 'GeoAppData')
    for m in MyModel.objects.all():
        u = ResourceBase.objects.filter(id=m.resource.id)
        u.update(**{"blob": m.blob})


class Migration(migrations.Migration):

    dependencies = [
        ('geoapps', '0001_initial'),
        ('base', '0066_resourcebase_data')
    ]

    operations = [        
        migrations.RunPython(move_data_blob),
        migrations.RemoveField(
            model_name='geoapp',
            name='data',
        ),
    ]
