from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Singleduct_Vav_Heatandcool_Reheat(EpBunch):
    """Central air system terminal unit, single duct, variable volume for both cooling and"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Damper_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """the outlet node of the damper and the inlet node of the reheat coil"""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """the inlet node to the terminal unit and the damper"""

    Maximum_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Zone_Minimum_Air_Flow_Fraction: Annotated[str, Field(default=...)]
    """fraction of maximum air flow"""

    Reheat_Coil_Object_Type: Annotated[Literal['Coil:Heating:Water', 'Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam'], Field(default=...)]

    Reheat_Coil_Name: Annotated[str, Field(default=...)]

    Maximum_Hot_Water_or_Steam_Flow_Rate: Annotated[str, Field()]
    """Not used when reheat coil type is gas or electric"""

    Minimum_Hot_Water_or_Steam_Flow_Rate: Annotated[str, Field(default='0.0')]
    """Not used when reheat coil type is gas or electric"""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """The outlet node of the terminal unit and the reheat coil."""

    Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]

    Maximum_Reheat_Air_Temperature: Annotated[float, Field(gt=0.0)]
    """Specifies the maximum allowable supply air temperature leaving the reheat coil."""