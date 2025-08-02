from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Autogrid(EpBunch):
    """AutoGrid only necessary when EquivalentSlab option not chosen."""

    Slabx__X_Dimension_Of_The_Building_Slab: Annotated[str, Field(default=...)]
    """typical values= 6 to 60.0"""

    Slaby__Y_Dimension_Of_The_Building_Slab: Annotated[str, Field(default=...)]
    """typical values= 6 to 60.0"""

    Slabdepth__Thickness_Of_Slab_On_Grade: Annotated[str, Field(default='0.1')]

    Clearance__Distance_From_Edge_Of_Slab_To_Domain_Edge: Annotated[str, Field(default='15.0')]

    Zclearance__Distance_From_Bottom_Of_Slab_To_Domain_Bottom: Annotated[str, Field(default='15.0')]