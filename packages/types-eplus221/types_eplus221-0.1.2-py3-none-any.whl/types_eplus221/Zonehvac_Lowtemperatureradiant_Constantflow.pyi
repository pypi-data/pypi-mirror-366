from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Zonehvac_Lowtemperatureradiant_Constantflow(EpBunch):
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
    """Total length of pipe embedded in surface"""

    Temperature_Control_Type: Annotated[Literal['MeanAirTemperature', 'MeanRadiantTemperature', 'OperativeTemperature', 'OutdoorDryBulbTemperature', 'OutdoorWetBulbTemperature'], Field(default='MeanAirTemperature')]
    """Temperature used to control system"""

    Rated_Flow_Rate: Annotated[str, Field()]

    Pump_Flow_Rate_Schedule_Name: Annotated[str, Field()]
    """Modifies the Rated Flow Rate of the pump on a time basis"""

    Rated_Pump_Head: Annotated[str, Field(default='179352')]
    """default head is 60 feet"""

    Rated_Power_Consumption: Annotated[str, Field()]

    Motor_Efficiency: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]

    Fraction_of_Motor_Inefficiencies_to_Fluid_Stream: Annotated[str, Field(default='0.0')]

    Heating_Water_Inlet_Node_Name: Annotated[str, Field()]

    Heating_Water_Outlet_Node_Name: Annotated[str, Field()]

    Heating_High_Water_Temperature_Schedule_Name: Annotated[str, Field()]
    """Water and control temperatures for heating work together to provide"""

    Heating_Low_Water_Temperature_Schedule_Name: Annotated[str, Field()]

    Heating_High_Control_Temperature_Schedule_Name: Annotated[str, Field()]

    Heating_Low_Control_Temperature_Schedule_Name: Annotated[str, Field()]

    Cooling_Water_Inlet_Node_Name: Annotated[str, Field()]

    Cooling_Water_Outlet_Node_Name: Annotated[str, Field()]

    Cooling_High_Water_Temperature_Schedule_Name: Annotated[str, Field()]
    """See note for Heating High Water Temperature Schedule above for"""

    Cooling_Low_Water_Temperature_Schedule_Name: Annotated[str, Field()]

    Cooling_High_Control_Temperature_Schedule_Name: Annotated[str, Field()]

    Cooling_Low_Control_Temperature_Schedule_Name: Annotated[str, Field()]

    Condensation_Control_Type: Annotated[Literal['Off', 'SimpleOff', 'VariableOff'], Field(default='SimpleOff')]

    Condensation_Control_Dewpoint_Offset: Annotated[str, Field(default='1.0')]

    Number_of_Circuits: Annotated[Literal['OnePerSurface', 'CalculateFromCircuitLength'], Field(default='OnePerSurface')]

    Circuit_Length: Annotated[str, Field(default='106.7')]