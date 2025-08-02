from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Distribution_Node(EpBunch):
    """This object represents an air distribution node in the AirflowNetwork model."""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    Component_Name_or_Node_Name: Annotated[str, Field()]
    """Designates node names defined in another object. The node name may occur in air branches."""

    Component_Object_Type_or_Node_Type: Annotated[Literal['AirLoopHVAC:ZoneMixer', 'AirLoopHVAC:ZoneSplitter', 'AirLoopHVAC:OutdoorAirSystem', 'OAMixerOutdoorAirStreamNode', 'OutdoorAir:NodeList', 'OutdoorAir:Node', 'Other'], Field(default='Other')]
    """Designates Node type for the Node or Component Name defined in the field above."""

    Node_Height: Annotated[float, Field(default=0.0)]
    """Enter the reference height used to calculate the relative pressure."""