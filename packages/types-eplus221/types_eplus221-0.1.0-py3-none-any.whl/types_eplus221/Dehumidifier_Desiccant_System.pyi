from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Dehumidifier_Desiccant_System(EpBunch):
    """This compound object models a desiccant heat exchanger, an optional"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Desiccant_Heat_Exchanger_Object_Type: Annotated[Literal['HeatExchanger:Desiccant:BalancedFlow'], Field(default=...)]

    Desiccant_Heat_Exchanger_Name: Annotated[str, Field(default=...)]

    Sensor_Node_Name: Annotated[str, Field(default=...)]

    Regeneration_Air_Fan_Object_Type: Annotated[Literal['Fan:SystemModel', 'Fan:OnOff', 'Fan:ConstantVolume'], Field(default=...)]

    Regeneration_Air_Fan_Name: Annotated[str, Field(default=...)]

    Regeneration_Air_Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='DrawThrough')]

    Regeneration_Air_Heater_Object_Type: Annotated[Literal['Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field()]
    """works with gas, electric, hot water and steam heating coils."""

    Regeneration_Air_Heater_Name: Annotated[str, Field()]

    Regeneration_Inlet_Air_Setpoint_Temperature: Annotated[float, Field(default=46.0)]
    """This value is also used as regeneration air heater design coil air"""

    Companion_Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:DX:SingleSpeed', 'Coil:Cooling:DX:TwoStageWithHumidityControlMode', 'Coil:Cooling:DX:VariableSpeed'], Field()]

    Companion_Cooling_Coil_Name: Annotated[str, Field()]

    Companion_Cooling_Coil_Upstream_Of_Dehumidifier_Process_Inlet: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Select Yes if the companion cooling coil is located directly upstream"""

    Companion_Coil_Regeneration_Air_Heating: Annotated[Literal['Yes', 'No'], Field(default='No')]

    Exhaust_Fan_Maximum_Flow_Rate: Annotated[float, Field()]

    Exhaust_Fan_Maximum_Power: Annotated[float, Field()]

    Exhaust_Fan_Power_Curve_Name: Annotated[str, Field()]
    """Curve object type must be Curve:Quadratic or Curve:Cubic"""