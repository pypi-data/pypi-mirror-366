from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Waterheating_Desuperheater(EpBunch):
    """Desuperheater air heating coil. The heating energy provided by this coil is reclaimed"""

    Name: Annotated[str, Field(default=...)]
    """Unique name for this instance of a desuperheater water heating coil."""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Setpoint_Temperature_Schedule_Name: Annotated[str, Field(default=...)]
    """Defines the cut-out temperature where the desuperheater water heating coil turns off."""

    Dead_Band_Temperature_Difference: Annotated[float, Field(gt=0, le=20, default=5)]
    """Setpoint temperature minus the dead band temperature difference defines"""

    Rated_Heat_Reclaim_Recovery_Efficiency: Annotated[float, Field(gt=0.0)]
    """Enter the fraction of waste heat reclaimed by the desuperheater water heating coil."""

    Rated_Inlet_Water_Temperature: Annotated[float, Field(default=...)]
    """The inlet water temperature corresponding to the rated heat reclaim recovery efficiency."""

    Rated_Outdoor_Air_Temperature: Annotated[float, Field(default=...)]
    """The outdoor air dry-bulb temperature corresponding to the"""

    Maximum_Inlet_Water_Temperature_For_Heat_Reclaim: Annotated[float, Field(default=...)]
    """The desuperheater water heating coil is off when the inlet water temperature is above"""

    Heat_Reclaim_Efficiency_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """A biquadratic curve defining the performance of the desuperheater heating coil."""

    Water_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """The node from which the desuperheater heating coil draws its inlet water."""

    Water_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """The node to which the desuperheater heating coil sends its outlet water."""

    Tank_Object_Type: Annotated[Literal['WaterHeater:Mixed', 'WaterHeater:Stratified'], Field(default='WaterHeater:Mixed')]
    """Specify the type of water heater tank used by this desuperheater water heating coil."""

    Tank_Name: Annotated[str, Field(default=...)]
    """The name of the water heater tank used by this desuperheater water heating coil."""

    Heating_Source_Object_Type: Annotated[Literal['Coil:Cooling:DX:SingleSpeed', 'Coil:Cooling:DX:TwoSpeed', 'Coil:Cooling:DX:TwoStageWithHumidityControlMode', 'Coil:Cooling:DX:VariableSpeed', 'Coil:Cooling:DX:MultiSpeed', 'Coil:Cooling:WaterToAirHeatPump:EquationFit', 'Refrigeration:CompressorRack', 'Refrigeration:Condenser:AirCooled', 'Refrigeration:Condenser:EvaporativeCooled', 'Refrigeration:Condenser:WaterCooled'], Field(default=...)]
    """The type of DX system that is providing waste heat for reclaim."""

    Heating_Source_Name: Annotated[str, Field(default=...)]
    """The name of the DX system used for heat reclaim."""

    Water_Flow_Rate: Annotated[float, Field(default=..., gt=0)]
    """The operating water flow rate."""

    Water_Pump_Power: Annotated[float, Field(ge=0.0, default=0.0)]
    """The water circulation pump electric power."""

    Fraction_Of_Pump_Heat_To_Water: Annotated[float, Field(ge=0, le=1, default=0.2)]
    """The fraction of pump heat transferred to the water. The pump is assumed to be downstream of"""

    On_Cycle_Parasitic_Electric_Load: Annotated[float, Field(ge=0, default=0)]
    """Parasitic electric power consumed when the desuperheater water heating coil operates."""

    Off_Cycle_Parasitic_Electric_Load: Annotated[float, Field(ge=0, default=0)]
    """Parasitic electric load consumed when the desuperheater water heating coil is off."""