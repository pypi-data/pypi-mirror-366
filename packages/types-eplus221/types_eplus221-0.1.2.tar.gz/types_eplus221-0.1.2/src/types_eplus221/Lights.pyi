from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Lights(EpBunch):
    """Sets internal gains for lights in the zone."""

    Name: Annotated[str, Field(default=...)]

    Zone_or_ZoneList_Name: Annotated[str, Field(default=...)]

    Schedule_Name: Annotated[str, Field(default=...)]
    """units in schedule should be fraction applied to design level of lights, generally (0.0 - 1.0)"""

    Design_Level_Calculation_Method: Annotated[Literal['LightingLevel', 'Watts/Area', 'Watts/Person'], Field(default='LightingLevel')]
    """The entered calculation method is used to create the maximum amount of lights"""

    Lighting_Level: Annotated[float, Field(ge=0)]

    Watts_per_Zone_Floor_Area: Annotated[float, Field(ge=0)]

    Watts_per_Person: Annotated[float, Field(ge=0)]

    Return_Air_Fraction: Annotated[float, Field(ge=0.0, le=1.0, default=0)]
    """Used only for sizing calculation if return-air-fraction"""

    Fraction_Radiant: Annotated[float, Field(ge=0.0, le=1.0, default=0)]

    Fraction_Visible: Annotated[float, Field(ge=0.0, le=1.0, default=0)]

    Fraction_Replaceable: Annotated[float, Field(ge=0.0, le=1.0, default=1.0)]
    """For Daylighting:Controls must be 0 or 1: 0 = no dimming control, 1 = full dimming control"""

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Return_Air_Fraction_Calculated_from_Plenum_Temperature: Annotated[Literal['Yes', 'No'], Field(default='No')]

    Return_Air_Fraction_Function_of_Plenum_Temperature_Coefficient_1: Annotated[float, Field(ge=0.0, default=0.0)]
    """Used only if Return Air Fraction Is Calculated from Plenum Temperature = Yes"""

    Return_Air_Fraction_Function_of_Plenum_Temperature_Coefficient_2: Annotated[float, Field(ge=0.0, default=0.0)]
    """Used only if Return Air Fraction Is Calculated from Plenum Temperature = Yes"""

    Return_Air_Heat_Gain_Node_Name: Annotated[str, Field()]
    """Name of the return air node for this heat gain."""