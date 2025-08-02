from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Electricloadcenter_Inverter_Simple(EpBunch):
    """Electric power inverter to convert from direct current (DC) to alternating current"""

    Name: Annotated[str, Field()]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Name: Annotated[str, Field()]
    """enter name of zone to receive inverter losses as heat"""

    Radiative_Fraction: Annotated[str, Field()]

    Inverter_Efficiency: Annotated[str, Field()]