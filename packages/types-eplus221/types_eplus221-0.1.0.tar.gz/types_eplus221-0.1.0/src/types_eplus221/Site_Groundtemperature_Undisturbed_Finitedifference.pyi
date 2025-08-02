from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Groundtemperature_Undisturbed_Finitedifference(EpBunch):
    """Undisturbed ground temperature object using a"""

    Name: Annotated[str, Field(default=...)]

    Soil_Thermal_Conductivity: Annotated[float, Field(default=..., gt=0.0)]

    Soil_Density: Annotated[float, Field(default=..., gt=0.0)]

    Soil_Specific_Heat: Annotated[float, Field(default=..., gt=0.0)]

    Soil_Moisture_Content_Volume_Fraction: Annotated[float, Field(ge=0, le=100, default=30)]

    Soil_Moisture_Content_Volume_Fraction_At_Saturation: Annotated[float, Field(ge=0, le=100, default=50)]

    Evapotranspiration_Ground_Cover_Parameter: Annotated[float, Field(ge=0, le=1.5, default=0.4)]
    """This specifies the ground cover effects during evapotranspiration"""