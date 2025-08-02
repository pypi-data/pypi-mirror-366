from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Matlprops(EpBunch):
    """Specifies the material properties for the Basement preprocessor ground heat"""

    NMAT_Number_of_materials_in_this_domain: Annotated[str, Field(default=...)]

    Density_for_Foundation_Wall: Annotated[str, Field(default='2243')]

    density_for_Floor_Slab: Annotated[str, Field(default='2243')]

    density_for_Ceiling: Annotated[str, Field(default='311')]

    density_for_Soil: Annotated[str, Field(default='1500')]

    density_for_Gravel: Annotated[str, Field(default='2000')]

    density_for_Wood: Annotated[str, Field(default='449')]

    Specific_heat_for_foundation_wall: Annotated[str, Field(default='880')]

    Specific_heat_for_floor_slab: Annotated[str, Field(default='880')]

    Specific_heat_for_ceiling: Annotated[str, Field(default='1530')]

    Specific_heat_for_soil: Annotated[str, Field(default='840')]

    Specific_heat_for_gravel: Annotated[str, Field(default='720')]

    Specific_heat_for_wood: Annotated[str, Field(default='1530')]

    Thermal_conductivity_for_foundation_wall: Annotated[str, Field(default='1.4')]

    Thermal_conductivity_for_floor_slab: Annotated[str, Field(default='1.4')]

    Thermal_conductivity_for_ceiling: Annotated[str, Field(default='0.09')]

    thermal_conductivity_for_soil: Annotated[str, Field(default='1.1')]

    thermal_conductivity_for_gravel: Annotated[str, Field(default='1.9')]

    thermal_conductivity_for_wood: Annotated[str, Field(default='0.12')]