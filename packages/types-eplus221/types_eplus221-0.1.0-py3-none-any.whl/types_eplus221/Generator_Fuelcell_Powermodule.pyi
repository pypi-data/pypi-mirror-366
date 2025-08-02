from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Fuelcell_Powermodule(EpBunch):
    """Describe the core power module subsystem of a fuel cell power generator. This includes"""

    Name: Annotated[str, Field(default=...)]

    Efficiency_Curve_Mode: Annotated[Literal['Annex42', 'Normalized'], Field()]

    Efficiency_Curve_Name: Annotated[str, Field(default=...)]

    Nominal_Efficiency: Annotated[str, Field()]
    """This field is not used."""

    Nominal_Electrical_Power: Annotated[str, Field()]
    """This field is not used"""

    Number_Of_Stops_At_Start_Of_Simulation: Annotated[str, Field()]
    """this is Nstops in SOFC model specification"""

    Cycling_Performance_Degradation_Coefficient: Annotated[str, Field()]
    """this is D in SOFC model specification"""

    Number_Of_Run_Hours_At_Beginning_Of_Simulation: Annotated[str, Field()]

    Accumulated_Run_Time_Degradation_Coefficient: Annotated[str, Field()]
    """this is L in SOFC model specification"""

    Run_Time_Degradation_Initiation_Time_Threshold: Annotated[str, Field()]

    Power_Up_Transient_Limit: Annotated[str, Field()]
    """Maximum rate of change in electrical output [power increasing]"""

    Power_Down_Transient_Limit: Annotated[str, Field()]
    """Maximum rate of change in electrical output [power decreasing]"""

    Start_Up_Time: Annotated[str, Field()]
    """Time from start up to normal operation"""

    Start_Up_Fuel: Annotated[str, Field()]

    Start_Up_Electricity_Consumption: Annotated[str, Field()]

    Start_Up_Electricity_Produced: Annotated[str, Field()]

    Shut_Down_Time: Annotated[str, Field()]

    Shut_Down_Fuel: Annotated[str, Field()]

    Shut_Down_Electricity_Consumption: Annotated[str, Field()]

    Ancillary_Electricity_Constant_Term: Annotated[str, Field()]

    Ancillary_Electricity_Linear_Term: Annotated[str, Field()]

    Skin_Loss_Calculation_Mode: Annotated[Literal['ConstantRate', 'UAForProcessGasTemperature', 'QuadraticFunctionOfFuelRate'], Field()]

    Zone_Name: Annotated[str, Field()]

    Skin_Loss_Radiative_Fraction: Annotated[str, Field()]

    Constant_Skin_Loss_Rate: Annotated[str, Field()]

    Skin_Loss_U_Factor_Times_Area_Term: Annotated[str, Field()]

    Skin_Loss_Quadratic_Curve_Name: Annotated[str, Field()]
    """curve is function of fuel use rate"""

    Dilution_Air_Flow_Rate: Annotated[str, Field()]

    Stack_Heat_Loss_To_Dilution_Air: Annotated[str, Field()]

    Dilution_Inlet_Air_Node_Name: Annotated[str, Field()]

    Dilution_Outlet_Air_Node_Name: Annotated[str, Field()]

    Minimum_Operating_Point: Annotated[str, Field()]

    Maximum_Operating_Point: Annotated[str, Field()]