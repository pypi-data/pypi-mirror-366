from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Fuelcell_Exhaustgastowaterheatexchanger(EpBunch):
    """Describes the exhaust gas heat exchanger subsystem of a fuel cell power generator"""

    Name: Annotated[str, Field(default=...)]

    Heat_Recovery_Water_Inlet_Node_Name: Annotated[str, Field()]

    Heat_Recovery_Water_Outlet_Node_Name: Annotated[str, Field()]

    Heat_Recovery_Water_Maximum_Flow_Rate: Annotated[str, Field()]

    Exhaust_Outlet_Air_Node_Name: Annotated[str, Field()]

    Heat_Exchanger_Calculation_Method: Annotated[Literal['FixedEffectiveness', 'EmpiricalUAeff', 'FundementalUAeff', 'Condensing'], Field()]

    Method_1_Heat_Exchanger_Effectiveness: Annotated[str, Field()]

    Method_2_Parameter_Hxs0: Annotated[str, Field()]

    Method_2_Parameter_Hxs1: Annotated[str, Field()]

    Method_2_Parameter_Hxs2: Annotated[str, Field()]

    Method_2_Parameter_Hxs3: Annotated[str, Field()]

    Method_2_Parameter_Hxs4: Annotated[str, Field()]

    Method_3_H0Gas_Coefficient: Annotated[str, Field()]

    Method_3_Ndotgasref_Coefficient: Annotated[str, Field()]

    Method_3_N_Coefficient: Annotated[str, Field()]

    Method_3_Gas_Area: Annotated[str, Field()]

    Method_3_H0_Water_Coefficient: Annotated[str, Field()]

    Method_3_N_Dot_Water_Ref_Coefficient: Annotated[str, Field()]

    Method_3_M_Coefficient: Annotated[str, Field()]

    Method_3_Water_Area: Annotated[str, Field()]

    Method_3_F_Adjustment_Factor: Annotated[str, Field()]

    Method_4_Hxl1_Coefficient: Annotated[str, Field()]

    Method_4_Hxl2_Coefficient: Annotated[str, Field()]

    Method_4_Condensation_Threshold: Annotated[str, Field()]