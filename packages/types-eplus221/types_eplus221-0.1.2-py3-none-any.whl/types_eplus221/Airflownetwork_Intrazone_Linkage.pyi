from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Intrazone_Linkage(EpBunch):
    """This object defines the connection between two nodes and a component used"""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    Node_1_Name: Annotated[str, Field(default=...)]
    """Enter the name of zone or AirflowNetwork Node."""

    Node_2_Name: Annotated[str, Field(default=...)]
    """Enter the name of zone or AirflowNetwork Node."""

    Component_Name: Annotated[str, Field()]
    """Enter the name of an AirflowNetwork component. A component is one of the"""

    AirflowNetworkMultiZoneSurface_Name: Annotated[str, Field()]
    """Only used when one of two nodes defined above are not located in the same zone, and"""