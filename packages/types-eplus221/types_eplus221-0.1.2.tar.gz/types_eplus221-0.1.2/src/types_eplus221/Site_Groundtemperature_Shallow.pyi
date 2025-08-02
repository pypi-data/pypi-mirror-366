from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Groundtemperature_Shallow(EpBunch):
    """These temperatures are specifically for the Surface Ground Heat Exchanger and"""

    January_Surface_Ground_Temperature: Annotated[float, Field(default=13)]

    February_Surface_Ground_Temperature: Annotated[float, Field(default=13)]

    March_Surface_Ground_Temperature: Annotated[float, Field(default=13)]

    April_Surface_Ground_Temperature: Annotated[float, Field(default=13)]

    May_Surface_Ground_Temperature: Annotated[float, Field(default=13)]

    June_Surface_Ground_Temperature: Annotated[float, Field(default=13)]

    July_Surface_Ground_Temperature: Annotated[float, Field(default=13)]

    August_Surface_Ground_Temperature: Annotated[float, Field(default=13)]

    September_Surface_Ground_Temperature: Annotated[float, Field(default=13)]

    October_Surface_Ground_Temperature: Annotated[float, Field(default=13)]

    November_Surface_Ground_Temperature: Annotated[float, Field(default=13)]

    December_Surface_Ground_Temperature: Annotated[float, Field(default=13)]