from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheatexchanger_Pond(EpBunch):
    """A model of a shallow pond with immersed pipe loops."""

    Name: Annotated[str, Field(default=...)]

    Fluid_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Fluid_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Pond_Depth: Annotated[float, Field(default=..., gt=0)]

    Pond_Area: Annotated[float, Field(default=..., gt=0)]

    Hydronic_Tubing_Inside_Diameter: Annotated[float, Field(default=..., gt=0)]

    Hydronic_Tubing_Outside_Diameter: Annotated[float, Field(default=..., gt=0)]

    Hydronic_Tubing_Thermal_Conductivity: Annotated[float, Field(default=..., gt=0)]

    Ground_Thermal_Conductivity: Annotated[float, Field(default=..., gt=0)]

    Number_of_Tubing_Circuits: Annotated[int, Field(default=..., ge=1)]

    Length_of_Each_Tubing_Circuit: Annotated[float, Field(default=..., ge=0)]