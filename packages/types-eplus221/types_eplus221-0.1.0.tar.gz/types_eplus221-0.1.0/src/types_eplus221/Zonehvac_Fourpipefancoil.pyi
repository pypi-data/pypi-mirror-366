from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Fourpipefancoil(EpBunch):
    """Four pipe fan coil system. Forced-convection hydronic heating-cooling unit with"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Capacity_Control_Method: Annotated[Literal['ConstantFanVariableFlow', 'CyclingFan', 'VariableFanVariableFlow', 'VariableFanConstantFlow', 'MultiSpeedFan', 'ASHRAE90VariableFan'], Field(default=...)]

    Maximum_Supply_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Low_Speed_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0.0, default=0.33)]

    Medium_Speed_Supply_Air_Flow_Ratio: Annotated[float, Field(gt=0.0, default=0.66)]
    """Medium Speed Supply Air Flow Ratio should be greater"""

    Maximum_Outdoor_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Outdoor_Air_Schedule_Name: Annotated[str, Field()]
    """Value of schedule multiplies maximum outdoor air flow rate"""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Outdoor_Air_Mixer_Object_Type: Annotated[Literal['OutdoorAir:Mixer'], Field()]
    """Currently only one type OutdoorAir:Mixer object is available."""

    Outdoor_Air_Mixer_Name: Annotated[str, Field()]
    """If this field is blank, the OutdoorAir:Mixer is not used."""

    Supply_Air_Fan_Object_Type: Annotated[Literal['Fan:OnOff', 'Fan:ConstantVolume', 'Fan:VariableVolume', 'Fan:SystemModel'], Field(default=...)]
    """Fan type must be according to capacity control method (see I/O)"""

    Supply_Air_Fan_Name: Annotated[str, Field(default=...)]

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry', 'CoilSystem:Cooling:Water:HeatExchangerAssisted'], Field(default=...)]

    Cooling_Coil_Name: Annotated[str, Field(default=...)]

    Maximum_Cold_Water_Flow_Rate: Annotated[str, Field(default=...)]

    Minimum_Cold_Water_Flow_Rate: Annotated[str, Field(default='0.0')]

    Cooling_Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Water', 'Coil:Heating:Electric'], Field(default=...)]

    Heating_Coil_Name: Annotated[str, Field(default=...)]

    Maximum_Hot_Water_Flow_Rate: Annotated[str, Field(default=...)]

    Minimum_Hot_Water_Flow_Rate: Annotated[str, Field(default='0.0')]

    Heating_Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""

    Design_Specification_Zonehvac_Sizing_Object_Name: Annotated[str, Field()]
    """Enter the name of a DesignSpecificationZoneHVACSizing object."""

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Enter the name of a schedule that controls fan operation. Schedule Name values of 0 denote"""

    Minimum_Supply_Air_Temperature_In_Cooling_Mode: Annotated[float, Field(ge=0.0, default=autosize)]
    """For Capacity Control Method = ASHRAE90VariableFan, enter the minimum air temperature in cooling mode."""

    Maximum_Supply_Air_Temperature_In_Heating_Mode: Annotated[float, Field(ge=0.0, default=autosize)]
    """For Capacity Control Method = ASHRAE90VariableFan, enter the maximum air temperature in heating mode."""