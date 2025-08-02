from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Material_Roofvegetation(EpBunch):
    """EcoRoof model, plant layer plus soil layer"""

    Name: Annotated[str, Field(default=...)]

    Height_Of_Plants: Annotated[float, Field(gt=0.005, le=1.0, default=.2)]
    """The ecoroof module is designed for short plants and shrubs."""

    Leaf_Area_Index: Annotated[float, Field(gt=0.001, le=5.0, default=1.0)]
    """Entire surface is assumed covered, so decrease LAI accordingly."""

    Leaf_Reflectivity: Annotated[float, Field(ge=0.05, le=0.5, default=0.22)]
    """Leaf reflectivity (albedo) is typically 0.18-0.25"""

    Leaf_Emissivity: Annotated[float, Field(ge=0.8, le=1.0, default=0.95)]

    Minimum_Stomatal_Resistance: Annotated[float, Field(ge=50.0, le=300., default=180.0)]
    """This depends upon plant type"""

    Soil_Layer_Name: Annotated[str, Field(default='Green Roof Soil')]

    Roughness: Annotated[Literal['VeryRough', 'MediumRough', 'Rough', 'Smooth', 'MediumSmooth', 'VerySmooth'], Field(default='MediumRough')]

    Thickness: Annotated[float, Field(gt=0.05, le=0.7, default=0.1)]
    """thickness of the soil layer of the EcoRoof"""

    Conductivity_Of_Dry_Soil: Annotated[float, Field(ge=0.2, le=1.5, default=0.35)]
    """Thermal conductivity of dry soil."""

    Density_Of_Dry_Soil: Annotated[float, Field(ge=300, le=2000, default=1100)]
    """Density of dry soil (the code modifies this as the soil becomes moist)"""

    Specific_Heat_Of_Dry_Soil: Annotated[float, Field(gt=500, le=2000, default=1200)]
    """Specific heat of dry soil"""

    Thermal_Absorptance: Annotated[float, Field(gt=0.8, le=1.0, default=.9)]
    """Soil emissivity is typically in range of 0.90 to 0.98"""

    Solar_Absorptance: Annotated[float, Field(ge=0.40, le=0.9, default=.70)]
    """Solar absorptance of dry soil (1-albedo) is typically 0.60 to 0.85"""

    Visible_Absorptance: Annotated[float, Field(gt=0.5, le=1.0, default=.75)]

    Saturation_Volumetric_Moisture_Content_Of_The_Soil_Layer: Annotated[float, Field(gt=0.1, le=0.5, default=0.3)]
    """Maximum moisture content is typically less than 0.5"""

    Residual_Volumetric_Moisture_Content_Of_The_Soil_Layer: Annotated[float, Field(ge=0.01, le=0.1, default=0.01)]

    Initial_Volumetric_Moisture_Content_Of_The_Soil_Layer: Annotated[float, Field(gt=0.05, le=0.5, default=0.1)]

    Moisture_Diffusion_Calculation_Method: Annotated[Literal['Simple', 'Advanced'], Field(default='Advanced')]
    """Advanced calculation requires increased number of timesteps (recommended >20)."""