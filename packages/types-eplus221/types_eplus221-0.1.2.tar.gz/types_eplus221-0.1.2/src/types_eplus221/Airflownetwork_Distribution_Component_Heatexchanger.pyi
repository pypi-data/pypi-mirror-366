from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Distribution_Component_Heatexchanger(EpBunch):
    """This object defines the name of an air-to-air heat exchanger used in an air loop."""

    HeatExchanger_Name: Annotated[str, Field(default=...)]
    """Enter the name of an air-to-air heat exchanger in the primary Air loop."""

    HeatExchanger_Object_Type: Annotated[Literal['HeatExchanger:AirToAir:FlatPlate', 'HeatExchanger:AirToAir:SensibleAndLatent', 'HeatExchanger:Desiccant:BalancedFlow'], Field(default=...)]
    """Select the type of heat exchanger corresponding to the name entered in the field above."""

    Air_Path_Length: Annotated[float, Field(default=..., gt=0)]
    """Enter the air path length (depth) for the heat exchanger."""

    Air_Path_Hydraulic_Diameter: Annotated[float, Field(default=..., gt=0)]
    """Enter the hydraulic diameter of this heat exchanger. The hydraulic diameter is"""