from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Zone_Watertoairheatpump(EpBunch):
    """Water to Air Heat Pump to be used with HVACTemplate:Plant:MixedWaterLoop"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Zone name must match a building zone name"""

    Template_Thermostat_Name: Annotated[str, Field()]
    """Enter the name of a HVACTemplate:Thermostat object."""

    Cooling_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]
    """Supply air flow rate during cooling operation"""

    Heating_Supply_Air_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]
    """Supply air flow rate during heating operation"""

    No_Load_Supply_Air_Flow_Rate: Annotated[float, Field(ge=0)]
    """Supply air flow rate when no cooling or heating is needed"""

    Zone_Heating_Sizing_Factor: Annotated[str, Field()]
    """If blank, value from Sizing:Parameters will be used."""

    Zone_Cooling_Sizing_Factor: Annotated[str, Field()]
    """If blank, value from Sizing:Parameters will be used."""

    Outdoor_Air_Method: Annotated[Literal['Flow/Person', 'Flow/Zone', 'Flow/Area', 'Sum', 'Maximum', 'DetailedSpecification'], Field(default='Flow/Person')]
    """Flow/Person, Flow/Zone, Flow/Area, Sum, and Maximum use the values in the next three"""

    Outdoor_Air_Flow_Rate_Per_Person: Annotated[str, Field(default='0.00944')]
    """Default 0.00944 is 20 cfm per person"""

    Outdoor_Air_Flow_Rate_Per_Zone_Floor_Area: Annotated[str, Field(default='0.0')]
    """This input is used if the field Outdoor Air Method is"""

    Outdoor_Air_Flow_Rate_Per_Zone: Annotated[float, Field(default=0.0)]
    """This input is used if the field Outdoor Air Method is"""

    System_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Supply_Fan_Operating_Mode_Schedule_Name: Annotated[str, Field()]
    """Refers to a schedule to specify unitary supply fan operating mode."""

    Supply_Fan_Placement: Annotated[Literal['BlowThrough', 'DrawThrough'], Field(default='DrawThrough')]

    Supply_Fan_Total_Efficiency: Annotated[str, Field(default='0.7')]

    Supply_Fan_Delta_Pressure: Annotated[str, Field(default='75')]

    Supply_Fan_Motor_Efficiency: Annotated[str, Field(default='0.9')]

    Cooling_Coil_Type: Annotated[Literal['Coil:Cooling:WaterToAirHeatPump:EquationFit'], Field(default='Coil:Cooling:WaterToAirHeatPump:EquationFit')]

    Cooling_Coil_Gross_Rated_Total_Capacity: Annotated[float, Field(gt=0.0, default=autosize)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Cooling_Coil_Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0.5, le=1.0, default=autosize)]
    """Rated sensible heat ratio (gross sensible capacity/gross total capacity)"""

    Cooling_Coil_Gross_Rated_Cop: Annotated[float, Field(gt=0.0, default=3.5)]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    Heat_Pump_Heating_Coil_Type: Annotated[Literal['Coil:Heating:WaterToAirHeatPump:EquationFit'], Field(default='Coil:Heating:WaterToAirHeatPump:EquationFit')]

    Heat_Pump_Heating_Coil_Gross_Rated_Capacity: Annotated[float, Field(gt=0.0, default=autosize)]
    """Capacity excluding supply air fan heat"""

    Heat_Pump_Heating_Coil_Gross_Rated_Cop: Annotated[str, Field(default='4.2')]
    """Heat Pump Heating Coil Rated Capacity divided by power input to the compressor and outdoor fan,"""

    Supplemental_Heating_Coil_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Supplemental_Heating_Coil_Capacity: Annotated[str, Field(default='autosize')]

    Maximum_Cycling_Rate: Annotated[float, Field(ge=0.0, le=5.0, default=2.5)]
    """The maximum on-off cycling rate for the compressor"""

    Heat_Pump_Time_Constant: Annotated[float, Field(ge=0.0, le=500.0, default=60.0)]
    """Time constant for the cooling coil's capacity to reach steady state after startup"""

    Fraction_Of_On_Cycle_Power_Use: Annotated[str, Field(default='0.01')]
    """The fraction of on-cycle power use to adjust the part load fraction based on"""

    Heat_Pump_Fan_Delay_Time: Annotated[str, Field(default='60')]
    """Programmed time delay for heat pump fan to shut off after compressor cycle off."""

    Dedicated_Outdoor_Air_System_Name: Annotated[str, Field()]
    """Enter the name of an HVACTemplate:System:DedicatedOutdoorAir object if this"""

    Supplemental_Heating_Coil_Type: Annotated[Literal['Electric', 'HotWater'], Field(default='Electric')]

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

    Heat_Pump_Coil_Water_Flow_Mode: Annotated[Literal['Constant', 'Cycling', 'ConstantOnDemand'], Field(default='Cycling')]
    """used only when the heat pump coils are of the type WaterToAirHeatPump:EquationFit"""

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """This field is used only when Outdoor Air Method=DetailedSpecification."""

    Design_Specification_Zone_Air_Distribution_Object_Name: Annotated[str, Field()]
    """This field is used only when Outdoor Air Method=DetailedSpecification."""

    Baseboard_Heating_Type: Annotated[Literal['HotWater', 'Electric', 'None'], Field()]

    Baseboard_Heating_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Baseboard_Heating_Capacity: Annotated[str, Field(default='autosize')]