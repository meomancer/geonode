# Generated by Django 3.2 on 2021-06-14 17:35

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('harvesting', '0018_auto_20210614_1733'),
    ]

    operations = [
        migrations.AlterField(
            model_name='harvester',
            name='default_access_permissions',
            field=jsonfield.fields.JSONField(blank=True, default=dict, help_text='Default access permissions of harvested resources'),
        ),
        migrations.AlterField(
            model_name='harvester',
            name='harvester_type_specific_configuration',
            field=jsonfield.fields.JSONField(blank=True, default=dict, help_text='Configuration specific to each harvester type. Please consult GeoNode documentation on harvesting for more info. This field is mandatory, so at the very least an empty object (i.e. {}) must be supplied.'),
        ),
    ]
