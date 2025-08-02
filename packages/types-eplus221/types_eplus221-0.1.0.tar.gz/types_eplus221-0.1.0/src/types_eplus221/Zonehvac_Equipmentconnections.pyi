from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Equipmentconnections(EpBunch):
    """Specifies the HVAC equipment connections for a zone. Node names are specified for the"""

    Zone_Name: Annotated[str, Field(default=...)]

    Zone_Conditioning_Equipment_List_Name: Annotated[str, Field(default=...)]
    """Enter the name of a ZoneHVAC:EquipmentList object."""

    Zone_Air_Inlet_Node_Or_Nodelist_Name: Annotated[str, Field()]

    Zone_Air_Exhaust_Node_Or_Nodelist_Name: Annotated[str, Field()]

    Zone_Air_Node_Name: Annotated[str, Field(default=...)]

    Zone_Return_Air_Node_Or_Nodelist_Name: Annotated[str, Field()]

    Zone_Return_Air_Node_1_Flow_Rate_Fraction_Schedule_Name: Annotated[str, Field()]
    """This schedule is multiplied times the base return air flow rate."""

    Zone_Return_Air_Node_1_Flow_Rate_Basis_Node_Or_Nodelist_Name: Annotated[str, Field()]
    """The optional basis node(s) used to calculate the base return air flow"""