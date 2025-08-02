from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Ventilatedslab(EpBunch):
    """Ventilated slab system where outdoor air flows through hollow cores in a building"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Name: Annotated[str, Field(default=...)]
    """(name of zone system is serving)"""

    Surface_Name_Or_Radiant_Surface_Group_Name: Annotated[str, Field()]
    """(name of surface system is embedded in) or list of surfaces"""

    Maximum_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Outdoor_Air_Control_Type: Annotated[Literal['VariablePercent', 'FixedTemperature', 'FixedAmount'], Field(default=...)]

    Minimum_Outdoor_Air_Flow_Rate: Annotated[str, Field(default=...)]

    Minimum_Outdoor_Air_Schedule_Name: Annotated[str, Field(default=...)]

    Maximum_Outdoor_Air_Flow_Rate: Annotated[str, Field(default=...)]
    """schedule values multiply the minimum outdoor air flow rate"""

    Maximum_Outdoor_Air_Fraction_Or_Temperature_Schedule_Name: Annotated[str, Field(default=...)]
    """Note that this depends on the control type as to whether schedule values are a fraction or temperature"""

    System_Configuration_Type: Annotated[Literal['SlabOnly', 'SlabAndZone', 'SeriesSlabs'], Field(default='SlabOnly')]

    Hollow_Core_Inside_Diameter: Annotated[str, Field(default='0.05')]

    Hollow_Core_Length: Annotated[str, Field()]
    """(length of core cavity embedded in surface)"""

    Number_Of_Cores: Annotated[str, Field()]
    """flow will be divided evenly among the cores"""

    Temperature_Control_Type: Annotated[Literal['MeanAirTemperature', 'MeanRadiantTemperature', 'OperativeTemperature', 'OutdoorDryBulbTemperature', 'OutdoorWetBulbTemperature', 'SurfaceTemperature', 'ZoneAirDewPointTemperature'], Field(default='OutdoorDryBulbTemperature')]
    """(temperature on which unit is controlled)"""

    Heating_High_Air_Temperature_Schedule_Name: Annotated[str, Field(default=...)]
    """Air and control temperatures for heating work together to provide"""

    Heating_Low_Air_Temperature_Schedule_Name: Annotated[str, Field(default=...)]

    Heating_High_Control_Temperature_Schedule_Name: Annotated[str, Field(default=...)]

    Heating_Low_Control_Temperature_Schedule_Name: Annotated[str, Field(default=...)]

    Cooling_High_Air_Temperature_Schedule_Name: Annotated[str, Field(default=...)]
    """See note for heating high air temperature schedule above for"""

    Cooling_Low_Air_Temperature_Schedule_Name: Annotated[str, Field(default=...)]

    Cooling_High_Control_Temperature_Schedule_Name: Annotated[str, Field(default=...)]

    Cooling_Low_Control_Temperature_Schedule_Name: Annotated[str, Field(default=...)]

    Return_Air_Node_Name: Annotated[str, Field(default=...)]
    """This is the zone return air inlet to the ventilated slab system outdoor air mixer."""

    Slab_In_Node_Name: Annotated[str, Field(default=...)]
    """This is the node entering the slab or series of slabs after the fan and coil(s)."""

    Zone_Supply_Air_Node_Name: Annotated[str, Field()]
    """This is the node name exiting the slab."""

    Outdoor_Air_Node_Name: Annotated[str, Field(default=...)]
    """This node is the outdoor air inlet to the ventilated slab oa mixer."""

    Relief_Air_Node_Name: Annotated[str, Field(default=...)]
    """This node is the relief air node from the ventilated slab outdoor air mixer."""

    Outdoor_Air_Mixer_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """This is the node name leaving the outdoor air mixer and entering the fan and coil(s)."""

    Fan_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """This is the node name of the fan outlet."""

    Fan_Name: Annotated[str, Field(default=...)]
    """Allowable fan types are Fan:SystemModel and Fan:ConstantVolume"""

    Coil_Option_Type: Annotated[Literal['None', 'Heating', 'Cooling', 'HeatingAndCooling'], Field(default=...)]

    Heating_Coil_Object_Type: Annotated[Literal['Coil:Heating:Water', 'Coil:Heating:Electric', 'Coil:Heating:Fuel', 'Coil:Heating:Steam'], Field()]

    Heating_Coil_Name: Annotated[str, Field()]

    Hot_Water_Or_Steam_Inlet_Node_Name: Annotated[str, Field()]

    Cooling_Coil_Object_Type: Annotated[Literal['Coil:Cooling:Water', 'Coil:Cooling:Water:DetailedGeometry', 'CoilSystem:Cooling:Water:HeatExchangerAssisted'], Field()]

    Cooling_Coil_Name: Annotated[str, Field()]

    Cold_Water_Inlet_Node_Name: Annotated[str, Field()]

    Availability_Manager_List_Name: Annotated[str, Field()]
    """Enter the name of an AvailabilityManagerAssignmentList object."""

    Design_Specification_Zonehvac_Sizing_Object_Name: Annotated[str, Field()]
    """Enter the name of a DesignSpecificationZoneHVACSizing object."""