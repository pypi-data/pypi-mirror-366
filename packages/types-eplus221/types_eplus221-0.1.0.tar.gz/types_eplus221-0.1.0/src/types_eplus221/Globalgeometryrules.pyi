from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Globalgeometryrules(EpBunch):
    """Specifies the geometric rules used to describe the input of surface vertices and"""

    Starting_Vertex_Position: Annotated[Literal['UpperLeftCorner', 'LowerLeftCorner', 'UpperRightCorner', 'LowerRightCorner'], Field(default=...)]
    """Specified as entry for a 4 sided surface/rectangle"""

    Vertex_Entry_Direction: Annotated[Literal['Counterclockwise', 'Clockwise'], Field(default=...)]

    Coordinate_System: Annotated[Literal['Relative', 'World', 'Absolute'], Field(default=...)]
    """relative -- coordinates are entered relative to zone origin"""

    Daylighting_Reference_Point_Coordinate_System: Annotated[Literal['Relative', 'World', 'Absolute'], Field(default='Relative')]
    """Relative -- coordinates are entered relative to zone origin"""

    Rectangular_Surface_Coordinate_System: Annotated[Literal['Relative', 'World', 'Absolute'], Field(default='Relative')]
    """Relative -- Starting corner is entered relative to zone origin"""