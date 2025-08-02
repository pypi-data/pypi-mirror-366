from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Plantcomponent_Temperaturesource(EpBunch):
    """Simulates an object of pre-determined (constant or scheduled) source temperature"""

    Name: Annotated[str, Field(default=...)]
    """Component Name"""

    Inlet_Node: Annotated[str, Field(default=...)]
    """Name of the source inlet node"""

    Outlet_Node: Annotated[str, Field(default=...)]
    """Name of the source outlet node"""

    Design_Volume_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """The design volumetric flow rate for this source"""

    Temperature_Specification_Type: Annotated[Literal['Constant', 'Scheduled'], Field()]

    Source_Temperature: Annotated[float, Field()]
    """Used if Temperature Specification Type = Constant"""

    Source_Temperature_Schedule_Name: Annotated[str, Field()]
    """Used if Temperature Specification Type = Scheduled"""