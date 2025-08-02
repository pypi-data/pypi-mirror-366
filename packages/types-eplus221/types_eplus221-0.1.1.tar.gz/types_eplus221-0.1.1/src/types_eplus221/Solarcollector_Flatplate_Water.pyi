from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Solarcollector_Flatplate_Water(EpBunch):
    """Flat plate water solar collector (single glazed, unglazed, or evacuated tube)."""

    Name: Annotated[str, Field(default=...)]

    Solarcollectorperformance_Name: Annotated[str, Field(default=...)]

    Surface_Name: Annotated[str, Field(default=...)]

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]

    Maximum_Flow_Rate: Annotated[float, Field(gt=0)]