from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Glazing_Refractionextinctionmethod(EpBunch):
    """Glass material properties for Windows or Glass Doors"""

    Name: Annotated[str, Field(default=...)]

    Thickness: Annotated[float, Field(default=..., gt=0.0)]

    Solar_Index_Of_Refraction: Annotated[float, Field(default=..., gt=1.0)]

    Solar_Extinction_Coefficient: Annotated[float, Field(default=..., gt=0.0)]

    Visible_Index_Of_Refraction: Annotated[float, Field(default=..., gt=1.0)]

    Visible_Extinction_Coefficient: Annotated[float, Field(default=..., gt=0.0)]

    Infrared_Transmittance_At_Normal_Incidence: Annotated[float, Field(ge=0.0, lt=1.0, default=0.0)]

    Infrared_Hemispherical_Emissivity: Annotated[float, Field(gt=0.0, lt=1.0, default=0.84)]
    """Emissivity of front and back side assumed equal"""

    Conductivity: Annotated[float, Field(gt=0.0, default=0.9)]

    Dirt_Correction_Factor_For_Solar_And_Visible_Transmittance: Annotated[float, Field(gt=0.0, le=1.0, default=1.0)]

    Solar_Diffusing: Annotated[Literal['No', 'Yes'], Field(default='No')]