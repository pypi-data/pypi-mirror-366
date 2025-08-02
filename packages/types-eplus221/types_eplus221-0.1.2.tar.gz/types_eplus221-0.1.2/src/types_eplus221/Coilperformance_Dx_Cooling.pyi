from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Coilperformance_Dx_Cooling(EpBunch):
    """Used to specify DX cooling coil performance for one mode of operation for a"""

    Name: Annotated[str, Field(default=...)]

    Gross_Rated_Total_Cooling_Capacity: Annotated[float, Field(default=..., gt=0.0)]
    """Total cooling capacity not accounting for the effect of supply air fan heat"""

    Gross_Rated_Sensible_Heat_Ratio: Annotated[float, Field(default=..., ge=0.5, le=1.0)]
    """Rated sensible heat ratio (gross sensible capacity/gross total capacity)"""

    Gross_Rated_Cooling_COP: Annotated[float, Field(gt=0.0, default=3.0)]
    """Gross cooling capacity divided by power input to the compressor and outdoor fan,"""

    Rated_Air_Flow_Rate: Annotated[float, Field(default=..., gt=0.0)]
    """Flow rate corresponding to Rated total Cooling capacity, Rated SHR and Rated COP"""

    Fraction_of_Air_Flow_Bypassed_Around_Coil: Annotated[float, Field(ge=0.0, lt=1.0, default=0.0)]
    """Fraction of Rated Air Flow Rate which bypasses the cooling coil"""

    Total_Cooling_Capacity_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Total_Cooling_Capacity_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Energy_Input_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field(default=...)]
    """curve = a + b*wb + c*wb**2 + d*edb + e*edb**2 + f*wb*edb"""

    Energy_Input_Ratio_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*ff + c*ff**2"""

    Part_Load_Fraction_Correlation_Curve_Name: Annotated[str, Field(default=...)]
    """quadratic curve = a + b*PLR + c*PLR**2"""

    Nominal_Time_for_Condensate_Removal_to_Begin: Annotated[float, Field(ge=0.0, le=3000.0, default=0.0)]
    """The nominal time for condensate to begin leaving the coil's condensate"""

    Ratio_of_Initial_Moisture_Evaporation_Rate_and_Steady_State_Latent_Capacity: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """Ratio of the initial moisture evaporation rate from the cooling coil (when"""

    Maximum_Cycling_Rate: Annotated[float, Field(ge=0.0, le=5.0, default=0.0)]
    """The maximum on-off cycling rate for the compressor, which occurs at 50% run time"""

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

    Sensible_Heat_Ratio_Function_of_Temperature_Curve_Name: Annotated[str, Field()]
    """curve = a + b*wb + c*wb**2 + d*db + e*db**2 + f*wb*db"""

    Sensible_Heat_Ratio_Function_of_Flow_Fraction_Curve_Name: Annotated[str, Field()]
    """quadratic curve = a + b*ff + c*ff**2"""