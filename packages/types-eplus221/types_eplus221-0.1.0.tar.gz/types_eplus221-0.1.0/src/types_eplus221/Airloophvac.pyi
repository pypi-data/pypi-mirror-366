from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airloophvac(EpBunch):
    """Defines a central forced air system."""

    Name: Annotated[str, Field(default=...)]

    Controller_List_Name: Annotated[str, Field()]
    """Enter the name of an AirLoopHVAC:ControllerList object."""

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""

    Design_Supply_Air_Flow_Rate: Annotated[str, Field(default='0')]

    Branch_List_Name: Annotated[str, Field(default=...)]
    """Name of a BranchList containing all the branches in this air loop"""

    Connector_List_Name: Annotated[str, Field()]
    """Name of a ConnectorList containing all the splitters and mixers in the loop"""

    Supply_Side_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Name of inlet node where air enters the supply side of the air loop."""

    Demand_Side_Outlet_Node_Name: Annotated[str, Field()]
    """Name of outlet node where return air leaves the demand side and enters the supply side."""

    Demand_Side_Inlet_Node_Names: Annotated[str, Field(default=...)]
    """Name of a Node or NodeList containing the inlet node(s) supplying air to zone equipment."""

    Supply_Side_Outlet_Node_Names: Annotated[str, Field(default=...)]
    """Name of a Node or NodeList containing the outlet node(s) supplying air to the demand side."""

    Design_Return_Air_Flow_Fraction_Of_Supply_Air_Flow: Annotated[str, Field(default='1.0')]
    """The design return air flow rate as a fraction of supply air flow rate with no exhaust."""