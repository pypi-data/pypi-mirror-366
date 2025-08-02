from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Groundheatexchanger_Horizontaltrench(EpBunch):
    """This models a horizontal heat exchanger placed in a series of trenches"""

    Name: Annotated[str, Field(default=...)]

    Inlet_Node_Name: Annotated[str, Field(default=...)]

    Outlet_Node_Name: Annotated[str, Field(default=...)]

    Design_Flow_Rate: Annotated[float, Field(default=..., gt=0)]

    Trench_Length_in_Pipe_Axial_Direction: Annotated[float, Field(gt=0, default=50)]
    """This is the total pipe axial length of the heat exchanger"""

    Number_of_Trenches: Annotated[int, Field(ge=1, default=1)]
    """This is the number of horizontal legs that will be used"""

    Horizontal_Spacing_Between_Pipes: Annotated[float, Field(gt=0, default=1.0)]
    """This represents the average horizontal spacing between any two"""

    Pipe_Inner_Diameter: Annotated[float, Field(gt=0, default=0.016)]

    Pipe_Outer_Diameter: Annotated[float, Field(gt=0, default=0.026)]

    Burial_Depth: Annotated[float, Field(gt=0, default=1.5)]
    """This is the burial depth of the pipes, or the trenches"""

    Soil_Thermal_Conductivity: Annotated[float, Field(gt=0, default=1.08)]

    Soil_Density: Annotated[float, Field(gt=0, default=962)]

    Soil_Specific_Heat: Annotated[float, Field(gt=0, default=2576)]

    Pipe_Thermal_Conductivity: Annotated[float, Field(gt=0, default=0.3895)]

    Pipe_Density: Annotated[float, Field(gt=0, default=641)]

    Pipe_Specific_Heat: Annotated[float, Field(gt=0, default=2405)]

    Soil_Moisture_Content_Percent: Annotated[float, Field(ge=0, le=100, default=30)]

    Soil_Moisture_Content_Percent_at_Saturation: Annotated[float, Field(ge=0, le=100, default=50)]

    Undisturbed_Ground_Temperature_Model_Type: Annotated[Literal['Site:GroundTemperature:Undisturbed:FiniteDifference', 'Site:GroundTemperature:Undisturbed:KusudaAchenbach', 'Site:GroundTemperature:Undisturbed:Xing'], Field(default=...)]

    Undisturbed_Ground_Temperature_Model_Name: Annotated[str, Field(default=...)]

    Evapotranspiration_Ground_Cover_Parameter: Annotated[float, Field(ge=0, le=1.5, default=0.4)]
    """This specifies the ground cover effects during evapotranspiration"""