from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Screen_Equivalentlayer(EpBunch):
    """Equivalent layer window screen physical properties. Can only be"""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this window screen material."""

    Screen_BeamBeam_Solar_Transmittance: Annotated[float, Field(ge=0, lt=1, default=autocalculate)]
    """The beam-beam transmittance of the screen material at normal incidence."""

    Screen_BeamDiffuse_Solar_Transmittance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The beam-diffuse solar transmittance of the screen material at normal"""

    Screen_BeamDiffuse_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The beam-diffuse solar reflectance of the screen material at normal"""

    Screen_BeamBeam_Visible_Transmittance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The beam-beam visible transmittance of the screen material at normal"""

    Screen_BeamDiffuse_Visible_Transmittance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The beam-diffuse visible transmittance of the screen material at normal"""

    Screen_BeamDiffuse_Visible_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """Beam-diffuse visible reflectance of the screen material at normal"""

    Screen_Infrared_Transmittance: Annotated[float, Field(ge=0, lt=1, default=0.02)]
    """The long-wave hemispherical transmittance of the screen material."""

    Screen_Infrared_Emissivity: Annotated[float, Field(gt=0, lt=1, default=0.93)]
    """The long-wave hemispherical emissivity of the screen material."""

    Screen_Wire_Spacing: Annotated[float, Field(gt=0, default=0.025)]
    """Spacing assumed to be the same in both directions."""

    Screen_Wire_Diameter: Annotated[float, Field(gt=0, default=0.005)]
    """Diameter assumed to be the same in both directions."""