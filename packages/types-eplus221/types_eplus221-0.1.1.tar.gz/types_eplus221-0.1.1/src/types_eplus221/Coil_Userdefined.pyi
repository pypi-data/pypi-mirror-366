from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Userdefined(EpBunch):
    """Defines a generic air system component for custom modeling"""

    Name: Annotated[str, Field(default=...)]
    """This is the name of the coil"""

    Overall_Model_Simulation_Program_Calling_Manager_Name: Annotated[str, Field()]

    Model_Setup_And_Sizing_Program_Calling_Manager_Name: Annotated[str, Field(default=...)]

    Number_Of_Air_Connections: Annotated[int, Field(default=..., ge=1, le=2)]

    Air_Connection_1_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Inlet air for primary air stream"""

    Air_Connection_1_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Outlet air for primary air stream"""

    Air_Connection_2_Inlet_Node_Name: Annotated[str, Field()]
    """Inlet air for secondary air stream"""

    Air_Connection_2_Outlet_Node_Name: Annotated[str, Field()]
    """Outlet air for secondary air stream"""

    Plant_Connection_Is_Used: Annotated[Literal['Yes', 'No'], Field()]

    Plant_Connection_Inlet_Node_Name: Annotated[str, Field()]

    Plant_Connection_Outlet_Node_Name: Annotated[str, Field()]

    Supply_Inlet_Water_Storage_Tank_Name: Annotated[str, Field()]
    """Water use storage tank for alternate source of water consumed by device"""

    Collection_Outlet_Water_Storage_Tank_Name: Annotated[str, Field()]
    """Water use storage tank for collection of condensate by device"""

    Ambient_Zone_Name: Annotated[str, Field()]
    """Used for modeling device losses to surrounding zone"""