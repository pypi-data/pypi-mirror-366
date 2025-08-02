from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Energyrecoveryventilator_Controller(EpBunch):
    """This controller is used exclusively by the ZoneHVAC:EnergyRecoveryVentilator object"""

    Name: Annotated[str, Field(default=...)]

    Temperature_High_Limit: Annotated[float, Field()]
    """Enter the maximum outdoor dry-bulb temperature limit for economizer operation."""

    Temperature_Low_Limit: Annotated[float, Field()]
    """Enter the minimum outdoor dry-bulb temperature limit for economizer operation."""

    Enthalpy_High_Limit: Annotated[float, Field()]
    """Enter the maximum outdoor enthalpy limit for economizer operation."""

    Dewpoint_Temperature_Limit: Annotated[float, Field()]
    """Enter the maximum outdoor dew point temperature limit for economizer operation."""

    Electronic_Enthalpy_Limit_Curve_Name: Annotated[str, Field()]
    """Enter the name of a quadratic or cubic curve which defines the maximum outdoor"""

    Exhaust_Air_Temperature_Limit: Annotated[Literal['ExhaustAirTemperatureLimit', 'NoExhaustAirTemperatureLimit'], Field(default='NoExhaustAirTemperatureLimit')]

    Exhaust_Air_Enthalpy_Limit: Annotated[Literal['ExhaustAirEnthalpyLimit', 'NoExhaustAirEnthalpyLimit'], Field(default='NoExhaustAirEnthalpyLimit')]

    Time_Of_Day_Economizer_Flow_Control_Schedule_Name: Annotated[str, Field()]
    """Schedule values greater than 0 indicate economizer operation is active. This"""

    High_Humidity_Control_Flag: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Select Yes to modify air flow rates based on a zone humidistat."""

    Humidistat_Control_Zone_Name: Annotated[str, Field()]
    """Enter the name of the zone where the humidistat is located."""

    High_Humidity_Outdoor_Air_Flow_Ratio: Annotated[float, Field(gt=0.0, default=1.0)]
    """Enter the ratio of supply (outdoor) air to the maximum supply air flow rate when modified"""

    Control_High_Indoor_Humidity_Based_On_Outdoor_Humidity_Ratio: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """If NO is selected, the air flow rate is modified any time indoor relative"""