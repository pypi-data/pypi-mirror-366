from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Condenserenteringreset_Ideal(EpBunch):
    """This setpoint manager determine the ideal optimum condenser entering water temperature"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature'], Field(default='Temperature')]

    Minimum_Lift: Annotated[float, Field(default=11.1)]

    Maximum_Condenser_Entering_Water_Temperature: Annotated[float, Field(default=32)]

    Setpoint_Node_or_NodeList_Name: Annotated[str, Field(default=...)]
    """Node(s) at which control variable will be set"""