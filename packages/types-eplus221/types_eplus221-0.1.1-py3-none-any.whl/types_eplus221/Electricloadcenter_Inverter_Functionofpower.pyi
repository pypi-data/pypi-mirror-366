from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Electricloadcenter_Inverter_Functionofpower(EpBunch):
    """Electric power inverter to convert from direct current (DC) to alternating current"""

    Name: Annotated[str, Field()]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Name: Annotated[str, Field()]
    """Enter name of zone to receive inverter losses as heat"""

    Radiative_Fraction: Annotated[str, Field()]

    Efficiency_Function_Of_Power_Curve_Name: Annotated[str, Field()]
    """curve describes efficiency as a function of power"""

    Rated_Maximum_Continuous_Input_Power: Annotated[str, Field()]

    Minimum_Efficiency: Annotated[str, Field()]

    Maximum_Efficiency: Annotated[str, Field()]

    Minimum_Power_Output: Annotated[str, Field()]

    Maximum_Power_Output: Annotated[str, Field()]

    Ancillary_Power_Consumed_In_Standby: Annotated[str, Field()]