# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-04-04 08:20


from django.db import migrations

import logging
logger = logging.getLogger(__name__)
   
SQL_MIGRATION = '''WITH mapstore_blob AS (
	SELECT
		msd.resource_id, msd.blob
	FROM
		public.mapstore2_adapter_mapstoredata msd
	LEFT JOIN public.maps_mapdata md 
	ON msd.resource_id =md.resource_id WHERE md.resource_id IS NOT NULL)
INSERT
	into
	public.maps_mapdata(resource_id,
	blob)
SELECT
	mb.resource_id,
	mb.blob
FROM mapstore_blob mb
WHERE NOT EXISTS (SELECT resource_id FROM public.maps_map )
'''

class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0032_auto_20190404_0820'),
    ]

    operations = [
        migrations.RunSQL(SQL_MIGRATION)
    ]
