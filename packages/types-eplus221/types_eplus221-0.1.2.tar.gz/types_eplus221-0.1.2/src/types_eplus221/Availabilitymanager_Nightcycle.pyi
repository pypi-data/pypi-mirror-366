from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Availabilitymanager_Nightcycle(EpBunch):
    """Determines the availability of a loop or system: whether it is on or off."""

    Name: Annotated[str, Field(default=...)]

    Applicability_Schedule_Name: Annotated[str, Field(default=...)]

    Fan_Schedule_Name: Annotated[str, Field(default=...)]

    Control_Type: Annotated[Literal['StayOff', 'CycleOnAny', 'CycleOnControlZone', 'CycleOnAnyZoneFansOnly', 'CycleOnAnyCoolingOrHeatingZone', 'CycleOnAnyCoolingZone', 'CycleOnAnyHeatingZone', 'CycleOnAnyHeatingZoneFansOnly'], Field(default='StayOff')]
    """When AvailabilityManager:NightCycle is used in the zone component availability"""

    Thermostat_Tolerance: Annotated[str, Field(default='1.0')]

    Cycling_Run_Time_Control_Type: Annotated[Literal['FixedRunTime', 'Thermostat', 'ThermostatWithMinimumRunTime'], Field(default='FixedRunTime')]

    Cycling_Run_Time: Annotated[str, Field(default='3600.')]

    Control_Zone_or_Zone_List_Name: Annotated[str, Field()]
    """When AvailabilityManager:NightCycle is used in the zone component availability"""

    Cooling_Control_Zone_or_Zone_List_Name: Annotated[str, Field()]

    Heating_Control_Zone_or_Zone_List_Name: Annotated[str, Field()]

    Heating_Zone_Fans_Only_Zone_or_Zone_List_Name: Annotated[str, Field()]