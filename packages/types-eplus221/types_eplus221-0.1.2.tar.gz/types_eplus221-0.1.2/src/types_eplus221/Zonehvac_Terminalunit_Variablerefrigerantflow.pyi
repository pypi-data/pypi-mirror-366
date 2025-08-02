from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Terminalunit_Variablerefrigerantflow(EpBunch):
    """Zone terminal unit with variable refrigerant flow (VRF) DX cooling and heating coils"""

    Zone_Terminal_Unit_Name: Annotated[str, Field(default=...)]

    Terminal_Unit_Availability_Schedule: Annotated[str, Field()]
    """The unit is available the entire simulation if this field is left blank"""

    Terminal_Unit_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """the inlet node to the terminal unit"""

    Terminal_Unit_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """the outlet node of the terminal unit"""

    Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]

    No_Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]

    No_Heating_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]

    Cooling_Outdoor_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """This field is set to zero flow when the VRF terminal unit is connected to"""

    Heating_Outdoor_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """This field is set to zero flow when the VRF terminal unit is connected to"""

    No_Load_Outdoor_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """This field is set to zero flow when the VRF terminal unit is connected to"""

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field(default=...)]

    Supply_Air_Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='BlowThrough')]
    """Select fan placement as either blow through or draw through."""

    Supply_Air_Fan_Object_Type: Annotated[Literal['Fan:SystemModel', 'Fan:OnOff', 'Fan:ConstantVolume', 'Fan:VariableVolume'], Field(default='Fan:ConstantVolume')]
    """Supply Air Fan Object Type must be Fan:SystemModel, Fan:OnOff, or Fan:ConstantVolume"""

    Supply_Air_Fan_Object_Name: Annotated[str, Field(default=...)]

    Outside_Air_Mixer_Object_Type: Annotated[Literal['OutdoorAir:Mixer'], Field()]
    """Currently only one type OutdoorAir:Mixer object is available."""

    Outside_Air_Mixer_Object_Name: Annotated[str, Field()]
    """If this field is blank, the OutdoorAir:Mixer is not used."""

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:DX:VariableRefrigerantFlow', 'Coil:Cooling:DX:VariableRefrigerantFlow:FluidTemperatureControl'], Field()]
    """Cooling Coil Type must be Coil:Cooling:DX:VariableRefrigerantFlow"""

    Cooling_Coil_Object_Name: Annotated[str, Field()]
    """Cooling Coil Type must be Coil:Cooling:DX:VariableRefrigerantFlow"""

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:DX:VariableRefrigerantFlow', 'Coil:Heating:DX:VariableRefrigerantFlow:FluidTemperatureControl'], Field()]
    """Heating Coil Type must be Coil:Heating:DX:VariableRefrigerantFlow"""

    Heating_Coil_Object_Name: Annotated[str, Field()]
    """Heating Coil Type must be Coil:Heating:DX:VariableRefrigerantFlow"""

    Zone_Terminal_Unit_On_Parasitic_Electric_Energy_Use: Annotated[float, Field(ge=0, default=0)]

    Zone_Terminal_Unit_Off_Parasitic_Electric_Energy_Use: Annotated[float, Field(ge=0, default=0)]

    Rated_Heating_Capacity_Sizing_Ratio: Annotated[float, Field(ge=1.0, default=1.0)]
    """If this terminal unit's heating coil is autosized, the heating capacity is sized"""

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""

    Design_Specification_ZoneHVAC_Sizing_Object_Name: Annotated[str, Field()]
    """Enter the name of a DesignSpecificationZoneHVACSizing object."""

    Supplemental_Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Fuel', 'Coil:Heating:Electric', 'Coil:Heating:Water', 'Coil:Heating:Steam'], Field()]
    """works with gas, electric, hot water and steam heating coil."""

    Supplemental_Heating_Coil_Name: Annotated[str, Field()]
    """Needs to match in the supplemental heating coil object."""

    Maximum_Supply_Air_Temperature_from_Supplemental_Heater: Annotated[float, Field(default=autosize)]
    """Supply air temperature from the supplemental heater will not exceed this value."""

    Maximum_Outdoor_DryBulb_Temperature_for_Supplemental_Heater_Operation: Annotated[float, Field(le=21.0, default=21.0)]
    """Supplemental heater will not operate when outdoor temperature exceeds this value."""