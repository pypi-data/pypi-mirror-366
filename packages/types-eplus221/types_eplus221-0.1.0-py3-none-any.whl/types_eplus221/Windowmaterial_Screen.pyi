from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowmaterial_Screen(EpBunch):
    """Window screen physical properties. Can only be located on the exterior side of a window construction."""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this window screen material."""

    Reflected_Beam_Transmittance_Accounting_Method: Annotated[Literal['DoNotModel', 'ModelAsDirectBeam', 'ModelAsDiffuse'], Field(default='ModelAsDiffuse')]
    """Select the method used to account for the beam solar reflected off the material surface."""

    Diffuse_Solar_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """Diffuse reflectance of the screen material over the entire solar radiation spectrum."""

    Diffuse_Visible_Reflectance: Annotated[float, Field(default=..., ge=0, lt=1)]
    """Diffuse visible reflectance of the screen material averaged over the solar spectrum"""

    Thermal_Hemispherical_Emissivity: Annotated[float, Field(gt=0, lt=1, default=0.9)]
    """Long-wave emissivity of the screen material."""

    Conductivity: Annotated[float, Field(gt=0, default=221.0)]
    """Thermal conductivity of the screen material."""

    Screen_Material_Spacing: Annotated[float, Field(default=..., gt=0)]
    """Spacing assumed to be the same in both directions."""

    Screen_Material_Diameter: Annotated[float, Field(default=..., gt=0)]
    """Diameter assumed to be the same in both directions."""

    Screen_To_Glass_Distance: Annotated[float, Field(ge=0.001, le=1.0, default=0.025)]
    """Distance from the window screen to the adjacent glass surface."""

    Top_Opening_Multiplier: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Effective area for air flow at the top of the screen divided by the perpendicular"""

    Bottom_Opening_Multiplier: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Effective area for air flow at the bottom of the screen divided by the perpendicular"""

    Left_Side_Opening_Multiplier: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Effective area for air flow at the left side of the screen divided by the perpendicular"""

    Right_Side_Opening_Multiplier: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]
    """Effective area for air flow at the right side of the screen divided by the perpendicular"""

    Angle_Of_Resolution_For_Screen_Transmittance_Output_Map: Annotated[Literal['0', '1', '2', '3', '5'], Field(default='0')]
    """Select the resolution of azimuth and altitude angles for the screen transmittance map."""