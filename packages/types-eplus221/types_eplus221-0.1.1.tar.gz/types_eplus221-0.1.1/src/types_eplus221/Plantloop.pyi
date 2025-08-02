from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Plantloop(EpBunch):
    """Defines a central plant loop."""

    Name: Annotated[str, Field(default=...)]

    Fluid_Type: Annotated[Literal['Water', 'Steam', 'UserDefinedFluidType'], Field(default='Water')]

    User_Defined_Fluid_Type: Annotated[str, Field()]
    """This field is only required when Fluid Type is UserDefinedFluidType"""

    Plant_Equipment_Operation_Scheme_Name: Annotated[str, Field(default=...)]

    Loop_Temperature_Setpoint_Node_Name: Annotated[str, Field(default=...)]

    Maximum_Loop_Temperature: Annotated[str, Field(default=...)]

    Minimum_Loop_Temperature: Annotated[str, Field(default=...)]

    Maximum_Loop_Flow_Rate: Annotated[float, Field(default=..., ge=0)]

    Minimum_Loop_Flow_Rate: Annotated[float, Field(default=0.0)]

    Plant_Loop_Volume: Annotated[float, Field(ge=0.0, default=Autocalculate)]

    Plant_Side_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Plant_Side_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Plant_Side_Branch_List_Name: Annotated[str, Field(default=...)]

    Plant_Side_Connector_List_Name: Annotated[str, Field()]

    Demand_Side_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Demand_Side_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Demand_Side_Branch_List_Name: Annotated[str, Field(default=...)]

    Demand_Side_Connector_List_Name: Annotated[str, Field()]

    Load_Distribution_Scheme: Annotated[Literal['Optimal', 'SequentialLoad', 'UniformLoad', 'UniformPLR', 'SequentialUniformPLR'], Field(default='SequentialLoad')]

    Availability_Manager_List_Name: Annotated[str, Field()]

    Plant_Loop_Demand_Calculation_Scheme: Annotated[Literal['SingleSetpoint', 'DualSetpointDeadband'], Field(default='SingleSetpoint')]

    Common_Pipe_Simulation: Annotated[Literal['CommonPipe', 'TwoWayCommonPipe', 'None'], Field()]
    """Specifies a primary-secondary loop configuration. The plant side is the"""

    Pressure_Simulation_Type: Annotated[Literal['PumpPowerCorrection', 'LoopFlowCorrection', 'None'], Field()]

    Loop_Circulation_Time: Annotated[float, Field(ge=0.0, default=2.0)]
    """This field is only used to autocalulate the Plant Loop Volume."""