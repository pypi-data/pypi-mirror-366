from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Singlezone_Humidity_Minimum(EpBunch):
    """The Single Zone Minimum Humidity Setpoint Manager allows the"""

    Name: Annotated[str, Field(default=...)]

    Setpoint_Node_Or_Nodelist_Name: Annotated[str, Field(default=...)]
    """Node(s) at which humidity ratio setpoint will be set"""

    Control_Zone_Air_Node_Name: Annotated[str, Field(default=...)]
    """Name of the zone air node for the humidity control zone"""