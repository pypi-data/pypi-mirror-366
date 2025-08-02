from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowproperty_Frameanddivider(EpBunch):
    """Specifies the dimensions of a window frame, dividers, and inside reveal surfaces."""

    Name: Annotated[str, Field(default=...)]
    """Referenced by surfaces that are exterior windows"""

    Frame_Width: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Width of frame in plane of window"""

    Frame_Outside_Projection: Annotated[float, Field(ge=0.0, le=0.5, default=0.0)]
    """Amount that frame projects outward from the outside face of the glazing"""

    Frame_Inside_Projection: Annotated[float, Field(ge=0.0, le=0.5, default=0.0)]
    """Amount that frame projects inward from the inside face of the glazing"""

    Frame_Conductance: Annotated[float, Field(ge=0.0)]
    """Effective conductance of frame"""

    Ratio_Of_Frame_Edge_Glass_Conductance_To_Center_Of_Glass_Conductance: Annotated[float, Field(gt=0.0, le=4.0, default=1.0)]
    """Excludes air films; applies only to multipane windows"""

    Frame_Solar_Absorptance: Annotated[float, Field(ge=0.0, le=1.0, default=0.7)]
    """Assumed same on outside and inside of frame"""

    Frame_Visible_Absorptance: Annotated[float, Field(ge=0.0, le=1.0, default=0.7)]
    """Assumed same on outside and inside of frame"""

    Frame_Thermal_Hemispherical_Emissivity: Annotated[float, Field(gt=0.0, default=0.9)]
    """Assumed same on outside and inside of frame"""

    Divider_Type: Annotated[Literal['DividedLite', 'Suspended'], Field(default='DividedLite')]

    Divider_Width: Annotated[float, Field(ge=0.0, le=0.5, default=0.0)]
    """Width of dividers in plane of window"""

    Number_Of_Horizontal_Dividers: Annotated[float, Field(ge=0, default=0)]
    """"Horizontal" means parallel to local window X-axis"""

    Number_Of_Vertical_Dividers: Annotated[float, Field(ge=0, default=0)]
    """"Vertical" means parallel to local window Y-axis"""

    Divider_Outside_Projection: Annotated[float, Field(ge=0.0, le=0.5, default=0.0)]
    """Amount that divider projects outward from the outside face of the glazing"""

    Divider_Inside_Projection: Annotated[float, Field(ge=0.0, le=0.5, default=0.0)]
    """Amount that divider projects inward from the inside face of the glazing"""

    Divider_Conductance: Annotated[float, Field(ge=0.0, default=0.0)]
    """Effective conductance of divider"""

    Ratio_Of_Divider_Edge_Glass_Conductance_To_Center_Of_Glass_Conductance: Annotated[float, Field(gt=0.0, le=4.0, default=1.0)]
    """Excludes air films"""

    Divider_Solar_Absorptance: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Assumed same on outside and inside of divider"""

    Divider_Visible_Absorptance: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Assumed same on outside and inside of divider"""

    Divider_Thermal_Hemispherical_Emissivity: Annotated[float, Field(gt=0.0, lt=1.0, default=0.9)]
    """Assumed same on outside and inside of divider"""

    Outside_Reveal_Solar_Absorptance: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Inside_Sill_Depth: Annotated[float, Field(ge=0.0, le=2.0, default=0.0)]

    Inside_Sill_Solar_Absorptance: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Inside_Reveal_Depth: Annotated[str, Field(default='0.0')]
    """Distance from plane of inside surface of glazing"""

    Inside_Reveal_Solar_Absorptance: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]