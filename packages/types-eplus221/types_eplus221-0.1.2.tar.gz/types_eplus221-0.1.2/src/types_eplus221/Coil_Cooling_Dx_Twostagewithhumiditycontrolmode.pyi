from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Cooling_Dx_Twostagewithhumiditycontrolmode(EpBunch):
    """Direct expansion (DX) cooling coil and condensing unit (includes electric compressor"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Crankcase_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]

    Maximum_Outdoor_DryBulb_Temperature_for_Crankcase_Heater_Operation: Annotated[float, Field(ge=0.0, default=10.0)]

    Number_of_Capacity_Stages: Annotated[int, Field(ge=1, le=2, default=1)]

    Number_of_Enhanced_Dehumidification_Modes: Annotated[int, Field(ge=0, le=1, default=0)]

    Normal_Mode_Stage_1_Coil_Performance_Object_Type: Annotated[Literal['CoilPerformance:DX:Cooling'], Field(default=...)]

    Normal_Mode_Stage_1_Coil_Performance_Name: Annotated[str, Field(default=...)]

    Normal_Mode_Stage_12_Coil_Performance_Object_Type: Annotated[Literal['CoilPerformance:DX:Cooling'], Field()]

    Normal_Mode_Stage_12_Coil_Performance_Name: Annotated[str, Field()]

    Dehumidification_Mode_1_Stage_1_Coil_Performance_Object_Type: Annotated[Literal['CoilPerformance:DX:Cooling'], Field()]

    Dehumidification_Mode_1_Stage_1_Coil_Performance_Name: Annotated[str, Field()]

    Dehumidification_Mode_1_Stage_12_Coil_Performance_Object_Type: Annotated[Literal['CoilPerformance:DX:Cooling'], Field()]

    Dehumidification_Mode_1_Stage_12_Coil_Performance_Name: Annotated[str, Field()]

    Supply_Water_Storage_Tank_Name: Annotated[str, Field()]

    Condensate_Collection_Water_Storage_Tank_Name: Annotated[str, Field()]

    Minimum_Outdoor_DryBulb_Temperature_for_Compressor_Operation: Annotated[float, Field(default=-25.0)]

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled and for periods"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Basin_Heater_Operating_Schedule_Name: Annotated[str, Field()]
    """This field is only used for Condenser Type = EvaporativelyCooled."""