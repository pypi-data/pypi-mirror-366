from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Singleduct_Constantvolume_Fourpipeinduction(EpBunch):
    """Central air system terminal unit, single duct, variable volume, induction unit with"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Maximum_Total_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0.0)]

    Induction_Ratio: Annotated[float, Field(ge=0.0, default=2.5)]
    """ratio of induced air flow rate to primary air flow rate"""

    Supply_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Induced_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """should be a zone exhaust node, also the heating coil inlet node"""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """should be a zone inlet node"""

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Water'], Field(default=...)]

    Heating_Coil_Name: Annotated[str, Field(default=...)]

    Maximum_Hot_Water_Flow_Rate: Annotated[float, Field()]
    """Not used when heating coil type is gas or electric"""

    Minimum_Hot_Water_Flow_Rate: Annotated[float, Field(ge=0.0, default=0.0)]
    """Not used when heating coil type is gas or electric"""

    Heating_Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry'], Field()]

    Cooling_Coil_Name: Annotated[str, Field()]

    Maximum_Cold_Water_Flow_Rate: Annotated[float, Field()]

    Minimum_Cold_Water_Flow_Rate: Annotated[float, Field(ge=0.0, default=0.0)]

    Cooling_Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]

    Zone_Mixer_Name: Annotated[str, Field(default=...)]