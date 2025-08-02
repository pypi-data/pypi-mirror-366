from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Manualgrid(EpBunch):
    """Manual Grid only necessary when using manual gridding (not recommended)"""

    Nx__Number_Of_Cells_In_The_X_Direction: Annotated[str, Field(default=...)]

    Ny__Number_Of_Cells_In_The_Y_Direction: Annotated[str, Field(default=...)]

    Nz__Number_Of_Cells_In_The_Z_Direction: Annotated[str, Field(default=...)]

    Ibox__X_Direction_Cell_Indicator_Of_Slab_Edge: Annotated[str, Field(default=...)]
    """typical values= 1-10"""

    Jbox__Y_Direction_Cell_Indicator_Of_Slab_Edge: Annotated[str, Field(default=...)]
    """typical values= 1-10"""