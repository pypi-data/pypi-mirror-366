from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Generator_Fuelcell_Stackcooler(EpBunch):
    """This object is optional and is used to define details needed to model the stack cooler"""

    Name: Annotated[str, Field(default=...)]

    Heat_Recovery_Water_Inlet_Node_Name: Annotated[str, Field()]

    Heat_Recovery_Water_Outlet_Node_Name: Annotated[str, Field()]

    Nominal_Stack_Temperature: Annotated[str, Field()]

    Actual_Stack_Temperature: Annotated[str, Field()]

    Coefficient_r0: Annotated[str, Field()]

    Coefficient_r1: Annotated[str, Field()]

    Coefficient_r2: Annotated[str, Field()]

    Coefficient_r3: Annotated[str, Field()]

    Stack_Coolant_Flow_Rate: Annotated[str, Field()]

    Stack_Cooler_UFactor_Times_Area_Value: Annotated[str, Field()]

    Fscogen_Adjustment_Factor: Annotated[str, Field()]

    Stack_Cogeneration_Exchanger_Area: Annotated[str, Field()]

    Stack_Cogeneration_Exchanger_Nominal_Flow_Rate: Annotated[str, Field()]

    Stack_Cogeneration_Exchanger_Nominal_Heat_Transfer_Coefficient: Annotated[str, Field()]

    Stack_Cogeneration_Exchanger_Nominal_Heat_Transfer_Coefficient_Exponent: Annotated[str, Field()]

    Stack_Cooler_Pump_Power: Annotated[str, Field()]

    Stack_Cooler_Pump_Heat_Loss_Fraction: Annotated[str, Field()]

    Stack_Air_Cooler_Fan_Coefficient_f0: Annotated[str, Field()]

    Stack_Air_Cooler_Fan_Coefficient_f1: Annotated[str, Field()]

    Stack_Air_Cooler_Fan_Coefficient_f2: Annotated[str, Field()]