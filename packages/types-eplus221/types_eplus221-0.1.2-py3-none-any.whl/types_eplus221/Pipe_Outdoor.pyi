from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Pipe_Outdoor(EpBunch):
    """Pipe model with transport delay and heat transfer to the environment."""

    Name: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]

    Fluid_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Fluid_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Ambient_Temperature_Outdoor_Air_Node_Name: Annotated[str, Field()]

    Pipe_Inside_Diameter: Annotated[float, Field(gt=0)]

    Pipe_Length: Annotated[float, Field(gt=0.0)]