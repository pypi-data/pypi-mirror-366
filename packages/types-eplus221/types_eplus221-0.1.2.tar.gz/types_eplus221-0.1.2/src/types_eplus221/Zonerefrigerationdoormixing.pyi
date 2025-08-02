from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonerefrigerationdoormixing(EpBunch):
    """Refrigeration Door Mixing is used for an opening between two zones that are at the"""

    Name: Annotated[str, Field(default=...)]

    Zone_1_Name: Annotated[str, Field(default=...)]

    Zone_2_Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]
    """This schedule defines the fraction of the time the refrigeration door is open"""

    Door_Height: Annotated[float, Field(ge=0, le=50., default=3.0)]

    Door_Area: Annotated[float, Field(ge=0, le=400., default=9.)]

    Door_Protection_Type: Annotated[Literal['None', 'AirCurtain', 'StripCurtain'], Field()]
    """Door protection can reduce the air flow through a refrigeration door"""