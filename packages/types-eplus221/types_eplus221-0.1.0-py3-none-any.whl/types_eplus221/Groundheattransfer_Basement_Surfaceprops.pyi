from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Surfaceprops(EpBunch):
    """Specifies the soil surface properties for the Basement preprocessor ground"""

    Albedo__Surface_Albedo_For_No_Snow_Conditions: Annotated[str, Field(default='0.16')]

    Albedo__Surface_Albedo_For_Snow_Conditions: Annotated[str, Field(default='0.40')]

    Epsln__Surface_Emissivity_No_Snow: Annotated[str, Field(default='0.94')]

    Epsln__Surface_Emissivity_With_Snow: Annotated[str, Field(default='0.86')]

    Veght__Surface_Roughness_No_Snow_Conditions: Annotated[str, Field(default='6.0')]

    Veght__Surface_Roughness_Snow_Conditions: Annotated[str, Field(default='0.25')]

    Pet__Flag__Potential_Evapotranspiration_On_: Annotated[Literal['TRUE', 'FALSE'], Field(default='FALSE')]
    """Typically, PET is False"""