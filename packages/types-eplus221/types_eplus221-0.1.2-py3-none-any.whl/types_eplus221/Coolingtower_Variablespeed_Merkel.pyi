from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coolingtower_Variablespeed_Merkel(EpBunch):
    """This tower model is based on Merkel's theory, which is also the basis"""

    Name: Annotated[str, Field(default=...)]
    """Tower Name"""

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of tower water inlet node"""

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of tower water outlet node"""

    Performance_Input_Method: Annotated[Literal['UFactorTimesAreaAndDesignWaterFlowRate', 'NominalCapacity'], Field(default='NominalCapacity')]
    """User can define tower thermal performance by specifying the tower UA,"""

    Heat_Rejection_Capacity_and_Nominal_Capacity_Sizing_Ratio: Annotated[float, Field(default=1.25)]

    Nominal_Capacity: Annotated[float, Field(gt=0.0)]
    """Nominal tower capacity with entering water at 35C (95F), leaving water at"""

    Free_Convection_Nominal_Capacity: Annotated[float, Field(ge=0.0)]
    """required field when performance method is NominalCapacity"""

    Free_Convection_Nominal_Capacity_Sizing_Factor: Annotated[float, Field(gt=0.0, lt=1.0, default=0.1)]
    """This field is only used if the previous field is set to autocalculate"""

    Design_Water_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Design_Water_Flow_Rate_per_Unit_of_Nominal_Capacity: Annotated[float, Field(default=5.382E-8)]
    """This field is only used if the previous is set to autocalculate and performance input method is NominalCapacity"""

    Design_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """This is the air flow rate at full fan speed"""

    Design_Air_Flow_Rate_Per_Unit_of_Nominal_Capacity: Annotated[float, Field(default=2.76316E-5)]
    """This field is only used if the previous is set to autocalculate"""

    Minimum_Air_Flow_Rate_Ratio: Annotated[float, Field(ge=0.1, le=0.5, default=0.2)]
    """Enter the minimum air flow rate ratio. This is typically determined by the variable"""

    Design_Fan_Power: Annotated[float, Field(default=..., gt=0.0)]
    """This is the fan motor electric input power at high speed"""

    Design_Fan_Power_Per_Unit_of_Nominal_Capacity: Annotated[float, Field(default=0.0105)]
    """This field is only used if the previous is set to autocalculate"""

    Fan_Power_Modifier_Function_of_Air_Flow_Rate_Ratio_Curve_Name: Annotated[str, Field(default=...)]
    """Any curve or table with one independent variable can be used"""

    Free_Convection_Regime_Air_Flow_Rate: Annotated[float, Field(ge=0.0, default=0.0)]

    Free_Convection_Regime_Air_Flow_Rate_Sizing_Factor: Annotated[float, Field(gt=0.0, lt=1.0, default=0.1)]
    """This field is only used if the previous field is set to autocalculate."""

    Design_Air_Flow_Rate_UFactor_Times_Area_Value: Annotated[float, Field()]
    """required field when performance method is UFactorTimesAreaAndDesignWaterFlowRate"""

    Free_Convection_Regime_UFactor_Times_Area_Value: Annotated[float, Field(ge=0.0, le=300000.0, default=0.0)]
    """required field when performance input method is UFactorTimesAreaAndDesignWaterFlowRate"""

    Free_Convection_UFactor_Times_Area_Value_Sizing_Factor: Annotated[float, Field(gt=0.0, lt=1.0, default=0.1)]
    """required field when performance input method is UFactorTimesAreaAndDesignWaterFlowRate"""

    UFactor_Times_Area_Modifier_Function_of_Air_Flow_Ratio_Curve_Name: Annotated[str, Field(default=...)]
    """This curve describes how tower's design UA changes with variable air flow rate"""

    UFactor_Times_Area_Modifier_Function_of_Wetbulb_Temperature_Difference_Curve_Name: Annotated[str, Field(default=...)]
    """curve describes how tower UA changes with outdoor air wet-bulb temperature difference from design wet-bulb"""

    UFactor_Times_Area_Modifier_Function_of_Water_Flow_Ratio_Curve_Name: Annotated[str, Field(default=...)]
    """curve describes how tower UA changes with the flow rate of condenser water through the tower"""

    Design_Inlet_Air_DryBulb_Temperature: Annotated[float, Field(ge=20.0, default=35.0)]
    """Enter the tower's design inlet air dry-bulb temperature"""

    Design_Inlet_Air_WetBulb_Temperature: Annotated[float, Field(ge=20.0, default=25.6)]
    """Enter the tower's design inlet air wet-bulb temperature"""

    Design_Approach_Temperature: Annotated[float, Field(gt=0, default=autosize)]
    """Enter the approach temperature corresponding to the design inlet air"""

    Design_Range_Temperature: Annotated[float, Field(gt=0, default=autosize)]
    """Enter the range temperature corresponding to the design inlet air"""

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """This heater maintains the basin water temperature at the basin heater setpoint"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """Enter the outdoor dry-bulb temperature when the basin heater turns on"""

    Basin_Heater_Operating_Schedule_Name: Annotated[str, Field()]
    """Schedule values greater than 0 allow the basin heater to operate whenever the outdoor"""

    Evaporation_Loss_Mode: Annotated[Literal['LossFactor', 'SaturatedExit'], Field()]

    Evaporation_Loss_Factor: Annotated[float, Field(default=0.2)]
    """Rate of water evaporated from the cooling tower and lost to the outdoor air [%/K]"""

    Drift_Loss_Percent: Annotated[float, Field(default=0.008)]
    """Rate of drift loss as a percentage of circulating condenser water flow rate"""

    Blowdown_Calculation_Mode: Annotated[Literal['ConcentrationRatio', 'ScheduledRate'], Field()]

    Blowdown_Concentration_Ratio: Annotated[float, Field(ge=2.0, default=3.0)]
    """Characterizes the rate of blowdown in the cooling tower."""

    Blowdown_Makeup_Water_Usage_Schedule_Name: Annotated[str, Field()]
    """Makeup water usage due to blowdown results from occasionally draining some amount"""

    Supply_Water_Storage_Tank_Name: Annotated[str, Field()]

    Outdoor_Air_Inlet_Node_Name: Annotated[str, Field()]
    """Enter the name of an outdoor air node"""

    Number_of_Cells: Annotated[int, Field(ge=1, default=1)]

    Cell_Control: Annotated[Literal['MinimalCell', 'MaximalCell'], Field(default='MinimalCell')]

    Cell_Minimum_Water_Flow_Rate_Fraction: Annotated[float, Field(gt=0.0, le=1.0, default=0.33)]
    """The allowable minimal fraction of the nominal flow rate per cell"""

    Cell_Maximum_Water_Flow_Rate_Fraction: Annotated[float, Field(ge=1, default=2.5)]
    """The allowable maximal fraction of the nominal flow rate per cell"""

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""