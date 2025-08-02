from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Internalmass(EpBunch):
    """Used to describe internal zone surface area that does not need to be part of geometric"""

    Name: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]
    """To be matched with a construction in this input file"""

    Zone_or_ZoneList_Name: Annotated[str, Field(default=...)]
    """Zone the surface is a part of"""

    Surface_Area: Annotated[str, Field(default=...)]