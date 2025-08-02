from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Materialproperty_Moisturepenetrationdepth_Settings(EpBunch):
    """Additional properties for moisture using EMPD procedure"""

    Name: Annotated[str, Field(default=...)]
    """Material Name that the moisture properties will be added to."""

    Water_Vapor_Diffusion_Resistance_Factor: Annotated[float, Field(default=..., ge=0.0)]
    """Ratio of water vapor permeability of stagnant air to water vapor"""

    Moisture_Equation_Coefficient_A: Annotated[float, Field(default=...)]

    Moisture_Equation_Coefficient_B: Annotated[float, Field(default=...)]

    Moisture_Equation_Coefficient_C: Annotated[float, Field(default=...)]

    Moisture_Equation_Coefficient_D: Annotated[float, Field(default=...)]

    Surface_Layer_Penetration_Depth: Annotated[float, Field(gt=0, default=autocalculate)]

    Deep_Layer_Penetration_Depth: Annotated[float, Field(ge=0, default=autocalculate)]

    Coating_Layer_Thickness: Annotated[float, Field(default=..., ge=0)]

    Coating_Layer_Water_Vapor_Diffusion_Resistance_Factor: Annotated[float, Field(default=..., ge=0)]
    """The coating's resistance to water vapor diffusion relative to the"""