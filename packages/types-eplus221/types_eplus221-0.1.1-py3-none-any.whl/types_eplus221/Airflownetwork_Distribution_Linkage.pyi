from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airflownetwork_Distribution_Linkage(EpBunch):
    """This object defines the connection between two nodes and a component."""

    Name: Annotated[str, Field(default=...)]
    """Enter a unique name for this object."""

    Node_1_Name: Annotated[str, Field(default=...)]
    """Enter the name of zone or AirflowNetwork Node."""

    Node_2_Name: Annotated[str, Field(default=...)]
    """Enter the name of zone or AirflowNetwork Node."""

    Component_Name: Annotated[str, Field(default=...)]
    """Enter the name of an AirflowNetwork component. A component is one of the"""

    Thermal_Zone_Name: Annotated[str, Field()]
    """Only used if component = AirflowNetwork:Distribution:Component:Duct"""