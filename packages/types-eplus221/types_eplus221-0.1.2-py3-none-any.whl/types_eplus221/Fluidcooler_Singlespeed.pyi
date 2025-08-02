from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fluidcooler_Singlespeed(EpBunch):
    """The fluid cooler is modeled as a cross flow heat exchanger (both streams unmixed) with"""

    Name: Annotated[str, Field(default=...)]
    """fluid cooler name"""

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of fluid cooler water inlet node"""

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of fluid cooler water outlet node"""

    Performance_Input_Method: Annotated[Literal['UFactorTimesAreaAndDesignWaterFlowRate', 'NominalCapacity'], Field(default='NominalCapacity')]
    """User can define fluid cooler thermal performance by specifying the fluid cooler UA"""

    Design_Air_Flow_Rate_Ufactor_Times_Area_Value: Annotated[float, Field(gt=0.0, le=2100000.0)]
    """Leave field blank if fluid cooler Performance Input Method is NominalCapacity"""

    Nominal_Capacity: Annotated[float, Field(gt=0.0)]
    """Nominal fluid cooler capacity"""

    Design_Entering_Water_Temperature: Annotated[float, Field(default=..., gt=0.0)]
    """Design Entering Water Temperature must be specified for both the performance input methods and"""

    Design_Entering_Air_Temperature: Annotated[float, Field(default=..., gt=0.0)]
    """Design Entering Air Temperature must be specified for both the performance input methods and"""

    Design_Entering_Air_Wetbulb_Temperature: Annotated[float, Field(default=..., gt=0.0)]
    """Design Entering Air Wet-bulb Temperature must be specified for both the performance input methods and"""

    Design_Water_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Design_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Design_Air_Flow_Rate_Fan_Power: Annotated[float, Field(default=..., gt=0.0)]
    """This is the fan motor electric input power"""

    Outdoor_Air_Inlet_Node_Name: Annotated[str, Field()]
    """Enter the name of an outdoor air node"""