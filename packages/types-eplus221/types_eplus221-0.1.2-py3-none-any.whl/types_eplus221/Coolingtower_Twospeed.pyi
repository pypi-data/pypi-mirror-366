from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coolingtower_Twospeed(EpBunch):
    """This tower model is based on Merkel's theory, which is also the basis"""

    Name: Annotated[str, Field(default=...)]
    """Tower Name"""

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of tower Water Inlet Node"""

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of tower Water Outlet Node"""

    Design_Water_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Leave field blank if Tower Performance Input Method is NominalCapacity"""

    High_Fan_Speed_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    High_Fan_Speed_Fan_Power: Annotated[float, Field(default=..., gt=0.0)]
    """This is the fan motor electric input power at high speed"""

    High_Fan_Speed_UFactor_Times_Area_Value: Annotated[float, Field(gt=0.0, le=2100000.0)]
    """Leave field blank if Tower Performance Input Method is NominalCapacity"""

    Low_Fan_Speed_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Low speed air flow rate must be less than high speed air flow rate"""

    Low_Fan_Speed_Air_Flow_Rate_Sizing_Factor: Annotated[float, Field(gt=0.0, lt=1.0, default=0.5)]
    """This field is only used if the previous field is set to autocalculate."""

    Low_Fan_Speed_Fan_Power: Annotated[float, Field(default=..., gt=0.0)]
    """This is the fan motor electric input power at low speed"""

    Low_Fan_Speed_Fan_Power_Sizing_Factor: Annotated[float, Field(gt=0.0, lt=1.0, default=0.16)]
    """This field is only used if the previous field is set to autocalculate."""

    Low_Fan_Speed_UFactor_Times_Area_Value: Annotated[float, Field(gt=0.0, le=300000.0)]
    """Leave field blank if tower Performance Input Method is NominalCapacity"""

    Low_Fan_Speed_UFactor_Times_Area_Sizing_Factor: Annotated[float, Field(gt=0.0, lt=1.0, default=0.6)]
    """This field is only used if the previous field is set to autocalculate and"""

    Free_Convection_Regime_Air_Flow_Rate: Annotated[float, Field(ge=0.0, default=0.0)]

    Free_Convection_Regime_Air_Flow_Rate_Sizing_Factor: Annotated[float, Field(gt=0.0, lt=1.0, default=0.1)]
    """This field is only used if the previous field is set to autocalculate."""

    Free_Convection_Regime_UFactor_Times_Area_Value: Annotated[float, Field(ge=0.0, le=300000.0, default=0.0)]
    """Leave field blank if Tower Performance Input Method is NominalCapacity"""

    Free_Convection_UFactor_Times_Area_Value_Sizing_Factor: Annotated[float, Field(gt=0.0, lt=1.0, default=0.1)]
    """This field is only used if the previous field is set to autocalculate and"""

    Performance_Input_Method: Annotated[Literal['UFactorTimesAreaAndDesignWaterFlowRate', 'NominalCapacity'], Field(default='UFactorTimesAreaAndDesignWaterFlowRate')]
    """User can define tower thermal performance by specifying the tower UA,"""

    Heat_Rejection_Capacity_and_Nominal_Capacity_Sizing_Ratio: Annotated[float, Field(default=1.25)]

    High_Speed_Nominal_Capacity: Annotated[float, Field(gt=0.0)]
    """Nominal tower capacity with entering water at 35C (95F), leaving water at"""

    Low_Speed_Nominal_Capacity: Annotated[float, Field(gt=0.0)]
    """Nominal tower capacity with entering water at 35C (95F), leaving water at"""

    Low_Speed_Nominal_Capacity_Sizing_Factor: Annotated[float, Field(gt=0.0, lt=1.0, default=0.5)]
    """This field is only used if the previous field is set to autocalculate"""

    Free_Convection_Nominal_Capacity: Annotated[float, Field(ge=0.0)]
    """Tower capacity in free convection regime with entering water at 35C (95F),"""

    Free_Convection_Nominal_Capacity_Sizing_Factor: Annotated[float, Field(gt=0.0, lt=1.0, default=0.1)]
    """This field is only used if the previous field is set to autocalculate"""

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