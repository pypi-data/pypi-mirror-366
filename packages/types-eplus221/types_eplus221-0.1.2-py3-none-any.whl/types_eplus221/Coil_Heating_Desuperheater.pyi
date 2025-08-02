from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Heating_Desuperheater(EpBunch):
    """Desuperheater air heating coil. The heating energy provided by this coil is reclaimed"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Heat_Reclaim_Recovery_Efficiency: Annotated[float, Field(ge=0.0)]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Heating_Source_Object_Type: Annotated[Literal['Coil:Cooling:DX:SingleSpeed', 'Coil:Cooling:DX:VariableSpeed', 'Coil:Cooling:DX:TwoSpeed', 'Coil:Cooling:DX:TwoStageWithHumidityControlMode', 'Refrigeration:CompressorRack', 'Refrigeration:Condenser:AirCooled', 'Refrigeration:Condenser:EvaporativeCooled', 'Refrigeration:Condenser:WaterCooled'], Field(default=...)]

    Heating_Source_Name: Annotated[str, Field(default=...)]

    Temperature_Setpoint_Node_Name: Annotated[str, Field()]
    """Required if coil is temperature controlled."""

    Parasitic_Electric_Load: Annotated[float, Field(ge=0)]
    """parasitic electric load associated with the desuperheater coil operation"""