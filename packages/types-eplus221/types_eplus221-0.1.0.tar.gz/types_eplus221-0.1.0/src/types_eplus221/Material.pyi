from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Material(EpBunch):
    """Regular materials described with full set of thermal properties"""

    Name: Annotated[str, Field(default=...)]

    Roughness: Annotated[Literal['VeryRough', 'Rough', 'MediumRough', 'MediumSmooth', 'Smooth', 'VerySmooth'], Field(default=...)]

    Thickness: Annotated[float, Field(default=..., gt=0)]

    Conductivity: Annotated[float, Field(default=..., gt=0)]

    Density: Annotated[float, Field(default=..., gt=0)]

    Specific_Heat: Annotated[float, Field(default=..., ge=100)]

    Thermal_Absorptance: Annotated[float, Field(gt=0, le=0.99999, default=.9)]

    Solar_Absorptance: Annotated[float, Field(ge=0, le=1, default=.7)]

    Visible_Absorptance: Annotated[float, Field(ge=0, le=1, default=.7)]