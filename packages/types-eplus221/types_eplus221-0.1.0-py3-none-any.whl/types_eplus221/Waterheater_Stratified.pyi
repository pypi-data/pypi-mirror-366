from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Waterheater_Stratified(EpBunch):
    """Water heater with stratified, multi-node water tank. May be used to model a tankless"""

    Name: Annotated[str, Field(default=...)]

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Tank_Volume: Annotated[float, Field(default=..., gt=0.0)]

    Tank_Height: Annotated[float, Field(default=..., gt=0.0)]
    """Height is measured in the axial direction for horizontal cylinders"""

    Tank_Shape: Annotated[Literal['VerticalCylinder', 'HorizontalCylinder', 'Other'], Field(default='VerticalCylinder')]

    Tank_Perimeter: Annotated[float, Field(ge=0.0)]
    """Only used if Tank Shape is Other"""

    Maximum_Temperature_Limit: Annotated[float, Field()]

    Heater_Priority_Control: Annotated[Literal['MasterSlave', 'Simultaneous'], Field(default='MasterSlave')]

    Heater_1_Setpoint_Temperature_Schedule_Name: Annotated[str, Field(default=...)]

    Heater_1_Deadband_Temperature_Difference: Annotated[float, Field(ge=0.0, default=0.0)]

    Heater_1_Capacity: Annotated[float, Field(ge=0.0)]

    Heater_1_Height: Annotated[float, Field(ge=0.0)]

    Heater_2_Setpoint_Temperature_Schedule_Name: Annotated[str, Field(default=...)]

    Heater_2_Deadband_Temperature_Difference: Annotated[float, Field(ge=0.0, default=0.0)]

    Heater_2_Capacity: Annotated[float, Field(ge=0.0)]

    Heater_2_Height: Annotated[float, Field(ge=0.0)]

    Heater_Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Coal', 'Diesel', 'Gasoline', 'OtherFuel1', 'OtherFuel2', 'Steam', 'DistrictHeating'], Field(default=...)]

    Heater_Thermal_Efficiency: Annotated[float, Field(default=..., gt=0.0, le=1.0)]

    Off_Cycle_Parasitic_Fuel_Consumption_Rate: Annotated[float, Field(ge=0.0, default=0.0)]

    Off_Cycle_Parasitic_Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Coal', 'Diesel', 'Gasoline', 'OtherFuel1', 'OtherFuel2', 'Steam', 'DistrictHeating'], Field()]

    Off_Cycle_Parasitic_Heat_Fraction_To_Tank: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Off_Cycle_Parasitic_Height: Annotated[float, Field(ge=0.0, default=0.0)]

    On_Cycle_Parasitic_Fuel_Consumption_Rate: Annotated[float, Field(ge=0.0, default=0.0)]

    On_Cycle_Parasitic_Fuel_Type: Annotated[Literal['Electricity', 'NaturalGas', 'PropaneGas', 'FuelOil#1', 'FuelOil#2', 'Coal', 'Diesel', 'Gasoline', 'OtherFuel1', 'OtherFuel2', 'Steam', 'DistrictHeating'], Field()]

    On_Cycle_Parasitic_Heat_Fraction_To_Tank: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    On_Cycle_Parasitic_Height: Annotated[float, Field(ge=0.0, default=0.0)]

    Ambient_Temperature_Indicator: Annotated[Literal['Schedule', 'Zone', 'Outdoors'], Field(default=...)]

    Ambient_Temperature_Schedule_Name: Annotated[str, Field()]

    Ambient_Temperature_Zone_Name: Annotated[str, Field()]

    Ambient_Temperature_Outdoor_Air_Node_Name: Annotated[str, Field()]
    """required for Ambient Temperature Indicator=Outdoors"""

    Uniform_Skin_Loss_Coefficient_Per_Unit_Area_To_Ambient_Temperature: Annotated[float, Field(ge=0.0)]

    Skin_Loss_Fraction_To_Zone: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Off_Cycle_Flue_Loss_Coefficient_To_Ambient_Temperature: Annotated[float, Field(ge=0.0)]

    Off_Cycle_Flue_Loss_Fraction_To_Zone: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]

    Peak_Use_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Only used if Use Side Node connections are blank"""

    Use_Flow_Rate_Fraction_Schedule_Name: Annotated[str, Field()]
    """If blank, defaults to 1.0 at all times"""

    Cold_Water_Supply_Temperature_Schedule_Name: Annotated[str, Field()]
    """Only used if use side node connections are blank"""

    Use_Side_Inlet_Node_Name: Annotated[str, Field()]

    Use_Side_Outlet_Node_Name: Annotated[str, Field()]

    Use_Side_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]
    """The use side effectiveness in the stratified tank model is a simplified analogy of"""

    Use_Side_Inlet_Height: Annotated[float, Field(ge=0.0, default=0.0)]
    """Defaults to bottom of tank"""

    Use_Side_Outlet_Height: Annotated[float, Field(ge=0.0, default=Autocalculate)]
    """Defaults to top of tank"""

    Source_Side_Inlet_Node_Name: Annotated[str, Field()]

    Source_Side_Outlet_Node_Name: Annotated[str, Field()]

    Source_Side_Effectiveness: Annotated[float, Field(gt=0.0, le=1.0, default=1.0)]
    """The source side effectiveness in the stratified tank model is a simplified analogy of"""

    Source_Side_Inlet_Height: Annotated[float, Field(ge=0.0, default=Autocalculate)]
    """Defaults to top of tank"""

    Source_Side_Outlet_Height: Annotated[float, Field(ge=0.0, default=0.0)]
    """Defaults to bottom of tank"""

    Inlet_Mode: Annotated[Literal['Fixed', 'Seeking'], Field(default='Fixed')]

    Use_Side_Design_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Source_Side_Design_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Indirect_Water_Heating_Recovery_Time: Annotated[float, Field(gt=0.0, default=1.5)]
    """Parameter for autosizing design flow rates for indirectly heated water tanks"""

    Number_Of_Nodes: Annotated[int, Field(ge=1, le=12, default=1)]

    Additional_Destratification_Conductivity: Annotated[float, Field(ge=0.0, default=0.0)]

    Node_1_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_2_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_3_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_4_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_5_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_6_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_7_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_8_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_9_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_10_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_11_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Node_12_Additional_Loss_Coefficient: Annotated[float, Field(default=0.0)]

    Source_Side_Flow_Control_Mode: Annotated[Literal['StorageTank', 'IndirectHeatPrimarySetpoint', 'IndirectHeatAlternateSetpoint'], Field(default='IndirectHeatPrimarySetpoint')]
    """StorageTank mode always requests flow unless tank is at its Maximum Temperature Limit"""

    Indirect_Alternate_Setpoint_Temperature_Schedule_Name: Annotated[str, Field()]
    """This field is only used if the previous is set to IndirectHeatAlternateSetpoint"""