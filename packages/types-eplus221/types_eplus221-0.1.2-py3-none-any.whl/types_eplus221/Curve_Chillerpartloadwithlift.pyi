from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Curve_Chillerpartloadwithlift(EpBunch):
    """This chiller part-load performance curve has three independent variables."""

    Name: Annotated[str, Field(default=...)]

    Coefficient1_C1: Annotated[float, Field(default=...)]

    Coefficient2_C2: Annotated[float, Field(default=...)]

    Coefficient3_C3: Annotated[float, Field(default=...)]

    Coefficient4_C4: Annotated[float, Field(default=...)]

    Coefficient5_C5: Annotated[float, Field(default=...)]

    Coefficient6_C6: Annotated[float, Field(default=...)]

    Coefficient7_C7: Annotated[float, Field(default=...)]

    Coefficient8_C8: Annotated[float, Field(default=...)]

    Coefficient9_C9: Annotated[float, Field(default=...)]

    Coefficient10_C10: Annotated[float, Field(default=...)]

    Coefficient11_C11: Annotated[float, Field(default=...)]

    Coefficient12_C12: Annotated[float, Field(default=...)]

    Minimum_Value_of_x: Annotated[float, Field(default=...)]

    Maximum_Value_of_x: Annotated[float, Field(default=...)]

    Minimum_Value_of_y: Annotated[float, Field(default=...)]

    Maximum_Value_of_y: Annotated[float, Field(default=...)]

    Minimum_Value_of_z: Annotated[float, Field(default=...)]

    Maximum_Value_of_z: Annotated[float, Field(default=...)]

    Minimum_Curve_Output: Annotated[float, Field()]
    """Specify the minimum value calculated by this curve object"""

    Maximum_Curve_Output: Annotated[float, Field()]
    """Specify the maximum value calculated by this curve object"""

    Input_Unit_Type_for_x: Annotated[Literal['Dimensionless'], Field(default='Dimensionless')]

    Input_Unit_Type_for_y: Annotated[Literal['Dimensionless'], Field(default='Dimensionless')]

    Input_Unit_Type_for_z: Annotated[Literal['Dimensionless'], Field(default='Dimensionless')]

    Output_Unit_Type: Annotated[Literal['Dimensionless'], Field(default='Dimensionless')]