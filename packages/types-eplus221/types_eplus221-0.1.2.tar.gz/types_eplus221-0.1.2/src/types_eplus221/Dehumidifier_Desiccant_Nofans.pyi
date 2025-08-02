from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Dehumidifier_Desiccant_Nofans(EpBunch):
    """This object models a solid desiccant dehumidifier. The process"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Process_Air_Inlet_Node_Name: Annotated[str, Field()]
    """This is the node entering the process side of the desiccant wheel."""

    Process_Air_Outlet_Node_Name: Annotated[str, Field()]
    """This is the node leaving the process side of the desiccant wheel."""

    Regeneration_Air_Inlet_Node_Name: Annotated[str, Field()]
    """This is the node entering the regeneration side of the desiccant wheel"""

    Regeneration_Fan_Inlet_Node_Name: Annotated[str, Field()]
    """Node for air entering the regeneration fan, mass flow is set"""

    Control_Type: Annotated[Literal['LeavingMaximumHumidityRatioSetpoint', 'SystemNodeMaximumHumidityRatioSetpoint'], Field()]
    """Type of setpoint control:"""

    Leaving_Maximum_Humidity_Ratio_Setpoint: Annotated[float, Field()]
    """Fixed setpoint for maximum process air leaving humidity ratio"""

    Nominal_Process_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Process air flow rate at nominal conditions"""

    Nominal_Process_Air_Velocity: Annotated[float, Field(gt=0.0, le=6)]
    """Process air velocity at nominal flow"""

    Rotor_Power: Annotated[float, Field(ge=0.0)]
    """Power input to wheel rotor motor"""

    Regeneration_Coil_Object_Type: Annotated[Literal['Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field()]
    """heating coil type"""

    Regeneration_Coil_Name: Annotated[str, Field()]
    """Name of heating coil object for regeneration air"""

    Regeneration_Fan_Object_Type: Annotated[Literal['Fan:SystemModel', 'Fan:VariableVolume', 'Fan:ConstantVolume'], Field()]
    """Type of fan object for regeneration air. When using the Default"""

    Regeneration_Fan_Name: Annotated[str, Field()]
    """Name of fan object for regeneration air"""

    Performance_Model_Type: Annotated[Literal['Default', 'UserCurves'], Field()]
    """Specifies whether the default performance model or user-specified"""

    Leaving_DryBulb_Function_of_Entering_DryBulb_and_Humidity_Ratio_Curve_Name: Annotated[str, Field()]
    """Leaving dry-bulb of process air as a function of entering dry-bulb"""

    Leaving_DryBulb_Function_of_Air_Velocity_Curve_Name: Annotated[str, Field()]
    """Leaving dry-bulb of process air as a function of air velocity,"""

    Leaving_Humidity_Ratio_Function_of_Entering_DryBulb_and_Humidity_Ratio_Curve_Name: Annotated[str, Field()]
    """Leaving humidity ratio of process air as a function of entering dry-bulb"""

    Leaving_Humidity_Ratio_Function_of_Air_Velocity_Curve_Name: Annotated[str, Field()]
    """Leaving humidity ratio of process air as a function of"""

    Regeneration_Energy_Function_of_Entering_DryBulb_and_Humidity_Ratio_Curve_Name: Annotated[str, Field()]
    """Regeneration energy [J/kg of water removed] as a function of"""

    Regeneration_Energy_Function_of_Air_Velocity_Curve_Name: Annotated[str, Field()]
    """Regeneration energy [J/kg of water removed] as a function of"""

    Regeneration_Velocity_Function_of_Entering_DryBulb_and_Humidity_Ratio_Curve_Name: Annotated[str, Field()]
    """Regeneration velocity [m/s] as a function of"""

    Regeneration_Velocity_Function_of_Air_Velocity_Curve_Name: Annotated[str, Field()]
    """Regeneration velocity [m/s] as a function of"""

    Nominal_Regeneration_Temperature: Annotated[float, Field(ge=40, le=250)]
    """Nominal regen temperature upon which the regen energy modifier"""