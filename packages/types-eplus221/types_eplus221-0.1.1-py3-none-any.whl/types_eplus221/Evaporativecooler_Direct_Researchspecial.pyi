from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Evaporativecooler_Direct_Researchspecial(EpBunch):
    """Direct evaporative cooler with user-specified effectiveness (can represent rigid pad"""

    Name: Annotated[str, Field()]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Cooler_Design_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0)]
    """effectiveness with respect to wet-bulb depression"""

    Effectiveness_Flow_Ratio_Modifier_Curve_Name: Annotated[str, Field()]
    """this curve modifies the design effectiveness in the previous field"""

    Primary_Air_Design_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]

    Recirculating_Water_Pump_Design_Power: Annotated[str, Field(default='autosize')]
    """This is the design water pump or spray for evaporation at the primary air design air flow rates"""

    Water_Pump_Power_Sizing_Factor: Annotated[float, Field(default=90.0)]
    """This field is used when the previous field is set to autosize. The pump power is scaled with Primary Air"""

    Water_Pump_Power_Modifier_Curve_Name: Annotated[str, Field()]
    """this curve modifies the pump power in the previous field by multiplying the design power by the result of this curve."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Sensor_Node_Name: Annotated[str, Field(default=...)]

    Water_Supply_Storage_Tank_Name: Annotated[str, Field()]

    Drift_Loss_Fraction: Annotated[float, Field(ge=0.0)]
    """Rate of drift loss as a fraction of evaporated water flow rate"""

    Blowdown_Concentration_Ratio: Annotated[float, Field(ge=2.0)]
    """Characterizes the rate of blowdown in the evaporative cooler."""

    Evaporative_Operation_Minimum_Drybulb_Temperature: Annotated[float, Field(ge=-99.0)]
    """This numeric field defines the evaporative cooler air inlet node drybulb temperature minimum"""

    Evaporative_Operation_Maximum_Limit_Wetbulb_Temperature: Annotated[float, Field()]
    """when outdoor wetbulb temperature rises above this limit the cooler shuts down."""

    Evaporative_Operation_Maximum_Limit_Drybulb_Temperature: Annotated[float, Field()]
    """This numeric field defines the evaporative cooler air inlet node dry-bulb temperature maximum"""