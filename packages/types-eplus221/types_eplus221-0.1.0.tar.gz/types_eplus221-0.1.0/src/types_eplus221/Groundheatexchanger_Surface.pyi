from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheatexchanger_Surface(EpBunch):
    """A hydronic surface/panel consisting of a multi-layer construction with embedded rows of tubes."""

    Name: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]

    Fluid_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Fluid_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Hydronic_Tubing_Inside_Diameter: Annotated[float, Field(gt=0)]

    Number_Of_Tubing_Circuits: Annotated[int, Field(ge=1)]

    Hydronic_Tube_Spacing: Annotated[float, Field(gt=0.0)]

    Surface_Length: Annotated[float, Field(gt=0.0)]

    Surface_Width: Annotated[float, Field(gt=0.0)]

    Lower_Surface_Environment: Annotated[Literal['Ground', 'Exposed'], Field(default='Ground')]