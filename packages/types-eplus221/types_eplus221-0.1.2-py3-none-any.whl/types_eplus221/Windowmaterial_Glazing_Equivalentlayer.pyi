from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Glazing_Equivalentlayer(EpBunch):
    """Glass material properties for Windows or Glass Doors"""

    Name: Annotated[str, Field(default=...)]

    Optical_Data_Type: Annotated[Literal['Spectral'], Field(default='SpectralAverage')]
    """Spectral is not currently supported and SpectralAverage is the default."""

    Window_Glass_Spectral_Data_Set_Name: Annotated[str, Field()]
    """Spectral data is not currently supported."""

    Front_Side_BeamBeam_Solar_Transmittance: Annotated[float, Field(default=..., ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Back_Side_BeamBeam_Solar_Transmittance: Annotated[float, Field(default=..., ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Front_Side_BeamBeam_Solar_Reflectance: Annotated[float, Field(default=..., ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Back_Side_BeamBeam_Solar_Reflectance: Annotated[float, Field(default=..., ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Front_Side_BeamBeam_Visible_Solar_Transmittance: Annotated[float, Field(ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Back_Side_BeamBeam_Visible_Solar_Transmittance: Annotated[float, Field(ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Front_Side_BeamBeam_Visible_Solar_Reflectance: Annotated[float, Field(ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Back_Side_BeamBeam_Visible_Solar_Reflectance: Annotated[float, Field(ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Front_Side_BeamDiffuse_Solar_Transmittance: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Back_Side_BeamDiffuse_Solar_Transmittance: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Front_Side_BeamDiffuse_Solar_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Back_Side_BeamDiffuse_Solar_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Front_Side_BeamDiffuse_Visible_Solar_Transmittance: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Back_Side_BeamDiffuse_Visible_Solar_Transmittance: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Front_Side_BeamDiffuse_Visible_Solar_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Back_Side_BeamDiffuse_Visible_Solar_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    DiffuseDiffuse_Solar_Transmittance: Annotated[float, Field(ge=0.0, le=1.0, default=autocalculate)]
    """Used only when Optical Data Type = SpectralAverage"""

    Front_Side_DiffuseDiffuse_Solar_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=autocalculate)]
    """Used only when Optical Data Type = SpectralAverage"""

    Back_Side_DiffuseDiffuse_Solar_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=autocalculate)]
    """Used only when Optical Data Type = SpectralAverage"""

    DiffuseDiffuse_Visible_Solar_Transmittance: Annotated[float, Field(ge=0.0, le=1.0, default=autocalculate)]
    """Used only when Optical Data Type = SpectralAverage"""

    Front_Side_DiffuseDiffuse_Visible_Solar_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=autocalculate)]
    """Used only when Optical Data Type = SpectralAverage"""

    Back_Side_DiffuseDiffuse_Visible_Solar_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=autocalculate)]
    """Used only when Optical Data Type = SpectralAverage"""

    Infrared_Transmittance_applies_to_front_and_back: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """The long-wave hemispherical transmittance of the glazing."""

    Front_Side_Infrared_Emissivity: Annotated[float, Field(gt=0.0, lt=1.0, default=0.84)]
    """The front side long-wave hemispherical emissivity of the glazing."""

    Back_Side_Infrared_Emissivity: Annotated[float, Field(gt=0.0, lt=1.0, default=0.84)]
    """The back side long-wave hemispherical emissivity of the glazing."""

    Thermal_Resistance: Annotated[float, Field(gt=0.0, default=0.158)]
    """This is the R-Value in SI for the glass. The default value is an"""