from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Singleduct_Parallelpiu_Reheat(EpBunch):
    """Central air system terminal unit, single duct, variable volume, parallel powered"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Maximum_Primary_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0.0)]

    Maximum_Secondary_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0.0)]

    Minimum_Primary_Air_Flow_Fraction: Annotated[float, Field(default=..., ge=0.0, le=1.0)]

    Fan_On_Flow_Fraction: Annotated[float, Field(default=..., ge=0.0, le=1.0)]
    """the fraction of the primary air flow at which fan turns on"""

    Supply_Air_Inlet_Node_Name: Annotated[str, Field()]

    Secondary_Air_Inlet_Node_Name: Annotated[str, Field()]

    Outlet_Node_Name: Annotated[str, Field()]

    Reheat_Coil_Air_Inlet_Node_Name: Annotated[str, Field()]
    """mixer outlet node"""

    Zone_Mixer_Name: Annotated[str, Field()]

    Fan_Name: Annotated[str, Field()]
    """Fan type must be Fan:SystemModel or Fan:ConstantVolume"""

    Reheat_Coil_Object_Type: Annotated[Literal['Coil:Heating:Water', 'Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam'], Field(default=...)]

    Reheat_Coil_Name: Annotated[str, Field(default=...)]

    Maximum_Hot_Water_or_Steam_Flow_Rate: Annotated[float, Field()]
    """Not used when reheat coil type is gas or electric"""

    Minimum_Hot_Water_or_Steam_Flow_Rate: Annotated[float, Field(ge=0.0, default=0.0)]
    """Not used when reheat coil type is gas or electric"""

    Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]