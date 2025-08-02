from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Material_Infraredtransparent(EpBunch):
    """Special infrared transparent material. Similar to a Material:Nomass with low thermal resistance."""

    Name: Annotated[str, Field(default=...)]