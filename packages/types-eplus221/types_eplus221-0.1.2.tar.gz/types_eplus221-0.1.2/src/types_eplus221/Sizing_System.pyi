from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Sizing_System(EpBunch):
    """Specifies the input needed to perform sizing calculations for a central forced air"""

    AirLoop_Name: Annotated[str, Field(default=...)]

    Type_of_Load_to_Size_On: Annotated[Literal['Sensible', 'Total', 'VentilationRequirement'], Field(default='Sensible')]
    """Specifies the basis for sizing the system supply air flow rate"""

    Design_Outdoor_Air_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]

    Central_Heating_Maximum_System_Air_Flow_Ratio: Annotated[float, Field(ge=0.0, le=1.0, default=autosize)]

    Preheat_Design_Temperature: Annotated[float, Field(default=...)]

    Preheat_Design_Humidity_Ratio: Annotated[float, Field(default=...)]

    Precool_Design_Temperature: Annotated[float, Field(default=...)]

    Precool_Design_Humidity_Ratio: Annotated[float, Field(default=...)]

    Central_Cooling_Design_Supply_Air_Temperature: Annotated[float, Field(default=...)]

    Central_Heating_Design_Supply_Air_Temperature: Annotated[float, Field(default=...)]

    Type_of_Zone_Sum_to_Use: Annotated[Literal['Coincident', 'NonCoincident'], Field(default='NonCoincident')]

    100_Outdoor_Air_in_Cooling: Annotated[Literal['Yes', 'No'], Field(default='No')]

    100_Outdoor_Air_in_Heating: Annotated[Literal['Yes', 'No'], Field(default='No')]

    Central_Cooling_Design_Supply_Air_Humidity_Ratio: Annotated[float, Field(default=0.008)]

    Central_Heating_Design_Supply_Air_Humidity_Ratio: Annotated[float, Field(default=0.008)]

    Cooling_Supply_Air_Flow_Rate_Method: Annotated[Literal['Flow/System', 'DesignDay', 'FlowPerFloorArea', 'FractionOfAutosizedCoolingAirflow', 'FlowPerCoolingCapacity'], Field(default='DesignDay')]

    Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0, default=0)]
    """This input is used if Cooling Supply Air Flow Rate Method is Flow/System"""

    Cooling_Supply_Air_Flow_Rate_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the cooling supply air volume flow rate per total conditioned floor area."""

    Cooling_Fraction_of_Autosized_Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the cooling supply air flow rate."""

    Cooling_Supply_Air_Flow_Rate_Per_Unit_Cooling_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate per unit cooling capacity."""

    Heating_Supply_Air_Flow_Rate_Method: Annotated[Literal['Flow/System', 'DesignDay', 'FlowPerFloorArea', 'FractionOfAutosizedHeatingAirflow', 'FractionOfAutosizedCoolingAirflow', 'FlowPerHeatingCapacity'], Field(default='DesignDay')]

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0, default=0)]
    """Required field when Heating Supply Air Flow Rate Method is Flow/System"""

    Heating_Supply_Air_Flow_Rate_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the heating supply air volume flow rate per total conditioned floor area."""

    Heating_Fraction_of_Autosized_Heating_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the heating supply air flow rate."""

    Heating_Fraction_of_Autosized_Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0)]
    """Enter the supply air volume flow rate as a fraction of the cooling supply air flow rate."""

    Heating_Supply_Air_Flow_Rate_Per_Unit_Heating_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the heating supply air volume flow rate per unit heating capacity."""

    System_Outdoor_Air_Method: Annotated[Literal['ZoneSum', 'VentilationRateProcedure'], Field(default='ZoneSum')]

    Zone_Maximum_Outdoor_Air_Fraction: Annotated[float, Field(gt=0.0, default=1.0)]

    Cooling_Design_Capacity_Method: Annotated[Literal['None', 'CoolingDesignCapacity', 'CapacityPerFloorArea', 'FractionOfAutosizedCoolingCapacity'], Field(default='CoolingDesignCapacity')]
    """Enter the method used to determine the system cooling design capacity for scalable sizing."""

    Cooling_Design_Capacity: Annotated[float, Field(ge=0.0, default=autosize)]
    """Enter the design cooling capacity."""

    Cooling_Design_Capacity_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the cooling design capacity per total floor area of cooled zones served by an airloop."""

    Fraction_of_Autosized_Cooling_Design_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the fraction of auto-sized cooling design capacity. Required field when the cooling"""

    Heating_Design_Capacity_Method: Annotated[Literal['None', 'HeatingDesignCapacity', 'CapacityPerFloorArea', 'FractionOfAutosizedHeatingCapacity'], Field(default='HeatingDesignCapacity')]
    """Enter the method used to determine the heating design capacity for scalable sizing."""

    Heating_Design_Capacity: Annotated[float, Field(ge=0.0, default=autosize)]
    """Enter the design heating capacity."""

    Heating_Design_Capacity_Per_Floor_Area: Annotated[float, Field(ge=0.0)]
    """Enter the heating design capacity per zone floor area. Required field when the heating design"""

    Fraction_of_Autosized_Heating_Design_Capacity: Annotated[float, Field(ge=0.0)]
    """Enter the fraction of auto-sized heating design capacity. Required field when capacity the"""

    Central_Cooling_Capacity_Control_Method: Annotated[Literal['VAV', 'Bypass', 'VT', 'OnOff'], Field(default='OnOff')]
    """Method used to control the coil's output"""