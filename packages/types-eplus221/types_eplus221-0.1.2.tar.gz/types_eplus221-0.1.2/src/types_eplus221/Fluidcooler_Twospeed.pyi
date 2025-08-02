from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fluidcooler_Twospeed(EpBunch):
    """The fluid cooler is modeled as a cross flow heat exchanger (both streams unmixed) with"""

    Name: Annotated[str, Field(default=...)]
    """fluid cooler name"""

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of fluid cooler water inlet node"""

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of fluid cooler water outlet node"""

    Performance_Input_Method: Annotated[Literal['UFactorTimesAreaAndDesignWaterFlowRate', 'NominalCapacity'], Field(default='NominalCapacity')]
    """User can define fluid cooler thermal performance by specifying the fluid cooler UA"""

    High_Fan_Speed_Ufactor_Times_Area_Value: Annotated[float, Field(gt=0.0, le=2100000.0)]
    """Leave field blank if fluid cooler Performance Input Method is NominalCapacity"""

    Low_Fan_Speed_Ufactor_Times_Area_Value: Annotated[float, Field(gt=0.0, le=300000.0)]
    """Leave field blank if fluid cooler Performance Input Method is NominalCapacity"""

    Low_Fan_Speed_UFactor_Times_Area_Sizing_Factor: Annotated[float, Field(default=0.6)]
    """This field is only used if the previous field is set to autocalculate and"""

    High_Speed_Nominal_Capacity: Annotated[float, Field(gt=0.0)]
    """Nominal fluid cooler capacity at high fan speed"""

    Low_Speed_Nominal_Capacity: Annotated[float, Field(gt=0.0)]
    """Nominal fluid cooler capacity at low fan speed"""

    Low_Speed_Nominal_Capacity_Sizing_Factor: Annotated[float, Field(default=0.5)]
    """This field is only used if the previous field is set to autocalculate and"""

    Design_Entering_Water_Temperature: Annotated[float, Field(default=..., gt=0.0)]
    """Design Entering Water Temperature must be specified for both the performance input methods and"""

    Design_Entering_Air_Temperature: Annotated[float, Field(default=..., gt=0.0)]
    """Design Entering Air Temperature must be specified for both the performance input methods and"""

    Design_Entering_Air_Wetbulb_Temperature: Annotated[float, Field(default=..., gt=0.0)]
    """Design Entering Air Wet-bulb Temperature must be specified for both the performance input methods and"""

    Design_Water_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    High_Fan_Speed_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Air Flow Rate at High Fan Speed must be greater than Air Flow Rate at Low Fan Speed"""

    High_Fan_Speed_Fan_Power: Annotated[float, Field(default=..., gt=0.0)]
    """This is the fan motor electric input power at high speed"""

    Low_Fan_Speed_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Air Flow Rate at Low Fan Speed must be less than Air Flow Rate at High Fan Speed"""

    Low_Fan_Speed_Air_Flow_Rate_Sizing_Factor: Annotated[float, Field(default=0.5)]
    """This field is only used if the previous field is set to autocalculate."""

    Low_Fan_Speed_Fan_Power: Annotated[float, Field(default=..., gt=0.0)]
    """This is the fan motor electric input power at low speed"""

    Low_Fan_Speed_Fan_Power_Sizing_Factor: Annotated[float, Field(default=0.16)]
    """This field is only used if the previous field is set to autocalculate."""

    Outdoor_Air_Inlet_Node_Name: Annotated[str, Field()]