from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Externalinterface_Schedule(EpBunch):
    """A ExternalInterface:Schedule contains only one value,"""

    Name: Annotated[str, Field(default=...)]

    Schedule_Type_Limits_Name: Annotated[str, Field()]

    Initial_Value: Annotated[float, Field(default=...)]
    """Used during warm-up and system sizing."""