from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Waterheater_Mixed(EpBunch):
    """Water heater with well-mixed, single-node water tank. May be used to model a tankless"""

    Name: Annotated[str, Field(default=...)]

    Tank_Volume: Annotated[float, Field(ge=0.0, default=0.0)]

    Setpoint_Temperature_Schedule_Name: Annotated[str, Field(default=...)]

    Deadband_Temperature_Difference: Annotated[float, Field(ge=0.0, default=0.0)]

    Maximum_Temperature_Limit: Annotated[float, Field()]

    Heater_Control_Type: Annotated[Literal['Cycle', 'Modulate'], Field(default='Cycle')]

    Heater_Maximum_Capacity: Annotated[float, Field(ge=0.0)]

    Heater_Minimum_Capacity: Annotated[float, Field(ge=0.0)]
    """Only used when Heater Control Type is set to Modulate"""

    Heater_Ignition_Minimum_Flow_Rate: Annotated[float, Field(ge=0.0, default=0.0)]
    """Not yet implemented"""

    Heater_Ignition_Delay: Annotated[float, Field(ge=0.0, default=0.0)]
    """Not yet implemented"""

    Heater_Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Coal', 'Diesel', 'Gasoline', 'OtherFuel1', 'OtherFuel2', 'Steam', 'DistrictHeating'], Field(default=...)]

    Heater_Thermal_Efficiency: Annotated[float, Field(default=..., gt=0.0, le=1.0)]

    Part_Load_Factor_Curve_Name: Annotated[str, Field()]

    Off_Cycle_Parasitic_Fuel_Consumption_Rate: Annotated[float, Field(ge=0.0, default=0.0)]

    Off_Cycle_Parasitic_Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Coal', 'Diesel', 'Gasoline', 'OtherFuel1', 'OtherFuel2', 'Steam', 'DistrictHeating'], Field()]

    Off_Cycle_Parasitic_Heat_Fraction_To_Tank: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    On_Cycle_Parasitic_Fuel_Consumption_Rate: Annotated[float, Field(ge=0.0, default=0.0)]

    On_Cycle_Parasitic_Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Coal', 'Diesel', 'Gasoline', 'OtherFuel1', 'OtherFuel2', 'Steam', 'DistrictHeating'], Field()]

    On_Cycle_Parasitic_Heat_Fraction_To_Tank: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Ambient_Temperature_Indicator: Annotated[Literal['Schedule', 'Zone', 'Outdoors'], Field(default=...)]

    Ambient_Temperature_Schedule_Name: Annotated[str, Field()]

    Ambient_Temperature_Zone_Name: Annotated[str, Field()]

    Ambient_Temperature_Outdoor_Air_Node_Name: Annotated[str, Field()]
    """required for Ambient Temperature Indicator=Outdoors"""

    Off_Cycle_Loss_Coefficient_To_Ambient_Temperature: Annotated[float, Field(ge=0.0)]

    Off_Cycle_Loss_Fraction_To_Zone: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    On_Cycle_Loss_Coefficient_To_Ambient_Temperature: Annotated[float, Field(ge=0.0)]

    On_Cycle_Loss_Fraction_To_Zone: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Peak_Use_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Only used if Use Side Node connections are blank"""

    Use_Flow_Rate_Fraction_Schedule_Name: Annotated[str, Field()]
    """Only used if Use Side Node connections are blank"""

    Cold_Water_Supply_Temperature_Schedule_Name: Annotated[str, Field()]
    """Only used if Use Side Node connections are blank"""

    Use_Side_Inlet_Node_Name: Annotated[str, Field()]

    Use_Side_Outlet_Node_Name: Annotated[str, Field()]

    Use_Side_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Source_Side_Inlet_Node_Name: Annotated[str, Field()]

    Source_Side_Outlet_Node_Name: Annotated[str, Field()]

    Source_Side_Effectiveness: Annotated[float, Field(gt=0.0, le=1.0, default=1.0)]

    Use_Side_Design_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Source_Side_Design_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Indirect_Water_Heating_Recovery_Time: Annotated[float, Field(gt=0.0, default=1.5)]
    """Parameter for autosizing design flow rates for indirectly heated water tanks"""

    Source_Side_Flow_Control_Mode: Annotated[Literal['StorageTank', 'IndirectHeatPrimarySetpoint', 'IndirectHeatAlternateSetpoint'], Field(default='IndirectHeatPrimarySetpoint')]
    """StorageTank mode always requests flow unless tank is at its Maximum Temperature Limit"""

    Indirect_Alternate_Setpoint_Temperature_Schedule_Name: Annotated[str, Field()]
    """This field is only used if the previous is set to IndirectHeatAlternateSetpoint"""

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""