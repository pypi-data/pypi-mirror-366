from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Airdistributionunit(EpBunch):
    """Central air system air distribution unit, serves as a wrapper for a specific type of"""

    Name: Annotated[str, Field(default=...)]

    Air_Distribution_Unit_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Terminal_Object_Type: Annotated[Literal['AirTerminal:DualDuct:ConstantVolume', 'AirTerminal:DualDuct:VAV', 'AirTerminal:SingleDuct:ConstantVolume:Reheat', 'AirTerminal:SingleDuct:ConstantVolume:NoReheat', 'AirTerminal:SingleDuct:ConstantVolume:FourPipeBeam', 'AirTerminal:SingleDuct:VAV:Reheat', 'AirTerminal:SingleDuct:VAV:NoReheat', 'AirTerminal:SingleDuct:SeriesPIU:Reheat', 'AirTerminal:SingleDuct:ParallelPIU:Reheat', 'AirTerminal:SingleDuct:ConstantVolume:FourPipeInduction', 'AirTerminal:SingleDuct:VAV:Reheat:VariableSpeedFan', 'AirTerminal:SingleDuct:VAV:HeatAndCool:Reheat', 'AirTerminal:SingleDuct:VAV:HeatAndCool:NoReheat', 'AirTerminal:SingleDuct:ConstantVolume:CooledBeam', 'AirTerminal:DualDuct:VAV:OutdoorAir', 'AirTerminal:SingleDuct:UserDefined', 'AirTerminal:SingleDuct:Mixer'], Field(default=...)]

    Air_Terminal_Name: Annotated[str, Field(default=...)]

    Nominal_Upstream_Leakage_Fraction: Annotated[float, Field(ge=0, le=0.3, default=0)]
    """fraction at system design Flow; leakage Flow constant, leakage fraction"""

    Constant_Downstream_Leakage_Fraction: Annotated[float, Field(ge=0, le=0.3, default=0)]

    Design_Specification_Air_Terminal_Sizing_Object_Name: Annotated[str, Field()]
    """This optional field is the name of a DesignSpecification:AirTerminal:Sizing object"""