from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Wateruse_Connections(EpBunch):
    """A subsystem that groups together multiple WaterUse:Equipment components."""

    Name: Annotated[str, Field(default=...)]

    Inlet_Node_Name: Annotated[str, Field()]

    Outlet_Node_Name: Annotated[str, Field()]

    Supply_Water_Storage_Tank_Name: Annotated[str, Field()]
    """If blank, or tank is empty, defaults to fresh water from the mains"""

    Reclamation_Water_Storage_Tank_Name: Annotated[str, Field()]

    Hot_Water_Supply_Temperature_Schedule_Name: Annotated[str, Field()]
    """Defaults to cold water supply temperature"""

    Cold_Water_Supply_Temperature_Schedule_Name: Annotated[str, Field()]
    """Defaults to water temperatures calculated by Site:WaterMainsTemperature object"""

    Drain_Water_Heat_Exchanger_Type: Annotated[Literal['None', 'Ideal', 'CounterFlow', 'CrossFlow'], Field()]

    Drain_Water_Heat_Exchanger_Destination: Annotated[Literal['Plant', 'Equipment', 'PlantAndEquipment'], Field(default='Plant')]

    Drain_Water_Heat_Exchanger_UFactor_Times_Area: Annotated[float, Field(ge=0.0)]

    Water_Use_Equipment_1_Name: Annotated[str, Field(default=...)]
    """Enter the name of a WaterUse:Equipment object."""

    Water_Use_Equipment_2_Name: Annotated[str, Field()]
    """Enter the name of a WaterUse:Equipment object."""

    Water_Use_Equipment_3_Name: Annotated[str, Field()]
    """Enter the name of a WaterUse:Equipment object."""

    Water_Use_Equipment_4_Name: Annotated[str, Field()]
    """Enter the name of a WaterUse:Equipment object."""

    Water_Use_Equipment_5_Name: Annotated[str, Field()]
    """Enter the name of a WaterUse:Equipment object."""

    Water_Use_Equipment_6_Name: Annotated[str, Field()]

    Water_Use_Equipment_7_Name: Annotated[str, Field()]

    Water_Use_Equipment_8_Name: Annotated[str, Field()]

    Water_Use_Equipment_9_Name: Annotated[str, Field()]

    Water_Use_Equipment_10_Name: Annotated[str, Field()]