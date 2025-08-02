from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Zone_Dualduct(EpBunch):
    """Zone terminal unit, dual-duct, constant or variable volume."""

    Zone_Name: Annotated[str, Field(default=...)]
    """Zone name must match a building zone name"""

    Template_Dual_Duct_System_Name: Annotated[str, Field(default=...)]
    """Name of a HVACTemplate:System:DualDuct object serving this zone"""

    Template_Thermostat_Name: Annotated[str, Field()]
    """Enter the name of a HVACTemplate:Thermostat object."""

    Supply_Air_Maximum_Flow_Rate: Annotated[str, Field(default='autosize')]
    """This field may be set to "autosize". If a value is entered, it will be"""

    Zone_Heating_Sizing_Factor: Annotated[str, Field()]
    """If blank, value from Sizing:Parameters will be used."""

    Zone_Cooling_Sizing_Factor: Annotated[str, Field()]
    """If blank, value from Sizing:Parameters will be used."""

    Zone_Minimum_Air_Flow_Fraction: Annotated[str, Field(default='0.2')]
    """This field is the Zone Minimum Air Flow Fraction specified as a fraction of the"""

    Outdoor_Air_Method: Annotated[Literal['Flow/Person', 'Flow/Zone', 'Flow/Area', 'Sum', 'Maximum', 'DetailedSpecification'], Field(default='Flow/Person')]
    """Flow/Person, Flow/Zone, Flow/Area, Sum, and Maximum use the values in the next three"""

    Outdoor_Air_Flow_Rate_Per_Person: Annotated[str, Field(default='0.00944')]
    """Default 0.00944 is 20 cfm per person"""

    Outdoor_Air_Flow_Rate_Per_Zone_Floor_Area: Annotated[str, Field(default='0.0')]
    """This input is used if the field Outdoor Air Method is"""

    Outdoor_Air_Flow_Rate_Per_Zone: Annotated[float, Field(default=0.0)]
    """This input is used if the field Outdoor Air Method is"""

    Design_Specification_Outdoor_Air_Object_Name_For_Sizing: Annotated[str, Field()]
    """This field is used only when Outdoor Air Method=DetailedSpecification."""

    Design_Specification_Zone_Air_Distribution_Object_Name: Annotated[str, Field()]
    """This field is used only when Outdoor Air Method=DetailedSpecification."""

    Design_Specification_Outdoor_Air_Object_Name_For_Control: Annotated[str, Field()]
    """When the name of a DesignSpecification:OutdoorAir object is entered, the terminal"""

    Cold_Supply_Plenum_Name: Annotated[str, Field()]
    """Plenum zone name. Cold supply plenum that serves only this zone."""

    Hot_Supply_Plenum_Name: Annotated[str, Field()]
    """Plenum zone name. Hot supply plenum that serves only this zone."""

    Return_Plenum_Name: Annotated[str, Field()]
    """Plenum zone name. Return plenum that serves only this zone."""

    Baseboard_Heating_Type: Annotated[Literal['HotWater', 'Electric', 'None'], Field()]

    Baseboard_Heating_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Baseboard_Heating_Capacity: Annotated[str, Field(default='autosize')]

    Zone_Cooling_Design_Supply_Air_Temperature_Input_Method: Annotated[Literal['SupplyAirTemperature', 'TemperatureDifference', 'SystemSupplyAirTemperature'], Field(default='SystemSupplyAirTemperature')]
    """SupplyAirTemperature = use the value from Zone Cooling Design Supply Air Temperature"""

    Zone_Cooling_Design_Supply_Air_Temperature: Annotated[float, Field(default=12.8)]
    """Zone Cooling Design Supply Air Temperature is only used when Zone Cooling Design"""

    Zone_Cooling_Design_Supply_Air_Temperature_Difference: Annotated[float, Field(default=11.11)]
    """Zone Cooling Design Supply Air Temperature is only used when Zone Cooling Design"""

    Zone_Heating_Design_Supply_Air_Temperature_Input_Method: Annotated[Literal['SupplyAirTemperature', 'TemperatureDifference', 'SystemSupplyAirTemperature'], Field(default='SystemSupplyAirTemperature')]
    """SupplyAirTemperature = use the value from Zone Heating Design Supply Air Temperature"""

    Zone_Heating_Design_Supply_Air_Temperature: Annotated[float, Field(default=50.0)]
    """Zone Heating Design Supply Air Temperature is only used when Zone Heating Design"""

    Zone_Heating_Design_Supply_Air_Temperature_Difference: Annotated[float, Field(default=30.0)]
    """Zone Heating Design Supply Air Temperature is only used when Zone Heating Design"""