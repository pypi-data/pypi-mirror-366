from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Plantcomponent_Userdefined(EpBunch):
    """Defines a generic plant component for custom modeling"""

    Name: Annotated[str, Field(default=...)]
    """This is the name of the plant component"""

    Main_Model_Program_Calling_Manager_Name: Annotated[str, Field()]

    Number_of_Plant_Loop_Connections: Annotated[int, Field(default=..., ge=1, le=4)]

    Plant_Connection_1_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Plant_Connection_1_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Plant_Connection_1_Loading_Mode: Annotated[Literal['DemandsLoad', 'MeetsLoadWithPassiveCapacity', 'MeetsLoadWithNominalCapacity', 'MeetsLoadWithNominalCapacityLowOutLimit', 'MeetsLoadWithNominalCapacityHiOutLimit'], Field(default=...)]

    Plant_Connection_1_Loop_Flow_Request_Mode: Annotated[Literal['NeedsFlowIfLoopOn', 'NeedsFlowAndTurnsLoopOn', 'ReceivesWhateverFlowAvailable'], Field(default=...)]

    Plant_Connection_1_Initialization_Program_Calling_Manager_Name: Annotated[str, Field()]

    Plant_Connection_1_Simulation_Program_Calling_Manager_Name: Annotated[str, Field()]

    Plant_Connection_2_Inlet_Node_Name: Annotated[str, Field()]

    Plant_Connection_2_Outlet_Node_Name: Annotated[str, Field()]

    Plant_Connection_2_Loading_Mode: Annotated[Literal['DemandsLoad', 'MeetLoadWithPassiveCapacity', 'MeetLoadWithNominalCapacity', 'MeetLoadWithNominalCapacityLowOutLimit', 'MeetLoadWithNominalCapacityHiOutLimit'], Field()]

    Plant_Connection_2_Loop_Flow_Request_Mode: Annotated[Literal['NeedsFlowIfLoopOn', 'NeedsFlowAndTurnsLoopOn', 'ReceivesWhateverFlowAvailable'], Field()]

    Plant_Connection_2_Initialization_Program_Calling_Manager_Name: Annotated[str, Field()]

    Plant_Connection_2_Simulation_Program_Calling_Manager_Name: Annotated[str, Field()]

    Plant_Connection_3_Inlet_Node_Name: Annotated[str, Field()]

    Plant_Connection_3_Outlet_Node_Name: Annotated[str, Field()]

    Plant_Connection_3_Loading_Mode: Annotated[Literal['DemandsLoad', 'MeetLoadWithPassiveCapacity', 'MeetLoadWithNominalCapacity', 'MeetLoadWithNominalCapacityLowOutLimit', 'MeetLoadWithNominalCapacityHiOutLimit'], Field()]

    Plant_Connection_3_Loop_Flow_Request_Mode: Annotated[Literal['NeedsFlowIfLoopOn', 'NeedsFlowAndTurnsLoopOn', 'ReceivesWhateverFlowAvailable'], Field()]

    Plant_Connection_3_Initialization_Program_Calling_Manager_Name: Annotated[str, Field()]

    Plant_Connection_3_Simulation_Program_Calling_Manager_Name: Annotated[str, Field()]

    Plant_Connection_4_Inlet_Node_Name: Annotated[str, Field()]

    Plant_Connection_4_Outlet_Node_Name: Annotated[str, Field()]

    Plant_Connection_4_Loading_Mode: Annotated[Literal['DemandsLoad', 'MeetLoadWithPassiveCapacity', 'MeetLoadWithNominalCapacity', 'MeetLoadWithNominalCapacityLowOutLimit', 'MeetLoadWithNominalCapacityHiOutLimit'], Field()]

    Plant_Connection_4_Loop_Flow_Request_Mode: Annotated[Literal['NeedsFlowIfLoopOn', 'NeedsFlowAndTurnsLoopOn', 'ReceivesWhateverFlowAvailable'], Field()]

    Plant_Connection_4_Initialization_Program_Calling_Manager_Name: Annotated[str, Field()]

    Plant_Connection_4_Simulation_Program_Calling_Manager_Name: Annotated[str, Field()]

    Air_Connection_Inlet_Node_Name: Annotated[str, Field()]
    """Inlet air used for heat rejection or air source"""

    Air_Connection_Outlet_Node_Name: Annotated[str, Field()]
    """Outlet air used for heat rejection or air source"""

    Supply_Inlet_Water_Storage_Tank_Name: Annotated[str, Field()]
    """Water use storage tank for alternate source of water consumed by device"""

    Collection_Outlet_Water_Storage_Tank_Name: Annotated[str, Field()]
    """Water use storage tank for collection of condensate by device"""

    Ambient_Zone_Name: Annotated[str, Field()]
    """Used for modeling device losses to surrounding zone"""