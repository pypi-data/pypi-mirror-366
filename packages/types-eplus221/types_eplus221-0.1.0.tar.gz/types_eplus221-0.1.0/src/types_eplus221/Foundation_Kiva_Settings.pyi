from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Foundation_Kiva_Settings(EpBunch):
    """Settings applied across all Kiva foundation calculations."""

    Soil_Conductivity: Annotated[float, Field(gt=0.0, default=1.73)]

    Soil_Density: Annotated[float, Field(gt=0.0, default=1842)]

    Soil_Specific_Heat: Annotated[float, Field(gt=0.0, default=419)]

    Ground_Solar_Absorptivity: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]

    Ground_Thermal_Absorptivity: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]

    Ground_Surface_Roughness: Annotated[float, Field(gt=0.0, default=0.03)]

    Far_Field_Width: Annotated[float, Field(gt=0.0, default=40)]

    Deep_Ground_Boundary_Condition: Annotated[Literal['ZeroFlux', 'GroundWater', 'Autoselect'], Field(default='Autoselect')]

    Deep_Ground_Depth: Annotated[float, Field(gt=0.0, default=autocalculate)]

    Minimum_Cell_Dimension: Annotated[float, Field(gt=0.0, default=0.02)]

    Maximum_Cell_Growth_Coefficient: Annotated[float, Field(ge=1.0, default=1.5)]

    Simulation_Timestep: Annotated[Literal['Hourly', 'Timestep'], Field(default='Hourly')]