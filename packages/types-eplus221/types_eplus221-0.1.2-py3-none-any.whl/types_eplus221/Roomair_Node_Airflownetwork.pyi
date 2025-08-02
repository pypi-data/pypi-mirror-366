from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomair_Node_Airflownetwork(EpBunch):
    """define an air node for some types of nodal air models"""

    Name: Annotated[str, Field()]

    Zone_Name: Annotated[str, Field(default=...)]

    Fraction_of_Zone_Air_Volume: Annotated[float, Field(ge=0.0, le=1.0)]

    RoomAirNodeAirflowNetworkAdjacentSurfaceList_Name: Annotated[str, Field()]

    RoomAirNodeAirflowNetworkInternalGains_Name: Annotated[str, Field()]

    RoomAirNodeAirflowNetworkHVACEquipment_Name: Annotated[str, Field()]