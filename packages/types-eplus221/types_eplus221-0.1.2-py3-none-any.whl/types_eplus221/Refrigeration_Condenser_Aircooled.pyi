from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Condenser_Aircooled(EpBunch):
    """Air cooled condenser for a refrigeration system (Refrigeration:System)."""

    Name: Annotated[str, Field(default=...)]

    Rated_Effective_Total_Heat_Rejection_Rate_Curve_Name: Annotated[str, Field()]
    """Rating as per ARI 460"""

    Rated_Subcooling_Temperature_Difference: Annotated[float, Field(ge=0.0, default=0.0)]
    """must correspond to rating given for total heat rejection effect"""

    Condenser_Fan_Speed_Control_Type: Annotated[Literal['Fixed', 'FixedLinear', 'VariableSpeed', 'TwoSpeed'], Field(default='Fixed')]

    Rated_Fan_Power: Annotated[float, Field(ge=0.0, default=250.0)]
    """Power for condenser fan(s) corresponding to rated total heat rejection effect."""

    Minimum_Fan_Air_Flow_Ratio: Annotated[float, Field(ge=0.0, default=0.2)]
    """Minimum air flow fraction through condenser fan"""

    Air_Inlet_Node_Name_or_Zone_Name: Annotated[str, Field()]
    """If field is left blank,"""

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Condenser_Refrigerant_Operating_Charge_Inventory: Annotated[float, Field(default=0.0)]
    """optional input"""

    Condensate_Receiver_Refrigerant_Inventory: Annotated[float, Field(default=0.0)]
    """optional input"""

    Condensate_Piping_Refrigerant_Inventory: Annotated[float, Field(default=0.0)]
    """optional input"""