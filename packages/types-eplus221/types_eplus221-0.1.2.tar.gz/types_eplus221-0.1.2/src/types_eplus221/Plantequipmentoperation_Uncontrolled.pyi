from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Plantequipmentoperation_Uncontrolled(EpBunch):
    """Plant equipment operation scheme for uncontrolled operation. Specifies a group of"""

    Name: Annotated[str, Field(default=...)]

    Equipment_List_Name: Annotated[str, Field(default=...)]