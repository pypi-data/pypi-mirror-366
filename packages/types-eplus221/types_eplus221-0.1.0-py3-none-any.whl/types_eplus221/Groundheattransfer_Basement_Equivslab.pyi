from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Equivslab(EpBunch):
    """Using an equivalent slab allows non-rectangular shapes to be"""

    Apratio__The_Area_To_Perimeter_Ratio_For_This_Slab: Annotated[str, Field(default=...)]

    Equivsizing__Flag: Annotated[Literal['TRUE', 'FALSE'], Field(default=...)]
    """Will the dimensions of an equivalent slab be calculated (TRUE)"""