from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coolingtower_Variablespeed(EpBunch):
    """This open wet tower model is based on purely empirical algorithms derived from manufacturer's"""

    Name: Annotated[str, Field(default=...)]
    """Tower Name"""

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of tower water inlet node"""

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of tower water outlet node"""

    Model_Type: Annotated[Literal['CoolToolsCrossFlow', 'CoolToolsUserDefined', 'YorkCalc', 'YorkCalcUserDefined'], Field(default='YorkCalc')]
    """Determines the coefficients and form of the equation for calculating"""

    Model_Coefficient_Name: Annotated[str, Field()]
    """Name of the tower model coefficient object."""

    Design_Inlet_Air_Wet_Bulb_Temperature: Annotated[float, Field(ge=20.0, default=25.6)]
    """Enter the tower's design inlet air wet-bulb temperature"""

    Design_Approach_Temperature: Annotated[float, Field(gt=0, default=3.9)]
    """Enter the approach temperature corresponding to the design inlet air"""

    Design_Range_Temperature: Annotated[float, Field(gt=0, default=5.6)]
    """Enter the range temperature corresponding to the design inlet air"""

    Design_Water_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Water flow rate through the tower at design conditions"""

    Design_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Design (maximum) air flow rate through the tower"""

    Design_Fan_Power: Annotated[float, Field(default=..., gt=0.0)]
    """Enter the fan motor electric input power at design (max) air flow through the tower"""

    Fan_Power_Ratio_Function_Of_Air_Flow_Rate_Ratio_Curve_Name: Annotated[str, Field()]
    """FPR = a + b*AFR + c*AFR**2 + d*AFR**3"""

    Minimum_Air_Flow_Rate_Ratio: Annotated[float, Field(ge=0.2, le=0.5, default=0.2)]
    """Enter the minimum air flow rate ratio. This is typically determined by the variable"""

    Fraction_Of_Tower_Capacity_In_Free_Convection_Regime: Annotated[float, Field(ge=0.0, le=0.2, default=0.125)]
    """Enter the fraction of tower capacity in the free convection regime. This is the"""

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """This heater maintains the basin water temperature at the basin heater setpoint"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """Enter the outdoor dry-bulb temperature when the basin heater turns on"""

    Basin_Heater_Operating_Schedule_Name: Annotated[str, Field()]
    """Schedule values greater than 0 allow the basin heater to operate whenever the outdoor"""

    Evaporation_Loss_Mode: Annotated[Literal['LossFactor', 'SaturatedExit'], Field()]

    Evaporation_Loss_Factor: Annotated[float, Field(default=0.2)]
    """Rate of water evaporated from the cooling tower and lost to the outdoor air [%/K]"""

    Drift_Loss_Percent: Annotated[float, Field()]
    """Rate of drift loss as a percentage of circulating condenser water flow rate"""

    Blowdown_Calculation_Mode: Annotated[Literal['ConcentrationRatio', 'ScheduledRate'], Field()]

    Blowdown_Concentration_Ratio: Annotated[float, Field(ge=2.0, default=3.0)]
    """Characterizes the rate of blowdown in the cooling tower."""

    Blowdown_Makeup_Water_Usage_Schedule_Name: Annotated[str, Field()]
    """Makeup water usage due to blowdown results from occasionally draining a small amount"""

    Supply_Water_Storage_Tank_Name: Annotated[str, Field()]

    Outdoor_Air_Inlet_Node_Name: Annotated[str, Field()]
    """Enter the name of an outdoor air node"""

    Number_Of_Cells: Annotated[int, Field(ge=1, default=1)]

    Cell_Control: Annotated[Literal['MinimalCell', 'MaximalCell'], Field(default='MinimalCell')]

    Cell_Minimum_Water_Flow_Rate_Fraction: Annotated[float, Field(gt=0.0, le=1.0, default=0.33)]
    """The allowable minimal fraction of the nominal flow rate per cell"""

    Cell_Maximum_Water_Flow_Rate_Fraction: Annotated[float, Field(ge=1, default=2.5)]
    """The allowable maximal fraction of the nominal flow rate per cell"""

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""