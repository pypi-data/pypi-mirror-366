from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomairsettings_Onenodedisplacementventilation(EpBunch):
    """The Mundt model for displacement ventilation"""

    Zone_Name: Annotated[str, Field(default=...)]

    Fraction_Of_Convective_Internal_Loads_Added_To_Floor_Air: Annotated[float, Field(ge=0.0, le=1.0)]

    Fraction_Of_Infiltration_Internal_Loads_Added_To_Floor_Air: Annotated[float, Field(ge=0.0, le=1.0)]