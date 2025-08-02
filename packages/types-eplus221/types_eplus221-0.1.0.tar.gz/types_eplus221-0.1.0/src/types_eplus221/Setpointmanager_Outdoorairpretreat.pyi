from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Setpointmanager_Outdoorairpretreat(EpBunch):
    """This setpoint manager determines the required"""

    Name: Annotated[str, Field(default=...)]

    Control_Variable: Annotated[Literal['Temperature', 'HumidityRatio', 'MaximumHumidityRatio', 'MinimumHumidityRatio'], Field()]

    Minimum_Setpoint_Temperature: Annotated[str, Field(default='-99')]
    """Applicable only if Control variable is Temperature"""

    Maximum_Setpoint_Temperature: Annotated[str, Field(default='99')]
    """Applicable only if Control variable is Temperature"""

    Minimum_Setpoint_Humidity_Ratio: Annotated[str, Field(default='0.00001')]
    """Applicable only if Control variable is"""

    Maximum_Setpoint_Humidity_Ratio: Annotated[str, Field(default='1.0')]
    """Applicable only if Control variable is"""

    Reference_Setpoint_Node_Name: Annotated[str, Field()]
    """The current setpoint at this node is the"""

    Mixed_Air_Stream_Node_Name: Annotated[str, Field(default=...)]
    """Name of Mixed Air Node"""

    Outdoor_Air_Stream_Node_Name: Annotated[str, Field(default=...)]
    """Name of Outdoor Air Stream Node"""

    Return_Air_Stream_Node_Name: Annotated[str, Field(default=...)]
    """Name of Return Air Stream Node"""

    Setpoint_Node_Or_Nodelist_Name: Annotated[str, Field(default=...)]
    """Node(s) at which the temperature or humidity"""