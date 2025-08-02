from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Thermalstorage_Ice_Simple(EpBunch):
    """This ice storage model is a simplified model"""

    Name: Annotated[str, Field(default=...)]

    Ice_Storage_Type: Annotated[Literal['IceOnCoilInternal', 'IceOnCoilExternal'], Field(default=...)]
    """IceOnCoilInternal = Ice-on-Coil, internal melt"""

    Capacity: Annotated[float, Field(default=...)]

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]