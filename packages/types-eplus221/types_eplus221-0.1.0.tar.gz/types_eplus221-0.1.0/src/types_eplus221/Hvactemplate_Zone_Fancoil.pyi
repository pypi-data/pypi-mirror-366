from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Zone_Fancoil(EpBunch):
    """4 pipe fan coil unit with optional outdoor air."""

    Zone_Name: Annotated[str, Field(default=...)]
    """Zone name must match a building zone name"""

    Template_Thermostat_Name: Annotated[str, Field()]
    """Enter the name of a HVACTemplate:Thermostat object."""

    Supply_Air_Maximum_Flow_Rate: Annotated[str, Field(default='autosize')]
    """This field may be set to "autosize". If a value is entered, it will be"""

    Zone_Heating_Sizing_Factor: Annotated[str, Field()]
    """If blank, value from Sizing:Parameters will be used."""

    Zone_Cooling_Sizing_Factor: Annotated[str, Field()]
    """If blank, value from Sizing:Parameters will be used."""

    Outdoor_Air_Method: Annotated[Literal['Flow/Person', 'Flow/Zone', 'Flow/Area', 'Sum', 'Maximum', 'DetailedSpecification'], Field(default='Flow/Person')]
    """Flow/Person, Flow/Zone, Flow/Area, Sum, and Maximum use the values in the next three"""

    Outdoor_Air_Flow_Rate_Per_Person: Annotated[str, Field(default='0.00944')]
    """Default 0.00944 is 20 cfm per person"""

    Outdoor_Air_Flow_Rate_Per_Zone_Floor_Area: Annotated[str, Field(default='0.0')]
    """This input is used if the field Outdoor Air Method is"""

    Outdoor_Air_Flow_Rate_Per_Zone: Annotated[float, Field(default=0.0)]
    """This input is used if the field Outdoor Air Method is"""

    System_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Supply_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Supply_Fan_Delta_Pressure: Annotated[str, Field(default='75')]

    Supply_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Supply_Fan_Motor_In_Air_Stream_Fraction: Annotated[str, Field(default='1.0')]

    Cooling_Coil_Type: Annotated[Literal['ChilledWater', 'ChilledWaterDetailedFlatModel', 'HeatExchangerAssistedChilledWater'], Field(default='ChilledWater')]

    Cooling_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Cooling_Coil_Design_Setpoint: Annotated[str, Field(default='14.0')]
    """Used for sizing when Zone Cooling Design"""

    Heating_Coil_Type: Annotated[Literal['HotWater', 'Electric'], Field(default='HotWater')]

    Heating_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Heating_Coil_Design_Setpoint: Annotated[str, Field(default='50.0')]
    """Used for sizing when Zone Heating Design"""

    Dedicated_Outdoor_Air_System_Name: Annotated[str, Field()]
    """Enter the name of an HVACTemplate:System:DedicatedOutdoorAir object if this"""

    Zone_Cooling_Design_Supply_Air_Temperature_Input_Method: Annotated[Literal['SupplyAirTemperature', 'TemperatureDifference'], Field(default='SupplyAirTemperature')]
    """SupplyAirTemperature = use the value from Cooling Coil Design Setpoint (above)"""

    Zone_Cooling_Design_Supply_Air_Temperature_Difference: Annotated[float, Field(default=11.11)]
    """Zone Cooling Design Supply Air Temperature is only used when Zone Cooling Design"""

    Zone_Heating_Design_Supply_Air_Temperature_Input_Method: Annotated[Literal['SupplyAirTemperature', 'TemperatureDifference'], Field(default='SupplyAirTemperature')]
    """SupplyAirTemperature = use the value from Heating Coil Design Setpoint (above)"""

    Zone_Heating_Design_Supply_Air_Temperature_Difference: Annotated[float, Field(default=30.0)]
    """Zone Heating Design Supply Air Temperature is only used when Zone Heating Design"""

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """This field is used only when Outdoor Air Method=DetailedSpecification."""

    Design_Specification_Zone_Air_Distribution_Object_Name: Annotated[str, Field()]
    """This field is used only when Outdoor Air Method=DetailedSpecification."""

    Capacity_Control_Method: Annotated[Literal['ConstantFanVariableFlow', 'CyclingFan', 'VariableFanVariableFlow', 'VariableFanConstantFlow', 'MultiSpeedFan', 'ASHRAE90VariableFan'], Field()]
    """If this field is left blank, it will default to CyclingFan if a Dedicated Outdoor Air"""

    Low_Speed_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0.0, default=0.33)]

    Medium_Speed_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0.0, default=0.66)]
    """Medium Speed Supply Air Flow Ratio should be greater"""

    Outdoor_Air_Schedule_Name: Annotated[str, Field()]
    """Value of schedule multiplies maximum outdoor air flow rate"""

    Baseboard_Heating_Type: Annotated[Literal['HotWater', 'Electric', 'None'], Field()]

    Baseboard_Heating_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Baseboard_Heating_Capacity: Annotated[str, Field(default='autosize')]