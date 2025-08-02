from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Condenser_Cascade(EpBunch):
    """Cascade condenser for a refrigeration system (Refrigeration:System). The cascade"""

    Name: Annotated[str, Field(default=...)]

    Rated_Condensing_Temperature: Annotated[float, Field(default=...)]
    """This is the condensing temperature for the lower temperature secondary loop"""

    Rated_Approach_Temperature_Difference: Annotated[float, Field(gt=0.0, default=3.0)]
    """This is the difference between the condensing and evaporating temperatures"""

    Rated_Effective_Total_Heat_Rejection_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """used for identification and rough system size error checking"""

    Condensing_Temperature_Control_Type: Annotated[Literal['Fixed', 'Float'], Field(default='Fixed')]
    """Fixed keeps condensing temperature constant"""

    Condenser_Refrigerant_Operating_Charge_Inventory: Annotated[float, Field()]
    """optional input"""

    Condensate_Receiver_Refrigerant_Inventory: Annotated[float, Field()]
    """optional input"""

    Condensate_Piping_Refrigerant_Inventory: Annotated[float, Field()]
    """optional input"""