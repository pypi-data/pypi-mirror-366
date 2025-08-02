from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Loadprofile_Plant(EpBunch):
    """Used to simulate a scheduled plant loop demand profile. Load and flow rate are"""

    Name: Annotated[str, Field(default=...)]

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]

    Load_Schedule_Name: Annotated[str, Field(default=...)]
    """Schedule values are load in [W]"""

    Peak_Flow_Rate: Annotated[float, Field(default=...)]

    Flow_Rate_Fraction_Schedule_Name: Annotated[str, Field(default=...)]