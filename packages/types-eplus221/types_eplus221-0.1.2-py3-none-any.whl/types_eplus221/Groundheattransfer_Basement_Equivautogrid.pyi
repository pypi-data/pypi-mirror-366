from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Equivautogrid(EpBunch):
    """EquivAutoGrid necessary when EquivSizing=TRUE, TRUE is is the normal case."""

    CLEARANCE_Distance_from_outside_of_wall_to_edge_of_3D_ground_domain: Annotated[str, Field(default='15')]

    SlabDepth_Thickness_of_the_floor_slab: Annotated[str, Field(default='0.1')]

    BaseDepth_Depth_of_the_basement_wall_below_grade: Annotated[str, Field(default='2')]