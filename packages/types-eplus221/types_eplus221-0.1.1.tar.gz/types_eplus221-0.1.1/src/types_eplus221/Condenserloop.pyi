from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Condenserloop(EpBunch):
    """Defines a central plant condenser loop. CondenserLoop and PlantLoop are nearly"""

    Name: Annotated[str, Field(default=...)]

    Fluid_Type: Annotated[Literal['Water', 'UserDefinedFluidType'], Field(default='Water')]

    User_Defined_Fluid_Type: Annotated[str, Field()]
    """This field is only required when Fluid Type is UserDefinedFluidType"""

    Condenser_Equipment_Operation_Scheme_Name: Annotated[str, Field(default=...)]

    Condenser_Loop_Temperature_Setpoint_Node_Name: Annotated[str, Field(default=...)]

    Maximum_Loop_Temperature: Annotated[str, Field(default=...)]

    Minimum_Loop_Temperature: Annotated[str, Field(default=...)]

    Maximum_Loop_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Minimum_Loop_Flow_Rate: Annotated[float, Field(default=0.0)]

    Condenser_Loop_Volume: Annotated[float, Field(ge=0.0, default=Autocalculate)]

    Condenser_Side_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Side_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Side_Branch_List_Name: Annotated[str, Field(default=...)]

    Condenser_Side_Connector_List_Name: Annotated[str, Field(default=...)]

    Demand_Side_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Demand_Side_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Condenser_Demand_Side_Branch_List_Name: Annotated[str, Field(default=...)]

    Condenser_Demand_Side_Connector_List_Name: Annotated[str, Field(default=...)]

    Load_Distribution_Scheme: Annotated[Literal['Optimal', 'SequentialLoad', 'UniformLoad', 'UniformPLR', 'SequentialUniformPLR'], Field(default='SequentialLoad')]

    Pressure_Simulation_Type: Annotated[Literal['PumpPowerCorrection', 'LoopFlowCorrection', 'None'], Field()]

    Loop_Circulation_Time: Annotated[float, Field(ge=0.0, default=2.0)]
    """This field is only used to autocalulate the Condenser Loop Volume."""