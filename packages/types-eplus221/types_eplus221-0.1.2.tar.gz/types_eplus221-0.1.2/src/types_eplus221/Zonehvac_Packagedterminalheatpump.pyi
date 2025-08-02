from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Packagedterminalheatpump(EpBunch):
    """Packaged terminal heat pump (PTHP). Forced-convection heating-cooling unit with"""

    Name: Annotated[str, Field(default=...)]
    """Unique name for this packaged terminal heat pump object."""

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Air inlet node for the PTHP must be a zone air exhaust node."""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Air outlet node for the PTHP must be a zone air inlet node."""

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
    """Only used when heat pump Fan operating mode is continuous. This air flow rate"""

    Supply_Air_Fan_Object_Type: Annotated[Literal['Fan:SystemModel', 'Fan:OnOff', 'Fan:ConstantVolume'], Field(default=...)]
    """Fan:ConstantVolume only works with fan operating mode is continuous."""

    Supply_Air_Fan_Name: Annotated[str, Field(default=...)]
    """Needs to match a fan object."""

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:DX:SingleSpeed', 'Coil:Heating:DX:VariableSpeed'], Field(default=...)]
    """Only works with Coil:Heating:DX:SingleSpeed or"""

    Heating_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the DX Heating Coil object."""

    Heating_Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]
    """Defines Heating convergence tolerance as a fraction of Heating load to be met."""

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:DX:SingleSpeed', 'Coil:Cooling:DX:VariableSpeed', 'CoilSystem:Cooling:DX:HeatExchangerAssisted'], Field(default=...)]
    """Only works with Coil:Cooling:DX:SingleSpeed or"""

    Cooling_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the DX Cooling Coil object."""

    Cooling_Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]
    """Defines Cooling convergence tolerance as a fraction of the Cooling load to be met."""

    Supplemental_Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Fuel', 'Coil:Heating:Electric', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field(default=...)]
    """works with gas, electric, hot water and steam heating coil."""

    Supplemental_Heating_Coil_Name: Annotated[str, Field(default=...)]
    """Needs to match in the supplemental heating coil object."""

    Maximum_Supply_Air_Temperature_from_Supplemental_Heater: Annotated[float, Field(default=...)]
    """Supply air temperature from the supplemental heater will not exceed this value."""

    Maximum_Outdoor_DryBulb_Temperature_for_Supplemental_Heater_Operation: Annotated[float, Field(le=21.0, default=21.0)]
    """Supplemental heater will not operate when outdoor temperature exceeds this value."""

    Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='DrawThrough')]
    """Select fan placement as either blow through or draw through."""

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Enter the name of a schedule that controls fan operation. Schedule values of 0 denote"""

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""

    Design_Specification_ZoneHVAC_Sizing_Object_Name: Annotated[str, Field()]
    """Enter the name of a DesignSpecificationZoneHVACSizing object."""

    Capacity_Control_Method: Annotated[Literal['None', 'SingleZoneVAV'], Field()]

    Minimum_Supply_Air_Temperature_in_Cooling_Mode: Annotated[float, Field(ge=0.0, default=autosize)]
    """For Capacity Control Method = SingleZoneVAV, enter the minimum air temperature limit for reduced fan speed."""

    Maximum_Supply_Air_Temperature_in_Heating_Mode: Annotated[float, Field(ge=0.0, default=autosize)]
    """For Capacity Control Method = SingleZoneVAV, enter the maximum air temperature limit for reduced fan speed."""