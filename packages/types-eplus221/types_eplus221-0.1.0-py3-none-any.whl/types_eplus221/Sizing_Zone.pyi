from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Sizing_Zone(EpBunch):
    """Specifies the data needed to perform a zone design air flow calculation."""

    Zone_Or_Zonelist_Name: Annotated[str, Field(default=...)]

    Zone_Cooling_Design_Supply_Air_Temperature_Input_Method: Annotated[Literal['SupplyAirTemperature', 'TemperatureDifference'], Field(default='SupplyAirTemperature')]

    Zone_Cooling_Design_Supply_Air_Temperature: Annotated[float, Field()]
    """Zone Cooling Design Supply Air Temperature is only used when Zone Cooling Design"""

    Zone_Cooling_Design_Supply_Air_Temperature_Difference: Annotated[float, Field()]
    """Zone Cooling Design Supply Air Temperature is only used when Zone Cooling Design"""

    Zone_Heating_Design_Supply_Air_Temperature_Input_Method: Annotated[Literal['SupplyAirTemperature', 'TemperatureDifference'], Field(default='SupplyAirTemperature')]

    Zone_Heating_Design_Supply_Air_Temperature: Annotated[float, Field()]
    """Zone Heating Design Supply Air Temperature is only used when Zone Heating Design"""

    Zone_Heating_Design_Supply_Air_Temperature_Difference: Annotated[float, Field()]
    """Zone Heating Design Supply Air Temperature is only used when Zone Heating Design"""

    Zone_Cooling_Design_Supply_Air_Humidity_Ratio: Annotated[float, Field(default=..., ge=0.0)]

    Zone_Heating_Design_Supply_Air_Humidity_Ratio: Annotated[float, Field(default=..., ge=0.0)]

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]

    Zone_Heating_Sizing_Factor: Annotated[str, Field()]
    """if blank or zero, global heating sizing factor from Sizing:Parameters is used."""

    Zone_Cooling_Sizing_Factor: Annotated[str, Field()]
    """if blank or zero, global cooling sizing factor from Sizing:Parameters is used."""

    Cooling_Design_Air_Flow_Method: Annotated[Literal['Flow/Zone', 'DesignDay', 'DesignDayWithLimit'], Field(default='DesignDay')]

    Cooling_Design_Air_Flow_Rate: Annotated[float, Field(ge=0, default=0)]
    """This input is used if Cooling Design Air Flow Method is Flow/Zone"""

    Cooling_Minimum_Air_Flow_Per_Zone_Floor_Area: Annotated[float, Field(ge=0, default=.000762)]
    """default is .15 cfm/ft2"""

    Cooling_Minimum_Air_Flow: Annotated[float, Field(ge=0, default=0)]
    """This input is used if Cooling Design Air Flow Method is DesignDayWithLimit"""

    Cooling_Minimum_Air_Flow_Fraction: Annotated[float, Field(ge=0, default=0.2)]
    """fraction of the Cooling design Air Flow Rate"""

    Heating_Design_Air_Flow_Method: Annotated[Literal['Flow/Zone', 'DesignDay', 'DesignDayWithLimit'], Field(default='DesignDay')]

    Heating_Design_Air_Flow_Rate: Annotated[float, Field(ge=0, default=0)]
    """This input is used if Heating Design Air Flow Method is Flow/Zone."""

    Heating_Maximum_Air_Flow_Per_Zone_Floor_Area: Annotated[float, Field(ge=0, default=.002032)]
    """default is .40 cfm/ft2"""

    Heating_Maximum_Air_Flow: Annotated[float, Field(ge=0, default=.1415762)]
    """default is 300 cfm"""

    Heating_Maximum_Air_Flow_Fraction: Annotated[float, Field(ge=0, default=0.3)]
    """fraction of the Heating Design Air Flow Rate"""

    Design_Specification_Zone_Air_Distribution_Object_Name: Annotated[str, Field()]

    Account_For_Dedicated_Outdoor_Air_System: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """account for effect of dedicated outdoor air system supplying air directly to the zone"""

    Dedicated_Outdoor_Air_System_Control_Strategy: Annotated[Literal['NeutralSupplyAir', 'NeutralDehumidifiedSupplyAir', 'ColdSupplyAir'], Field(default='NeutralSupplyAir')]
    """1)supply neutral ventilation air; 2)supply neutral dehumidified and reheated"""

    Dedicated_Outdoor_Air_Low_Setpoint_Temperature_For_Design: Annotated[float, Field(default=autosize)]

    Dedicated_Outdoor_Air_High_Setpoint_Temperature_For_Design: Annotated[float, Field(default=autosize)]