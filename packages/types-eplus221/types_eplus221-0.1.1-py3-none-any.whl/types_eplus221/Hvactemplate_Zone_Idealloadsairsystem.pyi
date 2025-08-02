from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Hvactemplate_Zone_Idealloadsairsystem(EpBunch):
    """Zone with ideal air system that meets heating or cooling loads"""

    Zone_Name: Annotated[str, Field(default=...)]
    """Zone name must match a building zone name"""

    Template_Thermostat_Name: Annotated[str, Field()]
    """Enter the name of a HVACTemplate:Thermostat object."""

    System_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, always on"""

    Maximum_Heating_Supply_Air_Temperature: Annotated[str, Field(default='50')]

    Minimum_Cooling_Supply_Air_Temperature: Annotated[str, Field(default='13')]

    Maximum_Heating_Supply_Air_Humidity_Ratio: Annotated[str, Field(default='0.0156')]

    Minimum_Cooling_Supply_Air_Humidity_Ratio: Annotated[str, Field(default='0.0077')]

    Heating_Limit: Annotated[Literal['NoLimit', 'LimitFlowRate', 'LimitCapacity', 'LimitFlowRateAndCapacity'], Field(default='NoLimit')]

    Maximum_Heating_Air_Flow_Rate: Annotated[str, Field()]
    """This field is ignored if Heating Limit = NoLimit"""

    Maximum_Sensible_Heating_Capacity: Annotated[str, Field()]
    """This field is ignored if Heating Limit = NoLimit"""

    Cooling_Limit: Annotated[Literal['NoLimit', 'LimitFlowRate', 'LimitCapacity', 'LimitFlowRateAndCapacity'], Field(default='NoLimit')]

    Maximum_Cooling_Air_Flow_Rate: Annotated[str, Field()]
    """This field is ignored if Cooling Limit = NoLimit"""

    Maximum_Total_Cooling_Capacity: Annotated[str, Field()]
    """This field is ignored if Cooling Limit = NoLimit"""

    Heating_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, heating is always available."""

    Cooling_Availability_Schedule_Name: Annotated[str, Field()]
    """If blank, cooling is always available."""

    Dehumidification_Control_Type: Annotated[Literal['ConstantSensibleHeatRatio', 'Humidistat', 'None', 'ConstantSupplyHumidityRatio'], Field(default='ConstantSensibleHeatRatio')]
    """ConstantSensibleHeatRatio means that the ideal loads system"""

    Cooling_Sensible_Heat_Ratio: Annotated[str, Field(default='0.7')]
    """This field is applicable only when Dehumidification Control Type is ConstantSensibleHeatRatio"""

    Dehumidification_Setpoint: Annotated[float, Field(ge=0.0, le=100.0, default=60.0)]
    """Zone relative humidity setpoint in percent (0 to 100)"""

    Humidification_Control_Type: Annotated[Literal['None', 'Humidistat', 'ConstantSupplyHumidityRatio'], Field()]
    """None means that there is no humidification."""

    Humidification_Setpoint: Annotated[float, Field(ge=0.0, le=100.0, default=30.0)]
    """Zone relative humidity setpoint in percent (0 to 100)"""

    Outdoor_Air_Method: Annotated[Literal['None', 'Flow/Person', 'Flow/Zone', 'Flow/Area', 'Sum', 'Maximum', 'DetailedSpecification'], Field()]
    """None means there is no outdoor air and all related fields will be ignored"""

    Outdoor_Air_Flow_Rate_Per_Person: Annotated[str, Field(default='0.00944')]
    """Default 0.00944 is 20 cfm per person"""

    Outdoor_Air_Flow_Rate_Per_Zone_Floor_Area: Annotated[str, Field(default='0.0')]
    """This input is used if the field Outdoor Air Method is"""

    Outdoor_Air_Flow_Rate_Per_Zone: Annotated[float, Field(default=0.0)]
    """This input is used if the field Outdoor Air Method is"""

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """When the name of a DesignSpecification:OutdoorAir object is entered, the minimum"""

    Demand_Controlled_Ventilation_Type: Annotated[Literal['None', 'OccupancySchedule', 'CO2Setpoint'], Field()]
    """This field controls how the minimum outdoor air flow rate is calculated."""

    Outdoor_Air_Economizer_Type: Annotated[Literal['NoEconomizer', 'DifferentialDryBulb', 'DifferentialEnthalpy'], Field(default='NoEconomizer')]
    """DifferentialDryBulb and DifferentialEnthalpy will increase the outdoor air flow rate"""

    Heat_Recovery_Type: Annotated[Literal['None', 'Sensible', 'Enthalpy'], Field()]

    Sensible_Heat_Recovery_Effectiveness: Annotated[str, Field(default='0.70')]

    Latent_Heat_Recovery_Effectiveness: Annotated[str, Field(default='0.65')]
    """Applicable only if Heat Recovery Type is Enthalpy."""