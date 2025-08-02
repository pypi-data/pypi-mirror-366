from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Shade(EpBunch):
    """Specifies the properties of window shade materials. Reflectance and emissivity"""

    Name: Annotated[str, Field(default=...)]

    Solar_Transmittance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """Assumed independent of incidence angle"""

    Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """Assumed same for both sides"""

    Visible_Transmittance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """Assumed independent of incidence angle"""

    Visible_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """Assumed same for both sides"""

    Infrared_Hemispherical_Emissivity: Annotated[float, Field(default=..., gt=0, lt=1)]

    Infrared_Transmittance: Annotated[float, Field(default=..., ge=0, lt=1)]

    Thickness: Annotated[float, Field(default=..., gt=0)]

    Conductivity: Annotated[float, Field(default=..., gt=0)]

    Shade_To_Glass_Distance: Annotated[float, Field(ge=0.001, le=1.0, default=0.050)]

    Top_Opening_Multiplier: Annotated[float, Field(ge=0.0, le=1.0, default=0.5)]

    Bottom_Opening_Multiplier: Annotated[float, Field(ge=0.0, le=1.0, default=0.5)]

    Left_Side_Opening_Multiplier: Annotated[float, Field(ge=0.0, le=1.0, default=0.5)]

    Right_Side_Opening_Multiplier: Annotated[float, Field(ge=0.0, le=1.0, default=0.5)]

    Airflow_Permeability: Annotated[float, Field(ge=0.0, le=0.8, default=0.0)]