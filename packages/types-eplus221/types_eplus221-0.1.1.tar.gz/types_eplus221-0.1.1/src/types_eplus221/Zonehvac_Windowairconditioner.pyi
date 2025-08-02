from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Windowairconditioner(EpBunch):
    """Window air conditioner. Forced-convection cooling-only unit with supply fan, direct"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Maximum_Supply_Air_Flow_Rate: Annotated[float, Field(default=...)]

    Maximum_Outdoor_Air_Flow_Rate: Annotated[float, Field(default=...)]

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Outdoor_Air_Mixer_Object_Type: Annotated[Literal['OutdoorAir:Mixer'], Field(default=...)]
    """currently only one OutdoorAir:Mixer object type is available."""

    Outdoor_Air_Mixer_Name: Annotated[str, Field(default=...)]

    Supply_Air_Fan_Object_Type: Annotated[Literal['Fan:SystemModel', 'Fan:OnOff', 'Fan:ConstantVolume'], Field(default=...)]
    """Fan:ConstantVolume only works when continuous fan operation is used the entire"""

    Supply_Air_Fan_Name: Annotated[str, Field(default=...)]
    """Fan type Fan:ConstantVolume is used with continuous fan"""

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:DX:SingleSpeed', 'CoilSystem:Cooling:DX:HeatExchangerAssisted', 'Coil:Cooling:DX:VariableSpeed'], Field(default=...)]

    Dx_Cooling_Coil_Name: Annotated[str, Field(default=...)]

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Enter the name of a schedule that controls fan operation. Schedule Name values of 0 denote"""

    Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default=...)]

    Cooling_Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""

    Design_Specification_Zonehvac_Sizing_Object_Name: Annotated[str, Field()]
    """Enter the name of a DesignSpecificationZoneHVACSizing object."""