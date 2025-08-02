from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheattransfer_Basement_Matlprops(EpBunch):
    """Specifies the material properties for the Basement preprocessor ground heat"""

    Nmat__Number_Of_Materials_In_This_Domain: Annotated[str, Field(default=...)]

    Density_For_Foundation_Wall: Annotated[str, Field(default='2243')]

    Density_For_Floor_Slab: Annotated[str, Field(default='2243')]

    Density_For_Ceiling: Annotated[str, Field(default='311')]

    Density_For_Soil: Annotated[str, Field(default='1500')]

    Density_For_Gravel: Annotated[str, Field(default='2000')]

    Density_For_Wood: Annotated[str, Field(default='449')]

    Specific_Heat_For_Foundation_Wall: Annotated[str, Field(default='880')]

    Specific_Heat_For_Floor_Slab: Annotated[str, Field(default='880')]

    Specific_Heat_For_Ceiling: Annotated[str, Field(default='1530')]

    Specific_Heat_For_Soil: Annotated[str, Field(default='840')]

    Specific_Heat_For_Gravel: Annotated[str, Field(default='720')]

    Specific_Heat_For_Wood: Annotated[str, Field(default='1530')]

    Thermal_Conductivity_For_Foundation_Wall: Annotated[str, Field(default='1.4')]

    Thermal_Conductivity_For_Floor_Slab: Annotated[str, Field(default='1.4')]

    Thermal_Conductivity_For_Ceiling: Annotated[str, Field(default='0.09')]

    Thermal_Conductivity_For_Soil: Annotated[str, Field(default='1.1')]

    Thermal_Conductivity_For_Gravel: Annotated[str, Field(default='1.9')]

    Thermal_Conductivity_For_Wood: Annotated[str, Field(default='0.12')]