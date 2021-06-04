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

import functools
import json
import logging

from django.contrib import (
    admin,
    messages,
)
from django.db import transaction

from . import (
    forms,
    models,
    tasks,
    utils,
)

logger = logging.getLogger(__name__)


@admin.register(models.Harvester)
class HarvesterAdmin(admin.ModelAdmin):
    form = forms.HarvesterForm

    list_display = (
        "id",
        "status",
        "name",
        "scheduling_enabled",
        "remote_url",
        "remote_available",
        "update_frequency",
        "harvester_type",
        "get_num_harvestable_resources",
    )

    readonly_fields = (
        "remote_available",
        "last_checked_availability",
        "last_checked_harvestable_resources",
        "last_check_harvestable_resources_message",
    )

    list_editable = (
        "scheduling_enabled",
    )

    actions = [
        "update_harvester_availability",
        "update_harvestable_resources",
    ]

    def save_model(self, request, obj: models.Harvester, form, change):
        # TODO: disallow changing the model if it is not ready
        with transaction.atomic():
            super().save_model(request, obj, form, change)
            available = utils.update_harvester_availability(obj)
            if available:
                partial_task = functools.partial(
                    tasks.update_harvestable_resources.apply_async, args=(obj.pk,))
                # NOTE: below we are using transaction.on_commit in order to ensure
                # the harvester is already saved in the DB before we schedule the
                # celery task. This is needed in order to avoid the celery worker
                # picking up the task before it is saved in the DB. More info:
                #
                # https://docs.djangoproject.com/en/2.2/topics/db/transactions/#performing-actions-after-commit
                #
                if not change:
                    transaction.on_commit(partial_task)
                    message = (
                        f"Updating harvestable resources asynchronously for {obj!r}...")
                    self.message_user(request, message)
                    logger.debug(message)
                elif _worker_config_changed(form):
                    self.message_user(
                        request,
                        (
                            "Harvester worker specific configuration has been changed. "
                            "Regenerating list of this harvester's harvestable "
                            "resources asynchronously... "
                        ),
                        level=messages.WARNING
                    )
                    models.HarvestableResource.objects.filter(harvester=obj).delete()
                    transaction.on_commit(partial_task)
            else:
                self.message_user(
                    request,
                    f"Harvester {obj} is{'' if available else ' not'} available",
                    messages.INFO if available else messages.WARNING
                )

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["default_owner"].initial = request.user
        return form

    def update_harvester_availability(self, request, queryset):
        updated_harvesters = []
        non_available_harvesters = []
        for harvester in queryset:
            available = utils.update_harvester_availability(harvester)
            updated_harvesters.append(harvester)
            if not available:
                non_available_harvesters.append(harvester)
        self.message_user(
            request, f"Updated availability for harvesters: {updated_harvesters}")
        if len(non_available_harvesters) > 0:
            self.message_user(
                request,
                (
                    f"The following harvesters are not "
                    f"available: {non_available_harvesters}"
                ),
                messages.WARNING
            )
    update_harvester_availability.short_description = (
        "Check availability of selected harvesters")

    def update_harvestable_resources(self, request, queryset):
        being_updated = []
        for harvester in queryset:
            if harvester.status != harvester.STATUS_READY:
                self.message_user(
                    request,
                    f"Harvester {harvester!r} is currently busy. Please wait until "
                    f"its status is {harvester.STATUS_READY!r} before retrying",
                    level=messages.ERROR
                )
                continue
            available = utils.update_harvester_availability(harvester)
            if not available:
                self.message_user(
                    request,
                    (
                        f"harvester {harvester} is not available, skipping "
                        f"check of harvestable resources for it..."
                    ),
                    messages.ERROR
                )
                continue
            harvester.status = harvester.STATUS_UPDATING_HARVESTABLE_RESOURCES
            harvester.save()
            tasks.update_harvestable_resources.apply_async(args=(harvester.pk,))
            being_updated.append(harvester)
        if len(being_updated) > 0:
            self.message_user(
                request,
                f"Updating harvestable resources asynchronously for {being_updated}..."
            )
    update_harvestable_resources.short_description = (
            "Update harvestable resources from selected harvesters")

    def get_num_harvestable_resources(self, harvester: models.Harvester):
        return harvester.harvestable_resources.count()
    get_num_harvestable_resources.short_description = (
        "number of harvestable resources")


@admin.register(models.HarvestingSession)
class HarvestingSessionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "started",
        "updated",
        "ended",
        "total_records_found",
        "records_harvested",
        "harvester",
    )


@admin.register(models.HarvestableResource)
class HarvestableResourceAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "available",
        "last_updated",
        "unique_identifier",
        "title",
        "harvester",
        "should_be_harvested",
        "remote_resource_type",
    )
    readonly_fields = (
        "unique_identifier",
        "title",
        "harvester",
        "last_updated",
        "available",
        "remote_resource_type",
    )
    list_filter = (
        "harvester",
        "should_be_harvested",
        "available",
        "last_updated",
    )
    list_editable = (
        "should_be_harvested",
    )


def _worker_config_changed(form) -> bool:
    field_name = "harvester_type_specific_configuration"
    original = eval(form.data[f"initial-{field_name}"], {})
    cleaned = form.cleaned_data.get(field_name)
    return original != cleaned
