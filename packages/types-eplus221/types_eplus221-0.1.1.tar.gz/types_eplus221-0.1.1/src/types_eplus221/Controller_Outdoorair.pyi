from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Controller_Outdoorair(EpBunch):
    """Controller to set the outdoor air flow rate for an air loop. Control options include"""

    Name: Annotated[str, Field(default=...)]

    Relief_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Return_Air_Node_Name: Annotated[str, Field(default=...)]

    Mixed_Air_Node_Name: Annotated[str, Field(default=...)]

    Actuator_Node_Name: Annotated[str, Field(default=...)]
    """Outdoor air inlet node entering the first pre-treat component if any"""

    Minimum_Outdoor_Air_Flow_Rate: Annotated[float, Field(default=...)]
    """If there is a Mechanical Ventilation Controller (Controller:MechanicalVentilation), note"""

    Maximum_Outdoor_Air_Flow_Rate: Annotated[float, Field(default=...)]

    Economizer_Control_Type: Annotated[Literal['FixedDryBulb', 'FixedEnthalpy', 'DifferentialDryBulb', 'DifferentialEnthalpy', 'FixedDewPointAndDryBulb', 'ElectronicEnthalpy', 'DifferentialDryBulbAndEnthalpy', 'NoEconomizer'], Field(default='NoEconomizer')]

    Economizer_Control_Action_Type: Annotated[Literal['ModulateFlow', 'MinimumFlowWithBypass'], Field(default='ModulateFlow')]

    Economizer_Maximum_Limit_Dry_Bulb_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor dry-bulb temperature limit for FixedDryBulb"""

    Economizer_Maximum_Limit_Enthalpy: Annotated[float, Field()]
    """Enter the maximum outdoor enthalpy limit for FixedEnthalpy economizer control type."""

    Economizer_Maximum_Limit_Dewpoint_Temperature: Annotated[float, Field()]
    """Enter the maximum outdoor dewpoint temperature limit for FixedDewPointAndDryBulb"""

    Electronic_Enthalpy_Limit_Curve_Name: Annotated[str, Field()]
    """Enter the name of a quadratic or cubic curve which defines the maximum outdoor"""

    Economizer_Minimum_Limit_Dry_Bulb_Temperature: Annotated[float, Field()]
    """Enter the minimum outdoor dry-bulb temperature limit for economizer control."""

    Lockout_Type: Annotated[Literal['NoLockout', 'LockoutWithHeating', 'LockoutWithCompressor'], Field(default='NoLockout')]

    Minimum_Limit_Type: Annotated[Literal['FixedMinimum', 'ProportionalMinimum'], Field(default='ProportionalMinimum')]

    Minimum_Outdoor_Air_Schedule_Name: Annotated[str, Field()]
    """Schedule values multiply the minimum outdoor air flow rate"""

    Minimum_Fraction_Of_Outdoor_Air_Schedule_Name: Annotated[str, Field()]
    """schedule values multiply the design/mixed air flow rate"""

    Maximum_Fraction_Of_Outdoor_Air_Schedule_Name: Annotated[str, Field()]
    """schedule values multiply the design/mixed air flow rate"""

    Mechanical_Ventilation_Controller_Name: Annotated[str, Field()]
    """Enter the name of a Controller:MechanicalVentilation object."""

    Time_Of_Day_Economizer_Control_Schedule_Name: Annotated[str, Field()]
    """Optional schedule to simulate "push-button" type economizer control."""

    High_Humidity_Control: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Optional field to enable modified outdoor air flow rates based on zone relative humidity."""

    Humidistat_Control_Zone_Name: Annotated[str, Field()]
    """Enter the name of the zone where the humidistat is located."""

    High_Humidity_Outdoor_Air_Flow_Ratio: Annotated[float, Field(gt=0.0, default=1.0)]
    """Enter the ratio of outdoor air to the maximum outdoor air flow rate when modified air"""

    Control_High_Indoor_Humidity_Based_On_Outdoor_Humidity_Ratio: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """If No is selected, the outdoor air flow rate is modified any time indoor relative"""

    Heat_Recovery_Bypass_Control_Type: Annotated[Literal['BypassWhenWithinEconomizerLimits', 'BypassWhenOAFlowGreaterThanMinimum'], Field(default='BypassWhenWithinEconomizerLimits')]
    """BypassWhenWithinEconomizerLimits specifies that heat recovery"""