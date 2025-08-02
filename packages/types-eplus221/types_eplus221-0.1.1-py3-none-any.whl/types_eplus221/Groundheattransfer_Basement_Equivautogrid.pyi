from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Equivautogrid(EpBunch):
    """EquivAutoGrid necessary when EquivSizing=TRUE, TRUE is is the normal case."""

    Clearance__Distance_From_Outside_Of_Wall_To_Edge_Of_3_D_Ground_Domain: Annotated[str, Field(default='15')]

    Slabdepth__Thickness_Of_The_Floor_Slab: Annotated[str, Field(default='0.1')]

    Basedepth__Depth_Of_The_Basement_Wall_Below_Grade: Annotated[str, Field(default='2')]