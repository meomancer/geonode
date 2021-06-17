#########################################################################
#
# Copyright (C) 2021 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import datetime
import logging
import typing
import uuid

from django.contrib.gis.geos import Polygon
from geonode.services.serviceprocessors.wms import WmsServiceHandler
from owslib.map.wms111 import ContentMetadata
import requests
from lxml import etree

from .. import resourcedescriptor
from . import base

logger = logging.getLogger(__name__)


class OgcWmsHarvester(base.BaseHarvesterWorker):
    """Harvester for resources coming from OGC WMS web services"""

    layer_title_filter: typing.Optional[str]
    _base_wms_parameters: typing.Dict = {
        "service": "WMS",
        "version": "1.3.0",
    }
    RESOURCE_TYPE = 'layers'

    def __init__(
            self,
            *args,
            layer_title_filter: typing.Optional[str] = None,
            **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.http_session = requests.Session()
        self.http_session.headers = {
            "Content-Type": "application/xml"
        }
        self.layer_title_filter = layer_title_filter
        self.wms_handler = None
        self.check_availability()

    @property
    def allows_copying_resources(self) -> bool:
        return False

    @classmethod
    def from_django_record(cls, record: "Harvester"):
        return cls(
            record.remote_url,
            record.id,
            layer_title_filter=record.harvester_type_specific_configuration.get(
                "layer_title_filter")
        )

    @classmethod
    def get_extra_config_schema(cls) -> typing.Optional[typing.Dict]:
        return {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://geonode.org/harvesting/ogc-wms-harvester.schema.json",
            "title": "OGC WMS harvester config",
            "description": (
                "A jsonschema for validating configuration option for GeoNode's "
                "remote OGC WMS harvester"
            ),
            "type": "object",
            "properties": {
                "layer_title_filter": {
                    "type": "string",
                }
            },
            "additionalProperties": False,
        }

    def get_num_available_resources(self) -> int:
        return len(self.list_resources())

    def list_resources(
            self,
            offset: typing.Optional[int] = 0
    ) -> typing.List[base.BriefRemoteResource]:
        result = []

        # Return everything if the offset is empty
        if not offset:
            resources = self.wms_handler.get_resources()
            for resource in resources:
                if self.layer_title_filter is not None:
                    if self.layer_title_filter.lower() not in resource.name.lower():
                        continue
                brief_resource = base.BriefRemoteResource(
                    unique_identifier=resource.id,
                    title=resource.name,
                    resource_type=self.RESOURCE_TYPE,
                )
                result.append(brief_resource)
        return result

    def check_availability(self, timeout_seconds: typing.Optional[int] = 5) -> bool:
        try:
            self.wms_handler = WmsServiceHandler(
                self.remote_url)
        except (
                requests.HTTPError,
                requests.ConnectionError,
                requests.ConnectTimeout,
                requests.exceptions.MissingSchema,
                etree.XMLSyntaxError,
                etree.DocumentInvalid
        ):
            result = False
        else:
            result = True
        return result

    def get_contact(self):
        """ Return contact of wms """
        contact = self.wms_handler.parsed_service.provider.contact
        return resourcedescriptor.RecordDescriptionContact(
            role='',
            name=contact.name,
            organization=contact.organization,
            position=contact.position,
            phone_voice=None,
            phone_facsimile=None,
            address_delivery_point='',
            address_city=contact.city,
            address_administrative_area=contact.region,
            address_postal_code=contact.postcode,
            address_country=contact.country,
            address_email=contact.email,
        )

    def get_resource(
            self,
            resource_unique_identifier: str,
            resource_type: str,
            harvesting_session_id: typing.Optional[int] = None
    ) -> typing.Optional[resourcedescriptor.RecordDescription]:
        resource = self.wms_handler.get_resource(resource_unique_identifier)
        contact = self.get_contact()
        return resourcedescriptor.RecordDescription(
            uuid=uuid.uuid4(),
            language='',
            character_set='',
            hierarchy_level='',
            point_of_contact=contact,
            author=contact,
            date_stamp=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc),
            reference_system="EPSG:4326",
            identification=self.get_identification_resource(resource),
            distribution=self.get_distribution_resource(resource),
            data_quality=''
        )

    def get_contact_resource(self, resource: ContentMetadata):
        """ Return contact from resource """
        return resourcedescriptor.RecordDescriptionContact(
            role='',
            name=None,
            organization=None,
            position=None,
            phone_voice=None,
            phone_facsimile=None,
            address_delivery_point=None,
            address_city=None,
            address_administrative_area=None,
            address_postal_code=None,
            address_country=None,
            address_email=None,
        )

    def get_identification_resource(self, resource: ContentMetadata):
        """ Return identification from resource """
        contact = self.get_contact_resource(resource)
        return resourcedescriptor.RecordIdentification(
            name=resource.name,
            title=resource.title,
            date=datetime.datetime.now().replace(tzinfo=datetime.timezone.utc),
            date_type='',
            abstract=resource.abstract,
            purpose=None,
            status=None,
            originator=contact,
            graphic_overview_uri='',
            native_format='',
            place_keywords=[],
            other_keywords=resource.keywords,
            license=[],
            other_constraints=None,
            topic_category=None,
            spatial_extent=Polygon.from_bbox(resource.boundingBoxWGS84),
            temporal_extent=None,
            supplemental_information=None
        )

    def get_distribution_resource(self, resource: ContentMetadata):
        """ Return distribution from resource """
        return resourcedescriptor.RecordDistribution(
            link_url=None,
            wms_url=None,
            wfs_url=None,
            wcs_url=None,
            thumbnail_url='',
            legend_url=resource.styles[list(resource.styles.keys())[0]]['legend'],
            geojson_url=None,
            original_format_url=None)

    def update_geonode_resource(
            self,
            resource_descriptor: resourcedescriptor.RecordDescription,
            harvesting_session_id: typing.Optional[int] = None
    ):
        raise NotImplementedError
