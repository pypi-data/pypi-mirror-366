from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonecapacitancemultiplier_Researchspecial(EpBunch):
    """Multiplier altering the relative capacitance of the air compared to an empty zone"""

    Name: Annotated[str, Field(default=...)]

    Zone_Or_Zonelist_Name: Annotated[str, Field()]
    """If this field is left blank, the multipliers are applied to all the zones not specified"""

    Temperature_Capacity_Multiplier: Annotated[float, Field(gt=0.0, default=1.0)]
    """Used to alter the capacitance of zone air with respect to heat or temperature"""

    Humidity_Capacity_Multiplier: Annotated[float, Field(gt=0.0, default=1.0)]
    """Used to alter the capacitance of zone air with respect to moisture or humidity ratio"""

    Carbon_Dioxide_Capacity_Multiplier: Annotated[float, Field(gt=0.0, default=1.0)]
    """Used to alter the capacitance of zone air with respect to zone air carbon dioxide concentration"""

    Generic_Contaminant_Capacity_Multiplier: Annotated[float, Field(gt=0.0, default=1.0)]
    """Used to alter the capacitance of zone air with respect to zone air generic contaminant concentration"""