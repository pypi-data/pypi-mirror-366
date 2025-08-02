from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Blind_Equivalentlayer(EpBunch):
    """Window equivalent layer blind slat optical and thermal properties."""

    Name: Annotated[str, Field(default=...)]

    Slat_Orientation: Annotated[Literal['Horizontal', 'Vertical'], Field(default='Horizontal')]

    Slat_Width: Annotated[float, Field(default=..., gt=0, le=0.025)]

    Slat_Separation: Annotated[float, Field(default=..., gt=0, le=0.025)]
    """Distance between adjacent slat faces"""

    Slat_Crown: Annotated[float, Field(ge=0, le=0.00156, default=0.0015)]
    """Perpendicular length between the cord and the curve."""

    Slat_Angle: Annotated[float, Field(ge=-90, le=90, default=45)]
    """Slat angle is +ve if the tip of the slat front face is tilted upward, else"""

    Front_Side_Slat_BeamDiffuse_Solar_Transmittance: Annotated[float, Field(ge=0, lt=1, default=0)]
    """The front side beam-diffuse solar transmittance of the slat at normal"""

    Back_Side_Slat_BeamDiffuse_Solar_Transmittance: Annotated[float, Field(ge=0, lt=1, default=0)]
    """The back side beam-diffuse solar transmittance of the slat at normal"""

    Front_Side_Slat_BeamDiffuse_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The front side beam-diffuse solar reflectance of the slat at normal"""

    Back_Side_Slat_BeamDiffuse_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The back side beam-diffuse solar reflectance of the slat at normal"""

    Front_Side_Slat_BeamDiffuse_Visible_Transmittance: Annotated[float, Field(ge=0, lt=1, default=0)]
    """The front side beam-diffuse visible transmittance of the slat"""

    Back_Side_Slat_BeamDiffuse_Visible_Transmittance: Annotated[float, Field(ge=0, lt=1, default=0)]
    """The back side beam-diffuse visible transmittance of the slat"""

    Front_Side_Slat_BeamDiffuse_Visible_Reflectance: Annotated[float, Field(ge=0, lt=1)]
    """The front side beam-diffuse visible reflectance of the slat"""

    Back_Side_Slat_BeamDiffuse_Visible_Reflectance: Annotated[float, Field(ge=0, lt=1)]
    """The back side beam-diffuse visible reflectance of the slat"""

    Slat_DiffuseDiffuse_Solar_Transmittance: Annotated[float, Field(ge=0, lt=1, default=0)]
    """The beam-diffuse solar transmittance of the slat averaged"""

    Front_Side_Slat_DiffuseDiffuse_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The front side beam-diffuse solar reflectance of the slat"""

    Back_Side_Slat_DiffuseDiffuse_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """The back side beam-diffuse solar reflectance of the slat"""

    Slat_DiffuseDiffuse_Visible_Transmittance: Annotated[float, Field(ge=0, lt=1)]
    """The beam-diffuse visible transmittance of the slat averaged"""

    Front_Side_Slat_DiffuseDiffuse_Visible_Reflectance: Annotated[float, Field(ge=0, lt=1)]
    """The front side beam-diffuse visible reflectance of the slat"""

    Back_Side_Slat_DiffuseDiffuse_Visible_Reflectance: Annotated[float, Field(ge=0, lt=1)]
    """The back side beam-diffuse visible reflectance of the slat"""

    Slat_Infrared_Transmittance: Annotated[float, Field(ge=0, lt=1, default=0)]
    """Long-wave hemispherical transmittance of the slat material."""

    Front_Side_Slat_Infrared_Emissivity: Annotated[float, Field(ge=0, lt=1, default=0.9)]
    """Front side long-wave hemispherical emissivity of the slat material."""

    Back_Side_Slat_Infrared_Emissivity: Annotated[float, Field(ge=0, lt=1, default=0.9)]
    """Back side long-wave hemispherical emissivity of the slat material."""

    Slat_Angle_Control: Annotated[Literal['FixedSlatAngle', 'MaximizeSolar', 'BlockBeamSolar'], Field(default='FixedSlatAngle')]
    """Used only if slat angle control is desired to either maximize solar"""