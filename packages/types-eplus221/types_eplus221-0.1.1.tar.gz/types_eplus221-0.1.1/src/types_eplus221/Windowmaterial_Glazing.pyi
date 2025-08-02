from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Glazing(EpBunch):
    """Glass material properties for Windows or Glass Doors"""

    Name: Annotated[str, Field(default=...)]

    Optical_Data_Type: Annotated[Literal['SpectralAverage', 'Spectral', 'BSDF', 'SpectralAndAngle'], Field(default=...)]

    Window_Glass_Spectral_Data_Set_Name: Annotated[str, Field()]
    """Used only when Optical Data Type = Spectral"""

    Thickness: Annotated[float, Field(default=..., gt=0.0)]

    Solar_Transmittance_At_Normal_Incidence: Annotated[float, Field(ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Front_Side_Solar_Reflectance_At_Normal_Incidence: Annotated[float, Field(ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Back_Side_Solar_Reflectance_At_Normal_Incidence: Annotated[float, Field(ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Visible_Transmittance_At_Normal_Incidence: Annotated[float, Field(ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Front_Side_Visible_Reflectance_At_Normal_Incidence: Annotated[float, Field(ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Back_Side_Visible_Reflectance_At_Normal_Incidence: Annotated[float, Field(ge=0.0, le=1.0)]
    """Used only when Optical Data Type = SpectralAverage"""

    Infrared_Transmittance_At_Normal_Incidence: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Front_Side_Infrared_Hemispherical_Emissivity: Annotated[float, Field(gt=0.0, lt=1.0, default=0.84)]

    Back_Side_Infrared_Hemispherical_Emissivity: Annotated[float, Field(gt=0.0, lt=1.0, default=0.84)]

    Conductivity: Annotated[float, Field(gt=0.0, default=0.9)]

    Dirt_Correction_Factor_For_Solar_And_Visible_Transmittance: Annotated[float, Field(gt=0.0, le=1.0, default=1.0)]

    Solar_Diffusing: Annotated[Literal['No', 'Yes'], Field(default='No')]

    Young_S_Modulus: Annotated[float, Field(gt=0.0, default=7.2e10)]
    """coefficient used for deflection calculations. Used only with complex"""

    Poisson_S_Ratio: Annotated[float, Field(gt=0.0, lt=1.0, default=0.22)]
    """coefficient used for deflection calculations. Used only with complex"""

    Window_Glass_Spectral_And_Incident_Angle_Transmittance_Data_Set_Table_Name: Annotated[str, Field()]
    """Used only when Optical Data Type = SpectralAndAngle"""

    Window_Glass_Spectral_And_Incident_Angle_Front_Reflectance_Data_Set_Table_Name: Annotated[str, Field()]
    """Used only when Optical Data Type = SpectralAndAngle"""

    Window_Glass_Spectral_And_Incident_Angle_Back_Reflectance_Data_Set_Table_Name: Annotated[str, Field()]
    """Used only when Optical Data Type = SpectralAndAngle"""