from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonegroup(EpBunch):
    """Adds a multiplier to a ZoneList. This can be used to reduce the amount of input"""

    Name: Annotated[str, Field(default=...)]
    """Name of the Zone Group"""

    Zone_List_Name: Annotated[str, Field(default=...)]

    Zone_List_Multiplier: Annotated[int, Field(ge=1, default=1)]