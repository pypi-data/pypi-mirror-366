from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Complexshade(EpBunch):
    """Complex window shading layer thermal properties"""

    Name: Annotated[str, Field(default=...)]

    Layer_Type: Annotated[Literal['VenetianHorizontal', 'VenetianVertical', 'Woven', 'Perforated', 'BSDF', 'OtherShadingType'], Field(default='OtherShadingType')]

    Thickness: Annotated[float, Field(gt=0, default=0.002)]

    Conductivity: Annotated[float, Field(gt=0, default=1)]

    Ir_Transmittance: Annotated[float, Field(ge=0, le=1, default=0)]

    Front_Emissivity: Annotated[float, Field(ge=0, le=1, default=0.84)]

    Back_Emissivity: Annotated[float, Field(ge=0, le=1, default=0.84)]

    Top_Opening_Multiplier: Annotated[float, Field(ge=0, le=1, default=0)]

    Bottom_Opening_Multiplier: Annotated[float, Field(ge=0, le=1, default=0)]

    Left_Side_Opening_Multiplier: Annotated[float, Field(ge=0, le=1, default=0)]

    Right_Side_Opening_Multiplier: Annotated[float, Field(ge=0, le=1, default=0)]

    Front_Opening_Multiplier: Annotated[float, Field(ge=0, le=1, default=0.05)]

    Slat_Width: Annotated[float, Field(gt=0, default=0.016)]

    Slat_Spacing: Annotated[float, Field(gt=0, default=0.012)]
    """Distance between adjacent slat faces"""

    Slat_Thickness: Annotated[float, Field(gt=0, default=0.0006)]
    """Distance between top and bottom surfaces of slat"""

    Slat_Angle: Annotated[float, Field(ge=-90, le=90, default=90)]

    Slat_Conductivity: Annotated[float, Field(gt=0, default=160.0)]

    Slat_Curve: Annotated[float, Field(ge=0.0, default=0)]
    """this value represents curvature radius of the slat."""