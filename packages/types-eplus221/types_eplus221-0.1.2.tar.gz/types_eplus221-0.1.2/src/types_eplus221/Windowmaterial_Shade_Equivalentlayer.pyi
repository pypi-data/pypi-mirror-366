from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Shade_Equivalentlayer(EpBunch):
    """Specifies the properties of equivalent layer window shade material"""

    Name: Annotated[str, Field(default=...)]

    Shade_BeamBeam_Solar_Transmittance: Annotated[float, Field(ge=0.0, le=0.8, default=0.0)]
    """The beam-beam solar transmittance at normal incidence. This value is"""

    Front_Side_Shade_BeamDiffuse_Solar_Transmittance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The front side beam-diffuse solar transmittance at normal incidence averaged"""

    Back_Side_Shade_BeamDiffuse_Solar_Transmittance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The back side beam-diffuse solar transmittance at normal incidence averaged"""

    Front_Side_Shade_BeamDiffuse_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The front side beam-diffuse solar reflectance at normal incidence averaged"""

    Back_Side_Shade_BeamDiffuse_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The back side beam-diffuse solar reflectance at normal incidence averaged"""

    Shade_BeamBeam_Visible_Transmittance_at_Normal_Incidence: Annotated[float, Field(ge=0, lt=1)]
    """The beam-beam visible transmittance at normal incidence averaged over the"""

    Shade_BeamDiffuse_Visible_Transmittance_at_Normal_Incidence: Annotated[float, Field(ge=0, lt=1)]
    """The beam-diffuse visible transmittance at normal incidence averaged over the"""

    Shade_BeamDiffuse_Visible_Reflectance_at_Normal_Incidence: Annotated[float, Field(ge=0, lt=1)]
    """The beam-diffuse visible reflectance at normal incidence averaged over the"""

    Shade_Material_Infrared_Transmittance: Annotated[float, Field(ge=0, lt=1, default=0.05)]
    """The long-wave transmittance of the shade material at zero shade openness."""

    Front_Side_Shade_Material_Infrared_Emissivity: Annotated[float, Field(gt=0, lt=1, default=0.91)]
    """The front side long-wave emissivity of the shade material at zero shade"""

    Back_Side_Shade_Material_Infrared_Emissivity: Annotated[float, Field(gt=0, lt=1, default=0.91)]
    """The back side long-wave emissivity of the shade material at zero shade"""