from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Airterminal_Singleduct_Mixer(EpBunch):
    """The mixer air terminal unit provides a means of supplying central system"""

    Name: Annotated[str, Field(default=...)]

    Zonehvac_Unit_Object_Type: Annotated[Literal['ZoneHVAC:FourPipeFanCoil', 'ZoneHVAC:WaterToAirHeatPump', 'ZoneHVAC:PackagedTerminalAirConditioner', 'ZoneHVAC:PackagedTerminalHeatPump', 'ZoneHVAC:TerminalUnit:VariableRefrigerantFlow', 'ZoneHVAC:UnitVentilator', 'AirLoopHVAC:UnitarySystem'], Field(default=...)]
    """The type of ZoneHVAC equipment to which this terminal mixer will be connected."""

    Zonehvac_Unit_Object_Name: Annotated[str, Field(default=...)]
    """The name of ZoneHVAC equipment to which this terminal mixer will be connected."""

    Mixer_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """This is the outlet air node name of the mixer. This will be the inlet air node name"""

    Mixer_Primary_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """The primary air (treated outdoor air) inlet node name of the mixer. This will be an"""

    Mixer_Secondary_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """The secondary air (recirculating air) inlet node name of the mixer. This will be"""

    Mixer_Connection_Type: Annotated[Literal['InletSide', 'SupplySide'], Field(default=...)]
    """This input field allows user to specify the mixer connection type. Valid choices"""

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """When the name of a DesignSpecification:OutdoorAir object is entered, the terminal"""

    Per_Person_Ventilation_Rate_Mode: Annotated[Literal['CurrentOccupancy', 'DesignOccupancy'], Field(default='CurrentOccupancy')]
    """CurrentOccupancy models demand controlled ventilation using the current number of people"""