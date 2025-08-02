from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Evaporativecooler_Indirect_Researchspecial(EpBunch):
    """Indirect evaporative cooler with user-specified effectiveness (can represent rigid pad"""

    Name: Annotated[str, Field()]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Cooler_Wetbulb_Design_Effectiveness: Annotated[float, Field(default=..., ge=0.0, le=2.0)]
    """wet operation effectiveness with respect to wetbulb depression"""

    Wetbulb_Effectiveness_Flow_Ratio_Modifier_Curve_Name: Annotated[str, Field()]
    """this curve modifies the wetbulb effectiveness in the previous field (eff_wb_design)"""

    Cooler_Drybulb_Design_Effectiveness: Annotated[float, Field(ge=0.0)]
    """dry operation effectiveness with respect to drybulb temperature difference"""

    Drybulb_Effectiveness_Flow_Ratio_Modifier_Curve_Name: Annotated[str, Field()]
    """this curve modifies the drybulb effectiveness in the previous field (eff_db_design)"""

    Recirculating_Water_Pump_Design_Power: Annotated[str, Field(default='autosize')]
    """This is the nominal design pump power of water recirculation and spray for evaporation at design air flow"""

    Water_Pump_Power_Sizing_Factor: Annotated[float, Field(default=90.0)]
    """This field is used when the previous field is set to autosize. The pump power is scaled with Secondary Air"""

    Water_Pump_Power_Modifier_Curve_Name: Annotated[str, Field()]
    """this curve modifies the pump power in the previous field by multiplying the design power by the result of this curve."""

    Secondary_Air_Design_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]

    Secondary_Air_Flow_Scaling_Factor: Annotated[float, Field(default=1.0)]
    """This field is used when the previous field is set to autoize. The Primary Design Air Flow Rate is scaled using this factor"""

    Secondary_Air_Fan_Design_Power: Annotated[float, Field(default=autosize)]
    """This is the fan design power at Secondary Design Air Flow Rate. This is the nominal design power at full speed."""

    Secondary_Air_Fan_Sizing_Specific_Power: Annotated[float, Field(default=250.0)]
    """This field is used when the previous field is set to autosize. The fan power is scaled with Secondary Air Design Flow Rate."""

    Secondary_Air_Fan_Power_Modifier_Curve_Name: Annotated[str, Field()]
    """this curve modifies the design fan power in the previous field by multiplying the value by the result"""

    Primary_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Primary_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Primary_Air_Design_Flow_Rate: Annotated[float, Field(gt=0.0, default=autosize)]

    Dewpoint_Effectiveness_Factor: Annotated[float, Field(ge=0.0)]

    Secondary_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Secondary_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Sensor_Node_Name: Annotated[str, Field(default=...)]

    Relief_Air_Inlet_Node_Name: Annotated[str, Field()]

    Water_Supply_Storage_Tank_Name: Annotated[str, Field()]

    Drift_Loss_Fraction: Annotated[float, Field(ge=0.0, default=0.0)]
    """Rate of drift loss as a fraction of evaporated water flow rate."""

    Blowdown_Concentration_Ratio: Annotated[float, Field(ge=2.0)]
    """Characterizes the rate of blowdown in the evaporative cooler."""

    Evaporative_Operation_Minimum_Limit_Secondary_Air_Drybulb_Temperature: Annotated[float, Field()]
    """This input field value defines the secondary air inlet node drybulb temperature"""

    Evaporative_Operation_Maximum_Limit_Outdoor_Wetbulb_Temperature: Annotated[float, Field()]
    """This input field value defines the secondary air inlet node wetbulb temperature"""

    Dry_Operation_Maximum_Limit_Outdoor_Drybulb_Temperature: Annotated[float, Field()]
    """This input field value defines the secondary air inlet node drybulb temperature"""