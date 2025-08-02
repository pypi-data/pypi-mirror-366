from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Zone_Vrf(EpBunch):
    """Zone terminal unit with variable refrigerant flow (VRF) DX cooling and heating coils"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Zone name must match a building zone name"""

    Template_Vrf_System_Name: Annotated[str, Field(default=...)]
    """Name of a HVACTemplate:System:VRF object serving this zone"""

    Template_Thermostat_Name: Annotated[str, Field()]
    """Enter the name of a HVACTemplate:Thermostat object."""

    Zone_Heating_Sizing_Factor: Annotated[str, Field()]
    """If blank, value from Sizing:Parameters will be used."""

    Zone_Cooling_Sizing_Factor: Annotated[str, Field()]
    """If blank, value from Sizing:Parameters will be used."""

    Rated_Total_Heating_Capacity_Sizing_Ratio: Annotated[float, Field(ge=1.0, default=1.0)]
    """If this terminal unit's heating coil is autosized, the heating capacity is sized"""

    Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]
    """This field may be set to "autosize". If a value is entered, it will be"""

    No_Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]
    """This flow rate is used when the terminal is not cooling and the previous mode was cooling."""

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]
    """This field may be set to "autosize". If a value is entered, it will be"""

    No_Heating_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]
    """This flow rate is used when the terminal is not heating and the previous mode was heating."""

    Cooling_Outdoor_Air_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]
    """If this field is set to autosize it will be sized based on the outdoor air inputs below,"""

    Heating_Outdoor_Air_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]
    """If this field is set to autosize it will be sized based on the outdoor air inputs below,"""

    No_Load_Outdoor_Air_Flow_Rate: Annotated[float, Field(ge=0.0, default=autosize)]
    """If this field is set to autosize it will be sized based on the outdoor air inputs below,"""

    Outdoor_Air_Method: Annotated[Literal['Flow/Person', 'Flow/Zone', 'Flow/Area', 'Sum', 'Maximum', 'DetailedSpecification'], Field(default='Flow/Person')]
    """Flow/Person, Flow/Zone, Flow/Area, Sum, and Maximum use the values in the next three"""

    Outdoor_Air_Flow_Rate_Per_Person: Annotated[str, Field(default='0.00944')]
    """Default 0.00944 is 20 cfm per person"""

    Outdoor_Air_Flow_Rate_Per_Zone_Floor_Area: Annotated[str, Field(default='0.0')]
    """This input is used if the field Outdoor Air Method is"""

    Outdoor_Air_Flow_Rate_Per_Zone: Annotated[float, Field(default=0.0)]
    """This input is used if the field Outdoor Air Method is"""

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """This field is used only when Outdoor Air Method=DetailedSpecification."""

    Design_Specification_Zone_Air_Distribution_Object_Name: Annotated[str, Field()]
    """This field is used only when Outdoor Air Method=DetailedSpecification."""

    System_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Supply_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Refers to a schedule to specify unitary supply fan operating mode."""

    Supply_Air_Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='BlowThrough')]
    """Select fan placement as either blow through or draw through."""

    Supply_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Supply_Fan_Delta_Pressure: Annotated[str, Field(default='75')]

    Supply_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Cooling_Coil_Type: Annotated[Literal['VariableRefrigerantFlowDX', 'None'], Field(default='VariableRefrigerantFlowDX')]

    Cooling_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Cooling_Coil_Gross_Rated_Total_Capacity: Annotated[float, Field(gt=0.0, default=autosize)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Cooling_Coil_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0.5, le=1.0, default=autosize)]
    """Rated sensible heat ratio (gross sensible capacity/gross total capacity)"""

    Heat_Pump_Heating_Coil_Type: Annotated[Literal['VariableRefrigerantFlowDX', 'None'], Field(default='VariableRefrigerantFlowDX')]

    Heat_Pump_Heating_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Heat_Pump_Heating_Coil_Gross_Rated_Capacity: Annotated[float, Field(gt=0.0, default=autosize)]
    """Capacity excluding supply air fan heat"""

    Zone_Terminal_Unit_On_Parasitic_Electric_Energy_Use: Annotated[float, Field(ge=0, default=0)]

    Zone_Terminal_Unit_Off_Parasitic_Electric_Energy_Use: Annotated[float, Field(ge=0, default=0)]

    Dedicated_Outdoor_Air_System_Name: Annotated[str, Field()]
    """Enter the name of an HVACTemplate:System:DedicatedOutdoorAir object if this"""

    Zone_Cooling_Design_Supply_Air_Temperature_Input_Method: Annotated[Literal['SupplyAirTemperature', 'TemperatureDifference'], Field(default='SupplyAirTemperature')]
    """SupplyAirTemperature = use the value from Zone Cooling Design Supply Air Temperature"""

    Zone_Cooling_Design_Supply_Air_Temperature: Annotated[float, Field(default=14.0)]
    """Zone Cooling Design Supply Air Temperature is only used when Zone Cooling Design"""

    Zone_Cooling_Design_Supply_Air_Temperature_Difference: Annotated[float, Field(default=11.11)]
    """Zone Cooling Design Supply Air Temperature is only used when Zone Cooling Design"""

    Zone_Heating_Design_Supply_Air_Temperature_Input_Method: Annotated[Literal['SupplyAirTemperature', 'TemperatureDifference'], Field(default='SupplyAirTemperature')]
    """SupplyAirTemperature = use the value from Zone Heating Design Supply Air Temperature"""

    Zone_Heating_Design_Supply_Air_Temperature: Annotated[float, Field(default=50.0)]
    """Zone Heating Design Supply Air Temperature is only used when Zone Heating Design"""

    Zone_Heating_Design_Supply_Air_Temperature_Difference: Annotated[float, Field(default=30.0)]
    """Zone Heating Design Supply Air Temperature is only used when Zone Heating Design"""

    Baseboard_Heating_Type: Annotated[Literal['HotWater', 'Electric', 'None'], Field()]

    Baseboard_Heating_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Baseboard_Heating_Capacity: Annotated[str, Field(default='autosize')]