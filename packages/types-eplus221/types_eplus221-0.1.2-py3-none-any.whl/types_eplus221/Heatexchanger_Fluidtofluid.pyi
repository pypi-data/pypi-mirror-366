from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Heatexchanger_Fluidtofluid(EpBunch):
    """A fluid/fluid heat exchanger designed to couple the supply side of one loop to the demand side of another loop"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Loop_Demand_Side_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """This connection is to the demand side of a loop and is the inlet to the heat exchanger"""

    Loop_Demand_Side_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """This connection is to the demand side of a loop"""

    Loop_Demand_Side_Design_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Loop_Supply_Side_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Loop_Supply_Side_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Loop_Supply_Side_Design_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Heat_Exchange_Model_Type: Annotated[Literal['CrossFlowBothUnMixed', 'CrossFlowBothMixed', 'CrossFlowSupplyMixedDemandUnMixed', 'CrossFlowSupplyUnMixedDemandMixed', 'ParallelFlow', 'CounterFlow', 'Ideal'], Field(default='Ideal')]

    Heat_Exchanger_UFactor_Times_Area_Value: Annotated[float, Field(default=..., gt=0.0)]

    Control_Type: Annotated[Literal['UncontrolledOn', 'OperationSchemeModulated', 'OperationSchemeOnOff', 'HeatingSetpointModulated', 'HeatingSetpointOnOff', 'CoolingSetpointModulated', 'CoolingSetpointOnOff', 'DualDeadbandSetpointModulated', 'DualDeadbandSetpointOnOff', 'CoolingDifferentialOnOff', 'CoolingSetpointOnOffWithComponentOverride'], Field(default='UncontrolledOn')]

    Heat_Exchanger_Setpoint_Node_Name: Annotated[str, Field()]
    """Setpoint node is needed with any Control Type that is "*Setpoint*""""

    Minimum_Temperature_Difference_to_Activate_Heat_Exchanger: Annotated[float, Field(ge=0.0, le=50, default=0.01)]
    """Tolerance between control temperatures used to determine if heat exchanger should run."""

    Heat_Transfer_Metering_End_Use_Type: Annotated[Literal['FreeCooling', 'HeatRecovery', 'HeatRejection', 'HeatRecoveryForCooling', 'HeatRecoveryForHeating', 'LoopToLoop'], Field(default='LoopToLoop')]
    """This field controls end use reporting for heat transfer meters"""

    Component_Override_Loop_Supply_Side_Inlet_Node_Name: Annotated[str, Field()]
    """This field is only used if Control Type is set to CoolingSetpointOnOffWithComponentOverride"""

    Component_Override_Loop_Demand_Side_Inlet_Node_Name: Annotated[str, Field()]
    """This field is only used if Control Type is set to CoolingSetpointOnOffWithComponentOverride"""

    Component_Override_Cooling_Control_Temperature_Mode: Annotated[Literal['WetBulbTemperature', 'DryBulbTemperature', 'Loop'], Field(default='Loop')]
    """This field is only used if Control Type is set to CoolingSetpointOnOffWithComponentOverride"""

    Sizing_Factor: Annotated[float, Field(gt=0.0, default=1.0)]
    """Multiplies the autosized flow rates for this device"""

    Operation_Minimum_Temperature_Limit: Annotated[float, Field()]
    """Lower limit on inlet temperatures, heat exchanger will not operate if either inlet is below this limit"""

    Operation_Maximum_Temperature_Limit: Annotated[float, Field()]
    """Upper limit on inlet temperatures, heat exchanger will not operate if either inlet is above this limit"""