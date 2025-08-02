from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Idealloadsairsystem(EpBunch):
    """Ideal system used to calculate loads without modeling a full HVAC system. All that is"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Zone_Supply_Air_Node_Name: Annotated[str, Field(default=...)]
    """Must match a zone air inlet node name."""

    Zone_Exhaust_Air_Node_Name: Annotated[str, Field()]
    """Should match a zone air exhaust node name."""

    System_Inlet_Air_Node_Name: Annotated[str, Field()]
    """This field is only required when the Ideal Loads Air System is connected to an"""

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

    Humidification_Control_Type: Annotated[Literal['None', 'Humidistat', 'ConstantSupplyHumidityRatio'], Field()]
    """None means that there is no humidification."""

    Design_Specification_Outdoor_Air_Object_Name: Annotated[str, Field()]
    """When the name of a DesignSpecification:OutdoorAir object is entered, the minimum"""

    Outdoor_Air_Inlet_Node_Name: Annotated[str, Field()]
    """This field is required if the system provides outdoor air"""

    Demand_Controlled_Ventilation_Type: Annotated[Literal['None', 'OccupancySchedule', 'CO2Setpoint'], Field()]
    """This field controls how the minimum outdoor air flow rate is calculated."""

    Outdoor_Air_Economizer_Type: Annotated[Literal['NoEconomizer', 'DifferentialDryBulb', 'DifferentialEnthalpy'], Field(default='NoEconomizer')]
    """DifferentialDryBulb and DifferentialEnthalpy will increase the outdoor air flow rate"""

    Heat_Recovery_Type: Annotated[Literal['None', 'Sensible', 'Enthalpy'], Field()]

    Sensible_Heat_Recovery_Effectiveness: Annotated[str, Field(default='0.70')]

    Latent_Heat_Recovery_Effectiveness: Annotated[str, Field(default='0.65')]
    """Applicable only if Heat Recovery Type is Enthalpy."""

    Design_Specification_ZoneHVAC_Sizing_Object_Name: Annotated[str, Field()]
    """Enter the name of a DesignSpecificationZoneHVACSizing object."""