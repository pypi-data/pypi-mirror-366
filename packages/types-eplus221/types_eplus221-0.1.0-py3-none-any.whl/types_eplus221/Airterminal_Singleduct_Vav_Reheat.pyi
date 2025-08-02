from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Singleduct_Vav_Reheat(EpBunch):
    """Central air system terminal unit, single duct, variable volume, with reheat coil (hot"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Damper_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """the outlet node of the damper and the inlet node of the reheat coil"""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """the inlet node to the terminal unit and the damper"""

    Maximum_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Zone_Minimum_Air_Flow_Input_Method: Annotated[Literal['Constant', 'FixedFlowRate', 'Scheduled'], Field(default='Constant')]
    """Constant = Constant Minimum Air Flow Fraction (a fraction of Maximum Air Flow Rate)"""

    Constant_Minimum_Air_Flow_Fraction: Annotated[float, Field(default=autosize)]
    """This field is used if the field Zone Minimum Air Flow Input Method is Constant"""

    Fixed_Minimum_Air_Flow_Rate: Annotated[float, Field(default=autosize)]
    """This field is used if the field Zone Minimum Air Flow Input Method is FixedFlowRate."""

    Minimum_Air_Flow_Fraction_Schedule_Name: Annotated[str, Field()]
    """This field is used if the field Zone Minimum Air Flow Input Method is Scheduled"""

    Reheat_Coil_Object_Type: Annotated[Literal['Coil:Heating:Water', 'Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam'], Field(default=...)]

    Reheat_Coil_Name: Annotated[str, Field(default=...)]

    Maximum_Hot_Water_Or_Steam_Flow_Rate: Annotated[str, Field()]
    """Not used when reheat coil type is gas or electric"""

    Minimum_Hot_Water_Or_Steam_Flow_Rate: Annotated[str, Field(default='0.0')]
    """Not used when reheat coil type is gas or electric"""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """The outlet node of the terminal unit and the reheat coil."""

    Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]

    Damper_Heating_Action: Annotated[Literal['Normal', 'Reverse', 'ReverseWithLimits'], Field(default='ReverseWithLimits')]
    """Normal means the damper is fixed at the minimum position in heating mode"""

    Maximum_Flow_Per_Zone_Floor_Area_During_Reheat: Annotated[float, Field(default=autosize)]
    """Used only when Reheat Coil Object Type = Coil:Heating:Water and Damper Heating Action = ReverseWithLimits"""

    Maximum_Flow_Fraction_During_Reheat: Annotated[float, Field(default=autosize)]
    """Used only when Reheat Coil Object Type = Coil:Heating:Water and Damper Heating Action = ReverseWithLimits"""

    Maximum_Reheat_Air_Temperature: Annotated[float, Field(gt=0.0)]
    """Specifies the maximum allowable supply air temperature leaving the reheat coil."""

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """When the name of a DesignSpecification:OutdoorAir object is entered, the terminal"""