from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Electricloadcenter_Inverter_Pvwatts(EpBunch):
    """Electric power inverter to convert from direct current (DC) to alternating current"""

    Name: Annotated[str, Field()]

    Dc_To_Ac_Size_Ratio: Annotated[float, Field(gt=0, default=1.10)]

    Inverter_Efficiency: Annotated[float, Field(gt=0, le=1, default=0.96)]