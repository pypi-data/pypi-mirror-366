from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Groundreflectance(EpBunch):
    """Specifies the ground reflectance values used to calculate ground reflected solar."""

    January_Ground_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.2)]

    February_Ground_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.2)]

    March_Ground_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.2)]

    April_Ground_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.2)]

    May_Ground_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.2)]

    June_Ground_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.2)]

    July_Ground_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.2)]

    August_Ground_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.2)]

    September_Ground_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.2)]

    October_Ground_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.2)]

    November_Ground_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.2)]

    December_Ground_Reflectance: Annotated[float, Field(ge=0.0, le=1.0, default=0.2)]