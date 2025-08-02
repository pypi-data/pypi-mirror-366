from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Evaporativefluidcooler_Twospeed(EpBunch):
    """This model is based on Merkel's theory, which is also the basis"""

    Name: Annotated[str, Field(default=...)]
    """fluid cooler name"""

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of fluid cooler water inlet node"""

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of fluid cooler water outlet node"""

    High_Fan_Speed_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    High_Fan_Speed_Fan_Power: Annotated[float, Field(default=..., gt=0.0)]
    """This is the fan motor electric input power at high speed"""

    Low_Fan_Speed_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Low speed air flow rate must be less than high speed air flow rate"""

    Low_Fan_Speed_Air_Flow_Rate_Sizing_Factor: Annotated[float, Field(default=0.5)]
    """This field is only used if the previous field is set to autocalculate"""

    Low_Fan_Speed_Fan_Power: Annotated[float, Field(default=..., gt=0.0)]
    """This is the fan motor electric input power at low speed"""

    Low_Fan_Speed_Fan_Power_Sizing_Factor: Annotated[float, Field(default=0.16)]
    """This field is only used if the previous field is set to autocalculate."""

    Design_Spray_Water_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Performance_Input_Method: Annotated[Literal['UFactorTimesAreaAndDesignWaterFlowRate', 'StandardDesignCapacity', 'UserSpecifiedDesignCapacity'], Field(default=...)]
    """User can define fluid cooler thermal performance by specifying the fluid cooler UA"""

    Outdoor_Air_Inlet_Node_Name: Annotated[str, Field()]
    """Enter the name of an outdoor air node"""

    Heat_Rejection_Capacity_And_Nominal_Capacity_Sizing_Ratio: Annotated[float, Field(default=1.25)]

    High_Speed_Standard_Design_Capacity: Annotated[float, Field(gt=0.0)]
    """Standard design capacity with entering water at 35C (95F), leaving water at"""

    Low_Speed_Standard_Design_Capacity: Annotated[float, Field(gt=0.0)]
    """Standard design capacity with entering water at 35C (95F), leaving water at"""

    Low_Speed_Standard_Capacity_Sizing_Factor: Annotated[float, Field(default=0.5)]
    """This field is only used if the previous field is set to autocalculate"""

    High_Fan_Speed_U_Factor_Times_Area_Value: Annotated[float, Field(gt=0.0, le=2100000.0)]
    """Only used for Performance Input Method = UFactorTimesAreaAndDesignWaterFlowRate;"""

    Low_Fan_Speed_U_Factor_Times_Area_Value: Annotated[float, Field(gt=0.0, le=300000.0)]
    """Only used for Performance Input Method = UFactorTimesAreaAndDesignWaterFlowRate;"""

    Low_Fan_Speed_U_Factor_Times_Area_Sizing_Factor: Annotated[float, Field(default=0.6)]
    """This field is only used if the previous field is set to autocalculate and"""

    Design_Water_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Input value is ignored if fluid cooler Performance Input Method= StandardDesignCapacity"""

    High_Speed_User_Specified_Design_Capacity: Annotated[float, Field(gt=0.0)]
    """Only used for Performance Input Method = UserSpecifiedDesignCapacity;"""

    Low_Speed_User_Specified_Design_Capacity: Annotated[float, Field(gt=0.0)]
    """Only used for Performance Input Method = UserSpecifiedDesignCapacity;"""

    Low_Speed_User_Specified_Design_Capacity_Sizing_Factor: Annotated[float, Field(default=0.5)]
    """This field is only used if the previous field is set to autocalculate"""

    Design_Entering_Water_Temperature: Annotated[float, Field(gt=0.0)]
    """Only used for Performance Input Method = UserSpecifiedDesignCapacity;"""

    Design_Entering_Air_Temperature: Annotated[float, Field(gt=0.0)]
    """Only used for Performance Input Method = UserSpecifiedDesignCapacity;"""

    Design_Entering_Air_Wet_Bulb_Temperature: Annotated[float, Field(gt=0.0)]
    """Only used for Performance Input Method = UserSpecifiedDesignCapacity;"""

    High_Speed_Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized capacity and flow rates"""

    Evaporation_Loss_Mode: Annotated[Literal['LossFactor', 'SaturatedExit'], Field(default='SaturatedExit')]

    Evaporation_Loss_Factor: Annotated[float, Field()]
    """Rate of water evaporation from the Fluid Cooler and lost to the outdoor air [%/K]"""

    Drift_Loss_Percent: Annotated[float, Field(default=0.008)]
    """Default value is under investigation. For now cooling tower's default value is taken."""

    Blowdown_Calculation_Mode: Annotated[Literal['ConcentrationRatio', 'ScheduledRate'], Field(default='ConcentrationRatio')]

    Blowdown_Concentration_Ratio: Annotated[float, Field(ge=2.0, default=3.0)]
    """Characterizes the rate of blowdown in the Evaporative Fluid Cooler."""

    Blowdown_Makeup_Water_Usage_Schedule_Name: Annotated[str, Field()]
    """Makeup water usage due to blowdown results from occasionally draining some amount"""

    Supply_Water_Storage_Tank_Name: Annotated[str, Field()]