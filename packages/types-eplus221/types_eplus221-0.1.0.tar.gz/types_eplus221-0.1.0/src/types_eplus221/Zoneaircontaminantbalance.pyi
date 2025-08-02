from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zoneaircontaminantbalance(EpBunch):
    """Determines which contaminant concentration will be simulates."""

    Carbon_Dioxide_Concentration: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, CO2 simulation will be performed."""

    Outdoor_Carbon_Dioxide_Schedule_Name: Annotated[str, Field()]
    """Schedule values should be in parts per million (ppm)"""

    Generic_Contaminant_Concentration: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, generic contaminant simulation will be performed."""

    Outdoor_Generic_Contaminant_Schedule_Name: Annotated[str, Field()]
    """Schedule values should be generic contaminant concentration in parts per"""