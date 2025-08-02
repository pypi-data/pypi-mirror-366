from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Groundtemperature_Deep(EpBunch):
    """These temperatures are specifically for the ground heat exchangers that would use"""

    January_Deep_Ground_Temperature: Annotated[float, Field(default=16)]

    February_Deep_Ground_Temperature: Annotated[float, Field(default=16)]

    March_Deep_Ground_Temperature: Annotated[float, Field(default=16)]

    April_Deep_Ground_Temperature: Annotated[float, Field(default=16)]

    May_Deep_Ground_Temperature: Annotated[float, Field(default=16)]

    June_Deep_Ground_Temperature: Annotated[float, Field(default=16)]

    July_Deep_Ground_Temperature: Annotated[float, Field(default=16)]

    August_Deep_Ground_Temperature: Annotated[float, Field(default=16)]

    September_Deep_Ground_Temperature: Annotated[float, Field(default=16)]

    October_Deep_Ground_Temperature: Annotated[float, Field(default=16)]

    November_Deep_Ground_Temperature: Annotated[float, Field(default=16)]

    December_Deep_Ground_Temperature: Annotated[float, Field(default=16)]