from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Singleduct_Vav_Reheat_Variablespeedfan(EpBunch):
    """Central air system terminal unit, single duct, variable volume, with reheat coil (hot"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Maximum_Cooling_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0.0)]

    Maximum_Heating_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0.0)]

    Zone_Minimum_Air_Flow_Fraction: Annotated[str, Field(default=...)]
    """fraction of cooling air flow rate"""

    Air_Inlet_Node_Name: Annotated[str, Field()]
    """The name of the HVAC system node that is the air inlet node for the"""

    Air_Outlet_Node_Name: Annotated[str, Field()]
    """The name of the HVAC system node that is the air outlet node for the"""

    Fan_Object_Type: Annotated[Literal['Fan:SystemModel', 'Fan:VariableVolume'], Field(default=...)]

    Fan_Name: Annotated[str, Field(default=...)]

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Water', 'Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam'], Field(default=...)]

    Heating_Coil_Name: Annotated[str, Field(default=...)]

    Maximum_Hot_Water_or_Steam_Flow_Rate: Annotated[float, Field()]
    """Not used when heating coil type is gas or electric"""

    Minimum_Hot_Water_or_Steam_Flow_Rate: Annotated[float, Field(ge=0.0, default=0.0)]
    """Not used when heating coil type is gas or electric"""

    Heating_Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]