from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Bldgdata(EpBunch):
    """Specifies the surface and gravel thicknesses used for the Basement"""

    Dwall__Wall_Thickness: Annotated[str, Field(default='0.2')]

    Dslab__Floor_Slab_Thickness: Annotated[str, Field(default='0.1')]

    Dgravxy__Width_Of_Gravel_Pit_Beside_Basement_Wall: Annotated[str, Field(default='0.3')]

    Dgravzn__Gravel_Depth_Extending_Above_The_Floor_Slab: Annotated[str, Field(default='0.2')]

    Dgravzp__Gravel_Depth_Below_The_Floor_Slab: Annotated[str, Field(default='0.1')]