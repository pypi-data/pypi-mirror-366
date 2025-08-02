from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Condenser_Watercooled(EpBunch):
    """Water cooled condenser for a refrigeration system (Refrigeration:System)."""

    Name: Annotated[str, Field(default=...)]

    Rated_Effective_Total_Heat_Rejection_Rate: Annotated[float, Field(gt=0.0)]
    """Rating as per ARI 450"""

    Rated_Condensing_Temperature: Annotated[float, Field(default=..., gt=0.0)]
    """must correspond to rating given for total heat rejection effect"""

    Rated_Subcooling_Temperature_Difference: Annotated[float, Field(ge=0.0, default=0.0)]
    """must correspond to rating given for total heat rejection effect"""

    Rated_Water_Inlet_Temperature: Annotated[float, Field(default=..., gt=0.0)]
    """must correspond to rating given for total heat rejection effect"""

    Water_Inlet_Node_Name: Annotated[str, Field()]

    Water_Outlet_Node_Name: Annotated[str, Field()]

    Water_Cooled_Loop_Flow_Type: Annotated[Literal['VariableFlow', 'ConstantFlow'], Field(default='VariableFlow')]

    Water_Outlet_Temperature_Schedule_Name: Annotated[str, Field()]
    """Applicable only when loop flow type is Variable Flow."""

    Water_Design_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """note required units must be converted from L/s as specified in ARI 450-2007"""

    Water_Maximum_Flow_Rate: Annotated[float, Field(gt=0.0)]

    Water_Maximum_Water_Outlet_Temperature: Annotated[float, Field(ge=10.0, le=60.0, default=55.0)]

    Water_Minimum_Water_Inlet_Temperature: Annotated[float, Field(ge=10.0, le=30.0, default=10.0)]
    """related to the minimum allowed refrigeration system condensing temperature"""

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Condenser_Refrigerant_Operating_Charge_Inventory: Annotated[float, Field()]
    """optional input"""

    Condensate_Receiver_Refrigerant_Inventory: Annotated[float, Field()]
    """optional input"""

    Condensate_Piping_Refrigerant_Inventory: Annotated[float, Field()]
    """optional input"""