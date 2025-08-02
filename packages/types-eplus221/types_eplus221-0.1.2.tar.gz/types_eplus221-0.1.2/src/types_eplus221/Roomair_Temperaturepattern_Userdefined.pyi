from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomair_Temperaturepattern_Userdefined(EpBunch):
    """Used to explicitly define temperature patterns that are to be applied to the mean air"""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this model. Schedule value > 0 means the model is"""

    Pattern_Control_Schedule_Name: Annotated[str, Field(default=...)]
    """The schedule should contain integer values that"""