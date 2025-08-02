from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Site_Grounddomain_Basement(EpBunch):
    """Ground-coupled basement model for simulating basements"""

    Name: Annotated[str, Field(default=...)]

    Ground_Domain_Depth: Annotated[float, Field(gt=0.0, default=10)]
    """The depth from ground surface to the deep ground boundary of the domain."""

    Aspect_Ratio: Annotated[float, Field(default=1)]
    """This defines the height to width ratio of the basement zone."""

    Perimeter_Offset: Annotated[float, Field(gt=0.0, default=5)]
    """The distance from the basement wall edge to the edge of the ground domain"""

    Soil_Thermal_Conductivity: Annotated[float, Field(gt=0.0, default=1.5)]

    Soil_Density: Annotated[float, Field(gt=0.0, default=2800)]

    Soil_Specific_Heat: Annotated[float, Field(gt=0.0, default=850)]

    Soil_Moisture_Content_Volume_Fraction: Annotated[float, Field(ge=0, le=100, default=30)]

    Soil_Moisture_Content_Volume_Fraction_At_Saturation: Annotated[float, Field(ge=0, le=100, default=50)]

    Undisturbed_Ground_Temperature_Model_Type: Annotated[Literal['Site:GroundTemperature:Undisturbed:FiniteDifference', 'Site:GroundTemperature:Undisturbed:KusudaAchenbach', 'Site:GroundTemperature:Undisturbed:Xing'], Field(default=...)]

    Undisturbed_Ground_Temperature_Model_Name: Annotated[str, Field(default=...)]

    Evapotranspiration_Ground_Cover_Parameter: Annotated[float, Field(ge=0, le=1.5, default=0.4)]
    """This specifies the ground cover effects during evapotranspiration"""

    Basement_Floor_Boundary_Condition_Model_Name: Annotated[str, Field(default=...)]

    Horizontal_Insulation: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """This field specifies the presence of insulation beneath the basement floor."""

    Horizontal_Insulation_Material_Name: Annotated[str, Field()]

    Horizontal_Insulation_Extents: Annotated[Literal['Perimeter', 'Full'], Field(default='Full')]
    """This field specifies whether the horizontal insulation fully insulates"""

    Perimeter_Horizontal_Insulation_Width: Annotated[float, Field(gt=0.0)]
    """Width of horizontal perimeter insulation measured from"""

    Basement_Wall_Depth: Annotated[float, Field(gt=0.0)]
    """Depth measured from ground surface."""

    Basement_Wall_Boundary_Condition_Model_Name: Annotated[str, Field(default=...)]

    Vertical_Insulation: Annotated[Literal['Yes', 'No'], Field(default='No')]

    Basement_Wall_Vertical_Insulation_Material_Name: Annotated[str, Field()]

    Vertical_Insulation_Depth: Annotated[float, Field(gt=0.0)]
    """Depth measured from the ground surface."""

    Simulation_Timestep: Annotated[Literal['Timestep', 'Hourly'], Field(default='Hourly')]
    """This field specifies the basement domain simulation interval."""

    Mesh_Density_Parameter: Annotated[int, Field(ge=2, default=4)]