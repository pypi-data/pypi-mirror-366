from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Solarcollector_Unglazedtranspired_Multisystem(EpBunch):
    """quad-tuples of inlet, outlet, control, and zone nodes"""

    Solar_Collector_Name: Annotated[str, Field(default=...)]
    """Enter the name of a SolarCollector:UnglazedTranspired object."""

    Outdoor_Air_System_1_Collector_Inlet_Node: Annotated[str, Field()]

    Outdoor_Air_System_1_Collector_Outlet_Node: Annotated[str, Field()]

    Outdoor_Air_System_1_Mixed_Air_Node: Annotated[str, Field()]

    Outdoor_Air_System_1_Zone_Node: Annotated[str, Field()]

    Outdoor_Air_System_2_Collector_Inlet_Node: Annotated[str, Field()]

    Outdoor_Air_System_2_Collector_Outlet_Node: Annotated[str, Field()]

    Outdoor_Air_System_2_Mixed_Air_Node: Annotated[str, Field()]

    Outdoor_Air_System_2_Zone_Node: Annotated[str, Field()]

    Outdoor_Air_System_3_Collector_Inlet_Node: Annotated[str, Field()]

    Outdoor_Air_System_3_Collector_Outlet_Node: Annotated[str, Field()]

    Outdoor_Air_System_3_Mixed_Air_Node: Annotated[str, Field()]

    Outdoor_Air_System_3_Zone_Node: Annotated[str, Field()]

    Outdoor_Air_System_4_Collector_Inlet_Node: Annotated[str, Field()]

    Outdoor_Air_System_4_Collector_Outlet_Node: Annotated[str, Field()]

    Outdoor_Air_System_4_Mixed_Air_Node: Annotated[str, Field()]

    Outdoor_Air_System_4_Zone_Node: Annotated[str, Field()]

    Outdoor_Air_System_5_Collector_Inlet_Node: Annotated[str, Field()]

    Outdoor_Air_System_5_Collector_Outlet_Node: Annotated[str, Field()]

    Outdoor_Air_System_5_Mixed_Air_Node: Annotated[str, Field()]

    Outdoor_Air_System_5_Zone_Node: Annotated[str, Field()]