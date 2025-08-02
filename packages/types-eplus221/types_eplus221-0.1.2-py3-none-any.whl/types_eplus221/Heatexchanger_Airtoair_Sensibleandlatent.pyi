from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Heatexchanger_Airtoair_Sensibleandlatent(EpBunch):
    """This object models an air-to-air heat exchanger using effectiveness relationships."""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Nominal_Supply_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]

    Sensible_Effectiveness_at_100_Heating_Air_Flow: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Latent_Effectiveness_at_100_Heating_Air_Flow: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Sensible_Effectiveness_at_75_Heating_Air_Flow: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Latent_Effectiveness_at_75_Heating_Air_Flow: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Sensible_Effectiveness_at_100_Cooling_Air_Flow: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Latent_Effectiveness_at_100_Cooling_Air_Flow: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Sensible_Effectiveness_at_75_Cooling_Air_Flow: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Latent_Effectiveness_at_75_Cooling_Air_Flow: Annotated[float, Field(ge=0.0, le=1.0, default=0.0)]

    Supply_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Supply_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Exhaust_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Exhaust_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Nominal_Electric_Power: Annotated[float, Field(ge=0.0, default=0.0)]

    Supply_Air_Outlet_Temperature_Control: Annotated[Literal['No', 'Yes'], Field(default='No')]

    Heat_Exchanger_Type: Annotated[Literal['Plate', 'Rotary'], Field(default='Plate')]

    Frost_Control_Type: Annotated[Literal['None', 'ExhaustAirRecirculation', 'ExhaustOnly', 'MinimumExhaustTemperature'], Field()]

    Threshold_Temperature: Annotated[float, Field(default=1.7)]
    """Supply (outdoor) air inlet temp threshold for exhaust air recirculation and"""

    Initial_Defrost_Time_Fraction: Annotated[float, Field(ge=0.0, le=1.0, default=0.083)]
    """Fraction of the time when frost control will be invoked at the threshold temperature."""

    Rate_of_Defrost_Time_Fraction_Increase: Annotated[float, Field(ge=0.0, default=0.012)]
    """Rate of increase in defrost time fraction as actual temp falls below threshold temperature."""

    Economizer_Lockout: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """Yes means that the heat exchanger will be locked out (off)"""