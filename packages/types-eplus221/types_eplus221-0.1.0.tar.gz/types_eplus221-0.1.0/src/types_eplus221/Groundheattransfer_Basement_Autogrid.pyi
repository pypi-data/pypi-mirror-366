from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Autogrid(EpBunch):
    """AutoGrid only necessary when EquivSizing is false"""

    Clearance__Distance_From_Outside_Of_Wall_To_Edge_: Annotated[str, Field(default='15')]

    Slabx__X_Dimension_Of_The_Building_Slab: Annotated[str, Field(default=...)]

    Slaby__Y_Dimension_Of_The_Building_Slab: Annotated[str, Field(default=...)]

    Concagheight__Height_Of_The_Foundation_Wall_Above_Grade: Annotated[str, Field(default='0')]

    Slabdepth__Thickness_Of_The_Floor_Slab: Annotated[str, Field(default='0.1')]

    Basedepth__Depth_Of_The_Basement_Wall_Below_Grade: Annotated[str, Field(default='2')]