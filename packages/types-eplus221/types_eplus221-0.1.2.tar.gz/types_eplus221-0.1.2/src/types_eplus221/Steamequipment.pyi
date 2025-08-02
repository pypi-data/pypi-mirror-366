from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Steamequipment(EpBunch):
    """Sets internal gains for steam equipment in the zone."""

    Name: Annotated[str, Field(default=...)]

    Zone_or_ZoneList_Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]
    """units in Schedule should be fraction applied to design level of steam equipment, generally (0.0 - 1.0)"""

    Design_Level_Calculation_Method: Annotated[Literal['EquipmentLevel', 'Watts/Area', 'Watts/Person', 'Power/Area', 'Power/Person'], Field(default='EquipmentLevel')]
    """The entered calculation method is used to create the maximum amount of steam equipment"""

    Design_Level: Annotated[float, Field(ge=0)]

    Power_per_Zone_Floor_Area: Annotated[float, Field(ge=0)]

    Power_per_Person: Annotated[float, Field(ge=0)]

    Fraction_Latent: Annotated[float, Field(ge=0.0, le=1.0, default=0)]

    Fraction_Radiant: Annotated[float, Field(ge=0.0, le=1.0, default=0)]

    Fraction_Lost: Annotated[float, Field(ge=0.0, le=1.0, default=0)]

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""