from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Duct(EpBunch):
    """Passes inlet node state variables to outlet node state variables"""

    Name: Annotated[str, Field(default=...)]

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]