from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Unitventilator(EpBunch):
    """Unit ventilator. Forced-convection ventilation unit with supply fan (constant-volume"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Maximum_Supply_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Outdoor_Air_Control_Type: Annotated[Literal['FixedAmount', 'VariablePercent', 'FixedTemperature'], Field(default=...)]

    Minimum_Outdoor_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Minimum_Outdoor_Air_Schedule_Name: Annotated[str, Field(default=...)]
    """schedule values multiply the minimum outdoor air flow rate"""

    Maximum_Outdoor_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Maximum_Outdoor_Air_Fraction_or_Temperature_Schedule_Name: Annotated[str, Field(default=...)]
    """that this depends on the control type as to whether it is a fraction or temperature"""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """Inlet node name must be zone exhaust node name if there is no DOA Mixer, or if the"""

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """Outlet node name must be zone inlet node name if there is no DOA Mixer, or if the"""

    Outdoor_Air_Node_Name: Annotated[str, Field()]
    """this field is left blank only if the Unit Ventilator is connected to a central"""

    Exhaust_Air_Node_Name: Annotated[str, Field()]
    """this field is left blank only if the Unit Ventilator is connected to a central"""

    Mixed_Air_Node_Name: Annotated[str, Field()]
    """inlet to coils"""

    Supply_Air_Fan_Object_Type: Annotated[Literal['Fan:OnOff', 'Fan:ConstantVolume', 'Fan:VariableVolume', 'Fan:SystemModel'], Field(default=...)]
    """Allowable fan types are Fan:ConstantVolume, Fan:OnOff, Fan:VariableVolume, and Fan:SystemModel"""

    Supply_Air_Fan_Name: Annotated[str, Field(default=...)]

    Coil_Option: Annotated[Literal['None', 'Heating', 'Cooling', 'HeatingAndCooling'], Field(default=...)]

    Supply_Air_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Enter the name of a schedule that controls fan operation. Schedule"""

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Water', 'Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam'], Field()]

    Heating_Coil_Name: Annotated[str, Field()]

    Heating_Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry', 'CoilSystem:Cooling:Water:HeatExchangerAssisted'], Field()]

    Cooling_Coil_Name: Annotated[str, Field()]

    Cooling_Convergence_Tolerance: Annotated[float, Field(gt=0.0, default=0.001)]

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""

    Design_Specification_ZoneHVAC_Sizing_Object_Name: Annotated[str, Field()]
    """Enter the name of a DesignSpecificationZoneHVACSizing object."""