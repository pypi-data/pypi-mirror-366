from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Electricloadcenter_Inverter_Lookuptable(EpBunch):
    """California Energy Commission tests and publishes data on inverters"""

    Name: Annotated[str, Field()]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Name: Annotated[str, Field()]
    """Enter name of zone to receive inverter losses as heat"""

    Radiative_Fraction: Annotated[str, Field()]

    Rated_Maximum_Continuous_Output_Power: Annotated[str, Field()]

    Night_Tare_Loss_Power: Annotated[str, Field()]

    Nominal_Voltage_Input: Annotated[str, Field()]

    Efficiency_at_10_Power_and_Nominal_Voltage: Annotated[str, Field()]

    Efficiency_at_20_Power_and_Nominal_Voltage: Annotated[str, Field()]

    Efficiency_at_30_Power_and_Nominal_Voltage: Annotated[str, Field()]

    Efficiency_at_50_Power_and_Nominal_Voltage: Annotated[str, Field()]

    Efficiency_at_75_Power_and_Nominal_Voltage: Annotated[str, Field()]

    Efficiency_at_100_Power_and_Nominal_Voltage: Annotated[str, Field()]