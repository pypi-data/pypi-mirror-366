from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Surfacecontrol_Movableinsulation(EpBunch):
    """Exterior or Interior Insulation on opaque surfaces"""

    Insulation_Type: Annotated[Literal['Outside', 'Inside'], Field(default=...)]

    Surface_Name: Annotated[str, Field(default=...)]

    Material_Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]