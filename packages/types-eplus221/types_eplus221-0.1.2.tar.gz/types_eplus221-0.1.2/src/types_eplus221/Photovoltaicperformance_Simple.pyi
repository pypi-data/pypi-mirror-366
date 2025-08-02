from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Photovoltaicperformance_Simple(EpBunch):
    """Describes a simple model of photovoltaics that may be useful for early phase"""

    Name: Annotated[str, Field()]

    Fraction_of_Surface_Area_with_Active_Solar_Cells: Annotated[float, Field(default=..., ge=0.0, le=1.0)]

    Conversion_Efficiency_Input_Mode: Annotated[Literal['Fixed', 'Scheduled'], Field()]

    Value_for_Cell_Efficiency_if_Fixed: Annotated[float, Field(ge=0.0, le=1.0)]
    """Efficiency = (power generated [W])/(incident solar[W])"""

    Efficiency_Schedule_Name: Annotated[str, Field()]