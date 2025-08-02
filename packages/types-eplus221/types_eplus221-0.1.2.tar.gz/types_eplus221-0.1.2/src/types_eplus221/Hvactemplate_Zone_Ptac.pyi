from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Zone_Ptac(EpBunch):
    """Packaged Terminal Air Conditioner"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Zone name must match a building zone name"""

    Template_Thermostat_Name: Annotated[str, Field()]
    """Enter the name of a HVACTemplate:Thermostat object."""

    Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]
    """Supply air flow rate during cooling operation"""

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]
    """Supply air flow rate during heating operation"""

    No_Load_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0)]
    """Supply air flow rate when no cooling or heating is needed"""

    Zone_Heating_Sizing_Factor: Annotated[str, Field()]
    """If blank, value from Sizing:Parameters will be used."""

    Zone_Cooling_Sizing_Factor: Annotated[str, Field()]
    """If blank, value from Sizing:Parameters will be used."""

    Outdoor_Air_Method: Annotated[Literal['Flow/Person', 'Flow/Zone', 'Flow/Area', 'Sum', 'Maximum', 'DetailedSpecification'], Field(default='Flow/Person')]
    """Flow/Person, Flow/Zone, Flow/Area, Sum, and Maximum use the values in the next three"""

    Outdoor_Air_Flow_Rate_per_Person: Annotated[str, Field(default='0.00944')]
    """Default 0.00944 is 20 cfm per person"""

    Outdoor_Air_Flow_Rate_per_Zone_Floor_Area: Annotated[str, Field(default='0.0')]
    """This input is used if the field Outdoor Air Method is"""

    Outdoor_Air_Flow_Rate_per_Zone: Annotated[float, Field(default=0.0)]
    """This input is used if the field Outdoor Air Method is"""

    System_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Supply_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Refers to a schedule to specify unitary supply fan operating mode."""

    Supply_Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='DrawThrough')]

    Supply_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Supply_Fan_Delta_Pressure: Annotated[str, Field(default='75')]

    Supply_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Cooling_Coil_Type: Annotated[Literal['SingleSpeedDX'], Field(default='SingleSpeedDX')]

    Cooling_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Cooling_Coil_Gross_Rated_Total_Capacity: Annotated[float, Field(gt=0.0, default=autosize)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Cooling_Coil_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0.5, le=1.0, default=autosize)]
    """Rated sensible heat ratio (gross sensible capacity/gross total capacity)"""

    Cooling_Coil_Gross_Rated_Cooling_COP: Annotated[float, Field(gt=0.0, default=3.0)]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    Heating_Coil_Type: Annotated[Literal['Electric', 'HotWater', 'Gas'], Field(default='Electric')]

    Heating_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Heating_Coil_Capacity: Annotated[str, Field(default='autosize')]

    Gas_Heating_Coil_Efficiency: Annotated[str, Field(default='0.8')]
    """Applies only if Heating Coil Type is Gas"""

    Gas_Heating_Coil_Parasitic_Electric_Load: Annotated[str, Field(default='0.0')]
    """Applies only if Heating Coil Type is Gas"""

    Dedicated_Outdoor_Air_System_Name: Annotated[str, Field()]
    """Enter the name of an HVACTemplate:System:DedicatedOutdoorAir object if this"""

    Zone_Cooling_Design_Supply_Air_Temperature_Input_Method: Annotated[Literal['SupplyAirTemperature', 'TemperatureDifference'], Field(default='SupplyAirTemperature')]
    """SupplyAirTemperature = use the value from Zone Cooling Design Supply Air Temperature"""

    Zone_Cooling_Design_Supply_Air_Temperature: Annotated[float, Field(default=14.0)]
    """Zone Cooling Design Supply Air Temperature is only used when Zone Cooling Design"""

    Zone_Cooling_Design_Supply_Air_Temperature_Difference: Annotated[float, Field(default=11.11)]
    """Zone Cooling Design Supply Air Temperature is only used when Zone Cooling Design"""

    Zone_Heating_Design_Supply_Air_Temperature_Input_Method: Annotated[Literal['SupplyAirTemperature', 'TemperatureDifference'], Field(default='SupplyAirTemperature')]
    """SupplyAirTemperature = use the value from Zone Heating Design Supply Air Temperature"""

    Zone_Heating_Design_Supply_Air_Temperature: Annotated[float, Field(default=50.0)]
    """Zone Heating Design Supply Air Temperature is only used when Zone Heating Design"""

    Zone_Heating_Design_Supply_Air_Temperature_Difference: Annotated[float, Field(default=30.0)]
    """Zone Heating Design Supply Air Temperature is only used when Zone Heating Design"""

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """This field is used only when Outdoor Air Method=DetailedSpecification."""

    Design_Specification_Zone_Air_Distribution_Object_Name: Annotated[str, Field()]
    """This field is used only when Outdoor Air Method=DetailedSpecification."""

    Baseboard_Heating_Type: Annotated[Literal['HotWater', 'Electric', 'None'], Field()]

    Baseboard_Heating_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Baseboard_Heating_Capacity: Annotated[str, Field(default='autosize')]

    Capacity_Control_Method: Annotated[Literal['None', 'SingleZoneVAV'], Field()]