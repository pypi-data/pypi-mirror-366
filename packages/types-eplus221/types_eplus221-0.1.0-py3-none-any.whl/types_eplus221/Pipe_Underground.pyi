from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Pipe_Underground(EpBunch):
    """Buried Pipe model: For pipes buried at a depth less"""

    Name: Annotated[str, Field(default=...)]

    Construction_Name: Annotated[str, Field(default=...)]

    Fluid_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Fluid_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Sun_Exposure: Annotated[Literal['SunExposed', 'NoSun'], Field(default=...)]

    Pipe_Inside_Diameter: Annotated[float, Field(gt=0)]
    """pipe thickness is defined in the Construction object"""

    Pipe_Length: Annotated[float, Field(gt=0.0)]

    Soil_Material_Name: Annotated[str, Field(default=...)]

    Undisturbed_Ground_Temperature_Model_Type: Annotated[Literal['Site:GroundTemperature:Undisturbed:FiniteDifference', 'Site:GroundTemperature:Undisturbed:KusudaAchenbach', 'Site:GroundTemperature:Undisturbed:Xing'], Field(default=...)]

    Undisturbed_Ground_Temperature_Model_Name: Annotated[str, Field(default=...)]