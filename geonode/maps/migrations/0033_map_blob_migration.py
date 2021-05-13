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
	JOIN public.maps_map md 
	ON msd.resource_id =md.resourcebase_ptr_id)
INSERT
	into
	public.maps_mapdata(resource_id,
	blob)
SELECT
	mb.resource_id,
	mb.blob
FROM mapstore_blob mb
WHERE mb.resource_id NOT IN (SELECT resource_id FROM public.maps_mapdata )
'''

class Migration(migrations.Migration):

    dependencies = [
        ('maps', '0030_auto_20210506_0836')
    ]

    operations = [
        migrations.RunSQL(SQL_MIGRATION)
    ]
