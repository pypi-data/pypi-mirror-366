from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Slab_Manualgrid(EpBunch):
    """Manual Grid only necessary when using manual gridding (not recommended)"""

    NX_Number_of_cells_in_the_X_direction: Annotated[str, Field(default=...)]

    NY_Number_of_cells_in_the_Y_direction: Annotated[str, Field(default=...)]

    NZ_Number_of_cells_in_the_Z_direction: Annotated[str, Field(default=...)]

    IBOX_X_direction_cell_indicator_of_slab_edge: Annotated[str, Field(default=...)]
    """typical values= 1-10"""

    JBOX_Y_direction_cell_indicator_of_slab_edge: Annotated[str, Field(default=...)]
    """typical values= 1-10"""