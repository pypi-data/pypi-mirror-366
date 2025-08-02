from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Output_Surfaces_Drawing(EpBunch):
    """Produces reports/files that are capable of rendering graphically or"""

    Report_Type: Annotated[Literal['DXF', 'DXF:WireFrame', 'VRML'], Field(default=...)]

    Report_Specifications_1: Annotated[Literal['Triangulate3DFace', 'ThickPolyline', 'RegularPolyline'], Field(default='Triangulate3DFace')]
    """Triangulate3DFace (default), ThickPolyline, RegularPolyline apply to DXF"""

    Report_Specifications_2: Annotated[str, Field()]
    """Use ColorScheme Name for DXF reports"""