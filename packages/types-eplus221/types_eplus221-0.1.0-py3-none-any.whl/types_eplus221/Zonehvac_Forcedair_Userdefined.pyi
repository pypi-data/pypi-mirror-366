from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Forcedair_Userdefined(EpBunch):
    """Defines a generic zone air unit for custom modeling"""

    Name: Annotated[str, Field(default=...)]
    """This is the name of the zone unit"""

    Overall_Model_Simulation_Program_Calling_Manager_Name: Annotated[str, Field()]

    Model_Setup_And_Sizing_Program_Calling_Manager_Name: Annotated[str, Field()]

    Primary_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Air inlet node for the unit must be a zone air exhaust Node."""

    Primary_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Air outlet node for the unit must be a zone air inlet node."""

    Secondary_Air_Inlet_Node_Name: Annotated[str, Field()]
    """Inlet air used for heat rejection or air source"""

    Secondary_Air_Outlet_Node_Name: Annotated[str, Field()]
    """Outlet air used for heat rejection or air source"""

    Number_Of_Plant_Loop_Connections: Annotated[int, Field(default=..., ge=0, le=3)]

    Plant_Connection_1_Inlet_Node_Name: Annotated[str, Field()]

    Plant_Connection_1_Outlet_Node_Name: Annotated[str, Field()]

    Plant_Connection_2_Inlet_Node_Name: Annotated[str, Field()]

    Plant_Connection_2_Outlet_Node_Name: Annotated[str, Field()]

    Plant_Connection_3_Inlet_Node_Name: Annotated[str, Field()]

    Plant_Connection_3_Outlet_Node_Name: Annotated[str, Field()]

    Supply_Inlet_Water_Storage_Tank_Name: Annotated[str, Field()]
    """Water use storage tank for alternate source of water consumed by device"""

    Collection_Outlet_Water_Storage_Tank_Name: Annotated[str, Field()]
    """Water use storage tank for collection of condensate by device"""

    Ambient_Zone_Name: Annotated[str, Field()]
    """Used for modeling device losses to surrounding zone"""