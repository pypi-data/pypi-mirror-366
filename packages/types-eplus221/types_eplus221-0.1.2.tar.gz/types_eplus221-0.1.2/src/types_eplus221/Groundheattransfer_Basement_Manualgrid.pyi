from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Manualgrid(EpBunch):
    """Manual Grid only necessary using manual gridding (not recommended)"""

    NX_Number_of_cells_in_the_X_direction_20: Annotated[str, Field(default=...)]

    NY_Number_of_cells_in_the_Y_direction_20: Annotated[str, Field(default=...)]

    NZAG_Number_of_cells_in_the_Z_direction_above_grade_4_Always: Annotated[str, Field(default=...)]

    NZBG_Number_of_cells_in_Z_direction_below_grade_1035: Annotated[str, Field(default=...)]

    IBASE_X_direction_cell_indicator_of_slab_edge_520: Annotated[str, Field(default=...)]

    JBASE_Y_direction_cell_indicator_of_slab_edge_520: Annotated[str, Field(default=...)]

    KBASE_Z_direction_cell_indicator_of_the_top_of_the_floor_slab_520: Annotated[str, Field(default=...)]