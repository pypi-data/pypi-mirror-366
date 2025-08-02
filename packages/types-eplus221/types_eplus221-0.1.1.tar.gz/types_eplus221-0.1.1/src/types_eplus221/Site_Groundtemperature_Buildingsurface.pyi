from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Groundtemperature_Buildingsurface(EpBunch):
    """These temperatures are specifically for those surfaces that have the outside environment"""

    January_Ground_Temperature: Annotated[float, Field(default=18)]

    February_Ground_Temperature: Annotated[float, Field(default=18)]

    March_Ground_Temperature: Annotated[float, Field(default=18)]

    April_Ground_Temperature: Annotated[float, Field(default=18)]

    May_Ground_Temperature: Annotated[float, Field(default=18)]

    June_Ground_Temperature: Annotated[float, Field(default=18)]

    July_Ground_Temperature: Annotated[float, Field(default=18)]

    August_Ground_Temperature: Annotated[float, Field(default=18)]

    September_Ground_Temperature: Annotated[float, Field(default=18)]

    October_Ground_Temperature: Annotated[float, Field(default=18)]

    November_Ground_Temperature: Annotated[float, Field(default=18)]

    December_Ground_Temperature: Annotated[float, Field(default=18)]