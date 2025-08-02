from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheatexchanger_Vertical_Properties(EpBunch):
    """Properties for vertical ground heat exchanger systems"""

    Name: Annotated[str, Field(default=...)]

    Depth_of_Top_of_Borehole: Annotated[float, Field(default=..., ge=0.0)]

    Borehole_Length: Annotated[float, Field(default=..., gt=0.0)]

    Borehole_Diameter: Annotated[float, Field(default=..., gt=0.0)]

    Grout_Thermal_Conductivity: Annotated[float, Field(default=..., gt=0.0)]

    Grout_Thermal_Heat_Capacity: Annotated[float, Field(default=..., gt=0.0)]

    Pipe_Thermal_Conductivity: Annotated[float, Field(default=..., gt=0.0)]

    Pipe_Thermal_Heat_Capacity: Annotated[float, Field(default=..., gt=0.0)]

    Pipe_Outer_Diameter: Annotated[float, Field(default=..., gt=0.0)]

    Pipe_Thickness: Annotated[float, Field(default=..., gt=0.0)]

    UTube_Distance: Annotated[float, Field(default=..., gt=0.0)]