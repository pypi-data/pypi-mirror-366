from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Availabilitymanager_Nightventilation(EpBunch):
    """depending on zone and outdoor conditions overrides fan schedule to do"""

    Name: Annotated[str, Field(default=...)]

    Applicability_Schedule_Name: Annotated[str, Field(default=...)]

    Fan_Schedule_Name: Annotated[str, Field(default=...)]

    Ventilation_Temperature_Schedule_Name: Annotated[str, Field()]
    """One zone temperature must be above this scheduled temperature"""

    Ventilation_Temperature_Difference: Annotated[str, Field(default='2.0')]
    """The outdoor air temperature minus the control zone temperature"""

    Ventilation_Temperature_Low_Limit: Annotated[str, Field(default='15.')]
    """Night ventilation is disabled if any conditioned zone served by"""

    Night_Venting_Flow_Fraction: Annotated[str, Field(default='1.')]
    """the fraction (could be > 1) of the design system Flow Rate at which"""

    Control_Zone_Name: Annotated[str, Field(default=...)]
    """When AvailabilityManager:NightVentilation is used in the zone component availability"""