from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Evaporativecoolerunit(EpBunch):
    """Zone evaporative cooler. Forced-convection cooling-only unit with supply fan,"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""

    Outdoor_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """this is an outdoor air node"""

    Cooler_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """this is a zone inlet node"""

    Zone_Relief_Air_Node_Name: Annotated[str, Field()]
    """this is a zone exhaust node, optional if flow is being balanced elsewhere"""

    Supply_Air_Fan_Object_Type: Annotated[Literal['Fan:SystemModel', 'Fan:ComponentModel', 'Fan:ConstantVolume', 'Fan:OnOff', 'Fan:VariableVolume'], Field(default=...)]

    Supply_Air_Fan_Name: Annotated[str, Field(default=...)]

    Design_Supply_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default=...)]

    Cooler_Unit_Control_Method: Annotated[Literal['ZoneTemperatureDeadbandOnOffCycling', 'ZoneCoolingLoadOnOffCycling', 'ZoneCoolingLoadVariableSpeedFan'], Field(default=...)]

    Throttling_Range_Temperature_Difference: Annotated[float, Field(gt=0.0, default=1.0)]
    """used for ZoneTemperatureDeadbandOnOffCycling hystersis range for thermostatic control"""

    Cooling_Load_Control_Threshold_Heat_Transfer_Rate: Annotated[float, Field(gt=0.0, default=100.0)]
    """Sign convention is that positive values indicate a cooling load"""

    First_Evaporative_Cooler_Object_Type: Annotated[Literal['EvaporativeCooler:Direct:CelDekPad', 'EvaporativeCooler:Direct:ResearchSpecial', 'EvaporativeCooler:Indirect:CelDekPad', 'EvaporativeCooler:Indirect:WetCoil', 'EvaporativeCooler:Indirect:ResearchSpecial'], Field(default=...)]

    First_Evaporative_Cooler_Object_Name: Annotated[str, Field(default=...)]

    Second_Evaporative_Cooler_Object_Type: Annotated[Literal['EvaporativeCooler:Direct:CelDekPad', 'EvaporativeCooler:Direct:ResearchSpecial', 'EvaporativeCooler:Indirect:CelDekPad', 'EvaporativeCooler:Indirect:WetCoil', 'EvaporativeCooler:Indirect:ResearchSpecial'], Field()]
    """optional, used for direct/indirect configurations"""

    Second_Evaporative_Cooler_Name: Annotated[str, Field()]
    """optional, used for direct/indirect configurations"""

    Design_Specification_Zonehvac_Sizing_Object_Name: Annotated[str, Field()]
    """Enter the name of a DesignSpecificationZoneHVACSizing object."""