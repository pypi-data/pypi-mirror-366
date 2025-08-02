from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Refrigeration_Condenser_Evaporativecooled(EpBunch):
    """Evaporative-cooled condenser for a refrigeration system (Refrigeration:System)."""

    Name: Annotated[str, Field(default=...)]

    Rated_Effective_Total_Heat_Rejection_Rate: Annotated[float, Field(default=..., ge=0.0)]
    """Rating as per ARI 490"""

    Rated_Subcooling_Temperature_Difference: Annotated[float, Field(ge=0.0, default=0.0)]
    """must correspond to rating given for total heat rejection effect"""

    Fan_Speed_Control_Type: Annotated[Literal['Fixed', 'FixedLinear', 'VariableSpeed', 'TwoSpeed'], Field(default='Fixed')]

    Rated_Fan_Power: Annotated[float, Field(default=..., ge=0.0)]
    """Power for condenser fan(s) corresponding to rated total heat rejection effect."""

    Minimum_Fan_Air_Flow_Ratio: Annotated[float, Field(ge=0.0, default=0.2)]
    """Minimum air flow fraction through condenser fan"""

    Approach_Temperature_Constant_Term: Annotated[float, Field(ge=0.0, le=20.0, default=6.63)]
    """A1 in delta T = A1 + A2(hrcf) + A3/(hrcf) + A4(Twb)"""

    Approach_Temperature_Coefficient_2: Annotated[float, Field(ge=0.0, le=20.0, default=0.468)]
    """A2 in delta T = A1 + A2(hrcf) +A3/(hrcf) +A4(Twb)"""

    Approach_Temperature_Coefficient_3: Annotated[float, Field(ge=0.0, le=30.0, default=17.93)]
    """A3 in delta T = A1 + A2(hrcf) +A3/(hrcf) +A4(Twb)"""

    Approach_Temperature_Coefficient_4: Annotated[float, Field(ge=-20.0, le=20.0, default=-0.322)]
    """A4 in deltaT=A1 + A2(hrcf) +A3/(hrcf) +A4(Twb)"""

    Minimum_Capacity_Factor: Annotated[float, Field(default=0.50)]
    """taken from manufacturer's Heat Rejection Capacity Factor Table"""

    Maximum_Capacity_Factor: Annotated[float, Field(default=5.0)]
    """taken from manufacturer's Heat Rejection Capacity Factor Table"""

    Air_Inlet_Node_Name: Annotated[str, Field()]
    """If field is left blank,"""

    Rated_Air_Flow_Rate: Annotated[float, Field(default=autocalculate)]
    """Used to calculate evaporative condenser water use and fan energy use."""

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=200.0)]
    """This field is only used for periods"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """Enter the outdoor dry-bulb temperature at which the basin heater turns on."""

    Rated_Water_Pump_Power: Annotated[float, Field(default=1000.0)]
    """Design recirculating water pump power."""

    Evaporative_Water_Supply_Tank_Name: Annotated[str, Field()]
    """If blank, water supply is from Mains."""

    Evaporative_Condenser_Availability_Schedule_Name: Annotated[str, Field()]
    """Schedule values greater than 0 indicate that evaporative cooling of the"""

    EndUse_Subcategory: Annotated[str, Field(default='General')]
    """Any text may be used here to categorize the end-uses in the ABUPS End Uses by Subcategory table."""

    Condenser_Refrigerant_Operating_Charge_Inventory: Annotated[float, Field(default=0.0)]
    """optional input"""

    Condensate_Receiver_Refrigerant_Inventory: Annotated[float, Field(default=0.0)]
    """optional input"""

    Condensate_Piping_Refrigerant_Inventory: Annotated[float, Field(default=0.0)]
    """optional input"""