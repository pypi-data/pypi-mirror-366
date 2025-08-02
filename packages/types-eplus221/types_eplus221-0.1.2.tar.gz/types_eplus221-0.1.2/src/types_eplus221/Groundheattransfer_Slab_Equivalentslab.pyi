from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Equivalentslab(EpBunch):
    """Using an equivalent slab allows non-rectangular shapes to be modeled accurately."""

    APRatio_The_area_to_perimeter_ratio_for_this_slab: Annotated[str, Field(default=...)]
    """Equivalent square slab is simulated, side is 4*APRatio."""

    SLABDEPTH_Thickness_of_slab_on_grade: Annotated[str, Field(default='0.1')]
    """This field specifies the thickness of the slab. The slab top surface is level"""

    CLEARANCE_Distance_from_edge_of_slab_to_domain_edge: Annotated[str, Field(default='15.0')]
    """This field specifies the distance from the slab to the edge of"""

    ZCLEARANCE_Distance_from_bottom_of_slab_to_domain_bottom: Annotated[str, Field(default='15.0')]
    """This field specifies the vertical distance from the slab to the"""