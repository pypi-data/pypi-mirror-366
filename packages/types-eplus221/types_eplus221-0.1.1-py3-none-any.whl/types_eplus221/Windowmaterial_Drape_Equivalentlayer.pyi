from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Drape_Equivalentlayer(EpBunch):
    """Specifies the properties of equivalent layer drape fabric materials."""

    Name: Annotated[str, Field(default=...)]

    Drape_Beam_Beam_Solar_Transmittance_At_Normal_Incidence: Annotated[float, Field(ge=0.0, le=0.2, default=0.0)]
    """The beam-beam solar transmittance at normal incidence. This value is the"""

    Front_Side_Drape_Beam_Diffuse_Solar_Transmittance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The front side beam-diffuse solar transmittance at normal incidence averaged"""

    Back_Side_Drape_Beam_Diffuse_Solar_Transmittance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The back side beam-diffuse solar transmittance at normal incidence averaged"""

    Front_Side_Drape_Beam_Diffuse_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The front side beam-diffuse solar reflectance at normal incidence averaged"""

    Back_Side_Drape_Beam_Diffuse_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The back side beam-diffuse solar reflectance at normal incidence averaged"""

    Drape_Beam_Beam_Visible_Transmittance: Annotated[float, Field(ge=0, lt=1)]
    """The beam-beam visible transmittance at normal incidence averaged over the"""

    Drape_Beam_Diffuse_Visible_Transmittance: Annotated[float, Field(ge=0, lt=1)]
    """The beam-diffuse visible transmittance at normal incidence averaged over the"""

    Drape_Beam_Diffuse_Visible_Reflectance: Annotated[float, Field(ge=0, lt=1)]
    """The beam-diffuse visible reflectance at normal incidence average over the"""

    Drape_Material_Infrared_Transmittance: Annotated[float, Field(ge=0, lt=1, default=0.05)]
    """Long-wave transmittance of the drape fabric at zero openness fraction."""

    Front_Side_Drape_Material_Infrared_Emissivity: Annotated[float, Field(gt=0, lt=1, default=0.87)]
    """Front side long-wave emissivity of the drape fabric at zero shade openness."""

    Back_Side_Drape_Material_Infrared_Emissivity: Annotated[float, Field(gt=0, lt=1, default=0.87)]
    """Back side long-wave emissivity of the drape fabric at zero shade openness."""

    Width_Of_Pleated_Fabric: Annotated[float, Field(ge=0, default=0)]
    """Width of the pleated section of the draped fabric. If the drape fabric is"""

    Length_Of_Pleated_Fabric: Annotated[float, Field(ge=0, default=0)]
    """Length of the pleated section of the draped fabric. If the drape fabric is"""