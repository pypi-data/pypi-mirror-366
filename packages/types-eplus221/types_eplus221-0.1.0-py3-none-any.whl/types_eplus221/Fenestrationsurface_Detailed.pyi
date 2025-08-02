from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Fenestrationsurface_Detailed(EpBunch):
    """Allows for detailed entry of subsurfaces"""

    Name: Annotated[str, Field(default=...)]

    Surface_Type: Annotated[Literal['Window', 'Door', 'GlassDoor', 'TubularDaylightDome', 'TubularDaylightDiffuser'], Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]
    """To be matched with a construction in this input file"""

    Building_Surface_Name: Annotated[str, Field(default=...)]

    Outside_Boundary_Condition_Object: Annotated[str, Field()]
    """Non-blank only if base surface field Outside Boundary Condition is"""

    View_Factor_To_Ground: Annotated[float, Field(ge=0.0, le=1.0, default=autocalculate)]
    """From the exterior of the surface"""

    Frame_And_Divider_Name: Annotated[str, Field()]
    """Enter the name of a WindowProperty:FrameAndDivider object"""

    Multiplier: Annotated[str, Field(default='1.0')]
    """Used only for Surface Type = WINDOW, GLASSDOOR or DOOR"""

    Number_Of_Vertices: Annotated[str, Field(default='autocalculate')]
    """vertices are given in GlobalGeometryRules coordinates -- if relative, all surface coordinates"""

    Vertex_1_X_Coordinate: Annotated[float, Field(default=...)]

    Vertex_1_Y_Coordinate: Annotated[float, Field(default=...)]

    Vertex_1_Z_Coordinate: Annotated[float, Field(default=...)]

    Vertex_2_X_Coordinate: Annotated[float, Field(default=...)]

    Vertex_2_Y_Coordinate: Annotated[float, Field(default=...)]

    Vertex_2_Z_Coordinate: Annotated[float, Field(default=...)]

    Vertex_3_X_Coordinate: Annotated[float, Field(default=...)]

    Vertex_3_Y_Coordinate: Annotated[float, Field(default=...)]

    Vertex_3_Z_Coordinate: Annotated[float, Field(default=...)]

    Vertex_4_X_Coordinate: Annotated[float, Field()]
    """Not used for triangles"""

    Vertex_4_Y_Coordinate: Annotated[float, Field()]
    """Not used for triangles"""

    Vertex_4_Z_Coordinate: Annotated[float, Field()]
    """Not used for triangles"""