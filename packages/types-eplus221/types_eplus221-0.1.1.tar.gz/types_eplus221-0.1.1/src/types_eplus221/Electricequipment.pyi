from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Electricequipment(EpBunch):
    """Sets internal gains for electric equipment in the zone."""

    Name: Annotated[str, Field(default=...)]

    Zone_Or_Zonelist_Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]
    """units in schedule should be fraction applied to design level of electric equipment, generally (0.0 - 1.0)"""

    Design_Level_Calculation_Method: Annotated[Literal['EquipmentLevel', 'Watts/Area', 'Watts/Person'], Field(default='EquipmentLevel')]
    """The entered calculation method is used to create the maximum amount of electric equipment"""

    Design_Level: Annotated[float, Field(ge=0)]

    Watts_Per_Zone_Floor_Area: Annotated[float, Field(ge=0)]

    Watts_Per_Person: Annotated[float, Field(ge=0)]

    Fraction_Latent: Annotated[float, Field(ge=0.0, le=1.0, default=0)]

    Fraction_Radiant: Annotated[float, Field(ge=0.0, le=1.0, default=0)]

    Fraction_Lost: Annotated[float, Field(ge=0.0, le=1.0, default=0)]

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""