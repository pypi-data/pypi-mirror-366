from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Curve_Bicubic(EpBunch):
    """Cubic curve with two independent variables. Input consists of the"""

    Name: Annotated[str, Field(default=...)]

    Coefficient1_Constant: Annotated[float, Field(default=...)]

    Coefficient2_x: Annotated[float, Field(default=...)]

    Coefficient3_x2: Annotated[float, Field(default=...)]

    Coefficient4_y: Annotated[float, Field(default=...)]

    Coefficient5_y2: Annotated[float, Field(default=...)]

    Coefficient6_xy: Annotated[float, Field(default=...)]

    Coefficient7_x3: Annotated[float, Field(default=...)]

    Coefficient8_y3: Annotated[float, Field(default=...)]

    Coefficient9_x2y: Annotated[float, Field(default=...)]

    Coefficient10_xy2: Annotated[float, Field(default=...)]

    Minimum_Value_of_x: Annotated[float, Field(default=...)]

    Maximum_Value_of_x: Annotated[float, Field(default=...)]

    Minimum_Value_of_y: Annotated[float, Field(default=...)]

    Maximum_Value_of_y: Annotated[float, Field(default=...)]

    Minimum_Curve_Output: Annotated[float, Field()]
    """Specify the minimum value calculated by this curve object"""

    Maximum_Curve_Output: Annotated[float, Field()]
    """Specify the maximum value calculated by this curve object"""

    Input_Unit_Type_for_X: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance'], Field(default='Dimensionless')]

    Input_Unit_Type_for_Y: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance'], Field(default='Dimensionless')]

    Output_Unit_Type: Annotated[Literal['Dimensionless', 'Capacity', 'Power', 'Temperature'], Field(default='Dimensionless')]