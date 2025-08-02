from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Gascooler_Aircooled(EpBunch):
    """The transcritical refrigeration system requires a single gas cooler to reject the"""

    Name: Annotated[str, Field(default=...)]

    Rated_Total_Heat_Rejection_Rate_Curve_Name: Annotated[str, Field(default=...)]
    """Be sure the rating corresponds to the correct refrigerant (R744)"""

    Gas_Cooler_Fan_Speed_Control_Type: Annotated[Literal['Fixed', 'FixedLinear', 'VariableSpeed', 'TwoSpeed'], Field(default='Fixed')]

    Rated_Fan_Power: Annotated[float, Field(ge=0.0, default=5000.0)]
    """Power for gas cooler fan(s) corresponding to rated total heat rejection effect."""

    Minimum_Fan_Air_Flow_Ratio: Annotated[float, Field(ge=0.0, default=0.2)]
    """Minimum air flow fraction through gas cooler fan"""

    Transition_Temperature: Annotated[float, Field(default=27.0)]
    """Temperature at which system transitions between subcritical and transcritical operation."""

    Transcritical_Approach_Temperature: Annotated[float, Field(default=3.0)]
    """Temperature difference between the CO2 exiting the gas cooler and the air entering the"""

    Subcritical_Temperature_Difference: Annotated[float, Field(default=10.0)]
    """Temperature difference between the saturated condensing temperature and the air"""

    Minimum_Condensing_Temperature: Annotated[float, Field(default=10.0)]
    """Minimum saturated condensing temperature during subcritical operation."""

    Air_Inlet_Node_Name: Annotated[str, Field()]
    """If field is left blank,"""

    End_Use_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Gas_Cooler_Refrigerant_Operating_Charge_Inventory: Annotated[float, Field(default=0.0)]
    """optional input"""

    Gas_Cooler_Receiver_Refrigerant_Inventory: Annotated[float, Field(default=0.0)]
    """optional input"""

    Gas_Cooler_Outlet_Piping_Refrigerant_Inventory: Annotated[float, Field(default=0.0)]
    """optional input"""