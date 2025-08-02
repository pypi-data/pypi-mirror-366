from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Equivslab(EpBunch):
    """Using an equivalent slab allows non-rectangular shapes to be"""

    APRatio_The_area_to_perimeter_ratio_for_this_slab: Annotated[str, Field(default=...)]

    EquivSizing_Flag: Annotated[Literal['TRUE', 'FALSE'], Field(default=...)]
    """Will the dimensions of an equivalent slab be calculated (TRUE)"""