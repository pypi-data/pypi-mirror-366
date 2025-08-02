from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Grounddomain_Slab(EpBunch):
    """Ground-coupled slab model for on-grade and"""

    Name: Annotated[str, Field(default=...)]

    Ground_Domain_Depth: Annotated[float, Field(gt=0.0, default=10)]

    Aspect_Ratio: Annotated[float, Field(default=1)]

    Perimeter_Offset: Annotated[float, Field(gt=0.0, default=5)]

    Soil_Thermal_Conductivity: Annotated[float, Field(gt=0.0, default=1.5)]

    Soil_Density: Annotated[float, Field(gt=0.0, default=2800)]

    Soil_Specific_Heat: Annotated[float, Field(gt=0.0, default=850)]

    Soil_Moisture_Content_Volume_Fraction: Annotated[float, Field(ge=0, le=100, default=30)]

    Soil_Moisture_Content_Volume_Fraction_at_Saturation: Annotated[float, Field(ge=0, le=100, default=50)]

    Undisturbed_Ground_Temperature_Model_Type: Annotated[Literal['Site:GroundTemperature:Undisturbed:FiniteDifference', 'Site:GroundTemperature:Undisturbed:KusudaAchenbach', 'Site:GroundTemperature:Undisturbed:Xing'], Field(default=...)]

    Undisturbed_Ground_Temperature_Model_Name: Annotated[str, Field(default=...)]

    Evapotranspiration_Ground_Cover_Parameter: Annotated[float, Field(ge=0, le=1.5, default=0.4)]
    """This specifies the ground cover effects during evapotranspiration"""

    Slab_Boundary_Condition_Model_Name: Annotated[str, Field(default=...)]

    Slab_Location: Annotated[Literal['InGrade', 'OnGrade'], Field(default=...)]
    """This field specifies whether the slab is located "in-grade" or "on-grade""""

    Slab_Material_Name: Annotated[str, Field()]
    """Only applicable for the in-grade case"""

    Horizontal_Insulation: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """This field specifies the presence of insulation beneath the slab."""

    Horizontal_Insulation_Material_Name: Annotated[str, Field()]
    """This field specifies the horizontal insulation material."""

    Horizontal_Insulation_Extents: Annotated[Literal['Full', 'Perimeter'], Field(default='Full')]
    """This field specifies whether the horizontal insulation fully insulates"""

    Perimeter_Insulation_Width: Annotated[float, Field(gt=0.0)]
    """This field specifies the width of the underfloor perimeter insulation"""

    Vertical_Insulation: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """This field specifies the presence of vertical insulation at the slab edge."""

    Vertical_Insulation_Material_Name: Annotated[str, Field()]
    """This field specifies the vertical insulation material."""

    Vertical_Insulation_Depth: Annotated[float, Field(gt=0.0)]
    """Only used when including vertical insulation"""

    Simulation_Timestep: Annotated[Literal['Timestep', 'Hourly'], Field(default='Hourly')]
    """This field specifies the ground domain simulation timestep."""

    Geometric_Mesh_Coefficient: Annotated[float, Field(ge=1.0, le=2.0, default=1.6)]

    Mesh_Density_Parameter: Annotated[int, Field(ge=4, default=6)]