from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowshadingcontrol(EpBunch):
    """Specifies the type, location, and controls for window shades, window blinds, and"""

    Name: Annotated[str, Field(default=...)]
    """Referenced by surfaces that are exterior windows"""

    Zone_Name: Annotated[str, Field(default=...)]

    Shading_Control_Sequence_Number: Annotated[int, Field(ge=1, default=1)]
    """If multiple WindowShadingControl objects are used than the order that they deploy the window shades"""

    Shading_Type: Annotated[Literal['InteriorShade', 'ExteriorShade', 'ExteriorScreen', 'InteriorBlind', 'ExteriorBlind', 'BetweenGlassShade', 'BetweenGlassBlind', 'SwitchableGlazing'], Field(default=...)]

    Construction_with_Shading_Name: Annotated[str, Field()]
    """Required if Shading Type = SwitchableGlazing"""

    Shading_Control_Type: Annotated[Literal['AlwaysOn', 'AlwaysOff', 'OnIfScheduleAllows', 'OnIfHighSolarOnWindow', 'OnIfHighHorizontalSolar', 'OnIfHighOutdoorAirTemperature', 'OnIfHighZoneAirTemperature', 'OnIfHighZoneCooling', 'OnIfHighGlare', 'MeetDaylightIlluminanceSetpoint', 'OnNightIfLowOutdoorTempAndOffDay', 'OnNightIfLowInsideTempAndOffDay', 'OnNightIfHeatingAndOffDay', 'OnNightIfLowOutdoorTempAndOnDayIfCooling', 'OnNightIfHeatingAndOnDayIfCooling', 'OffNightAndOnDayIfCoolingAndHighSolarOnWindow', 'OnNightAndOnDayIfCoolingAndHighSolarOnWindow', 'OnIfHighOutdoorAirTempAndHighSolarOnWindow', 'OnIfHighOutdoorAirTempAndHighHorizontalSolar', 'OnIfHighZoneAirTempAndHighSolarOnWindow', 'OnIfHighZoneAirTempAndHighHorizontalSolar'], Field(default=...)]
    """OnIfScheduleAllows requires that Schedule Name be specified and"""

    Schedule_Name: Annotated[str, Field()]
    """Required if Shading Control Is Scheduled = Yes."""

    Setpoint: Annotated[float, Field()]
    """W/m2 for solar-based controls, W for cooling- or heating-based controls,"""

    Shading_Control_Is_Scheduled: Annotated[Literal['No', 'Yes'], Field(default='No')]
    """If Yes, Schedule Name is required; if No, Schedule Name is not used."""

    Glare_Control_Is_Active: Annotated[Literal['No', 'Yes'], Field(default='No')]
    """If Yes and window is in a daylit zone, shading is on if zone's discomfort glare index exceeds"""

    Shading_Device_Material_Name: Annotated[str, Field()]
    """Enter the name of a WindowMaterial:Shade, WindowMaterial:Screen or WindowMaterial:Blind object."""

    Type_of_Slat_Angle_Control_for_Blinds: Annotated[Literal['FixedSlatAngle', 'ScheduledSlatAngle', 'BlockBeamSolar'], Field(default='FixedSlatAngle')]
    """Used only if Shading Type = InteriorBlind, ExteriorBlind or BetweenGlassBlind."""

    Slat_Angle_Schedule_Name: Annotated[str, Field()]
    """Used only if Shading Type = InteriorBlind, ExteriorBlind or BetweenGlassBlind."""

    Setpoint_2: Annotated[float, Field()]
    """W/m2 for solar-based controls, deg C for temperature-based controls."""

    Daylighting_Control_Object_Name: Annotated[str, Field()]
    """Reference to the Daylighting:Controls object that provides the glare and illuminance control to the zone."""

    Multiple_Surface_Control_Type: Annotated[Literal['Sequential', 'Group'], Field(default='Sequential')]
    """When Sequential is used the list of fenestration surfaces are controlled individually in the order specified"""

    Fenestration_Surface_1_Name: Annotated[str, Field(default=...)]
    """When Multiple Surface Control Type is set to Sequential the shades will be deployed for the referenced surface objects in order."""

    Fenestration_Surface_2_Name: Annotated[str, Field()]
    """When Multiple Surface Control Type is set to Sequential the shades will be deployed for the referenced surface objects in order."""

    Fenestration_Surface_3_Name: Annotated[str, Field()]
    """When Multiple Surface Control Type is set to Sequential the shades will be deployed for the referenced surface objects in order."""

    Fenestration_Surface_4_Name: Annotated[str, Field()]
    """When Multiple Surface Control Type is set to Sequential the shades will be deployed for the referenced surface objects in order."""

    Fenestration_Surface_5_Name: Annotated[str, Field()]
    """When Multiple Surface Control Type is set to Sequential the shades will be deployed for the referenced surface objects in order."""

    Fenestration_Surface_6_Name: Annotated[str, Field()]
    """When Multiple Surface Control Type is set to Sequential the shades will be deployed for the referenced surface objects in order."""

    Fenestration_Surface_7_Name: Annotated[str, Field()]
    """When Multiple Surface Control Type is set to Sequential the shades will be deployed for the referenced surface objects in order."""

    Fenestration_Surface_8_Name: Annotated[str, Field()]
    """When Multiple Surface Control Type is set to Sequential the shades will be deployed for the referenced surface objects in order."""

    Fenestration_Surface_9_Name: Annotated[str, Field()]
    """When Multiple Surface Control Type is set to Sequential the shades will be deployed for the referenced surface objects in order."""

    Fenestration_Surface_10_Name: Annotated[str, Field()]
    """When Multiple Surface Control Type is set to Sequential the shades will be deployed for the referenced surface objects in order."""