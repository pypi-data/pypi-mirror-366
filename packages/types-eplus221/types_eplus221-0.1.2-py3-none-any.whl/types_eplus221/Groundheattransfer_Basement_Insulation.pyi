from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Insulation(EpBunch):
    """Describes the insulation used on an exterior basement wall for the Basement"""

    REXT_R_Value_of_any_exterior_insulation: Annotated[str, Field()]

    INSFULL_Flag_Is_the_wall_fully_insulated: Annotated[Literal['TRUE', 'FALSE'], Field(default=...)]
    """True for full insulation"""