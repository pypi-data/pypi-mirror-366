from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheatexchanger_Slinky(EpBunch):
    """This models a slinky horizontal heat exchanger"""

    Name: Annotated[str, Field(default=...)]

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]

    Design_Flow_Rate: Annotated[float, Field(gt=0, default=0.002)]

    Soil_Thermal_Conductivity: Annotated[float, Field(gt=0, default=1.08)]

    Soil_Density: Annotated[float, Field(gt=0, default=962)]

    Soil_Specific_Heat: Annotated[float, Field(gt=0, default=2576)]

    Pipe_Thermal_Conductivity: Annotated[float, Field(gt=0, default=0.4)]

    Pipe_Density: Annotated[float, Field(gt=0, default=641)]

    Pipe_Specific_Heat: Annotated[float, Field(gt=0, default=2405)]

    Pipe_Outer_Diameter: Annotated[float, Field(gt=0, default=0.02667)]

    Pipe_Thickness: Annotated[float, Field(gt=0, default=0.002413)]

    Heat_Exchanger_Configuration: Annotated[Literal['Vertical', 'Horizontal'], Field()]
    """This is the orientation of the heat exchanger"""

    Coil_Diameter: Annotated[float, Field(gt=0, default=1.0)]
    """This is the diameter of the heat exchanger coil"""

    Coil_Pitch: Annotated[float, Field(gt=0, default=0.20)]
    """This is the center-to-center distance between coils"""

    Trench_Depth: Annotated[float, Field(gt=0, default=1.8)]
    """This is the distance from the ground surface to the"""

    Trench_Length: Annotated[float, Field(gt=0, default=10)]
    """This is the total length of a single trench"""

    Number_Of_Trenches: Annotated[int, Field(ge=1, default=1)]
    """This is the number of parallel trenches that"""

    Horizontal_Spacing_Between_Pipes: Annotated[float, Field(gt=0, default=2.0)]
    """This represents the average horizontal spacing"""

    Undisturbed_Ground_Temperature_Model_Type: Annotated[Literal['Site:GroundTemperature:Undisturbed:FiniteDifference', 'Site:GroundTemperature:Undisturbed:KusudaAchenbach', 'Site:GroundTemperature:Undisturbed:Xing'], Field(default=...)]

    Undisturbed_Ground_Temperature_Model_Name: Annotated[str, Field(default=...)]

    Maximum_Length_Of_Simulation: Annotated[float, Field()]