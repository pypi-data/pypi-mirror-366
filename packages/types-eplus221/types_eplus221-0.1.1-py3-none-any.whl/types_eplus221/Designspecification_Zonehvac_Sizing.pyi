from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Designspecification_Zonehvac_Sizing(EpBunch):
    """This object is used to describe general scalable zone HVAC equipment sizing which"""

    Name: Annotated[str, Field(default=...)]

    Cooling_Supply_Air_Flow_Rate_Method: Annotated[Literal['None', 'SupplyAirFlowRate', 'FlowPerFloorArea', 'FractionOfAutosizedCoolingAirflow', 'FlowPerCoolingCapacity'], Field(default='SupplyAirFlowRate')]
    """Enter the method used to determine the cooling supply air volume flow rate."""

    Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the magnitude of supply air volume flow rate during cooling operation."""

    Cooling_Supply_Air_Flow_Rate_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the cooling supply air volume flow rate per total conditioned floor area."""

    Cooling_Fraction_Of_Autosized_Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the cooling supply air flow rate."""

    Cooling_Supply_Air_Flow_Rate_Per_Unit_Cooling_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the cooling supply air volume flow rate unit cooling capacity."""

    No_Load_Supply_Air_Flow_Rate_Method: Annotated[Literal['None', 'SupplyAirFlowRate', 'FlowPerFloorArea', 'FractionOfAutosizedCoolingAirflow', 'FractionOfAutosizedHeatingAirflow'], Field(default='SupplyAirFlowRate')]
    """Enter the method used to determine the supply air volume flow rate When No Cooling or Heating"""

    No_Load_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the magnitude of the supply air volume flow rate during when no cooling or heating"""

    No_Load_Supply_Air_Flow_Rate_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate per total floor area."""

    No_Load_Fraction_Of_Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the cooling supply air flow rate."""

    No_Load_Fraction_Of_Heating_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the heating supply air flow rate."""

    Heating_Supply_Air_Flow_Rate_Method: Annotated[Literal['None', 'SupplyAirFlowRate', 'FlowPerFloorArea', 'FractionOfAutosizedHeatingAirflow', 'FlowPerHeatingCapacity'], Field(default='SupplyAirFlowRate')]
    """Enter the method used to determine the heating supply air volume flow rate."""

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the magnitude of the supply air volume flow rate during heating operation."""

    Heating_Supply_Air_Flow_Rate_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the heating supply air volume flow rate per total conditioned floor area."""

    Heating_Fraction_Of_Heating_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the heating supply air flow rate."""

    Heating_Supply_Air_Flow_Rate_Per_Unit_Heating_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate per unit heating capacity."""

    Cooling_Design_Capacity_Method: Annotated[Literal['None', 'CoolingDesignCapacity', 'CapacityPerFloorArea', 'FractionOfAutosizedCoolingCapacity'], Field()]
    """Enter the method used to determine the cooling design capacity for scalable sizing."""

    Cooling_Design_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the design cooling capacity. Required field when the cooling design capacity method"""

    Cooling_Design_Capacity_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the cooling design capacity per zone floor area. Required field when the cooling design"""

    Fraction_Of_Autosized_Cooling_Design_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the fraction of auto-sized cooling design capacity. Required field when the cooling"""

    Heating_Design_Capacity_Method: Annotated[Literal['None', 'HeatingDesignCapacity', 'CapacityPerFloorArea', 'FractionOfAutosizedHeatingCapacity'], Field()]
    """Enter the method used to determine the heating design capacity for scalable sizing."""

    Heating_Design_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the design heating capacity. Required field when the heating design capacity method"""

    Heating_Design_Capacity_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the heating design capacity per zone floor area. Required field when the heating design"""

    Fraction_Of_Autosized_Heating_Design_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the fraction of auto-sized heating design capacity. Required field when capacity the"""