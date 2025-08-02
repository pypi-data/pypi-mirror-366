from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Packagedterminalairconditioner(EpBunch):
    """Packaged terminal air conditioner (PTAC). Forced-convection heating-cooling unit"""

    Name: Annotated[str, Field(default=...)]
    """Unique name for this packaged terminal air conditioner object."""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Air inlet node for the PTAC must be a zone air exhaust Node."""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Air outlet node for the PTAC must be a zone air inlet node."""

    Outdoor_Air_Mixer_Object_Type: Annotated[Literal['OutdoorAir:Mixer'], Field()]
    """Currently only one OutdoorAir:Mixer object type is available."""

    Outdoor_Air_Mixer_Name: Annotated[str, Field()]
    """If this field is blank, the OutdoorAir:Mixer is not used."""

    Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Must be less than or equal to fan size."""

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Must be less than or equal to fan size."""

    No_Load_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0)]
    """Must be less than or equal to fan size."""

    Cooling_Outdoor_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0)]
    """Must be less than or equal to supply air flow rate during cooling operation."""

    Heating_Outdoor_Air_Flow_Rate: Annotated[float, Field(default=..., ge=0)]
    """Must be less than or equal to supply air flow rate during heating operation."""

    No_Load_Outdoor_Air_Flow_Rate: Annotated[float, Field(ge=0)]
    """Only used when supply air fan operating mode schedule values specify continuous fan"""

    Supply_Air_Fan_Object_Type: Annotated[Literal['Fan:SystemModel', 'Fan:OnOff', 'Fan:ConstantVolume'], Field(default=...)]
    """Fan:ConstantVolume only works when continuous fan operation is used the entire"""

    Supply_Air_Fan_Name: Annotated[str, Field(default=...)]
    """Needs to match in the fan object."""

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Fuel', 'Coil:Heating:Electric', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field(default=...)]
    """Select the type of heating coil."""

    Heating_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the heating coil object."""

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:DX:SingleSpeed', 'Coil:Cooling:DX:VariableSpeed', 'CoilSystem:Cooling:DX:HeatExchangerAssisted'], Field(default=...)]
    """Select the type of Cooling Coil."""

    Cooling_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match a DX cooling coil object."""

    Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='DrawThrough')]
    """Select fan placement as either blow through or draw through."""

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Enter the name of a schedule that controls fan operation. Schedule Name values of 0 denote"""

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""

    Design_Specification_ZoneHVAC_Sizing_Object_Name: Annotated[str, Field()]
    """Enter the name of a DesignSpecificationZoneHVACSizing object."""

    Capacity_Control_Method: Annotated[Literal['None', 'SingleZoneVAV'], Field()]

    Minimum_Supply_Air_Temperature_in_Cooling_Mode: Annotated[float, Field(ge=0.0, default=autosize)]
    """For Capacity Control Method = SingleZoneVAV, enter the minimum air temperature limit for reduced fan speed."""

    Maximum_Supply_Air_Temperature_in_Heating_Mode: Annotated[float, Field(ge=0.0, default=autosize)]
    """For Capacity Control Method = SingleZoneVAV, enter the maximum air temperature limit for reduced fan speed."""