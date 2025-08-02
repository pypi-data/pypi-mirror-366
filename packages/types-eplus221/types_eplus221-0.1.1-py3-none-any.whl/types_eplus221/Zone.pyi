from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zone(EpBunch):
    """Defines a thermal zone of the building."""

    Name: Annotated[str, Field(default=...)]

    Direction_Of_Relative_North: Annotated[float, Field(default=0)]

    X_Origin: Annotated[float, Field(default=0)]

    Y_Origin: Annotated[float, Field(default=0)]

    Z_Origin: Annotated[float, Field(default=0)]

    Type: Annotated[int, Field(ge=1, le=1, default=1)]

    Multiplier: Annotated[int, Field(ge=1, default=1)]

    Ceiling_Height: Annotated[float, Field(default=autocalculate)]
    """If this field is 0.0, negative or autocalculate, then the average height"""

    Volume: Annotated[float, Field(default=autocalculate)]
    """If this field is 0.0, negative or autocalculate, then the volume of the zone"""

    Floor_Area: Annotated[float, Field(default=autocalculate)]
    """If this field is 0.0, negative or autocalculate, then the floor area of the zone"""

    Zone_Inside_Convection_Algorithm: Annotated[Literal['Simple', 'TARP', 'CeilingDiffuser', 'AdaptiveConvectionAlgorithm', 'TrombeWall'], Field()]
    """Will default to same value as SurfaceConvectionAlgorithm:Inside object"""

    Zone_Outside_Convection_Algorithm: Annotated[Literal['SimpleCombined', 'TARP', 'DOE-2', 'MoWiTT', 'AdaptiveConvectionAlgorithm'], Field()]
    """Will default to same value as SurfaceConvectionAlgorithm:Outside object"""

    Part_Of_Total_Floor_Area: Annotated[Literal['Yes', 'No'], Field(default='Yes')]