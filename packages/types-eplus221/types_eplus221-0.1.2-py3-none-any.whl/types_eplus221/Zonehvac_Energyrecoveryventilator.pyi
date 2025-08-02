from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Energyrecoveryventilator(EpBunch):
    """This compound component models a stand-alone energy recovery ventilator (ERV)"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Heat_Exchanger_Name: Annotated[str, Field(default=...)]
    """Heat exchanger type must be HeatExchanger:AirToAir:SensibleAndLatent"""

    Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """This flow rate must match the supply fan's air flow rate."""

    Exhaust_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """This flow rate must match the supply fan air flow rate."""

    Supply_Air_Fan_Name: Annotated[str, Field(default=...)]
    """Fan type must be Fan:OnOff or Fan:SystemModel"""

    Exhaust_Air_Fan_Name: Annotated[str, Field(default=...)]
    """Fan type must be Fan:OnOff or Fan:SystemModel"""

    Controller_Name: Annotated[str, Field()]
    """Enter the name of a ZoneHVAC:EnergyRecoveryVentilator:Controller object."""

    Ventilation_Rate_per_Unit_Floor_Area: Annotated[float, Field(ge=0.0)]
    """0.000508 m3/s-m2 corresponds to 0.1 ft3/min-ft2"""

    Ventilation_Rate_per_Occupant: Annotated[float, Field(ge=0.0)]
    """0.00236 m3/s-person corresponds to 5 ft3/min-person"""

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""