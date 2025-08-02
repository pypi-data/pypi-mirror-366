from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coil_Cooling_Dx_Singlespeed(EpBunch):
    """Direct expansion (DX) cooling coil and condensing unit (includes electric compressor"""

    Name: Annotated[str, Field(default=...)]

    Availability_Schedule_Name: Annotated[str, Field()]
    """Availability schedule name for this system. Schedule value > 0 means the system is available."""

    Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(default=..., ge=0.5, le=1.0)]
    """Rated sensible heat ratio (gross sensible capacity/gross total capacity)"""

    Gross_Rated_Cooling_Cop: Annotated[float, Field(gt=0.0, default=3.0)]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Flow rate corresponding to rated total cooling capacity, Rated SHR and Rated COP"""

    Rated_Evaporator_Fan_Power_Per_Volume_Flow_Rate: Annotated[float, Field(ge=0.0, le=1250.0, default=773.3)]
    """Enter the evaporator fan power per air volume flow rate at the rated test conditions."""

    Air_Inlet_Node_Name: Annotated[str, Field(default=...)]

    Air_Outlet_Node_Name: Annotated[str, Field(default=...)]

    Total_Cooling_Capacity_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Total_Cooling_Capacity_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Energy_Input_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Energy_Input_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Minimum_Outdoor_Dry_Bulb_Temperature_For_Compressor_Operation: Annotated[float, Field(default=-25.0)]

    Nominal_Time_For_Condensate_Removal_To_Begin: Annotated[float, Field(ge=0.0, le=3000.0, default=0.0)]
    """The nominal time for condensate to begin leaving the coil's condensate"""

    Ratio_Of_Initial_Moisture_Evaporation_Rate_And_Steady_State_Latent_Capacity: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """Ratio of the initial moisture evaporation rate from the cooling coil (when"""

    Maximum_Cycling_Rate: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """The maximum on-off cycling Rate for the compressor, which occurs at 50% run time"""

    Latent_Capacity_Time_Constant: Annotated[float, Field(ge=0.0, le=500.0, default=0.0)]
    """Time constant for the cooling coil's latent capacity to reach steady state after"""

    Condenser_Air_Inlet_Node_Name: Annotated[str, Field()]
    """Enter the name of an outdoor air node. This node name is also specified in"""

    Condenser_Type: Annotated[Literal['AirCooled', 'EvaporativelyCooled'], Field(default='AirCooled')]

    Evaporative_Condenser_Effectiveness: Annotated[float, Field(ge=0.0, le=1.0, default=0.9)]

    Evaporative_Condenser_Air_Flow_Rate: Annotated[float, Field(gt=0.0)]
    """Used to calculate evaporative condenser water use"""

    Evaporative_Condenser_Pump_Rated_Power_Consumption: Annotated[float, Field(ge=0.0, default=0.0)]
    """Rated power consumed by the evaporative condenser's water pump"""

    Crankcase_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]

    Maximum_Outdoor_Dry_Bulb_Temperature_For_Crankcase_Heater_Operation: Annotated[float, Field(ge=0.0, default=10.0)]

    Supply_Water_Storage_Tank_Name: Annotated[str, Field()]

    Condensate_Collection_Water_Storage_Tank_Name: Annotated[str, Field()]

    Basin_Heater_Capacity: Annotated[float, Field(ge=0.0, default=0.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled and for periods"""

    Basin_Heater_Setpoint_Temperature: Annotated[float, Field(ge=2.0, default=2.0)]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Basin_Heater_Operating_Schedule_Name: Annotated[str, Field()]
    """This field is only used for Condenser Type = EvaporativelyCooled."""

    Sensible_Heat_Ratio_Function_Of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*db + e*db**2 + f*wb*db"""

    Sensible_Heat_Ratio_Function_Of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""

    Report_Ashrae_Standard_127_Performance_Ratings: Annotated[Literal['Yes', 'No'], Field(default='No')]
    """when this input field is specified as Yes then the program calculates the net cooling"""

    Zone_Name_For_Condenser_Placement: Annotated[str, Field()]
    """This input field is name of a conditioned or unconditioned zone where the secondary"""