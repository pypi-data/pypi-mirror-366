from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Construction_Ffactorgroundfloor(EpBunch):
    """Alternate method of describing slab-on-grade or underground floor constructions"""

    Name: Annotated[str, Field(default=...)]

    F_Factor: Annotated[float, Field(default=..., gt=0.0)]

    Area: Annotated[float, Field(default=..., gt=0.0)]
    """Enter area of the floor"""

    Perimeterexposed: Annotated[float, Field(default=..., ge=0.0)]
    """Enter exposed perimeter of the floor"""