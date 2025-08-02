from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonecontrol_Thermostat_Operativetemperature(EpBunch):
    """This object can be used with the ZoneList option on a thermostat or with one"""

    Thermostat_Name: Annotated[str, Field(default=...)]
    """Enter the name of a ZoneControl:Thermostat object."""

    Radiative_Fraction_Input_Mode: Annotated[Literal['Constant', 'Scheduled'], Field(default=...)]

    Fixed_Radiative_Fraction: Annotated[str, Field()]

    Radiative_Fraction_Schedule_Name: Annotated[str, Field()]
    """Schedule values of 0.0 indicate no operative temperature control"""

    Adaptive_Comfort_Model_Type: Annotated[Literal['None', 'AdaptiveASH55CentralLine', 'AdaptiveASH5580PercentUpperLine', 'AdaptiveASH5590PercentUpperLine', 'AdaptiveCEN15251CentralLine', 'AdaptiveCEN15251CategoryIUpperLine', 'AdaptiveCEN15251CategoryIIUpperLine', 'AdaptiveCEN15251CategoryIIIUpperLine'], Field()]
    """the cooling setpoint temperature schedule of the referenced thermostat will be adjusted based on the selected adaptive comfort model type"""