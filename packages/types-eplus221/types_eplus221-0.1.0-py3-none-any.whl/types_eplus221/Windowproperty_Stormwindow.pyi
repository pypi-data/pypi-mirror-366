from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Windowproperty_Stormwindow(EpBunch):
    """This is a movable exterior glass layer that is usually applied in the winter"""

    Window_Name: Annotated[str, Field(default=...)]
    """Must be the name of a FenestrationSurface:Detailed object with Surface Type = WINDOW."""

    Storm_Glass_Layer_Name: Annotated[str, Field(default=...)]
    """Must be a WindowMaterial:Glazing or WindowMaterial:Glazing:RefractionExtinctionMethod"""

    Distance_Between_Storm_Glass_Layer_And_Adjacent_Glass: Annotated[float, Field(gt=0.0, le=0.5, default=0.050)]

    Month_That_Storm_Glass_Layer_Is_Put_On: Annotated[int, Field(default=..., ge=1, le=12)]

    Day_Of_Month_That_Storm_Glass_Layer_Is_Put_On: Annotated[int, Field(default=..., ge=1, le=31)]

    Month_That_Storm_Glass_Layer_Is_Taken_Off: Annotated[int, Field(default=..., ge=1, le=12)]

    Day_Of_Month_That_Storm_Glass_Layer_Is_Taken_Off: Annotated[int, Field(default=..., ge=1, le=31)]