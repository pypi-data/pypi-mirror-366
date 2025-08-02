from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Roomairmodeltype(EpBunch):
    """Selects the type of room air model to be used in a given zone. If no RoomAirModelType"""

    Name: Annotated[str, Field(default=...)]

    Zone_Name: Annotated[str, Field(default=...)]

    Room_Air_Modeling_Type: Annotated[Literal['Mixing', 'UserDefined', 'OneNodeDisplacementVentilation', 'ThreeNodeDisplacementVentilation', 'CrossVentilation', 'UnderFloorAirDistributionInterior', 'UnderFloorAirDistributionExterior', 'AirflowNetwork'], Field(default='Mixing')]
    """Mixing = Complete mixing air model"""

    Air_Temperature_Coupling_Strategy: Annotated[Literal['Direct', 'Indirect'], Field(default='Direct')]