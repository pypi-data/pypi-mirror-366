from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zoneairmassflowconservation(EpBunch):
    """Enforces the zone air mass flow balance by adjusting zone mixing object and/or"""

    Adjust_Zone_Mixing_For_Zone_Air_Mass_Flow_Balance: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """If Yes, Zone mixing object flow rates are adjusted to balance the zone air mass flow"""

    Infiltration_Balancing_Method: Annotated[Literal['AddInfiltrationFlow', 'AdjustInfiltrationFlow', 'None'], Field(default='AddInfiltrationFlow')]
    """This input field allows user to choose how zone infiltration flow is treated during"""

    Infiltration_Balancing_Zones: Annotated[Literal['MixingSourceZonesOnly', 'AllZones'], Field(default='MixingSourceZonesOnly')]
    """This input field allows user to choose which zones are included in infiltration balancing."""