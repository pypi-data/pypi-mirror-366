from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Insulation(EpBunch):
    """Describes the insulation used on an exterior basement wall for the Basement"""

    Rext__R_Value_Of_Any_Exterior_Insulation: Annotated[str, Field()]

    Insfull__Flag__Is_The_Wall_Fully_Insulated_: Annotated[Literal['TRUE', 'FALSE'], Field(default=...)]
    """True for full insulation"""