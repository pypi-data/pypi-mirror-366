from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Surfaceprops(EpBunch):
    """Specifies the soil surface properties for the Basement preprocessor ground"""

    ALBEDO_Surface_albedo_for_No_snow_conditions: Annotated[str, Field(default='0.16')]

    ALBEDO_Surface_albedo_for_snow_conditions: Annotated[str, Field(default='0.40')]

    EPSLN_Surface_emissivity_No_Snow: Annotated[str, Field(default='0.94')]

    EPSLN_Surface_emissivity_with_Snow: Annotated[str, Field(default='0.86')]

    VEGHT_Surface_roughness_No_snow_conditions: Annotated[str, Field(default='6.0')]

    VEGHT_Surface_roughness_Snow_conditions: Annotated[str, Field(default='0.25')]

    PET_Flag_Potential_evapotranspiration_on: Annotated[Literal['TRUE', 'FALSE'], Field(default='FALSE')]
    """Typically, PET is False"""