from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Electricloadcenter_Storage_Simple(EpBunch):
    """Used to model storage of electricity in an electric load center. This is a simple"""

    Name: Annotated[str, Field()]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Name: Annotated[str, Field()]
    """Enter name of zone to receive storage losses as heat"""

    Radiative_Fraction_For_Zone_Heat_Gains: Annotated[str, Field()]

    Nominal_Energetic_Efficiency_For_Charging: Annotated[str, Field()]

    Nominal_Discharging_Energetic_Efficiency: Annotated[str, Field()]

    Maximum_Storage_Capacity: Annotated[str, Field()]

    Maximum_Power_For_Discharging: Annotated[str, Field()]

    Maximum_Power_For_Charging: Annotated[str, Field()]

    Initial_State_Of_Charge: Annotated[str, Field()]