from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Manualgrid(EpBunch):
    """Manual Grid only necessary using manual gridding (not recommended)"""

    Nx__Number_Of_Cells_In_The_X_Direction__20_: Annotated[str, Field(default=...)]

    Ny__Number_Of_Cells_In_The_Y_Direction__20_: Annotated[str, Field(default=...)]

    Nzag__Number_Of_Cells_In_The_Z_Direction__Above_Grade__4_Always_: Annotated[str, Field(default=...)]

    Nzbg__Number_Of_Cells_In_Z_Direction__Below_Grade__10_35_: Annotated[str, Field(default=...)]

    Ibase__X_Direction_Cell_Indicator_Of_Slab_Edge__5_20_: Annotated[str, Field(default=...)]

    Jbase__Y_Direction_Cell_Indicator_Of_Slab_Edge__5_20_: Annotated[str, Field(default=...)]

    Kbase__Z_Direction_Cell_Indicator_Of_The_Top_Of_The_Floor_Slab__5_20_: Annotated[str, Field(default=...)]