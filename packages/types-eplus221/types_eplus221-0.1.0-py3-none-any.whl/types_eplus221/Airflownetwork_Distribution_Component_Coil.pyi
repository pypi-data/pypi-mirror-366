from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Distribution_Component_Coil(EpBunch):
    """This object defines the name of a coil used in an air loop."""

    Coil_Name: Annotated[str, Field(default=...)]
    """Enter the name of a cooling or heating coil in the primary Air loop."""

    Coil_Object_Type: Annotated[Literal['Coil:Cooling:DX:SingleSpeed', 'Coil:Cooling:DX:TwoSpeed', 'Coil:Heating:Fuel', 'Coil:Heating:Electric', 'Coil:Heating:DX:SingleSpeed', 'Coil:Cooling:Water', 'Coil:Heating:Water', 'Coil:Cooling:Water:DetailedGeometry', 'Coil:Cooling:DX:TwoStageWithHumidityControlMode', 'Coil:Cooling:DX:MultiSpeed', 'Coil:Heating:DX:MultiSpeed', 'Coil:Heating:Desuperheater'], Field(default=...)]
    """Select the type of coil corresponding to the name entered in the field above."""

    Air_Path_Length: Annotated[float, Field(default=..., gt=0)]
    """Enter the air path length (depth) for the coil."""

    Air_Path_Hydraulic_Diameter: Annotated[float, Field(default=..., gt=0)]
    """Enter the hydraulic diameter of this coil. The hydraulic diameter is"""