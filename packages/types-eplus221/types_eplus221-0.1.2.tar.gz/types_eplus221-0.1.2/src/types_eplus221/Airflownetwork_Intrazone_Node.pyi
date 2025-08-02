from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Intrazone_Node(EpBunch):
    """This object represents a node in a zone in the combination of RoomAir and"""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    RoomAirNodeAirflowNetwork_Name: Annotated[str, Field(default=...)]
    """Enter the name of a RoomAir:Node object defined in a RoomAirSettings:AirflowNetwork"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Enter the name of a zone object defined in a AirflowNetwork:MultiZone:Zone"""

    Node_Height: Annotated[float, Field(default=0.0)]
    """Enter the reference height used to calculate the relative pressure"""