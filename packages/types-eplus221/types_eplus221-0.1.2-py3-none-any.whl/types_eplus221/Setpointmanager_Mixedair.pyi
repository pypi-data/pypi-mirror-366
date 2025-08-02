from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Mixedair(EpBunch):
    """The Mixed Air Setpoint Manager is meant to be used in conjunction"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature'], Field(default='Temperature')]

    Reference_Setpoint_Node_Name: Annotated[str, Field(default=...)]

    Fan_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Fan_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Setpoint_Node_or_NodeList_Name: Annotated[str, Field(default=...)]
    """Node(s) at which the temperature will be set"""

    Cooling_Coil_Inlet_Node_Name: Annotated[str, Field()]
    """Optional field used to limit economizer operation to prevent freezing of DX cooling coil."""

    Cooling_coil_Outlet_Node_Name: Annotated[str, Field()]
    """Optional field used to limit economizer operation to prevent freezing of DX cooling coil."""

    Minimum_Temperature_at_Cooling_Coil_Outlet_Node: Annotated[float, Field(gt=0.0, default=7.2)]
    """Optional field used to limit economizer operation to prevent freezing of DX cooling coil."""