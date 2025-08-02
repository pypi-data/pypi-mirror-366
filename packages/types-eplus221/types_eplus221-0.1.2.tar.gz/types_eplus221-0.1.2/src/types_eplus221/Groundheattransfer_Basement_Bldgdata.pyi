from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Bldgdata(EpBunch):
    """Specifies the surface and gravel thicknesses used for the Basement"""

    DWALL_Wall_thickness: Annotated[str, Field(default='0.2')]

    DSLAB_Floor_slab_thickness: Annotated[str, Field(default='0.1')]

    DGRAVXY_Width_of_gravel_pit_beside_basement_wall: Annotated[str, Field(default='0.3')]

    DGRAVZN_Gravel_depth_extending_above_the_floor_slab: Annotated[str, Field(default='0.2')]

    DGRAVZP_Gravel_depth_below_the_floor_slab: Annotated[str, Field(default='0.1')]