from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Pipingsystem_Underground_Domain(EpBunch):
    """The ground domain object for underground piping system simulation."""

    Name: Annotated[str, Field(default=...)]

    Xmax: Annotated[float, Field(default=..., gt=0)]
    """Domain extent in the local 'X' direction"""

    Ymax: Annotated[float, Field(default=..., gt=0)]
    """Domain extent in the local 'Y' direction"""

    Zmax: Annotated[float, Field(default=..., gt=0)]
    """Domain extent in the local 'Y' direction"""

    XDirection_Mesh_Density_Parameter: Annotated[int, Field(gt=0, default=4)]
    """If mesh type is symmetric geometric, this should be an even number."""

    XDirection_Mesh_Type: Annotated[Literal['Uniform', 'SymmetricGeometric'], Field(default=...)]

    XDirection_Geometric_Coefficient: Annotated[float, Field(ge=1, le=2, default=1.3)]
    """optional"""

    YDirection_Mesh_Density_Parameter: Annotated[int, Field(gt=0, default=4)]
    """If mesh type is symmetric geometric, this should be an even number."""

    YDirection_Mesh_Type: Annotated[Literal['Uniform', 'SymmetricGeometric'], Field(default=...)]

    YDirection_Geometric_Coefficient: Annotated[float, Field(ge=1, le=2, default=1.3)]
    """optional"""

    ZDirection_Mesh_Density_Parameter: Annotated[int, Field(gt=0, default=4)]
    """If mesh type is symmetric geometric, this should be an even number."""

    ZDirection_Mesh_Type: Annotated[Literal['Uniform', 'SymmetricGeometric'], Field(default=...)]

    ZDirection_Geometric_Coefficient: Annotated[float, Field(ge=1, le=2, default=1.3)]
    """optional"""

    Soil_Thermal_Conductivity: Annotated[float, Field(default=..., gt=0)]

    Soil_Density: Annotated[float, Field(default=..., gt=0)]

    Soil_Specific_Heat: Annotated[float, Field(default=..., gt=0)]
    """This is a dry soil property, which is adjusted for freezing effects"""

    Soil_Moisture_Content_Volume_Fraction: Annotated[float, Field(ge=0, le=100, default=30)]

    Soil_Moisture_Content_Volume_Fraction_at_Saturation: Annotated[float, Field(ge=0, le=100, default=50)]

    Undisturbed_Ground_Temperature_Model_Type: Annotated[Literal['Site:GroundTemperature:Undisturbed:FiniteDifference', 'Site:GroundTemperature:Undisturbed:KusudaAchenbach', 'Site:GroundTemperature:Undisturbed:Xing'], Field(default=...)]

    Undisturbed_Ground_Temperature_Model_Name: Annotated[str, Field(default=...)]

    This_Domain_Includes_Basement_Surface_Interaction: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """if Yes, then the following basement inputs are used"""

    Width_of_Basement_Floor_in_Ground_Domain: Annotated[float, Field()]
    """Required only if Domain Has Basement Interaction"""

    Depth_of_Basement_Wall_In_Ground_Domain: Annotated[float, Field()]
    """Required only if Domain Has Basement Interaction"""

    Shift_Pipe_X_Coordinates_By_Basement_Width: Annotated[Literal['Yes', 'No'], Field()]
    """Required only if Domain Has Basement Interaction"""

    Name_of_Basement_Wall_Boundary_Condition_Model: Annotated[str, Field()]
    """Required only if Domain Has Basement Interaction"""

    Name_of_Basement_Floor_Boundary_Condition_Model: Annotated[str, Field()]
    """Required only if Domain Has Basement Interaction"""

    Convergence_Criterion_for_the_Outer_Cartesian_Domain_Iteration_Loop: Annotated[float, Field(ge=0.000001, le=0.5, default=0.001)]

    Maximum_Iterations_in_the_Outer_Cartesian_Domain_Iteration_Loop: Annotated[int, Field(ge=3, le=10000, default=500)]

    Evapotranspiration_Ground_Cover_Parameter: Annotated[float, Field(ge=0, le=1.5, default=0.4)]
    """This specifies the ground cover effects during evapotranspiration"""

    Number_of_Pipe_Circuits_Entered_for_this_Domain: Annotated[int, Field(default=..., ge=1)]

    Pipe_Circuit_1: Annotated[str, Field(default=...)]
    """Name of a pipe circuit to be simulated in this domain"""

    Pipe_Circuit_2: Annotated[str, Field()]
    """optional"""

    Pipe_Circuit_3: Annotated[str, Field()]
    """optional"""

    Pipe_Circuit_4: Annotated[str, Field()]
    """optional"""

    Pipe_Circuit_5: Annotated[str, Field()]
    """optional"""

    Pipe_Circuit_6: Annotated[str, Field()]
    """optional"""