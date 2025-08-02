from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Equivalentslab(EpBunch):
    """Using an equivalent slab allows non-rectangular shapes to be modeled accurately."""

    Apratio__The_Area_To_Perimeter_Ratio_For_This_Slab: Annotated[str, Field(default=...)]
    """Equivalent square slab is simulated, side is 4*APRatio."""

    Slabdepth__Thickness_Of_Slab_On_Grade: Annotated[str, Field(default='0.1')]
    """This field specifies the thickness of the slab. The slab top surface is level"""

    Clearance__Distance_From_Edge_Of_Slab_To_Domain_Edge: Annotated[str, Field(default='15.0')]
    """This field specifies the distance from the slab to the edge of"""

    Zclearance__Distance_From_Bottom_Of_Slab_To_Domain_Bottom: Annotated[str, Field(default='15.0')]
    """This field specifies the vertical distance from the slab to the"""