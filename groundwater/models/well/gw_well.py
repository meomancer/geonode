from django.contrib.gis.db import models
from groundwater.models.well_construction import Borehole
from groundwater.models import Quantity


class WellStatusTypeTerm(models.Model):
    """
    Status of the well, Can be new, unfinished,
    reconditioned, deepened, not in use, standby,
    unknown, abandoned dry, abandoned
    insufficient, abandoned quality. (gwml1)
    """
    name = models.TextField()


class GWWell(models.Model):
    """
    7.6.38 GW_Well
    A shaft or hole sunk, dug or drilled into the Earth to observe, extract or inject water (after
    IGH1397)."""

    gw_well_name = models.TextField(
        null=False, blank=False, verbose_name="gwWellName",
        help_text="Name or ID of the well.")
    gw_well_location = models.PointField(
        null=False, blank=False, verbose_name="gwWellLocation",
        help_text="Surface location of the well.")
    gw_well_contribution_zone = models.GeometryField(
        null=True, blank=True, verbose_name="gwWellContributionZone",
        help_text="The area or volume surrounding a pumping well"
                  "or other discharge site that encompasses all areas"
                  "and features that supply groundwater to the well"
                  "or discharge site.")
    gw_well_construction = models.ForeignKey(
        Borehole, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwWellConstruction",
        help_text="Construction details for a well.")
    gw_well_total_length = models.FloatField(
        null=True, blank=True,
        verbose_name="gwWellTotalLength",
        help_text="Total length of the well from reference elevation.")
    gw_well_status = models.ForeignKey(
        WellStatusTypeTerm, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwWellStatus",
        help_text="Status of the well, Can be new, unfinished, "
                  "reconditioned, deepened, not in use, standby,"
                  "unknown, abandoned dry, abandoned"
                  "insufficient, abandoned quality. (gwml1)")
    gw_well_static_water_depth = models.ForeignKey(
        Quantity, null=True, blank=True,
        on_delete=models.SET_NULL, verbose_name="gwWellStaticWaterDepth",
        help_text="Depth of the fluid body (e.g. piezometric level).")
