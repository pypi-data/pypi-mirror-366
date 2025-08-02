from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Autogrid(EpBunch):
    """AutoGrid only necessary when EquivSizing is false"""

    CLEARANCE_Distance_from_outside_of_wall_to_edge: Annotated[str, Field(default='15')]

    SLABX_X_dimension_of_the_building_slab: Annotated[str, Field(default=...)]

    SLABY_Y_dimension_of_the_building_slab: Annotated[str, Field(default=...)]

    ConcAGHeight_Height_of_the_foundation_wall_above_grade: Annotated[str, Field(default='0')]

    SlabDepth_Thickness_of_the_floor_slab: Annotated[str, Field(default='0.1')]

    BaseDepth_Depth_of_the_basement_wall_below_grade: Annotated[str, Field(default='2')]