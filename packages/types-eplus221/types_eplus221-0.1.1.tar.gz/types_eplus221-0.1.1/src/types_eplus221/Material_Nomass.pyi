from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Material_Nomass(EpBunch):
    """Regular materials properties described whose principal description is R (Thermal Resistance)"""

    Name: Annotated[str, Field(default=...)]

    Roughness: Annotated[Literal['VeryRough', 'Rough', 'MediumRough', 'MediumSmooth', 'Smooth', 'VerySmooth'], Field(default=...)]

    Thermal_Resistance: Annotated[float, Field(default=..., ge=.001)]

    Thermal_Absorptance: Annotated[float, Field(gt=0, le=0.99999, default=.9)]

    Solar_Absorptance: Annotated[float, Field(ge=0, le=1, default=.7)]

    Visible_Absorptance: Annotated[float, Field(ge=0, le=1, default=.7)]