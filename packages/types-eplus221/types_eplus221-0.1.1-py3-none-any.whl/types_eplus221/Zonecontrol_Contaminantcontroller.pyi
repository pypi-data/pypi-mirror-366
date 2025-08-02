from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonecontrol_Contaminantcontroller(EpBunch):
    """Used to control a zone to a specified indoor level of CO2 or generic contaminants, or"""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Carbon_Dioxide_Control_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for CO2 controller. Schedule value > 0 means the CO2"""

    Carbon_Dioxide_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Schedule values should be carbon dioxide concentration in parts per million (ppm)"""

    Minimum_Carbon_Dioxide_Concentration_Schedule_Name: Annotated[str, Field()]
    """Schedule values should be carbon dioxide concentration in parts per"""

    Maximum_Carbon_Dioxide_Concentration_Schedule_Name: Annotated[str, Field()]
    """Schedule values should be carbon dioxide concentration in parts per"""

    Generic_Contaminant_Control_Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for generic contaminant controller. Schedule value > 0 means"""

    Generic_Contaminant_Setpoint_Schedule_Name: Annotated[str, Field()]
    """Schedule values should be generic contaminant concentration in parts per"""