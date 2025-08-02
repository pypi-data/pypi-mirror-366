from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Groundtemperature_Fcfactormethod(EpBunch):
    """These temperatures are specifically for underground walls and ground floors"""

    January_Ground_Temperature: Annotated[float, Field(default=13)]

    February_Ground_Temperature: Annotated[float, Field(default=13)]

    March_Ground_Temperature: Annotated[float, Field(default=13)]

    April_Ground_Temperature: Annotated[float, Field(default=13)]

    May_Ground_Temperature: Annotated[float, Field(default=13)]

    June_Ground_Temperature: Annotated[float, Field(default=13)]

    July_Ground_Temperature: Annotated[float, Field(default=13)]

    August_Ground_Temperature: Annotated[float, Field(default=13)]

    September_Ground_Temperature: Annotated[float, Field(default=13)]

    October_Ground_Temperature: Annotated[float, Field(default=13)]

    November_Ground_Temperature: Annotated[float, Field(default=13)]

    December_Ground_Temperature: Annotated[float, Field(default=13)]