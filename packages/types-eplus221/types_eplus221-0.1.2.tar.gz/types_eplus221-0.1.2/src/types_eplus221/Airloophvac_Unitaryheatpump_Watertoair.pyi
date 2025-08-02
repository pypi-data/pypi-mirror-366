from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac_Unitaryheatpump_Watertoair(EpBunch):
    """Unitary heat pump system, heating and cooling, single-speed with constant volume"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """This value should be > 0 and <= than the fan air flow rate."""

    Controlling_Zone_or_Thermostat_Location: Annotated[str, Field(default=...)]

    Supply_Air_Fan_Object_Type: Annotated[Literal['Fan:OnOff'], Field(default=...)]
    """Only works with On/Off Fan"""

    Supply_Air_Fan_Name: Annotated[str, Field(default=...)]
    """Needs to match Fan:OnOff object"""

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:WaterToAirHeatPump:ParameterEstimation', 'Coil:Heating:WaterToAirHeatPump:EquationFit', 'Coil:Heating:WaterToAirHeatPump:VariableSpeedEquationFit'], Field(default=...)]

    Heating_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the water-to-air heat pump heating coil object"""

    Heating_Convergence: Annotated[float, Field(gt=0.0, default=0.001)]

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:WaterToAirHeatPump:ParameterEstimation', 'Coil:Cooling:WaterToAirHeatPump:EquationFit', 'Coil:Cooling:WaterToAirHeatPump:VariableSpeedEquationFit'], Field(default=...)]

    Cooling_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the water-to-air heat pump cooling coil object"""

    Cooling_Convergence: Annotated[float, Field(gt=0.0, default=0.001)]

    Maximum_Cycling_Rate: Annotated[float, Field(ge=0.0, le=5.0, default=2.5)]
    """The maximum on-off cycling rate for the compressor"""

    Heat_Pump_Time_Constant: Annotated[float, Field(ge=0.0, le=500.0, default=60.0)]
    """Time constant for the cooling coil's capacity to reach steady state after startup"""

    Fraction_of_OnCycle_Power_Use: Annotated[str, Field(default='0.01')]
    """The fraction of on-cycle power use to adjust the part load fraction based on"""

    Heat_Pump_Fan_Delay_Time: Annotated[str, Field(default='60')]
    """Programmed time delay for heat pump fan to shut off after compressor cycle off."""

    Supplemental_Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Fuel', 'Coil:Heating:Electric', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field(default=...)]
    """works with gas, electric, hot water and steam heating coils"""

    Supplemental_Heating_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the supplemental heating coil object"""

    Maximum_Supply_Air_Temperature_from_Supplemental_Heater: Annotated[float, Field(default=...)]

    Maximum_Outdoor_DryBulb_Temperature_for_Supplemental_Heater_Operation: Annotated[float, Field(le=21.0, default=21.0)]

    Outdoor_DryBulb_Temperature_Sensor_Node_Name: Annotated[str, Field()]

    Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='BlowThrough')]

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Enter the name of a schedule that controls fan operation. Schedule values of 0 denote"""

    Dehumidification_Control_Type: Annotated[Literal['None', 'CoolReheat'], Field()]
    """None = meet sensible load only"""

    Heat_Pump_Coil_Water_Flow_Mode: Annotated[Literal['Constant', 'Cycling', 'ConstantOnDemand'], Field(default='Cycling')]
    """used only when the heat pump coils are of the type WaterToAirHeatPump:EquationFit"""