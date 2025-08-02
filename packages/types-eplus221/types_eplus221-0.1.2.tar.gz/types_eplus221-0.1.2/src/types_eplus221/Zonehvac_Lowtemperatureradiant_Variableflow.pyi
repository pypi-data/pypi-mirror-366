from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Lowtemperatureradiant_Variableflow(EpBunch):
    """Low temperature hydronic radiant heating and/or cooling system embedded in a building"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Name: Annotated[str, Field()]
    """Name of zone system is serving"""

    Surface_Name_or_Radiant_Surface_Group_Name: Annotated[str, Field()]
    """Identifies surfaces that radiant system is embedded in."""

    Hydronic_Tubing_Inside_Diameter: Annotated[str, Field(default='0.013')]

    Hydronic_Tubing_Length: Annotated[str, Field(default='autosize')]
    """(total length of pipe embedded in surface)"""

    Temperature_Control_Type: Annotated[Literal['MeanAirTemperature', 'MeanRadiantTemperature', 'OperativeTemperature', 'OutdoorDryBulbTemperature', 'OutdoorWetBulbTemperature'], Field(default='MeanAirTemperature')]
    """(Temperature on which unit is controlled)"""

    Heating_Design_Capacity_Method: Annotated[Literal['HeatingDesignCapacity', 'CapacityPerFloorArea', 'FractionOfAutosizedHeatingCapacity'], Field(default='HeatingDesignCapacity')]
    """Enter the method used to determine the heating design capacity."""

    Heating_Design_Capacity: Annotated[float, Field(ge=0.0, default=autosize)]
    """Enter the design heating capacity.Required field when the heating design capacity method"""

    Heating_Design_Capacity_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the heating design capacity per zone floor area.Required field when the heating design"""

    Fraction_of_Autosized_Heating_Design_Capacity: Annotated[float, Field(ge=0.0, default=1.0)]
    """Enter the fraction of auto - sized heating design capacity.Required field when capacity the"""

    Maximum_Hot_Water_Flow: Annotated[str, Field()]

    Heating_Water_Inlet_Node_Name: Annotated[str, Field()]

    Heating_Water_Outlet_Node_Name: Annotated[str, Field()]

    Heating_Control_Throttling_Range: Annotated[str, Field(default='0.5')]

    Heating_Control_Temperature_Schedule_Name: Annotated[str, Field()]

    Cooling_Design_Capacity_Method: Annotated[Literal['None', 'CoolingDesignCapacity', 'CapacityPerFloorArea', 'FractionOfAutosizedCoolingCapacity'], Field(default='CoolingDesignCapacity')]
    """Enter the method used to determine the cooling design capacity for scalable sizing."""

    Cooling_Design_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the design cooling capacity. Required field when the cooling design capacity method"""

    Cooling_Design_Capacity_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the cooling design capacity per total floor area of cooled zones served by the unit."""

    Fraction_of_Autosized_Cooling_Design_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the fraction of auto-sized cooling design capacity. Required field when the cooling"""

    Maximum_Cold_Water_Flow: Annotated[str, Field()]

    Cooling_Water_Inlet_Node_Name: Annotated[str, Field()]

    Cooling_Water_Outlet_Node_Name: Annotated[str, Field()]

    Cooling_Control_Throttling_Range: Annotated[str, Field(default='0.5')]

    Cooling_Control_Temperature_Schedule_Name: Annotated[str, Field()]

    Condensation_Control_Type: Annotated[Literal['Off', 'SimpleOff', 'VariableOff'], Field(default='SimpleOff')]

    Condensation_Control_Dewpoint_Offset: Annotated[str, Field(default='1.0')]

    Number_of_Circuits: Annotated[Literal['OnePerSurface', 'CalculateFromCircuitLength'], Field(default='OnePerSurface')]

    Circuit_Length: Annotated[str, Field(default='106.7')]