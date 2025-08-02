from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Connectorlist(EpBunch):
    """only two connectors allowed per loop"""

    Name: Annotated[str, Field(default=...)]

    Connector_1_Object_Type: Annotated[Literal['Connector:Splitter', 'Connector:Mixer'], Field(default=...)]

    Connector_1_Name: Annotated[str, Field(default=...)]

    Connector_2_Object_Type: Annotated[Literal['Connector:Splitter', 'Connector:Mixer'], Field()]

    Connector_2_Name: Annotated[str, Field()]