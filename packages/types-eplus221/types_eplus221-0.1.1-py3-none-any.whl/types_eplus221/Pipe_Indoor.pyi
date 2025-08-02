from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Pipe_Indoor(EpBunch):
    """Pipe model with transport delay and heat transfer to the environment."""

    Name: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]

    Fluid_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Fluid_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Environment_Type: Annotated[Literal['Zone', 'Schedule'], Field(default='Zone')]

    Ambient_Temperature_Zone_Name: Annotated[str, Field()]

    Ambient_Temperature_Schedule_Name: Annotated[str, Field()]

    Ambient_Air_Velocity_Schedule_Name: Annotated[str, Field()]

    Pipe_Inside_Diameter: Annotated[float, Field(gt=0)]

    Pipe_Length: Annotated[float, Field(gt=0.0)]