from typing import Annotated, Literal
from pydantic import Field

from eppy.bunch_subclass import EpBunch

class Curve_Triquadratic(EpBunch):
    """Quadratic curve with three independent variables. Input consists of the curve name,"""

    Name: Annotated[str, Field(default=...)]

    Coefficient1_Constant: Annotated[float, Field()]

    Coefficient2_X__2: Annotated[float, Field()]

    Coefficient3_X: Annotated[float, Field()]

    Coefficient4_Y__2: Annotated[float, Field()]

    Coefficient5_Y: Annotated[float, Field()]

    Coefficient6_Z__2: Annotated[float, Field()]

    Coefficient7_Z: Annotated[float, Field()]

    Coefficient8_X__2_Y__2: Annotated[float, Field()]

    Coefficient9_X_Y: Annotated[float, Field()]

    Coefficient10_X_Y__2: Annotated[float, Field()]

    Coefficient11_X__2_Y: Annotated[float, Field()]

    Coefficient12_X__2_Z__2: Annotated[float, Field()]

    Coefficient13_X_Z: Annotated[float, Field()]

    Coefficient14_X_Z__2: Annotated[float, Field()]

    Coefficient15_X__2_Z: Annotated[float, Field()]

    Coefficient16_Y__2_Z__2: Annotated[float, Field()]

    Coefficient17_Y_Z: Annotated[float, Field()]

    Coefficient18_Y_Z__2: Annotated[float, Field()]

    Coefficient19_Y__2_Z: Annotated[float, Field()]

    Coefficient20_X__2_Y__2_Z__2: Annotated[float, Field()]

    Coefficient21_X__2_Y__2_Z: Annotated[float, Field()]

    Coefficient22_X__2_Y_Z__2: Annotated[float, Field()]

    Coefficient23_X_Y__2_Z__2: Annotated[float, Field()]

    Coefficient24_X__2_Y_Z: Annotated[float, Field()]

    Coefficient25_X_Y__2_Z: Annotated[float, Field()]

    Coefficient26_X_Y_Z__2: Annotated[float, Field()]

    Coefficient27_X_Y_Z: Annotated[float, Field()]

    Minimum_Value_Of_X: Annotated[float, Field()]

    Maximum_Value_Of_X: Annotated[float, Field()]

    Minimum_Value_Of_Y: Annotated[float, Field()]

    Maximum_Value_Of_Y: Annotated[float, Field()]

    Minimum_Value_Of_Z: Annotated[float, Field()]

    Maximum_Value_Of_Z: Annotated[float, Field()]

    Minimum_Curve_Output: Annotated[float, Field()]
    """Specify the minimum value calculated by this curve object"""

    Maximum_Curve_Output: Annotated[float, Field()]
    """Specify the maximum value calculated by this curve object"""

    Input_Unit_Type_For_X: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance'], Field(default='Dimensionless')]

    Input_Unit_Type_For_Y: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance'], Field(default='Dimensionless')]

    Input_Unit_Type_For_Z: Annotated[Literal['Dimensionless', 'Temperature', 'VolumetricFlow', 'MassFlow', 'Power', 'Distance'], Field(default='Dimensionless')]

    Output_Unit_Type: Annotated[Literal['Dimensionless', 'Capacity', 'Power', 'Temperature'], Field(default='Dimensionless')]