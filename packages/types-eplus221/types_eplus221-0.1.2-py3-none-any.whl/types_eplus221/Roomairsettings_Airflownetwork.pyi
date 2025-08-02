from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomairsettings_Airflownetwork(EpBunch):
    """RoomAir modeling using Airflow pressure network solver"""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]
    """Name of Zone being described. Any existing zone name"""

    Control_Point_RoomAirflowNetworkNode_Name: Annotated[str, Field()]

    RoomAirflowNetworkNode_Name_1: Annotated[str, Field()]

    RoomAirflowNetworkNode_Name_2: Annotated[str, Field()]

    RoomAirflowNetworkNode_Name_3: Annotated[str, Field()]

    RoomAirflowNetworkNode_Name_4: Annotated[str, Field()]

    RoomAirflowNetworkNode_Name_5: Annotated[str, Field()]

    RoomAirflowNetworkNode_Name_6: Annotated[str, Field()]