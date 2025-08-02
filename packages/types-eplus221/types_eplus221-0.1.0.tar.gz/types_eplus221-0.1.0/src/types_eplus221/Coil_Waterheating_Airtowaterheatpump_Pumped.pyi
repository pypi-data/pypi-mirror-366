from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Waterheating_Airtowaterheatpump_Pumped(EpBunch):
    """Heat pump water heater (HPWH) heating coil, air-to-water direct-expansion (DX)"""

    Name: Annotated[str, Field(default=...)]
    """Unique name for this instance of a heat pump water heater DX coil."""

    Rated_Heating_Capacity: Annotated[float, Field(default=..., gt=0)]
    """Heating capacity at the rated inlet air temperatures, rated condenser inlet"""

    Rated_Cop: Annotated[float, Field(gt=0, default=3.2)]
    """Heating coefficient of performance at the rated inlet air temperatures,"""

    Rated_Sensible_Heat_Ratio: Annotated[float, Field(ge=0.5, le=1, default=0.85)]
    """Gross air-side sensible heat ratio at the rated inlet air temperatures,"""

    Rated_Evaporator_Inlet_Air_Dry_Bulb_Temperature: Annotated[float, Field(gt=5, default=19.7)]
    """Evaporator inlet air dry-bulb temperature corresponding to rated coil performance"""

    Rated_Evaporator_Inlet_Air_Wet_Bulb_Temperature: Annotated[float, Field(gt=5, default=13.5)]
    """Evaporator inlet air wet-bulb temperature corresponding to rated coil performance"""

    Rated_Condenser_Inlet_Water_Temperature: Annotated[float, Field(gt=25, default=57.5)]
    """Condenser inlet water temperature corresponding to rated coil performance"""

    Rated_Evaporator_Air_Flow_Rate: Annotated[float, Field(gt=0)]
    """Evaporator air flow rate corresponding to rated coil performance"""

    Rated_Condenser_Water_Flow_Rate: Annotated[float, Field(gt=0)]
    """Condenser water flow rate corresponding to rated coil performance"""

    Evaporator_Fan_Power_Included_In_Rated_Cop: Annotated[Literal['Yes', 'No'], Field(default='Yes')]
    """Select Yes if the evaporator fan power is included in the rated COP. This choice field"""

    Condenser_Pump_Power_Included_In_Rated_Cop: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Select Yes if the condenser pump power is included in the rated COP. This choice field"""

    Condenser_Pump_Heat_Included_In_Rated_Heating_Capacity_And_Rated_Cop: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """Select Yes if the condenser pump heat is included in the rated heating capacity and"""

    Condenser_Water_Pump_Power: Annotated[float, Field(ge=0, default=0)]
    """A warning message will be issued if the ratio of Condenser Water Pump Power to Rated"""

    Fraction_Of_Condenser_Pump_Heat_To_Water: Annotated[float, Field(ge=0, le=1, default=0.2)]
    """Fraction of pump heat transferred to the condenser water. The pump is assumed"""

    Evaporator_Air_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """The node from which the DX coil draws its inlet air."""

    Evaporator_Air_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """The node to which the DX coil sends its outlet air."""

    Condenser_Water_Inlet_Node_Name: Annotated[str, Field(default=...)]
    """The node from which the DX coil condenser draws its inlet water."""

    Condenser_Water_Outlet_Node_Name: Annotated[str, Field(default=...)]
    """The node to which the DX coil condenser sends its outlet water."""

    Crankcase_Heater_Capacity: Annotated[float, Field(ge=0, default=0)]
    """The compressor crankcase heater only operates when the dry-bulb temperature of air"""

    Maximum_Ambient_Temperature_For_Crankcase_Heater_Operation: Annotated[float, Field(ge=0, default=10)]
    """The compressor crankcase heater only operates when the dry-bulb temperature of air"""

    Evaporator_Air_Temperature_Type_For_Curve_Objects: Annotated[Literal['DryBulbTemperature', 'WetBulbTemperature'], Field(default='WetBulbTemperature')]
    """Determines temperature type for heating capacity curves and"""

    Heating_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Heating capacity modifier curve (function of temperature) should be biquadratic or cubic."""

    Heating_Capacity_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Heating capacity modifier curve (function of air flow fraction) should be quadratic or cubic."""

    Heating_Capacity_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Heating capacity modifier curve (function of water flow fraction) should be quadratic or cubic."""

    Heating_Cop_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """Heating COP modifier curve (function of temperature) should be biquadratic or cubic."""

    Heating_Cop_Function_Of_Air_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Heating COP modifier curve (function of air flow fraction) should be quadratic or cubic."""

    Heating_Cop_Function_Of_Water_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """Heating COP modifier curve (function of water flow fraction) should be quadratic or cubic."""

    Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field()]
    """Part Load Fraction Correlation (function of part load ratio) should be quadratic or cubic."""