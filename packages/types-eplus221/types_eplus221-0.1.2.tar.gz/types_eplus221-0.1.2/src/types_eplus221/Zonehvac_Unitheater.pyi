from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Unitheater(EpBunch):
    """Unit heater. Forced-convection heating-only unit with supply fan, heating coil"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Air_Inlet_Node_Name: Annotated[str, Field()]

    Air_Outlet_Node_Name: Annotated[str, Field()]

    Supply_Air_Fan_Object_Type: Annotated[Literal['Fan:OnOff', 'Fan:ConstantVolume', 'Fan:VariableVolume', 'Fan:SystemModel'], Field(default=...)]
    """Allowable fan types are Fan:ConstantVolume, Fan:OnOff, Fan:VariableVolume and Fan:SystemModel"""

    Supply_Air_Fan_Name: Annotated[str, Field(default=...)]

    Maximum_Supply_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Water', 'Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam'], Field(default=...)]

    Heating_Coil_Name: Annotated[str, Field(default=...)]

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Enter the name of a schedule that controls fan operation. Schedule"""

    Supply_Air_Fan_Operation_During_No_Heating: Annotated[Literal['Yes', 'No'], Field(default=...)]
    """This choice field allows the user to define how the unit heater will operate"""

    Maximum_Hot_Water_or_Steam_Flow_Rate: Annotated[str, Field()]
    """Not used when heating coil is gas or electric"""

    Minimum_Hot_Water_or_Steam_Flow_Rate: Annotated[str, Field(default='0')]
    """Not used when heating coil is gas or electric"""

    Heating_Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""

    Design_Specification_ZoneHVAC_Sizing_Object_Name: Annotated[str, Field()]
    """Enter the name of a DesignSpecificationZoneHVACSizing object."""