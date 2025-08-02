from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Exterior_Waterequipment(EpBunch):
    """only used for Meter type reporting, does not affect building loads"""

    Name: Annotated[str, Field(default=...)]

    Fuel_Use_Type: Annotated[Literal['Water'], Field(default='Water')]

    Schedule_Name: Annotated[str, Field(default=...)]
    """units in Schedule should be fraction applied to capacity of the exterior water equipment, generally (0.0 - 1.0)"""

    Design_Level: Annotated[float, Field(default=..., ge=0)]

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""