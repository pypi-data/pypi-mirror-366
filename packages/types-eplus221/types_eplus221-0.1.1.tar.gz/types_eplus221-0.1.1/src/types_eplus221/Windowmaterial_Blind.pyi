from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Blind(EpBunch):
    """Window blind thermal properties"""

    Name: Annotated[str, Field(default=...)]

    Slat_Orientation: Annotated[Literal['Horizontal', 'Vertical'], Field(default='Horizontal')]

    Slat_Width: Annotated[float, Field(default=..., gt=0, le=1)]

    Slat_Separation: Annotated[float, Field(default=..., gt=0, le=1)]
    """Distance between adjacent slat faces"""

    Slat_Thickness: Annotated[float, Field(gt=0, le=0.1, default=0.00025)]
    """Distance between top and bottom surfaces of slat"""

    Slat_Angle: Annotated[float, Field(ge=0, le=180, default=45)]
    """If WindowShadingControl referencing the window that incorporates this blind"""

    Slat_Conductivity: Annotated[float, Field(gt=0, default=221.0)]
    """default is for aluminum"""

    Slat_Beam_Solar_Transmittance: Annotated[float, Field(ge=0, lt=1, default=0)]

    Front_Side_Slat_Beam_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]

    Back_Side_Slat_Beam_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]

    Slat_Diffuse_Solar_Transmittance: Annotated[float, Field(ge=0, lt=1, default=0)]
    """Must equal "Slat beam solar transmittance""""

    Front_Side_Slat_Diffuse_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """Must equal "Front Side Slat Beam Solar Reflectance""""

    Back_Side_Slat_Diffuse_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """Must equal "Back Side Slat Beam Solar Reflectance""""

    Slat_Beam_Visible_Transmittance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """Required for detailed daylighting calculation"""

    Front_Side_Slat_Beam_Visible_Reflectance: Annotated[float, Field(ge=0, lt=1)]
    """Required for detailed daylighting calculation"""

    Back_Side_Slat_Beam_Visible_Reflectance: Annotated[float, Field(ge=0, lt=1)]
    """Required for detailed daylighting calculation"""

    Slat_Diffuse_Visible_Transmittance: Annotated[float, Field(ge=0, lt=1, default=0)]
    """Used only for detailed daylighting calculation"""

    Front_Side_Slat_Diffuse_Visible_Reflectance: Annotated[float, Field(ge=0, lt=1)]
    """Required for detailed daylighting calculation"""

    Back_Side_Slat_Diffuse_Visible_Reflectance: Annotated[float, Field(ge=0, lt=1)]
    """Required for detailed daylighting calculation"""

    Slat_Infrared_Hemispherical_Transmittance: Annotated[float, Field(ge=0, lt=1, default=0)]

    Front_Side_Slat_Infrared_Hemispherical_Emissivity: Annotated[float, Field(ge=0, lt=1, default=0.9)]

    Back_Side_Slat_Infrared_Hemispherical_Emissivity: Annotated[float, Field(ge=0, lt=1, default=0.9)]

    Blind_To_Glass_Distance: Annotated[float, Field(ge=0.01, le=1.0, default=0.050)]

    Blind_Top_Opening_Multiplier: Annotated[float, Field(ge=0.0, le=1.0, default=0.5)]

    Blind_Bottom_Opening_Multiplier: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Blind_Left_Side_Opening_Multiplier: Annotated[float, Field(ge=0.0, le=1.0, default=0.5)]

    Blind_Right_Side_Opening_Multiplier: Annotated[float, Field(ge=0.0, le=1.0, default=0.5)]

    Minimum_Slat_Angle: Annotated[float, Field(ge=0, le=180, default=0)]
    """Used only if WindowShadingControl referencing the window that incorporates"""

    Maximum_Slat_Angle: Annotated[float, Field(ge=0, le=180, default=180)]
    """Used only if WindowShadingControl referencing the window that incorporates"""